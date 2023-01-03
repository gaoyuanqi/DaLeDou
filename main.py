import time
from importlib import reload

import requests
from loguru import logger
from schedule import every, repeat, run_pending

import settings
from missions.deco import deco
from missions.pushplus import pushplus


def login(cookies: str) -> bool:
    url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
    headers = {
        'Cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    for _ in range(3):
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        if '商店' in res.text:
            return True


@deco
def daledou_one():
    from missions.daledou.daledouone import DaLeDouOne

    reload(settings)
    for i, cookies in enumerate(settings.DALEDOU_COOKIE):
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if login(cookies):
            logger.info(f'开始执行大乐斗第一轮第 {i + 1} 个账号')
            message_list = DaLeDouOne().main(cookies)
            pushplus(f'大乐斗第一轮第 {i + 1} 个账号', message_list)
        else:
            logger.error(f'第 {i + 1} 个大乐斗Cookie无效，跳过')
            pushplus(f'第 {i + 1} 个大乐斗Cookie无效', [start])


@deco
def daledou_two():
    from missions.daledou.daledoutwo import DaLeDouTwo

    reload(settings)
    for i, cookies in enumerate(settings.DALEDOU_COOKIE):
        start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if login(cookies):
            logger.info(f'开始执行大乐斗第一轮第 {i + 1} 个账号')
            message_list = DaLeDouTwo().main(cookies)
            pushplus(f'大乐斗第一轮第 {i + 1} 个账号', message_list)
        else:
            logger.error(f'第 {i + 1} 个大乐斗Cookie无效，跳过')
            pushplus(f'第 {i + 1} 个大乐斗Cookie无效', [start])


@deco
def daledou_cookies():
    reload(settings)
    for i, cookies in enumerate(settings.DALEDOU_COOKIE):
        if login(cookies):
            logger.info(f'第 {i + 1} 个大乐斗Cookie有效，脚本将在 13:01 和 20:01 运行...')
        else:
            msg = f'第 {i + 1} 个大乐斗Cookie无效，跳过'
            logger.error(msg)
            pushplus(msg, [msg])


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
