'''
乐斗黄历
'''
from src.daledou.daledou import DaLeDou


class LeDou(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 乐斗黄历(self):
        # 乐斗黄历
        LeDou.get('cmd=calender&op=0')
        self.msg += DaLeDou.findall(r'今日任务：(.*?)<br />')
        # 领取
        LeDou.get('cmd=calender&op=2')
        self.msg += DaLeDou.findall(r'【乐斗黄历】<br /><br />(.*?)<br />')
        if '任务未完成' in html:
            return
        # 占卜
        LeDou.get('cmd=calender&op=4')
        self.msg += DaLeDou.findall(r'【运势占卜】<br /><br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('乐斗黄历')

        self.乐斗黄历()

        return self.msg
