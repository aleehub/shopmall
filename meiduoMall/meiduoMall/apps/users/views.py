from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden

from .models import User

import re


# Create your views here.

class RegisterView(View):
    """类视图：处理注册"""

    def get(self, request):
        """处理GET请求，返回注册页面"""
        return render(request, 'register.html')

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
            User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        return HttpResponse('这里实现注册逻辑')
