import pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):
    """合并购物车"""
    # 先获取cookie购物车数据
    cart_str = request.COOKIES.get('carts')
    # 判断是否有cookie购物车数据,如果没有,提前结束函数
    if cart_str is None:
        return

    # 把cart_str 转换成 cart_dict
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 创建redis连接对象
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    user = request.user  # 获取当前用户
    # 遍历cookie购物车大字典
    for sku_id in cart_dict:
        # 将sku_id和count向 hash中添加 存在即修改,不存在就新增
        pl.hset('cart_%s' % user.id, sku_id, cart_dict[sku_id]['count'])
        if cart_dict[sku_id]['selected']:
            # 判断当前cookie中商品是否勾选,如果勾选就将sku_id添加到set,
            pl.sadd('selected_%s' % user.id, sku_id)
        else:
            # 不勾选就从set中移除
            pl.srem('selected_%s' % user.id, sku_id)

    pl.execute()  # 执行管道

    # 将cookie购物车数据删除
    response.delete_cookie('carts')
