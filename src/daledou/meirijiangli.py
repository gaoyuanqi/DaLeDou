from src.daledou.daledou import DaLeDou


class MeiRi(DaLeDou):
    '''每日奖励'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        for key in ['login', 'meridian', 'daren', 'wuzitianshu']:
            # 每日奖励
            MeiRi.get(f'cmd=dailygift&op=draw&key={key}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

        return self.msg
