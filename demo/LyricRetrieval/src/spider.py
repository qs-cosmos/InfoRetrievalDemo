# coding: utf-8
from spider.schedule.scheduler import seed_scheduler, fish_scheduler, analyse_scheduler, scheduler
from spider.message.message import MessageQueue

if __name__ == '__main__':
    '''
    # seeder 测试
    queue = MessageQueue()
    queue.clear()
    seed_scheduler(10)
    '''
    
    '''
    # fisher 测试
    fish_scheduler(10)
    '''

    '''
    # analyser 测试
    analyse_scheduler(10)
    '''
    scheduler(3, 1, analyser=False)
