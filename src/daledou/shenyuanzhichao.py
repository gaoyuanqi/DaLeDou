'''
深渊之潮
'''
from src.daledou.daledou import DaLeDou
from src.daledou._set import _readyaml, _getenvqq


class ShenYuan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 巡游赠礼(self):
        # 帮派巡礼 》领取巡游赠礼
        ShenYuan.get('cmd=abysstide&op=getfactiongift')
        self.msg += DaLeDou.findall(r'【帮派巡礼】<br />(.*?)<br />当前')
        if '您暂未加入帮派' in html:
            self.msg += ['帮派巡礼需要加入帮派才能领取']

    def 开始挑战(self):
        data: dict = _readyaml('深渊之潮', _getenvqq())
        id: int = data['id']
        for _ in range(3):
            ShenYuan.get(f'cmd=abysstide&op=enterabyss&id={id}')
            if '暂无可用挑战次数' in html:
                break
            elif '该副本需要顺序通关解锁' in html:
                self.msg += [f'该副本需要顺序通关解锁！，您需在{_getenvqq()}.yaml 改变策略']
                break
            for _ in range(5):
                # 开始挑战
                ShenYuan.get('cmd=abysstide&op=beginfight')
            # 退出副本
            ShenYuan.get('cmd=abysstide&op=endabyss')
            self.msg += DaLeDou.findall(r'【深渊秘境】<br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('深渊之潮')

        self.巡游赠礼()
        self.开始挑战()

        return self.msg
