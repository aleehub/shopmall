from django.shortcuts import render
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction

from meiduoMall.utils.views import LoginRequiredView
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU
from .models import OrderInfo, OrderGoods
from meiduoMall.utils.response_code import RETCODE
import logging

logger = logging.getLogger('django')


class OrderSettlementView(LoginRequiredView):
    """去结算"""

    def get(self, request):
        user = request.user
        # 查询当前登录用户的所有收货地址
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # addresses = addresses if addresses.exists() else None
        # 创建redis连接
        redis_conn = get_redis_connection('carts')
        # 获取hash购物车数据  {sku_id_1: 1, sku_id_2: 1}
        redis_carts = redis_conn.hgetall('cart_%s' % user.id)
        # 获取set购物车数据 {sku_id_1}
        selected_ids = redis_conn.smembers('selected_%s' % user.id)
        # 定义一个字典变量用来包装勾选商品的id和count {sku_id_1: 1}
        cart_dict = {}
        for sku_id_bytes in selected_ids:
            cart_dict[int(sku_id_bytes)] = int(redis_carts[sku_id_bytes])

        # 查询所有要购买商品的sku模型
        skus = SKU.objects.filter(id__in=cart_dict.keys())

        total_count = 0  # 记录商品总数量
        total_amount = Decimal('0.00')  # 商品总价

        # 遍历查询集,给每个sku模型多定义两个属性
        for sku in skus:
            sku.count = cart_dict[sku.id]
            sku.amount = sku.price * sku.count
            total_count += sku.count
            total_amount += sku.amount

        freight = Decimal('10.00')  # 运费

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredView):
    """提交订单"""

    def post(self, request):

        # 1.接收
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        user = request.user
        # 2. 校验
        try:
            address = Address.objects.get(id=address_id, user=user, is_deleted=False)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('address_id有误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('支付方式有误')

        # 生成订单编号: 20190820145030 + 000001
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id

        # 判断定义状态
        status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                  if (pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'])
                  else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        with transaction.atomic():  # 手动开启事务
            # 超卖
            # 创建事务保存点
            save_point = transaction.savepoint()
            try:
                # 3. 存储一条订单基本信息记录(一) OrderInfo
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                # 4. 获取购物车中redis数据
                # 创建redis连接
                redis_conn = get_redis_connection('carts')
                # 获取hash和set数据
                redis_carts = redis_conn.hgetall('cart_%s' % user.id)
                selected_ids = redis_conn.smembers('selected_%s' % user.id)
                # 定义一个字典用来装要购买的商品id和count
                cart_dict = {}
                for sku_id_bytes in selected_ids:
                    cart_dict[int(sku_id_bytes)] = int(redis_carts[sku_id_bytes])

                # 遍历要购买商品的大字典
                for sku_id in cart_dict:

                    while True:
                        # 获取sku模型
                        sku = SKU.objects.get(id=sku_id)
                        # 获取当前商品要购买的数量
                        buy_count = cart_dict[sku_id]
                        # 获取商品原有的库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # import time
                        # time.sleep(5)

                        # 判断库存
                        if buy_count > origin_stock:
                            # 回滚
                            transaction.savepoint_rollback(save_point)
                            return http.JsonResponse({"code": RETCODE.STOCKERR, 'errmsg': '库存不足'})
                        # 计算sku库存和销量
                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count
                        # 修改sku库存和销量
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        # 如果修改库存销量失败
                        if result == 0:
                            continue

                        # 修改spu
                        spu = sku.spu
                        spu.sales += buy_count
                        spu.save()

                        # 存储订单中商品信息记录(多)(OrderGoods)
                        order_goods = OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )

                        # 累加购买商品总数量
                        order.total_count += buy_count
                        # 累加商品总价
                        order.total_amount += (sku.price * buy_count)
                        # 当执行到这里说明当前这个商品购买成功,退下死循环
                        break

                # 累加运费一定要写在for外面
                order.total_amount += order.freight
                order.save()
            except Exception as error:
                logger.error(error)
                # 暴力回滚
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            else:
                # 提交事务
                transaction.savepoint_commit(save_point)

        pl = redis_conn.pipeline()
        # 删除购物车中已被购买的商品
        pl.hdel('cart_%s' % user.id, *selected_ids)  # 将hash中已购买商品全移除
        pl.delete('selected_%s' % user.id)  # 将set移除
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order_id})


class OrderSuccessView(LoginRequiredView):
    """展示订单提交成功界面"""

    def get(self, request):
        # 接收查询参数
        query_dict = request.GET
        payment_amount = query_dict.get('payment_amount')
        order_id = query_dict.get('order_id')
        pay_method = query_dict.get('pay_method')
        # 校验
        try:
            OrderInfo.objects.get(order_id=order_id, pay_method=pay_method, total_amount=payment_amount)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单有误')

        context = {
            'payment_amount': payment_amount,
            'order_id': order_id,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)
