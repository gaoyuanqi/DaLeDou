'''
每日宝箱
'''
from src.daledou.daledou import DaLeDou


class MeiRi(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 打开(self):
        # 每日宝箱
        MeiRi.get('cmd=dailychest')
        while type_list := DaLeDou.findall(r'type=(\d+)">打开'):
            # 打开
            MeiRi.get(f'cmd=dailychest&op=open&type={type_list[0]}')
            self.msg += DaLeDou.findall(r'规则说明</a><br />(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('每日宝箱')

        self.打开()

        return self.msg
