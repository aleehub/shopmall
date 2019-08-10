from pymysql import install_as_MySQLdb


# 'Did you install mysqlclient or MySQL-python?' % e
# django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module: No module named 'MySQLdb'.
# Did you install mysqlclient or MySQL-python?


# django库基于python2 创建，不支持python3下的pymysql 需要调用 pymysql 下的 函数使django兼容


install_as_MySQLdb()