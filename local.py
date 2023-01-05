from importlib import reload

import requests
from loguru import logger

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
        if login(cookies):
            logger.info(f'开始执行大乐斗第一轮第 {i + 1} 个账号')
            message_list = DaLeDouOne().main(cookies)
            pushplus(f'大乐斗第一轮第 {i + 1} 个账号', message_list)
        else:
            logger.error(f'第 {i + 1} 个大乐斗Cookie无效，跳过')


@deco
def daledou_two():
    from missions.daledou.daledoutwo import DaLeDouTwo

    reload(settings)
    for i, cookies in enumerate(settings.DALEDOU_COOKIE):
        if login(cookies):
            logger.info(f'开始执行大乐斗第一轮第 {i + 1} 个账号')
            message_list = DaLeDouTwo().main(cookies)
            pushplus(f'大乐斗第一轮第 {i + 1} 个账号', message_list)
        else:
            logger.error(f'第 {i + 1} 个大乐斗Cookie无效，跳过')


def main():
    lunci = input('输入1或2选择执行轮次：')
    if lunci == '1':
        daledou_one()
    elif lunci == '2':
        daledou_two()


main()
