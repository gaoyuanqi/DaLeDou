import time
from importlib import reload

from loguru import logger
from schedule import every, repeat, run_pending

import settings
from missions.pushplus import pushplus
from missions.daledou.session import session


def daledou_one():
    from missions.daledou.daledouone import DaLeDouOne

    reload(settings)
    for i, cookie in enumerate(settings.DALEDOU_COOKIE):
        # 2022-05-08 09:51:13
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = ['【开始时间】', start]
        sessions = session(cookie)
        if sessions is None:
            logger.error(f'第 {i + 1} 个大乐斗Cookie无效，跳过')
            msg_list = msg + ['\n【登陆】', f'第 {i + 1} 个大乐斗Cookie无效，跳过该账号']
            pushplus(f'第 {i + 1} 个大乐斗Cookie无效', msg_list)
            continue

        logger.info(f'开始执行大乐斗第一轮第 {i + 1} 个账号')
        message_list = msg + DaLeDouOne().main(sessions)
        pushplus(f'大乐斗第一轮第 {i + 1} 个账号', message_list)


def daledou_two():
    from missions.daledou.daledoutwo import DaLeDouTwo

    reload(settings)
    for i, cookie in enumerate(settings.DALEDOU_COOKIE):
        # 2022-05-08 09:51:13
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = ['【开始时间】', start]
        sessions = session(cookie)
        if sessions is None:
            logger.error(f'第 {i + 1} 个大乐斗Cookie无效，跳过')
            msg_list = msg + ['\n【登陆】', f'第 {i + 1} 个大乐斗Cookie无效，跳过该账号']
            pushplus(f'第 {i + 1} 个大乐斗Cookie无效', msg_list)
            continue

        logger.info(f'开始执行大乐斗第一轮第 {i + 1} 个账号')
        message_list = msg + DaLeDouTwo().main(sessions)
        pushplus(f'大乐斗第一轮第 {i + 1} 个账号', message_list)


def daledou_cookies():
    reload(settings)
    for i, cookie in enumerate(settings.DALEDOU_COOKIE):
        if session(cookie) is None:
            msg = f'第 {i + 1} 个大乐斗Cookie无效，请更换Cookie'
            logger.error(msg)
            pushplus(msg, [msg])
        else:
            logger.info(f'第 {i + 1} 个大乐斗Cookie有效，脚本将在指定时间运行...')


@repeat(every(30).minutes)
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
