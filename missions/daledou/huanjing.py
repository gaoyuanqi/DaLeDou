'''
幻境
'''
from missions.daledou.daledou import DaLeDou
from missions.daledou.config import read_yaml


class HuanJing(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 幻境(self):
        stage_id = read_yaml('stage_id', '幻境.yaml')
        HuanJing.get(f'cmd=misty&op=start&stage_id={stage_id}')
        for _ in range(5):
            # 乐斗
            HuanJing.get(f'cmd=misty&op=fight')
            self.msg += DaLeDou.findall(r'累积星数.*?<br />(.*?)<br /><br />')
        # 返回飘渺幻境
        HuanJing.get('cmd=misty&op=return')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('幻境')

        self.幻境()

        return self.msg
