'''
大乐斗第一轮
默认每天 13:01 执行
'''
from src.daledou._set import deco
from src.daledou.daledou import DaLeDou


class DaLeDouOne(DaLeDou):

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
    def 华山论剑(self):
        from src.daledou.huashanlunjian import HuaShan
        self.msg += HuaShan().run()

    @deco
    def 分享(self):
        from src.daledou.fenxiang import FenXiang
        self.msg += FenXiang().run()

    @deco
    def 乐斗(self):
        from src.daledou.ledou import LeDou
        self.msg += LeDou().run()

    @deco
    def 我要报名(self):
        from src.daledou.baoming import BaoMing
        self.msg += BaoMing().run()

    @deco
    def 巅峰之战进行中(self):
        from src.daledou.dianfeng import DianFeng
        self.msg += DianFeng().run()

    @deco
    def 矿洞(self):
        from src.daledou.kuangdong import KuangDong
        self.msg += KuangDong().run()

    @deco
    def 掠夺(self):
        from src.daledou.lueduo import LueDuo
        self.msg += LueDuo().run()

    @deco
    def 踢馆(self):
        from src.daledou.tiguan import TiGuan
        self.msg += TiGuan().run()

    @deco
    def 竞技场(self):
        from src.daledou.jingjichang import JingJiChang
        self.msg += JingJiChang().run()

    @deco
    def 十二宫(self):
        from src.daledou.shiergong import ShiErGong
        self.msg += ShiErGong().run()

    @deco
    def 许愿(self):
        from src.daledou.xuyuan import XuYuan
        self.msg += XuYuan().run()

    @deco
    def 抢地盘(self):
        from src.daledou.qiangdipan import QiangDiPan
        self.msg += QiangDiPan().run()

    @deco
    def 历练(self):
        from src.daledou.lilian import LiLian
        self.msg += LiLian().run()

    @deco
    def 镖行天下(self):
        from src.daledou.biaoxingtianxia import BiaoXing
        self.msg += BiaoXing().run()

    @deco
    def 幻境(self):
        from src.daledou.huanjing import HuanJing
        self.msg += HuanJing().run()

    @deco
    def 群雄逐鹿(self):
        from src.daledou.qunxiongzhulu import QunXiong
        self.msg += QunXiong().run()

    @deco
    def 画卷迷踪(self):
        from src.daledou.huajuanmizong import HuaJuan
        self.msg += HuaJuan().run()

    @deco
    def 门派(self):
        from src.daledou.menpai import MenPai
        self.msg += MenPai().run()

    @deco
    def 门派邀请赛(self):
        from src.daledou.menpaiyaoqingsai import MenPai
        self.msg += MenPai().run()

    @deco
    def 会武(self):
        from src.daledou.huiwu import HuiWu
        self.msg += HuiWu().run()

    @deco
    def 梦想之旅(self):
        from src.daledou.mengxiangzhilv import MengXiang
        self.msg += MengXiang().run()

    @deco
    def 问鼎天下(self):
        from src.daledou.wendingtianxia import WenDing
        self.msg += WenDing().main_one()

    @deco
    def 帮派商会(self):
        from src.daledou.bangpaishanghui import BangPai
        self.msg += BangPai().run()

    @deco
    def 帮派远征军(self):
        from src.daledou.baipaiyuanzhengjiu import BangPai
        self.msg += BangPai().run()

    @deco
    def 帮派黄金联赛(self):
        from src.daledou.baipaihuangjinliansai import BangPai
        self.msg += BangPai().run()

    @deco
    def 任务派遣中心(self):
        from src.daledou.renwupaiqianzhongxin import RenWu
        self.msg += RenWu().run()

    @deco
    def 武林盟主(self):
        from src.daledou.wulinmengzhu import WuLin
        self.msg += WuLin().run()

    @deco
    def 全民乱斗(self):
        from src.daledou.quanminluandou import QuanMin
        self.msg += QuanMin().run()

    @deco
    def 侠士客栈(self):
        from src.daledou.xiashikezhan import XiaShi
        self.msg += XiaShi().run()

    @deco
    def 江湖长梦(self):
        from src.daledou.jianghuchangmeng import JiangHu
        self.msg += JiangHu().run()

    @deco
    def 任务(self):
        from src.daledou.renwu import RenWu
        self.msg += RenWu().run()

    @deco
    def 我的帮派(self):
        from src.daledou.mygang import MyGang
        self.msg += MyGang().run()

    @deco
    def 帮派祭坛(self):
        from src.daledou.baipaijitan import BangPai
        self.msg += BangPai().run()

    @deco
    def 飞升大作战(self):
        from src.daledou.feisheng import FeiSheng
        self.msg += FeiSheng().run()

    @deco
    def 深渊之潮(self):
        from src.daledou.shenyuanzhichao import ShenYuan
        self.msg += ShenYuan().run()

    @deco
    def 活动(self):
        from src.daledou.events import Events
        self.msg += Events().main_one()

    @deco
    def 每日奖励(self):
        from src.daledou.meirijiangli import MeiRi
        self.msg += MeiRi().run()

    @deco
    def 今日活跃度(self):
        from src.daledou.jinrihuoyuedu import JinRi
        self.msg += JinRi().run()

    def run(self):
        # 首页
        DaLeDouOne.get('cmd=index')
        mission: str = html[:-200]

        if '邪神秘宝' in mission:
            self.邪神秘宝()

        if ('华山论剑' in mission) and (int(self.date) <= 25):
            self.华山论剑()

        self.分享()
        self.乐斗()
        self.我要报名()

        if '巅峰之战进行中' in mission:
            self.巅峰之战进行中()

        if '矿洞' in mission:
            self.矿洞()

        if ('掠夺' in mission) and (self.week == '3'):
            self.掠夺()

        if ('踢馆' in mission) and (self.week in ['5', '6']):
            self.踢馆()

        if ('竞技场' in mission) and (int(self.date) <= 25):
            self.竞技场()

        if '十二宫' in mission:
            self.十二宫()

        if '许愿' in mission:
            self.许愿()

        if '抢地盘' in mission:
            self.抢地盘()

        if '历练' in mission:
            self.历练()

        if '镖行天下' in mission:
            self.镖行天下()

        if '幻境' in mission:
            self.幻境()

        if ('群雄逐鹿' in mission) and (self.week == '6'):
            self.群雄逐鹿()

        if '画卷迷踪' in mission:
            self.画卷迷踪()

        if '门派' in mission:
            self.门派()

        if ('门派邀请赛' in mission) and (self.week != '2'):
            self.门派邀请赛()

        if ('会武' in mission) and (self.week not in ['5', '0']):
            self.会武()

        if '梦想之旅' in mission:
            self.梦想之旅()

        if '问鼎天下' in mission:
            self.问鼎天下()

        if '帮派商会' in mission:
            self.帮派商会()

        if '帮派远征军' in mission:
            self.帮派远征军()

        if '帮派黄金联赛' in mission:
            self.帮派黄金联赛()

        if '任务派遣中心' in mission:
            self.任务派遣中心()

        if '武林盟主' in mission:
            self.武林盟主()

        if '全民乱斗' in mission:
            self.全民乱斗()

        if '侠士客栈' in mission:
            self.侠士客栈()

        if '江湖长梦' in mission:
            self.江湖长梦()

        self.任务()
        self.我的帮派()

        if '帮派祭坛' in mission:
            self.帮派祭坛()

        if '飞升大作战' in mission:
            self.飞升大作战()

        if '深渊之潮' in mission:
            self.深渊之潮()

        self.活动()
        self.每日奖励()
        self.今日活跃度()
