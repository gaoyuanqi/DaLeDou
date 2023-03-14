import re
import time
import traceback
from shutil import copy
from importlib import reload
from os import environ, path, getenv

import yaml
import requests
from loguru import logger
from decorator import decorator

import settings


YAML_PATH = './config'


def daledou_timing():
    for qq, _ in get_dld_data():
        logger.info(f'{qq} 将在 13:01 和 20:01 运行...')


def daledou_one():
    from src.daledou.daledouone import DaLeDouOne

    for qq, cookie in get_dld_data():
        logger.info(f'开始运行第一轮账号：{qq}')
        msg: list = DaLeDouOne().main(cookie)
        pushplus(f'第一轮 {qq}', msg)


def daledou_two():
    from src.daledou.daledoutwo import DaLeDouTwo

    for qq, cookie in get_dld_data():
        logger.info(f'开始运行第二轮账号：{qq}')
        msg: list = DaLeDouTwo().main(cookie)
        pushplus(f'第二轮 {qq}', msg)


def get_dld_data():
    '''
    获取大乐斗qq及cookie

    return: generator
    '''
    reload(settings)
    for account in settings.DALEDOU_ACCOUNT:
        if data := defaults(account):
            yield data
        else:
            if 'uin' in account:
                qq: str = search(r'uin=o(\d+)', account)
                title: str = f'{qq} 无效'
            else:
                title: str = f'{account} 无效'
            logger.error(f'{title}')
            pushplus(f'{title}', [f'无效cookie：\n{account}'])


def defaults(account: str) -> tuple:
    '''
    对账号进行对应处理
    '''
    if cookie := match_cookie(account):
        if html := verification_cookie(cookie):
            # 匹配
            qq: str = search(r'uin=o(\d+);', cookie)
            rank: str = search(r'等级:(\d+)', html)
            combat_power: str = search(r'战斗力</a>:(\d+)', html)

            # 添加环境变量
            environ['QQ'] = qq
            environ['RANK'] = rank
            environ['COMBAT_POWER'] = combat_power

            # 创建 qq 命名的 yaml 文件
            copy_yaml(qq)

            return qq, cookie


def match_cookie(cookie: str) -> str:
    '''
    从cookie匹配 RK ptcz uin skey
    '''
    if 'Cookie' in cookie:
        return
    # cookie末尾没有 ; 会导致skey匹配不到
    cookies = f'{cookie};'
    RK: str = search(r'RK=(.*?);', cookies)
    ptcz: str = search(r'ptcz=(.*?);', cookies)
    uin: str = search(r'uin=(.*?);', cookies)
    skey: str = search(r'skey=(.*?);', cookies)
    return f'RK={RK}; ptcz={ptcz}; uin={uin}; skey={skey}'


def verification_cookie(cookie: str) -> str:
    '''
    验证大乐斗cookie是否有效
    '''
    try:
        url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        for _ in range(3):
            res = requests.get(url, headers=headers)
            res.encoding = 'utf-8'
            html: str = res.text
            if '商店' in html:
                return html
    except Exception:
        ...


def search(mode: str, html: str) -> str:
    '''
    返回第一个成功匹配的字符串，失败返回None
    '''
    result: str | None = re.search(mode, html, re.S)
    if result:
        return result.group(1)


def copy_yaml(qq: str) -> None:
    '''
    从 _daledou.yaml 文件复制一份 qq.yaml 文件
    '''
    srcpath: str = f'{YAML_PATH}/_daledou.yaml'
    yamlpath: str = f'{YAML_PATH}/{qq}.yaml'
    if not path.isfile(yamlpath):
        logger.info(f'脚本创建了一个 {qq}.yaml 配置文件')
        copy(srcpath, yamlpath)


def readyaml(key: str) -> dict:
    '''
    读取 config 目录下的 yaml 配置文件
    '''
    with open(f'{YAML_PATH}/{getenv("QQ")}.yaml', 'r', encoding='utf-8') as fp:
        users: dict = yaml.safe_load(fp)
        data: dict = users[key]
    return data


@decorator
def deco(func, *args, **kwargs):
    time.sleep(0.2)
    func_name = func.__name__
    try:
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        logger.info(f'【{func_name}】耗时: {round(end-start, 2)} s')
    except Exception:
        error = traceback.format_exc()
        logger.error(f'【{func_name}】error：\n{error}')
        pushplus(f'【{func_name}】异常', [error])


def pushplus(title: str, message: list) -> dict:
    '''
    '\n'.join(['aa', 'bb', 'cc'])
    >>>
    aa
    bb
    cc
    '''
    if not settings.PUSHPLUS_TOKEN:
        logger.error('pushplus没有配置token，取消推送')
        return
    url = 'http://www.pushplus.plus/send/'
    content = '\n'.join(message)
    data = {
        'token': settings.PUSHPLUS_TOKEN,
        'title': title,
        'content': content,
    }
    res = requests.post(url, data=data)
    json = res.json()
    return json.get('data')
