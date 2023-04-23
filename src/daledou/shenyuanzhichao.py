from src.daledou.daledou import DaLeDou


class ShenYuan(DaLeDou):
    '''深渊之潮'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 巡游赠礼(self):
        # 帮派巡礼 》领取巡游赠礼
        ShenYuan.get('cmd=abysstide&op=getfactiongift')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
        if '您暂未加入帮派' in html:
            self.msg.append('帮派巡礼需要加入帮派才能领取')

    def 深渊秘境(self):
        if yaml := DaLeDou.read_yaml('深渊之潮'):
            for _ in range(3):
                ShenYuan.get(f'cmd=abysstide&op=enterabyss&id={yaml}')
                if '暂无可用挑战次数' in html:
                    break
                elif '该副本需要顺序通关解锁' in html:
                    self.msg.append('该副本需要顺序通关解锁！')
                    break
                for _ in range(5):
                    # 开始挑战
                    ShenYuan.get('cmd=abysstide&op=beginfight')
                # 退出副本
                ShenYuan.get('cmd=abysstide&op=endabyss')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def run(self) -> list:
        self.巡游赠礼()
        self.深渊秘境()

        return self.msg
