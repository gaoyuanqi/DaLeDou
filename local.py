from importlib import reload

from loguru import logger

import settings
from missions.deco import deco
from missions.pushplus import pushplus
from missions.daledou.login import login


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
