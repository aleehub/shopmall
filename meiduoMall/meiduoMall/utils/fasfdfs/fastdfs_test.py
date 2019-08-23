# 导入模块
from fdfs_client.client import Fdfs_client

# 导入配置文件
# 注意：windows环境下绝对路径会发生转义，需要加上 "r" 说明是原生字符串

client = Fdfs_client(r'fastdfs_client.conf')

# 上传图片
# 注意：windows环境下绝对路径会发生转义，需要加上 "r" 说明是原生字符串

result = client.upload_by_filename(r'01.jpeg')

print(result)
# {'Group name': 'group1',
# 'Remote file_id': 'group1\\M00/00/00/wKgOW11fjBiAMy6hAAC4j90Tziw28.jpeg',
# 'Status': 'Upload successed.',
# 'Local file name': '01.jpeg',
# 'Uploaded size': '46.00KB',
# 'Storage IP': '192.168.14.91'}
