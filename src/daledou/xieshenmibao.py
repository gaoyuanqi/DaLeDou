'''
邪神秘宝
'''
from src.daledou.daledou import DaLeDou


class XieShen(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 邪神秘宝(self):
        '''
        免费一次 or 抽奖一次
        0: 高级秘宝 24h
        1: 极品秘宝 96h
        '''
        for i in [0, 1]:
            # 免费一次 or 抽奖一次
            XieShen.get(f'cmd=tenlottery&op=2&type={i}')
            self.msg += DaLeDou.findall(r'【邪神秘宝】</p>(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('邪神秘宝')

        self.邪神秘宝()

        return self.msg
