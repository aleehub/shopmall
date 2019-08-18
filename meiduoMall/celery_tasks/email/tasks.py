from celery_tasks.main import celery_app
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger('django')


# bind: 保证task对象会作为第一个参数自动传入
# name: 异步任务别名
# retry_backoff: 异常自动重试的时间间隔 第n次(retry_backoff*2(n-1))s
# max_retries: 异常自动重试次数的上限
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(to_email, verify_url):
    """

    :param to_email: 收件人邮箱
    :param verify_url: 验证链接
    :return:    None
    """

    # 拼接发送内容
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    try:
        send_mail(subject, "", settings.EMAIL, [to_email], html_message=html_message)
    except Exception as e:
        logger.error(e)

        # 有异常自动重试三次

    else:
        pass
