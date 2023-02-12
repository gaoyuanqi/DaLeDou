import re
from shutil import copy
from os import environ, path, getenv

import yaml
import requests


_YAML_PATH = './config'


def defaults(account: str) -> tuple[str] | None:
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


def verification_cookie(cookie: str) -> str | None:
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


def search(mode: str, html: str) -> str | None:
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
    srcpath: str = f'{_YAML_PATH}/_daledou.yaml'
    yamlpath: str = f'{_YAML_PATH}/{qq}.yaml'
    if not path.isfile(yamlpath):
        copy(srcpath, yamlpath)


def readyaml(key: str) -> dict:
    '''
    读取 config 目录下的 yaml 配置文件
    '''
    with open(f'{_YAML_PATH}/{getenv("QQ")}.yaml', 'r', encoding='utf-8') as fp:
        users: dict = yaml.safe_load(fp)
        data: dict = users[key]
    return data
