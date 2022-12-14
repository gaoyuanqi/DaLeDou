'''
问鼎天下
'''
from missions.daledou.daledou import DaLeDou


class WenDing(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        if self.week == '1':
            # 领取奖励
            WenDing.get('cmd=tbattle&op=drawreward')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def 攻占(self):
        if self.week not in ['6', '0']:
            self.msg += DaLeDou.conversion('问鼎天下')
            # 问鼎天下
            WenDing.get('cmd=tbattle')
            if '你占领的领地已经枯竭' in html:
                # 领取
                WenDing.get('cmd=tbattle&op=drawreleasereward')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
            elif '放弃' in html:
                # 放弃
                WenDing.get('cmd=tbattle&op=abandon')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

            # 领地
            # 1东海 2南荒   3西泽   4北寒
            WenDing.get(f'cmd=tbattle&op=showregion&region=1')
            text_list = DaLeDou.findall(r'id=(\d+).*?攻占</a>')
            # 攻占 倒数第一个
            WenDing.get(f'cmd=tbattle&op=occupy&id={text_list[-1]}&region=1')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def 淘汰赛(self):
        if self.week == '6':
            self.msg += DaLeDou.conversion('问鼎天下')
            # 助威 神ㄨ阁丶
            WenDing.get(f'cmd=tbattle&op=cheerregionbattle&id=10215')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def 排名赛(self):
        if self.week == '0':
            self.msg += DaLeDou.conversion('问鼎天下')
            # 助威 神ㄨ阁丶
            WenDing.get(f'cmd=tbattle&op=cheerchampionbattle&id=10215')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def main_one(self) -> list:
        # 大乐斗首页
        WenDing.get('cmd=index')
        if '问鼎天下' in html:
            self.领取奖励()
            self.攻占()
            self.淘汰赛()
            self.排名赛()
            return self.msg

        return []

    def main_two(self) -> list:
        # 大乐斗首页
        WenDing.get('cmd=index')
        if '问鼎天下' in html:
            self.攻占()
            return self.msg

        return []
