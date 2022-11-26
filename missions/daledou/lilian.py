'''
历练
'''
from missions.daledou.daledou import DaLeDou
from missions.daledou.config import read_yaml


class LiLian(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 历练(self):
        npcid_list = read_yaml('npcid', '历练.yaml')
        for npcid in npcid_list:
            for _ in range(3):
                LiLian.get(
                    f'cmd=mappush&subtype=3&mapid=6&npcid={npcid}&pageid=2')
                self.msg += DaLeDou.findall(r'阅历值：\d+<br />(.*?)<br />')
                if '活力不足' in html:
                    return

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('历练')

        self.历练()

        return self.msg
