from src.daledou.daledou import DaLeDou


class DaXia(DaLeDou):
    '''大侠回归三重好礼'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        # 大侠回归三重好礼
        DaXia.get('cmd=newAct&subtype=173&op=1')
        if data := DaLeDou.findall(r'subtype=(\d+).*?taskid=(\d+)'):
            for s, t in data:
                # 领取
                DaXia.get(f'cmd=newAct&subtype={s}&op=2&taskid={t}')
                self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)<br />'))
        else:
            self.msg.append('没有可领取的奖励')

        return self.msg
