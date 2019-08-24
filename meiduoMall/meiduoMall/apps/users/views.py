import json

# from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, \
    HttpResponseServerError
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse

from carts.utils import merge_cart_cookie_to_redis
from meiduoMall.utils import constants
from meiduoMall.utils.response_code import RETCODE
from .models import User, Address
import re
from django.contrib.auth import mixins
from django.conf import settings
from meiduoMall.utils.views import LoginRequiredView
from celery_tasks.email.tasks import send_verify_email

from .utils import generate_email_verify_url, check_email_verify_url
from django_redis import get_redis_connection

from goods.models import *
import logging

logger = logging.getLogger('django')


# Create your views here.

class RegisterView(View):
    """类视图：处理注册"""

    def get(self, request):
        """处理GET请求，返回注册页面"""
        return render(request, 'register.html')

    # form 提交表单地址如果不写的话，会自动提交给本地地址

    def post(self, request):
        """ 处理POST请求：实现注册逻辑"""

        username = request.POST.get('username')

        password = request.POST.get('password')

        password2 = request.POST.get('password2')

        mobile = request.POST.get('mobile')

        allow = request.POST.get('allow')

        # 判断参数是否齐全

        # all函数  none null "" [] {}  遇到空值都会返回false
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden('缺少必传参数')

        # 判断用户名是否是8~20个字符

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('用户名格式不对')

        # 判断密码是否是8-20个数字

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('密码格式不对')

        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseForbidden('两次的密码不一样')

        # 判断手机号是否合法

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('手机号格式不对')
        # 判断是否勾选用户协议

        # checkbox  如果没有设置预定值，则会传来on的字符串
        if allow != 'on':
            return HttpResponseForbidden('用户未勾选用户协议')

        # 保存用户数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)

        except Exception as e:

            print(e)


            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 状态保持

        # 登入用户，实现状态保持
        # 用户登录本质 ：
        # 状态保持
        # 将通过认证的用户的唯一标识信息写入到当前浏览器的cookie和服务端的session中
        # django 用户认证系统提供了login()方法
        # 封装了写入session的操作，帮助我们快速登入一个用户，并保持状态

        login(request, user)

        # 响应注册结果
        # return redirect(reverse("contents:index"))
        response = redirect('/')  # 创建好响应对象
        # setting 中的SESSION_COOKIE_AGE值在global.setting中，默认为两周
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
        # merge_cart_cookie_to_redis(request, response)
        return response


class UsernameCountView(View):
    """查询用户名重复识视图"""

    def get(self, request, username):
        """

        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """

        # 用模型对象的filter查询，对象是否查到都不会报错，只会返回一个空查询集
        count = User.objects.filter(username=username).count()

        # 采用json返回数据
        # jsonResponse喜欢的参数更喜欢是一个字典类型
        # 有参数safe: 默认为True,当传进来的参数不是字典时，要将safe变量置为false，否则会报错
        # JsonResponse ：默认响应体类型为json格式，利于前端浏览器解析

        # 创建时，会自动验证传输参数的格式：
        # if safe and not isinstance(data, dict):
        #     raise TypeError(
        #         'In order to allow non-dict objects to be serialized set the '
        #         'safe parameter to False.'
        #     )

        # return JsonResponse({'code': RETCODE.OK, 'error_msg': 'OK', 'count': count})

        # 返回的字典类型数据，在返回对象的data属性中
        return JsonResponse({'count': count})


