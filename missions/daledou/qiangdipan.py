'''
抢地盘
'''
import random

from missions.daledou.daledou import DaLeDou


class QiangDiPan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 抢地盘(self):
        '''
        等级  30级以下 40级以下 ... 120级以下 无限制区
        type  1       2            10        11
        等级
        text_list = DaLeDou.findall(r'.*?等级:(\d+)\(.*?')
        无限制区
        '''
        QiangDiPan.get('cmd=recommendmanor&type=11&page=1')
        text_list = DaLeDou.findall(r'manorid=(\d+)">攻占</a>')
        random_manorid = random.choice(text_list)
        # 攻占
        QiangDiPan.get(f'cmd=manorfight&fighttype=1&manorid={random_manorid}')
        self.msg += DaLeDou.findall(r'】</p><p>(.*?)。')
        # 兑换武器
        QiangDiPan.get('cmd=manor&sub=0')
        self.msg += DaLeDou.findall(r'【抢地盘】<br /><br />(.*?)<br /><br />')

    def main(self) -> list:
        if DaLeDou.rank() >= 22:
            self.msg += DaLeDou.conversion('抢地盘')
            self.抢地盘()
            return self.msg

        return []
