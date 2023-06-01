from src.daledou.daledou import DaLeDou


class QiHun(DaLeDou):
    '''器魂附魔'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        # 器魂附魔
        QiHun.get('cmd=enchant')
        for id in range(1, 4):
            # 领取
            QiHun.get(f'cmd=enchant&op=gettaskreward&task_id={id}')
            self.msg.append(DaLeDou.search(r'器魂附魔<br />(.*?)<br />'))

        return self.msg
