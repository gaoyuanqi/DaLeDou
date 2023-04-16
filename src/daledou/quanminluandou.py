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
        乱斗竞技、乱斗任务领取
        '''
        n = True
        for t in [2, 3, 4]:
            QuanMin.get(f'cmd=luandou&op=0&acttype={t}')
            for id in DaLeDou.findall(r'.*?id=(\d+)">领取</a>'):
                n = False
                # 领取
                QuanMin.get(f'cmd=luandou&op=8&id={id}')
                self.msg.append(DaLeDou.search(r'斗】<br /><br />(.*?)<br />'))
        if n:
            self.msg.append('没有可领取的')

    def run(self) -> list:
        self.全民乱斗()

        return self.msg
