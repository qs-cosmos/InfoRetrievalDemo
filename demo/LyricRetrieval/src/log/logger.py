# coding: utf-8

from enum import Enum, unique
import logging, sys

class Logger(object):
    ANALYSER = 'Analyser'
    DOWNLOADER = 'Downloader'
    FISHER = 'Fisher'
    SEEDER = 'Seeder'
    SCHEDULER = 'Scheduler'
    PROXY = 'ProxyPool'
    STORAGE = 'Storage'

def static_logger(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_logger(logger={})
def getLogger(name, level=logging.INFO):
    if name not in getLogger.logger.keys():
        # 获取logger实例，如果参数为空则返回root logger
        logger = logging.getLogger(name)
        # 指定logger输出格式
        fmt = "[%(name)-10s]-%(asctime)s pid<%(process)d> [%(levelname)s] : %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt, datefmt)
        # 控制台日志
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter
        # 为logger添加的日志处理器
        logger.addHandler(console_handler)
        # 指定日志的最低输出级别
        logger.setLevel(level)

        getLogger.logger[name] = logger

    return getLogger.logger[name]

if __name__ == "__main__":
    logger = getLogger(Logger.FISHER)
    logger.info("hello")
