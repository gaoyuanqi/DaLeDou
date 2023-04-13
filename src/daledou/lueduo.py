from src.daledou.daledou import DaLeDou


class LueDuo(DaLeDou):
    '''掠夺'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        '''周三领取胜负奖励'''
        LueDuo.get('cmd=forage_war&subtype=6')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

        return self.msg
