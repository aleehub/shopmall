from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import login, logout
from django.urls import reverse

from .models import User

import re


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
        return redirect(reverse("contents:index"))


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
