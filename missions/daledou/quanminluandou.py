'''
全民乱斗
'''
from missions.daledou.daledou import DaLeDou


class QuanMin(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 全民乱斗(self):
        '''
        大乱斗 领取
        六门会武 -> 武林盟主 -> 武林大会
        '''
        n = True
        msg = []
        for t in [2, 3, 4]:
            QuanMin.get(f'cmd=luandou&op=0&acttype={t}')
            test_list = DaLeDou.findall(r'.*?id=(\d+)">领取</a>')
            for id in test_list:
                n = False
                # 领取
                QuanMin.get(f'cmd=luandou&op=8&id={id}')
                msg += DaLeDou.findall(r'【全民乱斗】<br /><br />(.*?)<br />大乱斗')
        if not n:
            self.msg += DaLeDou.conversion('全民乱斗')
            self.msg += msg

    def main(self) -> list:
        if DaLeDou.rank() >= 40:
            # 40级开启
            self.全民乱斗()
            return self.msg

        return []
