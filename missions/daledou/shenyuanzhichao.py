'''
深渊之潮
'''
from missions.daledou.daledou import DaLeDou
from missions.daledou.config import read_yaml


class ShenYuan(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 巡游赠礼(self):
        # 帮派巡礼 》领取巡游赠礼
        ShenYuan.get('cmd=abysstide&op=getfactiongift')
        self.msg += DaLeDou.findall(r'【帮派巡礼】<br />(.*?)<br />当前')

    def 开始挑战(self):
        id = read_yaml('id', '深渊之潮.yaml')
        for _ in range(3):
            ShenYuan.get(f'cmd=abysstide&op=enterabyss&id={id}')
            if '暂无可用挑战次数' in html:
                break
            for _ in range(5):
                # 开始挑战
                ShenYuan.get('cmd=abysstide&op=beginfight')
            # 退出副本
            ShenYuan.get('cmd=abysstide&op=endabyss')
            self.msg += DaLeDou.findall(r'【深渊秘境】<br />(.*?)<br />')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('深渊之潮')

        self.巡游赠礼()
        self.开始挑战()

        return self.msg
