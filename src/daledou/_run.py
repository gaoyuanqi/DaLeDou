from importlib import reload

from loguru import logger

import settings
from src.pushplus import pushplus
from src.daledou.daledouone import DaLeDouOne
from src.daledou.daledoutwo import DaLeDouTwo
from src.daledou._set import defaults, search


def daledou_one():
    reload(settings)
    for account in settings.DALEDOU_ACCOUNT:
        if data := defaults(account):
            qq, cookie = data
            logger.info(f'开始运行第一轮账号：{qq}')
            msg: list = DaLeDouOne().main(cookie)
            pushplus(f'第一轮 {qq}', msg)
        else:
            error(account)


def daledou_two():
    reload(settings)
    for account in settings.DALEDOU_ACCOUNT:
        if data := defaults(account):
            qq, cookie = data
            logger.info(f'开始运行第二轮账号：{qq}')
            msg: list = DaLeDouTwo().main(cookie)
            pushplus(f'第二轮 {qq}', msg)
        else:
            error(account)


def daledou_account(t: type) -> None:
    reload(settings)
    for account in settings.DALEDOU_ACCOUNT:
        if type(account) == t:
            if data := defaults(account):
                qq, _ = data
                logger.info(f'账号：{qq} 将在 13:01 和 20:01 运行...')
            else:
                error(account)


def error(account: str):
    if 'uin' in account:
        qq: str = search(r'uin=o(\d+)', account)
        title: str = f'{qq} 无效'
    else:
        title: str = f'{account} 无效'

    logger.error(f'{title}')
    pushplus(f'{title}', [f'无效cookie：{account}'])
