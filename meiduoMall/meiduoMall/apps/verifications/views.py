from django.http import HttpResponse, JsonResponse

from django.views import View

# 验证码sdk
from meiduoMall.libs.captcha.captcha import captcha

# 在django中使用redis需要使用django_radis 的工具包
from django_redis import get_redis_connection

from . import constants

from meiduoMall.utils.response_code import RETCODE

import random

import logging

from meiduoMall.libs.yuntongxun.sms import CCP

logger = logging.getLogger()

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


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):

        """
        :param request: 请求对象
        请求对象查询字符串参数：
        image_code:验证码
        uuid: 前端浏览器生成的唯一标识码
        :param mobile:  手机号
        :return: JSON
        """
        req_dict = request.GET

        # 获取请求对象中的参数
        image_code_client = req_dict.get("image_code")
        uuid = req_dict.get("uuid")

        # 校验获得的参数
        # 先校验是否传入的值是否为空
        if not all([image_code_client, uuid]):
            # 状态码解释 NECESSARYPARAMERR： necessary parameter error
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, "errmsg": '缺少必传参数'})

        # 创建到redis的连接对象
        redis_conn = get_redis_connection('verify_code')

        # 提取，校验send_flag

        # 先从redis数据库中先提取是否有这个标记，如果没有则可以发送短信
        send_flag = redis_conn.get('send_flag_%s' % mobile)

        if send_flag:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 没有标记，重新写入
        # 设置参数说明：
        # 第一个值：键名称
        # 第二个值：键存活时间
        # 第三个值：设置一个随便值
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)  下面利用管道技术

        # 提取图形验证码
        image_code_redis = redis_conn.get('img_%s' % uuid)

        # 有两种情况:
        # 1.请求用户采用第三方非正常请求，没有正常uuid
        # 2.前面设置的图形验证码在一定时间后已经失效
        if image_code_redis is None:
            return JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码失效"})

        # 删除在redis中的图形验证码
        redis_conn.delete("img_%s" % uuid)

        # 对比两边的验证码是否相同

        # 现将从redis中取得的验证码转码成字符串
        image_code_server = image_code_redis.decode()  # bytes转字符串

        if image_code_client.lower() != image_code_server.lower():  # 将两边的验证码都做一个小写转换再进行比较

            return JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码错误"})

        # 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)

        logger.info(sms_code)

        # 保存短信验证码

        # redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)  下面利用管道技术

        # 解决如果redis服务端需要同时处理多个请求,加上网络延迟，那么服务端利用率不高，效率降低

        # 利用管道技术pipeline

        # 创建Redis管道
        pl = redis_conn.pipeline()

        # 将redis队列添加进入队列
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 执行请求
        pl.execute()

        #

        # 调用发送短信SDK进行发送短信

        # 参数说明：
        # mobile : 要发送的手机号
        # sms_code : 要发送的验证码值
        # constants.SMS_CODE_REDIS_EXPIRES //60  :  验证码失效的时间单位(分钟)
        # constants.SEND_SMS_TEMPLATE_ID  : 调用SDK 发送的验证码模板编号

        mobile = '15919440309'

        result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                         constants.SEND_SMS_TEMPLATE_ID)

        print('发送结果:', result)

        # 响应结果

        return JsonResponse({"code": RETCODE.OK, "errmsg": "发送短信成功"})
