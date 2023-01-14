'''
会武
'''
from src.daledou.daledou import DaLeDou


class HuiWu(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 挑战(self):
        if self.week in ['1', '2', '3']:
            self.msg += DaLeDou.conversion('会武')
            for _ in range(21):
                # 挑战
                HuiWu.get('cmd=sectmelee&op=dotraining')
                self.msg += DaLeDou.findall(r'最高伤害：\d+<br />(.*?)<br />')
                if '你已达今日挑战上限' in html:
                    self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
                    break
                elif '你的试炼书不足' in html:
                    # 兑换 试炼书*10
                    HuiWu.get(
                        'cmd=exchange&subtype=2&type=1265&times=10&costtype=13')

    def 助威(self):
        if self.week == '4':
            self.msg += DaLeDou.conversion('会武')
            # 冠军助威 丐帮
            HuiWu.get('cmd=sectmelee&op=cheer&sect=1003')
            # 冠军助威
            HuiWu.get('cmd=sectmelee&op=showcheer')
            self.msg += DaLeDou.findall(r'【冠军助威】<br />(.*?)<br /><br />')

    def 领奖(self):
        if self.week == '6':
            self.msg += DaLeDou.conversion('会武')
            # 领奖
            HuiWu.get('cmd=sectmelee&op=drawreward')
            self.msg += DaLeDou.findall(r'【领奖】<br />(.*?)<br />.*?领取')

    def 兑换(self):
        if self.week == '6':
            # 兑换 真黄金卷轴*10
            HuiWu.get(
                'cmd=exchange&subtype=2&type=1263&times=10&costtype=13')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    def main(self) -> list:
        # 门派
        HuiWu.get('cmd=sect')
        if '出师' in html:
            self.挑战()
            self.助威()
            self.领奖()
            self.兑换()
            return self.msg

        self.msg += DaLeDou.conversion('会武')
        return ['您需手动加入门派']
