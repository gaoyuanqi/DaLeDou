'''
历练
'''
from src.daledou.daledou import DaLeDou


class LiLian(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 历练(self):
        data: dict = DaLeDou.readyaml('历练')
        for id in data['id']:
            for _ in range(3):
                LiLian.get(
                    f'cmd=mappush&subtype=3&mapid=6&npcid={id}&pageid=2')
                if '您还没有打到该历练场景' in html:
                    self.msg += [f'您还没有打到历练场景：{id}']
                    break
                self.msg += DaLeDou.findall(r'阅历值：\d+<br />(.*?)<br />')
                if '活力不足' in html:
                    return

    def main(self) -> list:
        self.msg += DaLeDou.conversion('历练')

        self.历练()

        return self.msg
