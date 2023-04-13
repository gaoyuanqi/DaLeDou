from src.daledou.daledou import DaLeDou


class XieShen(DaLeDou):
    '''邪神秘宝'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        '''
        高级秘宝    免费一次 or 抽奖一次
        极品秘宝    免费一次 or 抽奖一次
        '''
        for i in [0, 1]:
            # 免费一次 or 抽奖一次
            XieShen.get(f'cmd=tenlottery&op=2&type={i}')
            msg = DaLeDou.search(r'【邪神秘宝】</p>(.*?)<br />')
            self.msg.append(msg)

        return self.msg
