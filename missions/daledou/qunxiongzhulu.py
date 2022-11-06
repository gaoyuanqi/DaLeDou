'''
群雄逐鹿
'''
from missions.daledou.daledou import DaLeDou


class QunXiong(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 群雄逐鹿(self):
        if self.week == '6':
            self.msg += DaLeDou.conversion('群雄逐鹿')
            # 报名
            QunXiong.get('cmd=thronesbattle&op=signup')
            self.msg += DaLeDou.findall(r'届群雄逐鹿<br />(.*?)<br />')
            # 领奖
            QunXiong.get('cmd=thronesbattle&op=drawreward')
            self.msg += DaLeDou.findall(r'届群雄逐鹿<br />(.*?)<br />')

    def main(self) -> list[str]:
        self.群雄逐鹿()

        return self.msg
