from django.conf.urls import url

from . import views

urlpatterns = [

    # 注册
    url(r'^areas/$', views.AreasView.as_view()),
]
