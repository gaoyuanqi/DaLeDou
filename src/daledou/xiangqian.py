'''
镶嵌
'''
from src.daledou.daledou import DaLeDou


class XiangQian(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def _data(self) -> tuple:
        '''
        魂珠碎片
        魂珠1级
        魂珠2级
        '''
        data = [
            zip('6666666', range(2000, 2007)),
            zip('3333333', range(4001, 4062, 10)),
            zip('3333333', range(4002, 4063, 10)),
        ]
        for iter in data:
            for t in iter:
                yield t

    def 镶嵌(self):
        '''
        魂珠升级（碎 -> 1 -> 2 -> 3）
        '''
        for k, v in self._data():
            for _ in range(50):
                if k == '6':
                    # 魂珠碎片 -> 1
                    XiangQian.get(
                        f'cmd=upgradepearl&type={k}&exchangetype={v}')
                else:
                    # 1 -> 2 -> 3
                    XiangQian.get(f'cmd=upgradepearl&type={k}&pearl_id={v}')
                if '抱歉' in html:
                    break

    def run(self) -> list:
        self.镶嵌()

        return self.msg
