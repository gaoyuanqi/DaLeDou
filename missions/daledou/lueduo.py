'''
掠夺
'''
from missions.daledou.daledou import DaLeDou


class LueDuo(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取胜负奖励(self):
        if self.week == '3':
            self.msg += DaLeDou.conversion('掠夺')
            # 领取胜负奖励
            LueDuo.get('cmd=forage_war&subtype=6')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def main(self) -> list[str]:
        self.领取胜负奖励()

        return self.msg
