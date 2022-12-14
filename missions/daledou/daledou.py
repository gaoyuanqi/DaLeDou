'''
辅助工具函数
'''
import re
import time

import requests
from loguru import logger


class DaLeDou:

    def __init__(self) -> None:
        self.start = time.time()
        self.msg = []
        self.date = time.strftime('%d', time.localtime())
        self.times = time.strftime('%H%M')
        self.week = time.strftime('%w')

    @staticmethod
    def conversion(name: str) -> list[str]:
        '''
        DaLeDou.conversion('aa') -> ['\n【aa】']
        '''
        return [f'\n【{name}】']

    @staticmethod
    def get(params: str) -> str:
        global html
        url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?' + params
        headers = {
            'Cookie': COOKIES,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        html = res.text
        time.sleep(0.2)
        return html

    @staticmethod
    def findall(mode: str) -> list[str, tuple]:
        '''
        return:
            空列表 []
            列表 ['str1', 'str2', ...]
            二元组列表 [('str1','str2')]
        '''
        re_list = re.findall(mode, html, re.S)
        return re_list

    @staticmethod
    def find_tuple(mode: str) -> list[str]:
        '''
        因为微信推送不能传入元素是元组的列表，列表元素只能是字符串

        re_list:
            只有一个二元组 [('str1', 'str2')] -> ['str1', 'str2']
        '''
        re_list = re.findall(mode, html, re.S)
        return list(re_list[0])

    @staticmethod
    def findall_tuple(mode: str) -> list[str]:
        '''
        因为微信推送不能传入元素是元组的列表，列表元素只能是字符串

        re_list:
            多元组 [('s1', 's2'), ('s3', 's4'), ...] -> ['s1 s2', 's3 s4', ...]
        '''
        data = []
        re_list = re.findall(mode, html, re.S)
        for k, v in re_list:
            data.append(f'{k} {v}')
        return data

    @staticmethod
    def rank() -> int:
        '''
        查询账号等级
        '''
        # 大乐斗首页
        DaLeDou.get('cmd=index')
        text_list = DaLeDou.findall(r'等级:(\d+)')
        if text_list:
            return int(text_list[0])

        # 如果网页繁忙返回100默认通过
        return 100

    def run(self):
        ...

    def main(self, cookies: str) -> list[str]:
        global COOKIES

        COOKIES = cookies

        self.run()
        end = time.time()
        self.msg += [
            '\n【运行时长】',
            f'时长：{int(end - self.start)} s'
        ]
        logger.info(f'\n{self.msg}')

        return self.msg
