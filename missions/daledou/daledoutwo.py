'''
大乐斗第二轮
默认每天 20:01 执行
'''
from missions.deco import deco
from missions.daledou.daledou import DaLeDou


class DaLeDouTwo(DaLeDou):

    def __init__(self):
        super().__init__()

    @deco
    def 邪神秘宝(self):
        from missions.daledou.xieshenmibao import XieShen
        self.msg += XieShen().main()

    @deco
    def 每日宝箱(self):
        from missions.daledou.meiribaoxiang import MeiRi
        self.msg += MeiRi().main()

    @deco
    def 问鼎天下(self):
        from missions.daledou.wendingtianxia import WenDing
        self.msg += WenDing().main_two()

    @deco
    def 任务派遣中心(self):
        from missions.daledou.renwupaiqianzhongxin import RenWu
        self.msg += RenWu().main()

    @deco
    def 侠士客栈(self):
        from missions.daledou.xiashikezhan import XiaShi
        self.msg += XiaShi().main()

    @deco
    def 仙武修真(self):
        from missions.daledou.xianwuxiuzhen import XianWu
        self.msg += XianWu().main()

    @deco
    def 大侠回归三重好礼(self):
        from missions.daledou.daxiahuigui import DaXia
        self.msg += DaXia().main()

    @deco
    def 乐斗黄历(self):
        from missions.daledou.ledouhuangli import LeDou
        self.msg += LeDou().main()

    @deco
    def 深渊之潮(self):
        from missions.daledou.shenyuanzhichao import ShenYuan
        self.msg += ShenYuan().main()

    @deco
    def 活动(self):
        from missions.daledou.events import Events
        self.msg += Events().main_two()

    @deco
    def 背包(self):
        from missions.daledou.beibao import BeiBao
        self.msg += BeiBao().main()

    def 商店积分(self):
        from missions.daledou.shangdianjifen import ShangDian
        self.msg += ShangDian().main()

    def run(self):
        self.邪神秘宝()
        self.每日宝箱()
        self.问鼎天下()
        self.任务派遣中心()
        self.侠士客栈()
        self.仙武修真()
        self.大侠回归三重好礼()
        self.乐斗黄历()
        self.深渊之潮()
        self.活动()
        self.背包()
        self.商店积分()
