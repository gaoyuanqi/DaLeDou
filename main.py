import time
from importlib import reload

from loguru import logger
from schedule import every, repeat, run_pending

import settings
from missions.pushplus import pushplus
from missions.daledou.session import session


def daledou_one():
    from missions.daledou.daledouone import DaLeDouOne
    message_list = DaLeDouOne().main()
    pushplus('大乐斗第一轮', message_list)


def daledou_two():
    from missions.daledou.daledoutwo import DaLeDouTwo
    message_list = DaLeDouTwo().main()
    pushplus('大乐斗第二轮', message_list)


def daledou_cookies():
    reload(settings)
    if session(settings.DALEDOU_COOKIE) is None:
        logger.error('大乐斗Cookie无效，请更换Cookie')
    else:
        logger.info('大乐斗Cookie有效，脚本将在指定时间运行...')


@repeat(every(10).minutes)
def job():
    daledou_cookies()


@repeat(every().day.at('13:01'))
def job_1():
    daledou_one()


@repeat(every().day.at('20:01'))
def job_2():
    daledou_two()


daledou_cookies()
while True:
    run_pending()
    time.sleep(1)
