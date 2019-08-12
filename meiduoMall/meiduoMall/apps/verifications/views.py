from django.http import HttpResponse

from django.views import View
from meiduoMall.libs.captcha.captcha import captcha

import redis


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """

        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """

        # SDK生成验证码
        # name : 唯一标识
        # text:  验证码文本
        # image: 验证码图片
        # 生成图片验证码
        name, text, image = captcha.generate_captcha()

        # 连接redis
        # 保存图片验证码

        # redis_conn = redis.get_redis_connection('verify_code')
        #
        # redis_conn.setex('img_%s'%uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码
        # 响应体类型 MIME
        return HttpResponse(image, content_type='image/jpg')  # 不设置响应体类型，则默认网页类型
