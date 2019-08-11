from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse


# Create your views here.

class RegisterView(View):
    """类视图：处理注册"""

    def get(self, request):
        """处理GET请求，返回注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """ 处理POST请求：实现注册逻辑"""

        return HttpResponse('这里实现注册逻辑')
