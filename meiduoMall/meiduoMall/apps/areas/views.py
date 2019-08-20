from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from meiduoMall.utils.response_code import RETCODE
from .models import Area
import logging

logger = logging.getLogger('django')
# Create your views here.


class AreasView(View):

    def get(self, request):
        """提供省市区数据"""

        area_id = request.GET.get('area_id')

        if not area_id:
            # 提供省份数据

            # 先查询省份是否有缓存数据
            province_list = cache.get('province_list')

            if not province_list:

                try:
                    # 查询省份数据

                    province_model_list = Area.objects.filter(parent=None)

                    # 序列化省份数据

                    province_list = []

                    for province_model in province_model_list:
                        province_list.append({'id': province_model.id, 'name': province_model.name})

                except Exception as e:

                    logger.error(e)

                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

                cache.set('province_list', province_list, 3600)

            # 响应省份数据
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'province_list': province_list})

        else:
            # 提供市或区数据

            # 读取市或区缓存数据
            sub_data = cache.get("sub_area_" + area_id)

            if not sub_data:

                try:

                    parent_model = Area.objects.get(id=area_id)

                    sub_model_list = parent_model.subs.all()

                    # 序列化市区数据

                    sub_list = []

                    for sub_model in sub_model_list:
                        sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                    sub_data = {
                        'id': parent_model.id,  # 父级pk
                        'name': parent_model.name,  # 父级name
                        'subs': sub_list,  # 父级的子集
                    }

                except Exception as e:

                    logger.error(e)

                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '市区数据错误'})

                # 存储市或区缓存数据

                cache.set('sub_area_' + area_id, sub_data, 3600)

                # 响应市区数据
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'sub_data': sub_data})
