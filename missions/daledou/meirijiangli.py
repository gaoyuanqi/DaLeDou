'''
每日奖励
'''
from missions.daledou.daledou import DaLeDou


class MeiRi(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 每日奖励(self):
        self.msg += DaLeDou.conversion('每日奖励')
        for key in ['login', 'meridian', 'daren', 'wuzitianshu']:
            # 每日奖励
            MeiRi.get(f'cmd=dailygift&op=draw&key={key}')
            self.msg += DaLeDou.findall(r'【每日奖励】<br />(.*?)<br />')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('深渊之潮')

        self.每日奖励()

        return self.msg
