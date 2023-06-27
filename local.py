import sys
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
    input = sys.argv
    if len(input) != 1:
        lunci = input[1]
        reload(settings)
        environ['PUSHPLUS_TOKEN'] = settings.PUSHPLUS_TOKEN
        for ck in settings.DALEDOU_ACCOUNT:
            if trace := DaLeDouInit(ck).main():
                if lunci == '0':
                    ...
                elif lunci == '1':
                    daledou('第一轮')
                elif lunci == '2':
                    daledou('第二轮')
                logger.remove(trace)
    else:
        print(
            '''只支持以下命令：
        首  次  python local.py 0
        第一轮  python local.py 1
        第二轮  python local.py 2
        '''
        )
