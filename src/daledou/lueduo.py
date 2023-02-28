'''
掠夺
'''
from src.daledou.daledou import DaLeDou


class LueDuo(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取胜负奖励(self):
        # 领取胜负奖励
        LueDuo.get('cmd=forage_war&subtype=6')
        self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('掠夺')

        self.领取胜负奖励()

        return self.msg
