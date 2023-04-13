from src.daledou.daledou import DaLeDou


class XianWu(DaLeDou):
    '''仙武修真'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取(self):
        for id in range(1, 4):
            # 领取
            XianWu.get(f'cmd=immortals&op=getreward&taskid={id}')
            self.msg.append(DaLeDou.search(r'帮助</a><br />(.*?)<br />'))

    def 挑战(self):
        for _ in range(5):
            # 寻访
            XianWu.get('cmd=immortals&op=visitimmortals&mountainId=1')
            self.msg.append(DaLeDou.search(r'帮助</a><br />(.*?)<br />'))
            if '你的今日寻访挑战次数已用光' in html:
                break
            # 挑战
            XianWu.get('cmd=immortals&op=fightimmortals')
            self.msg.append(DaLeDou.search(r'帮助</a><br />(.*?)<a'))

    def run(self) -> list:
        self.领取()
        self.挑战()

        return self.msg
