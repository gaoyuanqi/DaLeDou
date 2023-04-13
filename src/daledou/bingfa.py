from random import choice

from src.daledou.daledou import DaLeDou


class BingFa(DaLeDou):
    '''兵法'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 助威(self):
        # 助威
        BingFa.get('cmd=brofight&subtype=13')
        if teamid := DaLeDou.findall(r'.*?teamid=(\d+).*?助威</a>'):
            t = choice(teamid)
            # 确定
            BingFa.get(f'cmd=brofight&subtype=13&teamid={t}&type=5&op=cheer')
            self.msg.append(DaLeDou.search(r'领奖</a><br />(.*?)<br />'))

    def 领奖(self):
        # 兵法 -> 助威 -> 领奖
        BingFa.get('cmd=brofight&subtype=13&op=draw')
        self.msg.append(DaLeDou.search(r'领奖</a><br />(.*?)<br />'))

    def 领斗币(self):
        '''
        领取斗币
        '''
        for t in range(1, 6):
            BingFa.get(f'cmd=brofight&subtype=10&type={t}')
            for number, uin in DaLeDou.findall(r'50000&nbsp;&nbsp;(\d+).*?champion_uin=(\d+)'):
                if number == '0':
                    continue
                BingFa.get(
                    f'cmd=brofight&subtype=10&op=draw&champion_uin={uin}&type={t}')
                self.msg.append(DaLeDou.search(r'排行</a><br />(.*?)<br />'))
                return

    def run(self) -> list:
        if self.week == '4':
            self.助威()
        if self.week == '6':
            self.领奖()
            self.领斗币()

        return self.msg
