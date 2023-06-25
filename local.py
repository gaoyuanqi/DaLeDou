from os import environ
from importlib import reload

from loguru import logger

import settings
from daledou import DaLeDouInit, daledou


if __name__ == '__main__':
    '''
    1 表示第一轮
    2 表示第二轮
    '''
    lunci = input('输入1或2选择执行轮次：')
    reload(settings)
    environ['PUSHPLUS_TOKEN'] = settings.PUSHPLUS_TOKEN
    for ck in settings.DALEDOU_ACCOUNT:
        if trace := DaLeDouInit(ck).main():
            if lunci == '1':
                daledou('第一轮')
            elif lunci == '2':
                daledou('第二轮')
            logger.remove(trace)
