'''
群雄逐鹿
'''
from missions.daledou.daledou import DaLeDou


class QunXiong(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

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

    def main(self) -> list:
        # 大乐斗首页
        QunXiong.get('cmd=index')
        if '群雄逐鹿' in html:
            self.群雄逐鹿()
            return self.msg

        return []
