'''
大侠回归三重好礼
'''
from src.daledou.daledou import DaLeDou


class DaXia(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 大侠回归三重好礼(self):
        # 大侠回归三重好礼
        DaXia.get('cmd=newAct&subtype=173&op=1')
        two_tuple: list = DaLeDou.findall(r'subtype=(\d+).*?taskid=(\d+)')
        if not two_tuple:
            self.msg += ['没有可领取的奖励']
            return
        for s, t in two_tuple:
            # 领取
            DaXia.get(f'cmd=newAct&subtype={s}&op=2&taskid={t}')
            self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('大侠回归三重好礼')

        self.大侠回归三重好礼()

        return self.msg
