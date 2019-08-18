# Celery介绍和使用

# 消费者取到消息后，要消费掉（执行任务），需要我们去实现
# 任务可能出现高并发的情况，需要补充多任务的方式去执行
# 耗时任务很多种，每种耗时任务编写的生产者和消费者代码有重复
# 取到的消息什么时候执行，以什么样的方式执行


# 结论：
#   实际开发过程中，我们可以借助成熟的工具celery来完成
#   有了celery，我们在使用生产者模式 ，只需要关注任务本身，极大的简化了程序员的开发流程


# 1.celery介绍

#   一个简单 灵活且可靠，处理大量消息的分布系统，可以在一台或者机器运行。
#   单个celery进程每分钟可处理数以百万计的任务。
#   通过消息进行通信，使用消息队列（broker）在客户端和消费者之间协调

# 安转celery
#   pip install -U Celery


# 如何启动celery

# 在终端输入
# celery -A celery_tasks.main worker -l info -P eventlet

# 补充celery worker的工作模式
# 默认是进程池方式，进程数以当前机器的CPU核数为参考，每个CPU开四个进程。
# 如何自己指定进程数：celery worker -A proj --concurrency=4
# 如何改变进程池方式为协程方式：celery worker -A proj --concurrency=1000 -P eventlet -c 1000

# 安装eventlet模块
# $ pip install eventlet

# 启用 Eventlet 池
# $ celery -A celery_tasks.main worker -l info -P eventlet -c 1000
