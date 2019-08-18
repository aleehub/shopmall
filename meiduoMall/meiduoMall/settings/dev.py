"""
Django settings for meiduoMall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os, sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4&46e_c0omctt72p*zab#@a%*wci&^9t#y$dct(qx0p(0f&lin'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 此项设置代表允许访问的域名地址
ALLOWED_HOSTS = ['www.meiduo.site']


# Application definition

# 追加导包路径
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# 打印新的打包路径

# print(sys.path)

# ['F:\\Github\\meiduoMall\\shopmall\\meiduoMall\\meiduoMall\\apps', 'F:\\Github\\meiduoMall\\shopmall\\meiduoMall', 'F:\\Github\\meiduoMall\\shopmall', 'F:\\Github\\meiduoMall\\shopmall\\meiduoMall', 'C:\\Program Files\\JetBrains\\PyCharm 2019.1.3\\helpers\\pycharm_display', 'C:\\Prfogram Files\\Python-Virtual\\shopmall\\Scripts\\python36.zip', 'C:\\Program Files\\Python-Virtual\\shopmall\\DLLs', 'C:\\Program Files\\Python-Virtual\\shopmall\\lib', 'C:\\Program Files\\Python-Virtual\\shopmall\\Scripts', 'c:\\program files\\python36\\Lib', 'c:\\program files\\python36\\DLLs', 'C:\\Program Files\\Python-Virtual\\shopmall', 'C:\\Program Files\\Python-Virtual\\shopmall\\lib\\site-packages', 'C:\\Program Files\\JetBrains\\PyCharm 2019.1.3\\helpers\\pycharm_matplotlib_backend']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'meiduoMall.apps.users',  # 用户模块应用
    'users',  # 用户模型
    'contents',  # 主内容页面
    # 'verifications',  未迁移模型类 ，可先不用注册
    'oauth',  # QQ第三方登录应用
    'areas',  # 加载地址信息模块
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduoMall.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# 修改成配置jinja2模板引擎
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  # jinja2模板引擎
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充Jinja2模板引擎环境
            'environment': 'meiduoMall.utils.jinja2_env.jinja2_environment',
        },
    },
]

WSGI_APPLICATION = 'meiduoMall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
# 修改数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'USER': 'meiduo',
        'PASSWORD': 'meiduo',
        'NAME': 'meiduomall',
    }
}

CACHES = {
    "default": {  # 默认的redis数据库，采用0号数据库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
    "session": {   #session 状态保持的redis配置项 采用1号数据库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }

    },
    "verify_code": {  # 将验证码保存在redis二号数据库
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": 'django_redis.client.DefaultClient',
        }
    },
}

# 修改session存储机制 使用redis保存
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# 将session的默认配置改成session配置
SESSION_CACHE_ALIAS = "session"


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# 配置静态文件加载路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {     # 日执行新显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {    # 对日志进行过滤
        'require_debug_true': { # django在debug模式下才输出日志
            '()': "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {   # 日志处理方法
        "console": {    # 在终端中输出日志
            'level': "INFO",
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': "simple"
        },
        'file': {       # 在文件中输出日志
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),
                'maxBytes': 300*1024*1024,
                'backupCount': 10,
                'formatter': 'verbose'
        },
    },
    'loggers': {    # 日志器
        'django': { # 定义了一个名为djangod的日志器
            'handlers': ['console', 'file'],    # 可以向终端和日志中同时输出日志
            'propagate': True,      # 是否进行传递日志
            'level': "INFO",        # 日志器接收的最低日志级别
        },
    }


}

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileAuthBackend']

LOGIN_URL = '/login/'

# qq登录模块参数
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'

# 因为此时回调地址为一个域名，而这个域名是个假域名,因此需要到本地host文件中将域名映射到本地ip
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'  # 回调地址

# 配置邮箱服务器
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_PORT = 25  # 发邮件端口
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_HOST_USER = 'doomer_543d@163.com'  # 授权的邮箱
EMAIL_HOST_PASSWORD = 'lyh123456'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<doomer_543d@163.com>'  # 发件人抬头

# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'
