from django.http import HttpResponse

from django.views import View

# 验证码sdk
from meiduoMall.libs.captcha.captcha import captcha

# 在django中使用redis需要使用django_radis 的工具包
from django_redis import get_redis_connection

from . import constants

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

        # get_redis_connection参数说明:
        # alias: redis的默认配置，默认值为default
        # 设置后可以将默认配置换成其他配置
        redis_conn = get_redis_connection('verify_code')

        # setex参数说明：
        # key:设置键
        # 过期时间：定义一个新的py文件，单独存储这个常量，不用设置成数字
        # value: 键的值
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码
        # 响应体类型 MIME
        return HttpResponse(image, content_type='image/jpg')  # 不设置响应体类型，则默认网页类型
