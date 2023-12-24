import os
import re
from shutil import copy

import yaml
import requests
from requests import Session
from loguru import logger

from daledou import NOW, MISSIONS_ONE, MISSIONS_TWO


class CookieError(Exception):
    ...


def read_yaml(file: str, key: str = ''):
    '''读取config目录下的yaml配置文件'''
    try:
        with open(f'./config/{file}', 'r', encoding='utf-8') as fp:
            users: dict = yaml.safe_load(fp)
            return users[key] if key else users
    except FileNotFoundError as e:
        logger.error(f'./config/{file} 文件不存在：{e}')
    except yaml.YAMLError as e:
        logger.error(f'./config/{file} 文件格式不正确：{e}')
    except Exception as e:
        logger.error(f'./config/{file} 文件出现意外错误：{e}')


def clean_cookie(cookie: str) -> tuple[str, str]:
    '''清洁大乐斗cookie

    :return: ('qq', 'RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=xx')
    '''
    ck = ''
    for key in ['RK', 'ptcz', 'openId', 'accessToken', 'newuin']:
        try:
            result = re.search(
                f'{key}=(.*?); ',
                f'{cookie}; ',
                re.S
            ).group(0)
        except AttributeError:
            raise CookieError(
                f'大乐斗Cookie缺少 {key} 字段：\n{cookie}')
        ck += f'{result}'
    qq: str = re.search(r'newuin=(\d+)', ck, re.S).group(1)
    return qq, ck[:-2]


def session(cookie: str) -> Session | None:
    '''若cookie有效则返回Session对象，否则返回None'''
    url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    }
    with requests.session() as session:
        requests.utils.add_dict_to_cookiejar(
            session.cookies, {'Cookie': cookie})

    for _ in range(3):
        res = session.get(url, headers=headers, allow_redirects=False)
        res.encoding = 'utf-8'
        html = res.text
        if '商店' in html:
            return session


def create_yaml(qq: str):
    '''基于daledou.yaml创建一份以qq命名的yaml配置文件'''
    default_path = './config/daledou.yaml'
    create_path = f'./config/{qq}.yaml'
    if os.path.isfile(create_path):
        logger.success(f'检测到文件 ./config/{qq}.yaml')
    else:
        copy(default_path, create_path)
        logger.success(f'创建文件 ./config/{qq}.yaml')


def create_log(qq: str) -> int:
    '''创建当天日志文件

    文件夹以qq命名，日志文件以日期命名
    '''
    return logger.add(
        f'./log/{qq}/{NOW.strftime("%Y-%m-%d")}.log',
        format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>',
        enqueue=True,
        encoding='utf-8',
        retention='30 days'
    )


def push(title: str, message: list[str]) -> None:
    '''pushplus微信通知'''
    if token := read_yaml('settings.yaml', 'PUSHPLUS_TOKEN'):
        url = 'http://www.pushplus.plus/send/'
        content = '\n'.join(list(filter(lambda x:  x, message)))
        data = {
            'token': token,
            'title': title,
            'content': content,
        }
        res = requests.post(url, data=data)
        json: dict = res.json()
        if json.get('code') == 200:
            return logger.success(f'pushplus推送成功：{json}')
        return logger.warning(f'pushplus推送失败：{json}')
    logger.warning('你没有配置pushplus微信推送')


def get_index_html(session: Session) -> str | None:
    '''获取大乐斗首页html'''
    url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    }
    for _ in range(3):
        response = session.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        if '商店' in html:
            return html.split('【退出】')[0]


def init_config():
    if cookies := read_yaml('settings.yaml', 'DALEDOU_ACCOUNT'):
        for cookie in cookies:
            qq, ck = clean_cookie(cookie)
            if sessions := session(ck):
                logger.success(f'{qq}：Cookie在有效期内')
                create_yaml(qq)
                if html := get_index_html(sessions):
                    one = {k: v for k,
                           v in MISSIONS_ONE.items() if k in html}
                    two = {k: v for k,
                           v in MISSIONS_TWO.items() if k in html}
                    if '5.1礼包' in one:
                        del one['5.1礼包']
                        one['五一礼包'] = True
                    yield {
                        'QQ': qq,
                        'YAML': read_yaml(f'{qq}.yaml'),
                        'SESSION': sessions,
                        'MISSIONS': {
                            'one': list(one),
                            'two': list(two),
                        }
                    }
                else:
                    logger.warning(f'{qq}：大乐斗首页未找到')
                    push(f'{qq}：大乐斗首页未找到', ['可能官方繁忙或者维护'])
            else:
                logger.warning(f'{qq}：Cookie无效')
                push(f'{qq}：Cookie无效', [ck])
