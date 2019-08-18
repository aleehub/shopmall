"""meiduoMall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [

    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),

    # URL路径命名查询参数：英文问号加大写P，后面采用正则表达式
    # 用户名重复查询
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view()),

    # URL路径命名查询参数：英文问号加大写P，后面采用正则表达式
    # 手机号重复查询
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view()),

    # 登录界面
    url(r'^login/$', views.LoginView.as_view(), name='login'),

    # 退出登录状态
    url(r'^logout/$', views.Logout.as_view(), name='logout'),

    # 用户中心
    # login_required()装饰器，判断用户是否登录
    # 内部封装了is_authenticated()函数
    # 逻辑，如果用户登录了，则进入到视图内部，执行视图逻辑
    # 如果未通过登录，则重定向到LOGIN_URL配置项指定的地址
    # LOGIN_URL 配置在django全局配置文件里
    # login_required()里在URL路径里面集成了next参数，参数值如果没通过验证要去往的路径
    # url(r'^info/$', login_required(views.UserInfoView.as_view()), name='info')

    url(r'^info/$', views.UserInfoView.as_view(), name='info'),  # 此时采用在类里继承父类验证类

    url(r'^emails/$', views.EmailView.as_view(), name='emails')  # 此时采用在类里继承父类验证类

]
