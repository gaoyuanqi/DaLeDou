'''
大乐斗第二轮
默认每天 20:01 执行
'''
from src.daledou._set import deco
from src.daledou.daledou import DaLeDou


class DaLeDouTwo(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    @deco
    def 邪神秘宝(self):
        from src.daledou.xieshenmibao import XieShen
        self.msg += XieShen().run()

    @deco
    def 每日宝箱(self):
        from src.daledou.meiribaoxiang import MeiRi
        self.msg += MeiRi().run()

    @deco
    def 问鼎天下(self):
        from src.daledou.wendingtianxia import WenDing
        self.msg += WenDing().main_two()

    @deco
    def 任务派遣中心(self):
        from src.daledou.renwupaiqianzhongxin import RenWu
        self.msg += RenWu().run()

    @deco
    def 侠士客栈(self):
        from src.daledou.xiashikezhan import XiaShi
        self.msg += XiaShi().run()

    @deco
    def 仙武修真(self):
        from src.daledou.xianwuxiuzhen import XianWu
        self.msg += XianWu().run()

    @deco
    def 大侠回归三重好礼(self):
        from src.daledou.daxiahuigui import DaXia
        self.msg += DaXia().run()

    @deco
    def 乐斗黄历(self):
        from src.daledou.ledouhuangli import LeDou
        self.msg += LeDou().run()

    @deco
    def 深渊之潮(self):
        from src.daledou.shenyuanzhichao import ShenYuan
        self.msg += ShenYuan().run()

    @deco
    def 活动(self):
        from src.daledou.events import Events
        self.msg += Events().main_two()

    @deco
    def 背包(self):
        from src.daledou.beibao import BeiBao
        self.msg += BeiBao().run()

    @deco
    def 镶嵌(self):
        from src.daledou.xiangqian import XiangQian
        self.msg += XiangQian().run()

    @deco
    def 神匠坊(self):
        from src.daledou.shenjiangfang import ShenJiang
        self.msg += ShenJiang().run()

    @deco
    def 商店积分(self):
        from src.daledou.shangdianjifen import ShangDian
        self.msg += ShangDian().run()

    def run(self):
        # 首页
        DaLeDouTwo.get('cmd=index')
        mission: str = html[:-200]

        if '邪神秘宝' in mission:
            self.邪神秘宝()

        if ('每日宝箱' in mission) and (self.date == '20'):
            self.每日宝箱()

        if ('问鼎天下' in mission) and (self.week not in ['6', '0']):
            self.问鼎天下()

        if '任务派遣中心' in mission:
            self.任务派遣中心()

        if '侠士客栈' in mission:
            self.侠士客栈()

        if '仙武修真' in mission:
            self.仙武修真()

        if ('大侠回归三重好礼' in mission) and (self.week == '4'):
            self.大侠回归三重好礼()

        if '乐斗黄历' in mission:
            self.乐斗黄历()

        if '深渊之潮' in mission:
            self.深渊之潮()

        self.活动()
        self.背包()

        if ('镶嵌' in mission) and (self.week == '4'):
            self.镶嵌()

        if ('神匠坊' in mission) and (self.week == '4'):
            self.神匠坊()

        self.商店积分()
