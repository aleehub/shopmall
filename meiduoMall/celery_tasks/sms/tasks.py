from celery_tasks.main import celery_app
from meiduoMall.libs.yuntongxun.sms import CCP
from meiduoMall.apps.verifications import constants


# name : 异步任务别名
@celery_app.task(name='cpp_send_sms_code')
def ccp_send_sms_code(mobile, sms_code):  # 此处不是类，没有self参数
    """
    发送短信异步任务
    :param self:
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功0 或 失败 -1
    """

    send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                       constants.SEND_SMS_TEMPLATE_ID)

    return send_ret
