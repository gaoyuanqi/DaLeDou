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


def read_yaml(file: str, key: str | None =None):
    '''
    读取config目录下的yaml配置文件

    Args:
        file: 文件名称
        key: yaml文件中的键
    '''
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
    '''
    清洁大乐斗Cookie，改成 'RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=xx'

    Args:
        cookie: 大乐斗Cookie

    Returns: 
        tuple[str, str]: 第一个元素是qq，第二个元素是清洁后的大乐斗Cookie
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
    '''
    向Session会话添加大乐斗Cookie，若Cookie有效则返回Session会话，否则返回None

    Args:
        cookie: 大乐斗Cookie

    Returns:
        Session: 含有大乐斗Cookie的Session会话
        None: 大乐斗Cookie无效
    '''
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
    '''
    基于daledou.yaml创建一份以qq命名的yaml配置文件

    Args:
        qq: QQ号
    '''
    default_path = './config/daledou.yaml'
    create_path = f'./config/{qq}.yaml'
    if os.path.isfile(create_path):
        logger.success(f'检测到文件 ./config/{qq}.yaml')
    else:
        copy(default_path, create_path)
        logger.success(f'创建文件 ./config/{qq}.yaml')


def create_log(qq: str) -> int:
    '''
    创建当天日志文件，文件夹以qq命名，日志文件以日期命名

    Args:
        qq: QQ号

    Returns:
        int: 跟踪ID
    '''
    return logger.add(
        f'./log/{qq}/{NOW.strftime("%Y-%m-%d")}.log',
        format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>',
        enqueue=True,
        encoding='utf-8',
        retention='30 days'
    )


def push(title: str, message: list[str]) -> None:
    '''
    pushplus微信通知

    Args:
        title: 通知标题
        message: 通知内容，列表内的若干元素只能是str类型
    '''
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
    '''
    获取大乐斗首页HTML源码

    Args:
        session: 大乐斗session会话

    Returns:
        str: 找到大乐斗首页HTML源码
        None: 没有找到大乐斗首页HTML源码
    '''
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


def replace_mission(missions: dict) -> list[str]:
    '''
    替换 missions 中存在部分大乐斗首页任务名称不能作为函数名称的键

    可以通过修改 data 字典来扩展，其键为大乐斗首页任务名称，值为实际函数名称

    比如 5.1礼包 （函数名称不能以数字开头）需替换为 五一礼包 （必须是 run.py 文件中存在的函数）

    Args:
        missions: 大乐斗首页任务名称

    Returns:
        list[str]: 函数名称列表
    '''
    data = {
        '5.1礼包': '五一礼包',
    }
    for key, value in data.items():
        if key in missions:
            missions[value] = missions.pop(key)
    return list(missions)


def init_config():
    '''
    初始化账号配置，若Cookie有效则返回包含账号数据的生成器
    '''
    if cookies := read_yaml('settings.yaml', 'DALEDOU_ACCOUNT'):
        for cookie in cookies:
            qq, ck = clean_cookie(cookie)
            if sessions := session(ck):
                logger.success(f'{qq}：Cookie在有效期内')
                create_yaml(qq)
                if html := get_index_html(sessions):
                    one = {k: v for k, v in MISSIONS_ONE.items() if k in html}
                    two = {k: v for k, v in MISSIONS_TWO.items() if k in html}
                    yield {
                        'QQ': qq,
                        'YAML': read_yaml(f'{qq}.yaml'),
                        'SESSION': sessions,
                        'MISSIONS': {
                            'one': replace_mission(one),
                            'two': replace_mission(two),
                        }
                    }
                else:
                    logger.warning(f'{qq}：大乐斗首页未找到')
                    push(f'{qq}：大乐斗首页未找到', ['可能官方繁忙或者维护'])
            else:
                logger.warning(f'{qq}：Cookie无效')
                push(f'{qq}：Cookie无效', [ck])
