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
from django.conf.urls import url, include

from . import views

urlpatterns = [

    # 注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),

    # URL路径命名查询参数：英文问号加大写P，后面采用正则表达式
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view()),
    # URL路径命名查询参数：英文问号加大写P，后面采用正则表达式
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view())
]