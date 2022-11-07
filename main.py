import time

from loguru import logger
from schedule import every, repeat, run_pending

from missions.daledou.session import session
from missions.pushplus import pushplus


def daledou_one():
    from missions.daledou.daledouone import DaLeDouOne
    message_list = DaLeDouOne().main()
    pushplus('大乐斗第一轮', message_list)


def daledou_two():
    from missions.daledou.daledoutwo import DaLeDouTwo
    message_list = DaLeDouTwo().main()
    pushplus('大乐斗第二轮', message_list)


def daledou_cookies():
    if session() is None:
        logger.error('大乐斗Cookie无效，请更换Cookie，然后重启容器')
    else:
        logger.info('大乐斗Cookie有效，脚本开始定时运行...')


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
