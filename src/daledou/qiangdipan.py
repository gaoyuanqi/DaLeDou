from src.daledou.daledou import DaLeDou


class QiangDiPan(DaLeDou):
    '''抢地盘'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        '''
        等级  30级以下 40级以下 ... 120级以下 无限制区
        type  1       2            10        11
        '''
        QiangDiPan.get('cmd=recommendmanor&type=11&page=1')
        if id := DaLeDou.findall(r'manorid=(\d+)">攻占</a>'):
            # 攻占
            QiangDiPan.get(f'cmd=manorfight&fighttype=1&manorid={id[-1]}')
            self.msg.append(DaLeDou.search(r'】</p><p>(.*?)。'))
        # 兑换武器
        QiangDiPan.get('cmd=manor&sub=0')
        self.msg.append(DaLeDou.search(r'【抢地盘】<br /><br />(.*?)<br /><br />'))

        return self.msg
