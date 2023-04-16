from src.daledou.daledou import DaLeDou


class TiGuan(DaLeDou):
    '''踢馆'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 挑战(self):
        for t in [2, 2, 2, 2, 2, 4]:
            # 试炼、高倍转盘
            TiGuan.get(f'cmd=facchallenge&subtype={t}')
            self.msg.append(DaLeDou.search(r'功勋商店</a><br />(.*?)<br />'))
            if '你们帮没有报名参加这次比赛' in html:
                return
        for _ in range(30):
            # 挑战
            TiGuan.get('cmd=facchallenge&subtype=3')
            DaLeDou.search(r'功勋商店</a><br />(.*?)<br />')
            if '您的挑战次数已用光' in html:
                self.msg.append('您的挑战次数已用光')
                break
            elif '您的复活次数已耗尽' in html:
                self.msg.append('您的复活次数已耗尽')
                break

    def 领奖(self):
        '''周六领奖、报名'''
        for p in ['7', '1']:
            TiGuan.get(f'cmd=facchallenge&subtype={p}')
            self.msg.append(DaLeDou.search(r'功勋商店</a><br />(.*?)<br />'))

    def run(self) -> list:
        if self.week == '5':
            self.挑战()
        elif self.week == '6':
            self.领奖()

        return self.msg
