from django.shortcuts import render
from django.views import View

from .utils import get_categories

from .models import Content, ContentCategory


class IndexView(View):
    """展示首页界面"""

    def get(self, request):
        contents = {}  # 用来包装所有广告数据
        # 查询所有广告类别数据
        content_cat_qs = ContentCategory.objects.all()
        # 遍历广告类别查询集,来进行包装数据
        for content_cat in content_cat_qs:
            # 将每中类别下的所有广告查询出来,作为字典的value
            contents[content_cat.key] = content_cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': get_categories(),  # 商品分类数据
            'contents': contents  # 广告数据
        }

        return render(request, 'index.html', context)
