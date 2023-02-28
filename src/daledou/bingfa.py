'''
兵法
'''
import random

from src.daledou.daledou import DaLeDou


class BingFa(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 助威(self):
        # 助威
        BingFa.get('cmd=brofight&subtype=13')
        teamid: list = DaLeDou.findall(r'.*?teamid=(\d+).*?助威</a>')
        teamid_random = random.choice(teamid)
        # 确定
        BingFa.get(
            f'cmd=brofight&subtype=13&teamid={teamid_random}&type=5&op=cheer')
        self.msg += DaLeDou.findall(r'领奖</a><br />(.*?)<br /><br />')

    def 领奖(self):
        # 兵法 -> 助威 -> 领奖
        BingFa.get('cmd=brofight&subtype=13&op=draw')
        self.msg += DaLeDou.findall(r'领奖</a><br />(.*?)<br /><br />')

    def 领斗币(self):
        '''
        领取斗币
        '''
        for t in range(1, 6):
            BingFa.get(f'cmd=brofight&subtype=10&type={t}')
            champion_uin: list = DaLeDou.findall(
                r'50000&nbsp;&nbsp;(\d+).*?champion_uin=(\d+)')
            for number, uin in champion_uin:
                if number == '0':
                    continue
                BingFa.get(
                    f'cmd=brofight&subtype=10&op=draw&champion_uin={uin}&type={t}')
                self.msg += DaLeDou.findall(r'排行</a><br />(.*?)<br />')
                return

    def run(self) -> list:
        self.msg += DaLeDou.conversion('兵法')

        self.领斗币()
        if self.week == '4':
            self.助威()
        if self.week == '6':
            self.领奖()

        return self.msg
