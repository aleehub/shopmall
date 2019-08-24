import re
from django_redis import get_redis_connection

from django.http import JsonResponse, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View

# 导入qq登录模块工具包
from QQLoginTool.QQtool import OAuthQQ  #

from django.conf import settings

from carts.utils import merge_cart_cookie_to_redis
from .models import OAuthQQUser
from meiduoMall.utils.response_code import RETCODE
import logging
from django.contrib.auth import login
from .utils import generate_openid_signature, check_openid_signature
from users.models import User


logger = logging.getLogger('django')

class QQAuthURLView(View):
    """提供QQ登录页面网址"""

    def get(self, request):

        # next表示从哪个页面进入我的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')

        # 获取QQ登录页面网址,state参数代表意义
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        login_url = oauth.get_qq_url()

        return JsonResponse({"code": RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthUserView(View):
    """用户扫码登录的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 接收Authorization Code
        code = request.GET.get('code')

        if not code:
            return HttpResponseForbidden("缺少code")

        # 创建工具对象

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:

            # 使用code向QQ服务器请求access_token

            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)

        except Exception as e:
            logger.error(e)

            return HttpResponseServerError("OAuth2.0认证失败")

        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:

            # 如果openid没绑过美多商城用户
            openid = generate_openid_signature(openid)
            context = {'openid': openid}
            return render(request, 'oauth_callback.html', context)

        else:

            # 如果已经绑定过美多商城用户
            qq_user = oauth_user.user
            login(request, qq_user)

            # 响应结果

            # 获取界面跳转来源

            response = redirect(request.GET.get('state') or "/")

            # 登录时用户名写入到cookie，有效期15天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 14)

            merge_cart_cookie_to_redis(request, response)

            return response

    def post(self, request):
        """美多用户绑定到openid"""
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid_sign = request.POST.get('openid')

        # 校验参数
        # 判断参数是否齐全

        if not all([mobile, pwd, sms_code_client]):
            return HttpResponseForbidden("缺少必传参数")

        # 判断手机号是否合法
        if not re.match(r'^1[3-8]\d{8}', mobile):
            return HttpResponseForbidden("请输入正确的手机号码")

        # 判断密码是否合格
        if not re.match(r'^[a-zA-Z0-9]{8,20}', pwd):
            return HttpResponseForbidden("密码格式不正确")

        # 判断短信验证码是否正确

        # 先对redis进行链接
        redis_conn = get_redis_connection('verify_code')
        # 通过手机号的字符串拼接，对数据库进行查询
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 判断数据库是否存在验证码
        if sms_code_server is None:
            return render(request, "oauth_callback.html", {'sms_code_errmsg': '无效的短信验证码'})
        # 如果存在，在进行对比查询到的验证码
        if sms_code_server.decode() != sms_code_client:
            return render(request, "oauth_callback.html", {'sms_code_errmsg': '输入短信验证码有误'})

        # 判断openid是否有效
        openid = check_openid_signature(openid_sign)
        # 防止小人通过第三方接口对服务端发起请求
        if openid is None:
            return render(request, "oauth_callback.html", {'openid_errmsg': '无效的openid'})

        # 保存数据

        try:
            user = User.objects.get(mobile=mobile)

        except User.DoesExist:
            # 用户不存在，新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)

        else:
            # 如果用户存在检查用户密码
            if not user.check_password(pwd):
                return render(request, "oauth_callback.html", {'account_errmsg': '用户名或密码错误'})

        # 将用户名绑定openid

        try:

            OAuthQQUser.objects.create(openid=openid, user=user)

        except Exception as e:

            logger.error(e)

            print(e)

            return render(request, "oauth_callback.html", {'qq_login_errmsg': 'qq登录失败'})

        # 实现状态
        login(request, user)

        # 响应绑定结果

        response = redirect(request.GET.get('state') or "/")

        # 登录时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        merge_cart_cookie_to_redis(request, response)

        return response
