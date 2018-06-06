# coding: utf-8 

from spider.download.fisher import Fisher
from spider.download.seeder import Seeder
from spider.analyse.analyser import Analyser, LyricParser, IRModel
from spider.message.message import MessageQueue
from spider.config.configure import TIME_OUT
from log.logger import getLogger, Logger
from multiprocessing import Pool
import os, time, random, sys, traceback

'''
seed_scheduler —— 网页下载器调度程序
- frequency : 运行频次
'''
def seed_scheduler(frequency, name=0):
    try:
        logger = getLogger(Logger.SEEDER)
        
        logger.info('seed_scheduler %s start.' % (name))
        queue = MessageQueue()
        seeder = Seeder()
        while frequency:
            seed = None
            while seed is None or queue.exists(seed):
                seed = seeder.seed()
            
            queue.seed = seed
            queue.repeat(seed)
            logger.info('Seeder %s get the %dth seed : %s.' % (name, frequency, seed))
            frequency = frequency - 1

        logger.info('seed_scheduler %s end.' % (name))
    except Exception as e:
        logger.error('seed_scheduler %s exited. Caused by: %s' % (name, str(e)))
        traceback.print_exc()

'''
fish_scheduler —— 网页下载器调度程序
- frequency : 运行频次
'''
def fish_scheduler(frequency, name=0):
    try:
        logger = getLogger(Logger.FISHER)

        logger.info('fish_scheduler %s start..' % (name))
        queue = MessageQueue()
        fisher = Fisher()
        while frequency:
            frequency = frequency - 1
            seed = None
            html = None

            # 超时起点计时器
            start_time = time.time()
            while seed is None:
                seed = queue.seed
                if seed is None:
                    end_time = time.time()
                    if (end_time - start_time) > TIME_OUT:
                        logger.error("fish_scheduler %s exited. Caused by : the time waitting for seed is too long." % (name))
                        return
            if seed == '':
                html = ''
            else :
                seed = ('http://www.lyrics.com'  + seed).encode('utf-8')
                logger.info('Fisher %s start dealing the %dth seed : %s.' % (name, frequency, seed))
                html = fisher.fish(seed)
                if html is None:
                    html = ''
            queue.html = seed + "$S$E$E$D$" +html
            logger.info('Fisher %s stop dealing the %dth seed : %s.' % (name, frequency, seed))

        logger.info('fish_scheduler %s end..' % (name))
    except Exception as e:
        logger.error('fish_scheduler %s exited. Caused by: %s'  % (name, str(e)))
        traceback.print_exc()

'''
analyse_scheduler —— 解析器调度程序
- frequency : 运行频次
'''
def analyse_scheduler(frequency, name=0):
    try:
        logger = getLogger(Logger.ANALYSER)

        logger.info('analyse_scheduler %s start...' % (name))
        queue = MessageQueue()
        parser = LyricParser()
        database = IRModel()
        analyser = Analyser(parser, database)
        while frequency:
            frequency = frequency - 1
            html = None
            
            # 超时起点计时器
            start_time = time.time()
            while html is None:
                html = queue.html
                if html is None:
                    end_time = time.time()
                    if (end_time - start_time) > TIME_OUT:
                        logger.error("analyse_scheduler %s exited. Caused by : the time waitting for fish is too long." % (name))
                        return

            logger.info('Analyser %s  start parsing the %dth text.' % (name, frequency))
            analyser.resolve(html)
            logger.info('Analyser %s  stop parsing the %dth text.' % (name, frequency))
        logger.info('analyse_scheduler %s end...' % (name))
    except Exception as e:
        logger.error('analyse_scheduler %s exited. Caused by: %s' % (name, str(e)))
        traceback.print_exc()

'''
scheduler —— 总调度程序
- amount : 进程个数
- frequency : 每个进程的运行次数, 默认为1
'''
def scheduler(amount, frequency=1, analyser=True):
    logger = getLogger(Logger.SCHEDULER)

    logger.info('Scheduler start.')
    queue = MessageQueue()
    queue.clear()

    analyser_pool = Pool()
    fish_pool = Pool()
    seed_pool = Pool()

    for i in range(amount):
        fish_pool.apply_async(fish_scheduler, args=(frequency, i))
        seed_pool.apply_async(seed_scheduler, args=(frequency, i))
    '''
    网络 IO 时间远远大于本地解析时间
    因此将解析进程始终设置为一个
    '''
    fish_pool.close()
    seed_pool.close()
    if analyser:
        analyser_pool.apply_async(analyse_scheduler, args=(frequency * amount, 0))
        analyser_pool.close()
        analyser_pool.join()
    fish_pool.join()
    seed_pool.join()
    logger.info('Scheduler end.')
    queue.clear()

