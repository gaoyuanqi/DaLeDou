from src.daledou.daledou import DaLeDou


class QunXiong(DaLeDou):
    '''群雄逐鹿'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        '''周六报名、领奖'''
        for op in ['signup', 'drawreward']:
            QunXiong.get(f'cmd=thronesbattle&op={op}')
            self.msg.append(DaLeDou.search(r'届群雄逐鹿<br />(.*?)<br />'))

        return self.msg
