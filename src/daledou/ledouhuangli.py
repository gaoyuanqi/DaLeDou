from src.daledou.daledou import DaLeDou


class LeDou(DaLeDou):
    '''乐斗黄历'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 乐斗黄历(self):
        # 乐斗黄历
        LeDou.get('cmd=calender&op=0')
        self.msg.append(DaLeDou.search(r'今日任务：(.*?)<br />'))
        # 领取
        LeDou.get('cmd=calender&op=2')
        self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)<br />'))
        if '任务未完成' in html:
            return
        # 占卜
        LeDou.get('cmd=calender&op=4')
        self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)<br />'))

    def run(self) -> list:
        self.乐斗黄历()

        return self.msg
