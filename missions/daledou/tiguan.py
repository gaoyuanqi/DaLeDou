'''
踢馆
'''
from missions.daledou.daledou import DaLeDou


class TiGuan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 挑战(self):
        if self.week == '5':
            self.msg += DaLeDou.conversion('踢馆')
            for t in [2, 2, 2, 2, 2, 4]:
                # 试炼、高倍转盘
                TiGuan.get(f'cmd=facchallenge&subtype={t}')
                self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')
            for _ in range(30):
                # 挑战
                TiGuan.get('cmd=facchallenge&subtype=3')
                if '您的挑战次数已用光' in html:
                    break

    def 领奖(self):
        if self.week == '6':
            self.msg += DaLeDou.conversion('踢馆')
            # 领奖
            TiGuan.get('cmd=facchallenge&subtype=7')
            self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')
            if '还未报名' in html:
                # 报名
                TiGuan.get('cmd=facchallenge&subtype=1')
                self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')

    def main(self) -> list[str]:
        self.挑战()
        self.领奖()

        return self.msg
