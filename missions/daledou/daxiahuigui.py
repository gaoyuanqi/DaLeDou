'''
大侠回归三重好礼
'''
from missions.daledou.daledou import DaLeDou


class DaXia(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 大侠回归三重好礼(self):
        if self.week == '4':
            # 大侠回归三重好礼
            DaXia.get('cmd=newAct&subtype=173&op=1')
            two_tuple_list = DaLeDou.findall(r'subtype=(\d+).*?taskid=(\d+)')
            if not two_tuple_list:
                return
            self.msg += DaLeDou.conversion('大侠回归三重好礼')
            for s, t in two_tuple_list:
                # 领取
                DaXia.get(f'cmd=newAct&subtype={s}&op=2&taskid={t}')
                self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br />')

    def main(self) -> list[str]:
        self.大侠回归三重好礼()

        return self.msg
