# celery 启动文件
# 要在celery 上级目录去启动，不然找不到celery_tasks 模块

from celery import Celery
import os

# import sys
# print(sys.path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduoMall.settings.dev")

# 创建celery实例

celery_app = Celery('meiduo')

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册celery任务

celery_app.autodiscover_tasks(['celery_tasks.sms'])
