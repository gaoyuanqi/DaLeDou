from src.daledou.daledou import DaLeDou


class QuanMin(DaLeDou):
    '''全民乱斗'''

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
        for t in [2, 3, 4]:
            QuanMin.get(f'cmd=luandou&op=0&acttype={t}')
            for id in DaLeDou.findall(r'.*?id=(\d+)">领取</a>'):
                # 领取
                QuanMin.get(f'cmd=luandou&op=8&id={id}')
                self.msg.append(DaLeDou.search(r'斗】<br /><br />(.*?)<br />'))

    def run(self) -> list:
        self.全民乱斗()

        return self.msg
