'''
大乐斗父类模块
'''
import re
import time

import requests

from src.daledou._set import _readyaml


class DaLeDou:

    def __init__(self) -> None:
        self.start: float = time.time()
        self.msg: list = []
        self.date: str = time.strftime('%d', time.localtime())
        self.times: str = time.strftime('%H%M')
        self.week: str = time.strftime('%w')

    @staticmethod
    def conversion(name: str) -> list[str]:
        '''
        DaLeDou.conversion('aa') -> ['\n【aa】']
        '''
        return [f'\n【{name}】']

    @staticmethod
    def get(params: str) -> str:
        global html
        url: str = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?' + params
        headers = {
            'Cookie': COOKIE,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        html = res.text
        time.sleep(0.2)
        return html

    @staticmethod
    def findall(mode: str) -> list:
        '''
        return:
            空列表 []
            列表 ['str1', 'str2', ...]
            元组列表 [('str1', 'str2'), ('str3', 'str4'), ...]
        '''
        result: list = re.findall(mode, html, re.S)
        return result

    @staticmethod
    def readyaml(key: str) -> dict:
        '''
        读取当前账号的yaml
        '''
        return _readyaml(key)

    def run(self):
        ...

    def main(self, cookie: str) -> list:
        global COOKIE
        COOKIE = cookie

        self.run()
        end: float = time.time()
        self.msg += [
            '\n【运行时长】',
            f'时长：{int(end - self.start)} s'
        ]

        for msg in self.msg:
            print(msg)

        return self.msg
