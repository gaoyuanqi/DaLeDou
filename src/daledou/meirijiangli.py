'''
每日奖励
'''
from src.daledou.daledou import DaLeDou


class MeiRi(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 每日奖励(self):
        for key in ['login', 'meridian', 'daren', 'wuzitianshu']:
            # 每日奖励
            MeiRi.get(f'cmd=dailygift&op=draw&key={key}')
            self.msg += DaLeDou.findall(r'【每日奖励】<br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('每日奖励')

        self.每日奖励()

        return self.msg
