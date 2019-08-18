from django.conf.urls import url

from . import views

urlpatterns = [

    # 获取QQ登录url
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # QQ成功登录后的回调地址
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view()),
]
