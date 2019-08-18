from django.db import models


# Create your models here.
class Area(models.Model):
    """省市区"""
    name = models.CharField(max_length=20, verbose_name='名称')

    # 自关联的外键指向自身
    # 使用related_name指明父集查询自己数据的语法，默认为.area_set   现在为.subs
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = '省市区'

    def __str__(self):
        return self.name


"""
id  省  省和市之间  一对多
name


id 市  市和区之间  一对多
name

id 区
name


定义自关联的表
id      name   parent
20000   广东省   None
20001   深圳市   20000
20002   东莞市   20000

20011   宝安区   20001
20012   南山区   20001


Area.objects.filter(parent=None)  # 查询所有省的语法
Area.objects.filter(parent_id=20000)  # 查询广东省下面的所有市
Area.objects.filter(parent_id=20001)  # 查询深圳市下面所有的区
"""
