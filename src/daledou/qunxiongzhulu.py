'''
群雄逐鹿
'''
from src.daledou.daledou import DaLeDou


class QunXiong(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 群雄逐鹿(self):
        for op in ['signup', 'drawreward']:
            QunXiong.get(f'cmd=thronesbattle&op={op}')
            # 报名 》领奖
            self.msg += DaLeDou.findall(r'届群雄逐鹿<br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('群雄逐鹿')

        self.群雄逐鹿()

        return self.msg
