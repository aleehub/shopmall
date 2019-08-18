from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.views import View

# 导入qq登录模块工具包
from QQLoginTool.QQtool import OAuthQQ  #

from django.conf import settings

from .models import OAuthQQUser
from meiduoMall.utils.response_code import RETCODE
from django.http import HttpResponseForbidden
import logging
from django.contrib.auth import login
from .utils import generate_openid_signature, check_openid_signature

logger = logging.getLogger('django')

class QQAuthURLView(View):
    """提供QQ登录页面网址"""

    def get(self, request):

        # next表示从哪个页面进入我的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')

        # 获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=True)

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
                        redirect_uri=settings.QQ_REDIRECT_URI, state=True)

        try:

            # 使用code向QQ服务器请求access_token

            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)

        except Exception as e:
            logger.error(e)

            return HttpResponseServerError("OAuth2.0认证失败")

        else:

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
                next = request.GET.get('state')

                response = redirect(next)

                # 登录时用户名写入到cookie，有效期15天
                response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 14)

                return response
