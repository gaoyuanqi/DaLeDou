'''
辅助工具函数
'''
import re
import time

from loguru import logger

from daledou.deco import deco
from daledou.times import times_list
from daledou.session import session
from daledou.config import read_yaml


SESSIONS = session()


class DaLeDou:

    def __init__(self):
        self.start = time.time()
        self.msg = ['【开始时间】'] + times_list()
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

    @deco
    def 邪神秘宝(self):
        '''
        免费一次 or 抽奖一次
        0: 高级秘宝 24h
        1: 极品秘宝 96h
        '''
        self.msg += DaLeDou.conversion('邪神秘宝')
        for i in [0, 1]:
            # 免费一次 or 抽奖一次
            DaLeDou.get(f'cmd=tenlottery&op=2&type={i}')
            self.msg += DaLeDou.findall(r'【邪神秘宝】</p>(.*?)<br />')

    @deco
    def 问鼎天下(self):
        # 问鼎天下
        DaLeDou.get('cmd=tbattle')

        if self.week not in ['6', '0']:
            self.msg += DaLeDou.conversion('问鼎天下')
            if self.week == '1' and int(self.times) < 1310:
                # 领取奖励
                DaLeDou.get('cmd=tbattle&op=drawreward')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
            else:
                if '你占领的领地已经枯竭' in html:
                    # 领取
                    DaLeDou.get('cmd=tbattle&op=drawreleasereward')
                    self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
                elif '放弃' in html:
                    # 放弃
                    DaLeDou.get('cmd=tbattle&op=abandon')
                    self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
            # 领地
            # 1东海 2南荒   3西泽   4北寒
            DaLeDou.get(f'cmd=tbattle&op=showregion&region=1')
            text_list = DaLeDou.findall(r'id=(\d+).*?攻占</a>')
            # 攻占 倒数第一个
            DaLeDou.get(f'cmd=tbattle&op=occupy&id={text_list[-1]}&region=1')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

        elif self.week == '6' and int(self.times) < 1930:
            self.msg += DaLeDou.conversion('问鼎天下')
            # 助威 神ㄨ阁丶
            DaLeDou.get(f'cmd=tbattle&op=cheerregionbattle&id=10215')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

        elif self.week == '0' and int(self.times) < 1930:
            self.msg += DaLeDou.conversion('问鼎天下')
            # 助威 神ㄨ阁丶
            DaLeDou.get(f'cmd=tbattle&op=cheerchampionbattle&id=10215')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    @deco
    def 任务派遣中心(self):
        self.msg += DaLeDou.conversion('任务派遣中心')

        # 任务派遣中心
        DaLeDou.get('cmd=missionassign&subtype=0')

        # 查看 》领取奖励
        text_list = DaLeDou.findall(r'0时0分.*?mission_id=(.*?)">查看')
        for id in text_list:
            DaLeDou.get(f'cmd=missionassign&subtype=5&mission_id={id}')
            self.msg += DaLeDou.findall(r'\[任务派遣中心\](.*?)<br />')

        # 接受任务
        missions_dict = {
            '少女天团': '2',
            '闺蜜情深': '17',
            '男女搭配': '9',
            '鼓舞士气': '5',
            '仙人降临': '6',
            '雇佣军团': '11',
            '调整状态': '12',
            '防御工事': '10',
            '护送长老': '1',
            '坚持不懈': '4',
            '降妖除魔': '3',
            '深山隐士': '7',
            '抓捕小偷': '8',
            '小队巡逻': '13',
            '武艺切磋': '14',
            '哥俩好啊': '15',
            '协助村长': '16',
            '打扫房间': '18',
            '货物运送': '19',
            '消除虫害': '20',
            '帮助邻居': '21',
            '上山挑水': '22',
            '房屋维修': '23',
            '清理蟑螂': '24',
            '收割作物': '25',
            '炊烟袅袅': '26',
            '湖边垂钓': '27',
            '勤劳园丁': '29'
        }
        for _ in range(3):
            # 获取可接受任务id ['1', '2', '3']
            id_list = DaLeDou.findall(r'小时.*?mission_id=(.*?)">接受')
            for _, id in missions_dict.items():
                if id in id_list:
                    # 快速委派
                    DaLeDou.get(f'cmd=missionassign&subtype=7&mission_id={id}')
                    # 开始任务
                    DaLeDou.get(f'cmd=missionassign&subtype=8&mission_id={id}')
                    if '任务数已达上限' in html:
                        break
            # 任务派遣中心
            DaLeDou.get('cmd=missionassign&subtype=0')
            if '今日已领取了全部任务哦' in html:
                break
            elif html.count('查看') == 3:
                break
            elif '50斗豆' not in html:
                # 刷新任务
                DaLeDou.get('cmd=missionassign&subtype=3')

        self.msg += DaLeDou.findall(r'<br />(.*?)<a.*?查看')

    @deco
    def 侠士客栈(self):
        self.msg += DaLeDou.conversion('侠士客栈')
        # 侠士客栈
        DaLeDou.get('cmd=warriorinn')

        test_list = DaLeDou.findall(r'type=(\d+).*?领取奖励</a>')
        if test_list:
            for n in range(1, 4):
                # 领取奖励
                DaLeDou.get(
                    f'cmd=warriorinn&op=getlobbyreward&type={test_list[0]}&num={n}')
                self.msg += DaLeDou.findall(r'侠士客栈<br />(.*?)<br />')

        # 客栈奇遇
        # 黑市商人 -> 你去别人家问问吧 -> 确定
        for rejectadventure in ['黑市商人', '老乞丐']:
            if rejectadventure in html:
                for pos in range(2):
                    DaLeDou.get(
                        f'cmd=warriorinn&op=rejectadventure&pos={pos}')
                    self.msg += DaLeDou.findall(r'侠士客栈<br />(.*?)，<a')

        # 前来捣乱的柒承 -> 与TA理论 -> 确定
        for exceptadventure in ['前来捣乱的柒承', '前来捣乱的洪七公', '前来捣乱的欧阳锋', '前来捣乱的燕青', '前来捣乱的圣诞老鹅', '前来捣乱的断亦']:
            if exceptadventure in html:
                for pos in range(2):
                    DaLeDou.get(
                        f'cmd=warriorinn&op=exceptadventure&pos={pos}')
                    self.msg += DaLeDou.findall(r'侠士客栈<br />(.*?)，<a')

    @deco
    def 深渊之潮(self):
        self.msg += DaLeDou.conversion('深渊之潮')
        id = read_yaml('id', '深渊之潮.yaml')
        # 帮派巡礼
        # 领取巡游赠礼
        DaLeDou.get('cmd=abysstide&op=getfactiongift')
        self.msg += DaLeDou.findall(r'【帮派巡礼】<br />(.*?)<br />当前')
        for _ in range(3):
            DaLeDou.get(f'cmd=abysstide&op=enterabyss&id={id}')
            if '暂无可用挑战次数' in html:
                break
            for _ in range(5):
                # 开始挑战
                DaLeDou.get('cmd=abysstide&op=beginfight')
            # 退出副本
            DaLeDou.get('cmd=abysstide&op=endabyss')
            self.msg += DaLeDou.findall(r'【深渊秘境】<br />(.*?)<br />')

    def run(self):
        ...

    def main(self) -> list[str]:
        if SESSIONS is None:
            self.msg += ['\n【登陆】', '大乐斗Cookies失效，脚本结束']
            logger.error(f'\n{self.msg}')
            return self.msg

        self.run()

        end = time.time()
        self.msg += [
            '\n【运行时长】',
            f'时长：{int(end - self.start)} s'
        ]
        logger.info(f'\n{self.msg}')
        return self.msg
