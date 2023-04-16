from os import environ

from src.daledou.daledou import DaLeDou


class DaLeDouOne(DaLeDou):
    '''大乐斗第一轮'''

    def __init__(self) -> None:
        super().__init__()
        self.modulepath = [
            ['邪神秘宝', True, 'xieshenmibao.XieShen'],
            ['华山论剑', (int(self.date) <= 26), 'huashanlunjian.HuaShan'],
            ['分享', True, 'fenxiang.FenXiang'],
            ['乐斗', True, 'ledou.LeDou'],
            ['报名', True, 'baoming.BaoMing'],
            ['巅峰之战进行中', True, 'dianfengzhizhan.DianFeng'],
            ['矿洞', True, 'kuangdong.KuangDong'],
            ['掠夺', (self.week == '3'), 'lueduo.LueDuo'],
            ['踢馆', (self.week in ['5', '6']), 'tiguan.TiGuan'],
            ['竞技场', (int(self.date) <= 25), 'jingjichang.JingJiChang'],
            ['十二宫', True, 'shiergong.ShiErGong'],
            ['许愿', True, 'xuyuan.XuYuan'],
            ['抢地盘', True, 'qiangdipan.QiangDiPan'],
            ['历练', True, 'lilian.LiLian'],
            ['镖行天下', True, 'biaoxingtianxia.BiaoXing'],
            ['幻境', True, 'huanjing.HuanJing'],
            ['群雄逐鹿', (self.week == '6'), 'qunxiongzhulu.QunXiong'],
            ['画卷迷踪', True, 'huajuanmizong.HuaJuan'],
            ['门派', True, 'menpai.MenPai'],
            ['门派邀请赛', (self.week != '2'), 'menpaiyaoqingsai.MenPai'],
            ['会武', (self.week not in ['5', '0']), 'huiwu.HuiWu'],
            ['梦想之旅', True, 'mengxiangzhilv.MengXiang'],
            ['问鼎天下', True, 'wendingtianxia.WenDingOne'],
            ['帮派商会', True, 'bangpaishanghui.BangPai'],
            ['帮派远征军', True, 'baipaiyuanzhengjun.BangPai'],
            ['帮派黄金联赛', True, 'baipaihuangjinliansai.BangPai'],
            ['任务派遣中心', True, 'renwupaiqianzhongxin.RenWu'],
            ['武林盟主', True, 'wulinmengzhu.WuLin'],
            ['全民乱斗', True, 'quanminluandou.QuanMin'],
            ['侠士客栈', True, 'xiashikezhan.XiaShi'],
            ['江湖长梦', True, 'jianghuchangmeng.JiangHu'],
            ['任务', True, 'renwu.RenWu'],
            ['我的帮派', True, 'mygang.MyGang'],
            ['帮派祭坛', True, 'baipaijitan.BangPai'],
            ['飞升大作战', True, 'feisheng.FeiSheng'],
            ['深渊之潮', True, 'shenyuanzhichao.ShenYuan'],
            ['每日奖励', True, 'meirijiangli.MeiRi'],
            ['今日活跃度', True, 'jinrihuoyuedu.JinRi'],
            ['仙武修真', True, 'xianwuxiuzhen.XianWu'],
            ['大侠回归三重好礼', (self.week == '4'), 'daxiahuigui.DaXia'],
            ['乐斗黄历', True, 'ledouhuangli.LeDou'],
            ['活动', True, 'events.EventsOne'],
        ]

    def run(self):
        if mission := DaLeDou.is_dld():
            for name, bool, path in self.modulepath:
                if (name in mission) and bool:
                    if name not in ['乐斗', '活动']:
                        self.msg.append(f'\n【{name}】')
                    environ['DLD_MISSIONS'] = name
                    self.msg += DaLeDou.load_object(f'{self.path}{path}')
        # print(self.msg)
        return self.msg
