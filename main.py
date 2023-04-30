import time
from os import environ
from importlib import reload

from loguru import logger
from schedule import every, repeat, run_pending

import settings
from src.daledou.daledou import DaLeDouInit, DaLeDouOne, DaLeDouTwo


def run(job: str):
    reload(settings)
    environ['PUSHPLUS_TOKEN'] = settings.PUSHPLUS_TOKEN
    for ck in settings.DALEDOU_ACCOUNT:
        if trace := DaLeDouInit(ck).main():
            if job == 'timing':
                ...
            elif job == 'one':
                DaLeDouOne().main('第一轮')
            elif job == 'two':
                DaLeDouTwo().main('第二轮')
            logger.remove(trace)


@repeat(every(30).minutes)
def job_timing():
    # 每隔 30 分钟检测cookie有效期
    run('timing')


@repeat(every().day.at('13:01'))
def job_one():
    # 每天 13:01 运行第一轮
    run('one')


@repeat(every().day.at('20:01'))
def job_two():
    # 每天 20:01 运行第二轮
    run('two')


if __name__ == '__main__':
    run('timing')
    while True:
        run_pending()
        time.sleep(1)
