from importlib import reload

from loguru import logger

import settings
from src.pushplus import pushplus
from src.daledou.daledouone import DaLeDouOne
from src.daledou.daledoutwo import DaLeDouTwo
from src.daledou._set import _defaults, _search


def _daledouone():
    reload(settings)
    for cookie in settings.DALEDOU_COOKIE:
        if data := _defaults(cookie):
            qq, cookies = data
            logger.info(f'开始运行第一轮账号：{qq}')
            msg: list = DaLeDouOne().main(cookies)
            pushplus(f'第一轮 {qq}', msg)
        else:
            _error(cookie)


def _daledoutwo():
    reload(settings)
    for cookie in settings.DALEDOU_COOKIE:
        if data := _defaults(cookie):
            qq, cookies = data
            logger.info(f'开始运行第二轮账号：{qq}')
            msg: list = DaLeDouTwo().main(cookies)
            pushplus(f'第二轮 {qq}', msg)
        else:
            _error(cookie)


def _daledoucookie():
    reload(settings)
    for cookie in settings.DALEDOU_COOKIE:
        if data := _defaults(cookie):
            qq, _ = data
            logger.info(f'账号：{qq} 将在 13:01 和 20:01 运行...')
        else:
            _error(cookie)


def _error(cookie: str):
    if 'uin' in cookie:
        msg = _search(r'uin=o(\d+)', cookie)
    else:
        msg = cookie
    logger.error(f'无效cookie：{msg}')
    pushplus(f'无效cookie {msg}', [f'{msg}无效'])
