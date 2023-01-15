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
        if self.week == '4':
            # 助威
            BingFa.get('cmd=brofight&subtype=13')
            teamid: list = DaLeDou.findall(r'.*?teamid=(\d+).*?助威</a>')
            teamid_random = random.choice(teamid)
            # 确定
            BingFa.get(
                f'cmd=brofight&subtype=13&teamid={teamid_random}&type=5&op=cheer')
            self.msg += DaLeDou.findall(r'领奖</a><br />(.*?)<br /><br />')

    def 领奖(self):
        if self.week == '6':
            # 兵法 -> 助威 -> 领奖
            BingFa.get('cmd=brofight&subtype=13&op=draw')
            self.msg += DaLeDou.findall(r'领奖</a><br />(.*?)<br /><br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('兵法')

        self.助威()
        self.领奖()

        return self.msg
