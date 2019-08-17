from django.db import models


#  QQ登录成功后，我们需要将qq用户和美多商城用户关联到一起，方便下次QQ登录时使用，所以我们选择使用Mysql数据库进行存储
# 为了给项目中模型类补充数据创建时间更新时间两个字段，我们需要定义模型基类。
class BaseModel(models.Model):
    """为模型类补充字段"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True  # 说明是抽象基类，用于继承使用，数据库迁移时不会创建BaseModel的表
