'''
大乐斗第一轮
默认每天 13:01 执行
'''
from missions.deco import deco
from missions.daledou.daledou import DaLeDou


class DaLeDouOne(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @deco
    def 邪神秘宝(self):
        from missions.daledou.xieshenmibao import XieShen
        self.msg += XieShen().main()

    @deco
    def 分享(self):
        from missions.daledou.fenxiang import FenXiang
        self.msg += FenXiang().main()

    @deco
    def 乐斗(self):
        from missions.daledou.ledou import LeDou
        self.msg += LeDou().main()

    @deco
    def 兵法(self):
        from missions.daledou.bingfa import BingFa
        self.msg += BingFa().main()

    @deco
    def 我要报名(self):
        from missions.daledou.baoming import BaoMing
        self.msg += BaoMing().main()

    @deco
    def 巅峰之战进行中(self):
        from missions.daledou.dianfeng import DianFeng
        self.msg += DianFeng().main()

    @deco
    def 矿洞(self):
        from missions.daledou.kuangdong import KuangDong
        self.msg += KuangDong().main()

    @deco
    def 掠夺(self):
        from missions.daledou.lueduo import LueDuo
        self.msg += LueDuo().main()

    @deco
    def 踢馆(self):
        from missions.daledou.tiguan import TiGuan
        self.msg += TiGuan().main()

    @deco
    def 竞技场(self):
        from missions.daledou.jingjichang import JingJiChang
        self.msg += JingJiChang().main()

    @deco
    def 十二宫(self):
        from missions.daledou.shiergong import ShiErGong
        self.msg += ShiErGong().main()

    @deco
    def 许愿(self):
        from missions.daledou.xuyuan import XuYuan
        self.msg += XuYuan().main()

    @deco
    def 抢地盘(self):
        from missions.daledou.qiangdipan import QiangDiPan
        self.msg += QiangDiPan().main()

    @deco
    def 历练(self):
        from missions.daledou.lilian import LiLian
        self.msg += LiLian().main()

    @deco
    def 镖行天下(self):
        from missions.daledou.biaoxingtianxia import BiaoXing
        self.msg += BiaoXing().main()

    @deco
    def 幻境(self):
        from missions.daledou.huanjing import HuanJing
        self.msg += HuanJing().main()

    @deco
    def 群雄逐鹿(self):
        from missions.daledou.qunxiongzhulu import QunXiong
        self.msg += QunXiong().main()

    @deco
    def 画卷迷踪(self):
        from missions.daledou.huajuanmizong import HuaJuan
        self.msg += HuaJuan().main()

    @deco
    def 门派(self):
        from missions.daledou.menpai import MenPai
        self.msg += MenPai().main()

    @deco
    def 门派邀请赛(self):
        from missions.daledou.menpaiyaoqingsai import MenPai
        self.msg += MenPai().main()

    @deco
    def 会武(self):
        from missions.daledou.huiwu import HuiWu
        self.msg += HuiWu().main()

    @deco
    def 梦想之旅(self):
        from missions.daledou.mengxiangzhilv import MengXiang
        self.msg += MengXiang().main()

    @deco
    def 问鼎天下(self):
        from missions.daledou.wendingtianxia import WenDing
        self.msg += WenDing().main_one()

    @deco
    def 帮派商会(self):
        from missions.daledou.bangpaishanghui import BangPai
        self.msg += BangPai().main()

    @deco
    def 帮派远征军(self):
        from missions.daledou.baipaiyuanzhengjiu import BangPai
        self.msg += BangPai().main()

    @deco
    def 帮派黄金联赛(self):
        from missions.daledou.baipaihuangjinliansai import BangPai
        self.msg += BangPai().main()

    @deco
    def 任务派遣中心(self):
        from missions.daledou.renwupaiqianzhongxin import RenWu
        self.msg += RenWu().main()

    @deco
    def 武林盟主(self):
        from missions.daledou.wulinmengzhu import WuLin
        self.msg += WuLin().main()

    @deco
    def 全民乱斗(self):
        from missions.daledou.quanminluandou import QuanMin
        self.msg += QuanMin().main()

    @deco
    def 侠士客栈(self):
        from missions.daledou.xiashikezhan import XiaShi
        self.msg += XiaShi().main()

    @deco
    def 江湖长梦(self):
        from missions.daledou.jianghuchangmeng import JiangHu
        self.msg += JiangHu().main()

    @deco
    def 任务(self):
        from missions.daledou.renwu import RenWu
        self.msg += RenWu().main()

    @deco
    def 我的帮派(self):
        from missions.daledou.mygang import MyGang
        self.msg += MyGang().main()

    @deco
    def 帮派祭坛(self):
        from missions.daledou.baipaijitan import BangPai
        self.msg += BangPai().main()

    @deco
    def 飞升大作战(self):
        from missions.daledou.feisheng import FeiSheng
        self.msg += FeiSheng().main()

    @deco
    def 深渊之潮(self):
        from missions.daledou.shenyuanzhichao import ShenYuan
        self.msg += ShenYuan().main()

    @deco
    def 活动(self):
        from missions.daledou.events import Events
        self.msg += Events().main_one()

    @deco
    def 每日奖励(self):
        from missions.daledou.meirijiangli import MeiRi
        self.msg += MeiRi().main()

    @deco
    def 今日活跃度(self):
        from missions.daledou.jinrihuoyuedu import JinRi
        self.msg += JinRi().main()

    def run(self):
        self.邪神秘宝()
        self.分享()
        self.乐斗()
        self.兵法()
        self.我要报名()
        self.巅峰之战进行中()
        self.矿洞()
        self.掠夺()
        self.踢馆()
        self.竞技场()
        self.十二宫()
        self.许愿()
        self.抢地盘()
        self.历练()
        self.镖行天下()
        self.幻境()
        self.群雄逐鹿()
        self.画卷迷踪()
        self.门派()
        self.门派邀请赛()
        self.会武()
        self.梦想之旅()
        self.问鼎天下()
        self.帮派商会()
        self.帮派远征军()
        self.帮派黄金联赛()
        self.任务派遣中心()
        self.武林盟主()
        self.全民乱斗()
        self.侠士客栈()
        self.江湖长梦()
        self.任务()
        self.我的帮派()
        self.帮派祭坛()
        self.飞升大作战()
        self.深渊之潮()
        self.活动()
        self.每日奖励()
        self.今日活跃度()
