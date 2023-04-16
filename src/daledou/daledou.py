# -*- coding: utf-8 -*-
import re
import time
import traceback
from shutil import copy
from os import environ, path, getenv
from importlib import import_module

import yaml
import requests
from loguru import logger


YAML_PATH = './config'


class CookieError(Exception):
    ...


class InitDaLeDou:
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie

    def clean_cookie(self) -> str:
        '''清洁大乐斗cookie

        :return: 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx'
        '''
        ck = ''
        for key in ['RK', 'ptcz', 'uin', 'skey']:
            try:
                result = re.search(
                    f'{key}=(.*?); ',
                    f'{self.cookie}; ',
                    re.S
                ).group(0)
            except AttributeError:
                raise CookieError(f'大乐斗cookie不正确：{self.cookie}')
            ck += f'{result}'
        return ck[:-2]

    def verify_cookie(self, cookie: str):
        '''验证cookie是否有效（至多重试3次）

        :return: str | None
        '''
        url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
        headers = {
            'Cookie': cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        for _ in range(3):
            res = requests.get(url=url, headers=headers)
            res.encoding = 'utf-8'
            html = res.text
            if '商店' in html:
                return True

    @staticmethod
    def copy_yaml(qq: str):
        '''从 daledou.yaml 复制一份并命名为 qq.yaml 文件
        '''
        srcpath = f'{YAML_PATH}/daledou.yaml'
        yamlpath = f'{YAML_PATH}/{qq}.yaml'
        if not path.isfile(yamlpath):
            logger.success(f'脚本创建了一个配置文件：{YAML_PATH}/{qq}.yaml')
            copy(srcpath, yamlpath)

    @staticmethod
    def create_log() -> int:
        '''创建当天日志文件'''
        date = time.strftime("%Y-%m-%d", time.localtime())
        return logger.add(
            f'./log/{getenv("QQ")}/{date}.log',
            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>',
            enqueue=True,
            encoding='utf-8',
            retention='30 days'
        )

    def main(self):
        cookie = self.clean_cookie()
        qq = re.search(r'uin=o(\d+); ', cookie, re.S).group(1)
        environ['QQ'] = qq
        if self.verify_cookie(cookie):
            environ['COOKIE'] = cookie
            InitDaLeDou.copy_yaml(qq)
            if cookie != getenv(f'YOUXIAO_{qq}'):
                environ[f'YOUXIAO_{qq}'] = cookie
                logger.success(f'   {getenv("QQ")}：将在 13:01 和 20:01 定时运行...')
            return InitDaLeDou.create_log()

        if cookie != getenv(f'SHIXIAO_{qq}'):
            environ[f'SHIXIAO_{qq}'] = cookie
            logger.warning(f'   {getenv("QQ")}失效：{cookie}')
            push(f'cookie失效：{qq} ', [f'{cookie}'])


class DaLeDou:
    def __init__(self) -> None:
        self.msg: list = []
        self.date: str = time.strftime('%d', time.localtime())
        self.times: str = time.strftime('%H%M')
        self.week: str = time.strftime('%w')
        self.path = 'src.daledou.'

    @staticmethod
    def get(params: str) -> str:
        global html
        url = f'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{params}'
        headers = {
            'Cookie': getenv('COOKIE'),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        html = res.text
        time.sleep(0.2)
        return html

    @staticmethod
    def read_yaml(key: str) -> dict:
        '''读取 config 目录下的 yaml 配置文件'''
        try:
            with open(f'{YAML_PATH}/{getenv("QQ")}.yaml', 'r', encoding='utf-8') as fp:
                users: dict = yaml.safe_load(fp)
                data: dict = users[key]
            return data
        except Exception:
            error = traceback.format_exc()
            logger.error(f'{getenv("QQ")}.yaml 配置不正确：\n{error}')
            push(f'{getenv("QQ")}.yaml 异常', [error])

    @staticmethod
    def load_object(path: str) -> list:
        '''动态导入模块并运行实例方法run

        传入参数 src.daledou.xieshenmibao.XieShen 被拆分为：
            module：src.daledou.xieshenmibao
            name：XieShen
        '''
        dot = path.rindex('.')
        module, name = path[:dot], path[dot + 1:]
        mod = import_module(module)
        return getattr(mod, name)().run()

    @staticmethod
    def search(mode: str) -> str:
        '''查找首个'''
        match = re.search(mode, html, re.S)
        if match:
            result = match.group(1)
            logger.info(f'{getenv("QQ")} | {getenv("DLD_MISSIONS")}：{result}')
            return result

    @staticmethod
    def findall(mode: str) -> list:
        '''查找所有'''
        return re.findall(mode, html, re.S)

    @staticmethod
    def is_dld():
        '''判断是否大乐斗首页'''
        for _ in range(3):
            DaLeDou.get('cmd=index')
            if '退出' in html:
                return html.split('【退出】')[0]

    def run(self):
        ...

    def main(self, lunci: str):
        start = time.time()
        self.run()
        end = time.time()
        self.msg.append(f'\n【运行时长】\n时长：{int(end - start)} s')

        push(f'{getenv("QQ")} {lunci}', self.msg)


def push(title: str, message: list) -> None:
    ''' pushplus 微信通知'''
    if token := getenv('PUSHPLUS_TOKEN'):
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
            logger.success(f'  pushplus推送成功：{json}')
            return

        logger.warning(f'  pushplus推送失败：{json}')
        return

    logger.warning('  pushplus配置的token无效，取消微信推送')