class MobileCountView(View):
    """手机号重复验证"""

    def get(self, request, mobile):
        """

        :param request: 请求对象
        :param mobile:  手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({"count": count})


class LoginView(View):
    """ 用户名登录"""

    def get(self, request):

        """
        提供登录界面
        :param request: 请求对象
        :return: 登录界面
        """

        return render(request, "login.html")

    def post(self, request):

        """
        实现登录逻辑
        :param request: 请求对象
        :return:  登录结果
        """

        # 接收参数

        username = request.POST.get('username')

        password = request.POST.get('password')

        remembered = request.POST.get('remembered')

        # 认证登录用户

        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # 实现登录状态保持

        login(request, user)

        # 设置状态保持的周期

        if remembered != 'on':
            # 没有记住用户： 浏览器会话结束就过期，默认是两周

            request.session.set_expiry(0)

        next = request.GET.get('next')

        # if next:
        #
        #     response = redirect(next)
        #
        #
        # else:
        #     # 响应登录结果
        #
        #     # return redirect(reverse('contents:index'))  实现首页显示登录名，此处要将用户名等信息写出cookie
        #
        #     response = redirect(reverse('contents:index'))

        response = redirect(next or "/")

        # 登录时用户名写入cookie，有效期14天
        response.set_cookie('username', user.username,
                            max_age=(None if remembered is None else settings.SESSION_COOKIE_AGE))

        merge_cart_cookie_to_redis(request, response)

        return response


class Logout(View):
    """退出登录"""

    def get(self, request):
        # 清理session

        logout(request)

        # 退出登录，重定向到登录页

        response = redirect(reverse('users:login'))

        response.delete_cookie('username')

        return response


# class UserInfoView(View):
#     """用户中心,当用户登录才能访问用户中心"""
#
#     def get(self, request):
#         """提供个人信息界面"""
#
#         # is_authenticated django用户认证系统提供了方法request.user.is_authenticated()来判断用户是否登录
#         # 如果通过则返回True ,否则返回false
#         # 缺点，登录验证逻辑很多地方都需要，所以该代码需要重复编码好多次
#         # if request.user.is_authenticated():
#         #     return render(request, 'user_center_info.html')
#         #
#         # else:
#         #     return redirect(reverse("users:login"))
#
#         return render(request, 'user_center_info.html')
#

class UserInfoView(mixins.LoginRequiredMixin, View):
    """验证用户是否登录扩展类**"""

    def get(self, request):
        """提供个人信息界面"""

        # 为了方便实现用户添加邮箱时的局部刷新
        # 后端渲染的模板数据再传给vue.js
        # 将后端提供的数据传入到user_center_info.js中
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context=context)


class EmailView(LoginRequiredView, View):
    """增加邮箱后端逻辑实现"""

    def put(self, request):
        """实现添加邮箱逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())

        email = json_dict.get('email')

        print(email)

        # 校验参数

        # 先判断有没有邮箱
        if not email:
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少email参数'})

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '邮箱格式错误'})

        # 获取登录用户
        user = request.user

        # 修改email

        # User.objects.filter(username=user.username, email='').update(email=email)
        # 两种修改方式
        user.email = email
        user.save()

        # 发送邮件

        # verify_email = '邮箱验证链接'
        verify_url = generate_email_verify_url(user)


        # subject = "美多商城邮箱验证"
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_email, verify_email)
        #
        # send_mail(subject, "", settings.EMAIL_FROM, [email], html_message=html_message)

        send_verify_email.delay(email, verify_url)
        # 响应 添加邮箱结果

        return JsonResponse({'code': RETCODE.OK, 'errmsg': "添加邮箱成功"})


class VerifyEmailView(LoginRequiredView, View):

    def get(self, request):

        # 接收参数
        token = request.GET.get("token")

        # 校验参数: 判断token是否为空和过期， 提取user

        if not token:
            return HttpResponseBadRequest('缺少token')

        user = check_email_verify_url(token)

        if user is None:
            return HttpResponseForbidden('无效的token')

        # 修改email_active的值为True

        try:

            user.email_active = True
            user.save()

        except Exception as e:

            logger.error(e)

            return HttpResponseServerError('激活邮件失败')

        # 返回邮件验证结果

        return redirect(reverse('users:info'))


class AddressView(LoginRequiredView, View):
    """用户收货地址"""

    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        login_user = request.user

        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


class CreateAddressView(LoginRequiredView, View):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""

        # 判断是否超过地址上限
        # Address.objects.filter(username = request.user).count()

        count = request.user.addresses.count()

        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接收地址参数
        # 来自请求体的json数据，先进行二进制格式转换 ，再进行
        json_dict = json.loads(request.body.decode())

        receiver = json_dict.get('receiver')

        province_id = json_dict.get('province_id')

        city_id = json_dict.get('city_id')

        district_id = json_dict.get('district_id')

        place = json_dict.get('place')

        mobile = json_dict.get('mobile')

        mobile = json_dict.get('mobile')

        tel = json_dict.get('tel')

        email = json_dict.get('email')

        # 校验参数
        # 查询所有获取参数是否为空值
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')

        # 手机号正则表达式

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')

        if tel:
            # 电话校验
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')

        if email:

            # 邮件校验
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )

            # 设置默认地址
            # 查询请求里的用户的默认地址是否为空
            if not request.user.default_address:
                request.user.default_address = address

                request.user.save()

        except Exception as e:

            logger.error(e)

            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class UpdateDestroyAddressView(LoginRequiredView, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址,实际没有删除数据，只是将删除字段置为真"""

        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class DefaultAddressView(LoginRequiredView, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        try:
            # 接收参数,查询地址
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateTitleAddressView(LoginRequiredView, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


class ChangePasswordView(LoginRequiredView, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """实现修改密码逻辑"""

        # 接收参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断旧密码是否正确
        if request.user.check_password(old_password) is False:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return HttpResponseForbidden('两次输入的密码不一致')

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response


class UserBrowseHistory(LoginRequiredView, View):
    """用户浏览记录"""

    def post(self, request):
        """保存用户浏览记录"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('sku不存在')

        # 保存用户浏览数据
        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()
        user_id = request.user.id

        # 先去重
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 再存储
        pl.lpush('history_%s' % user_id, sku_id)
        # 最后截取
        pl.ltrim('history_%s' % user_id, 0, 4)
        # 执行管道
        pl.execute()

        # 响应结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)

        # 根据sku_ids列表数据，查询出商品sku信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})
