'''
辅助工具函数
'''
import re
import time

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29",
        }
        res = SESSIONS.get(url, headers=headers)
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

    def run(self):
        ...

    def main(self, sessions: object) -> list[str]:
        global SESSIONS

        SESSIONS = sessions

        self.run()
        end = time.time()
        self.msg += [
            '\n【运行时长】',
            f'时长：{int(end - self.start)} s'
        ]
        logger.info(f'\n{self.msg}')

        return self.msg
