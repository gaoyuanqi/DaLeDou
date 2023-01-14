'''
幻境
'''
from src.daledou.daledou import DaLeDou
from src.daledou._set import _readyaml, _getenvqq


class HuanJing(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 幻境(self):
        data: dict = _readyaml('幻境', _getenvqq())
        id: int = data['id']
        HuanJing.get(f'cmd=misty&op=start&stage_id={id}')
        for _ in range(5):
            # 乐斗
            HuanJing.get(f'cmd=misty&op=fight')
            self.msg += DaLeDou.findall(r'累积星数.*?<br />(.*?)<br /><br />')
        # 返回飘渺幻境
        HuanJing.get('cmd=misty&op=return')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('幻境')

        self.幻境()

        return self.msg
