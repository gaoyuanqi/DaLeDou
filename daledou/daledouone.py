'''
大乐斗第一轮
默认每天 13:01 执行
'''
import time
import random

from daledou.deco import deco
from daledou.daledou import DaLeDou
from daledou.config import read_yaml


class DaLeDouOne(DaLeDou):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    @deco
    def 分享(self):
        self.msg += DaLeDou.conversion('分享')

        # 一键分享
        DaLeDouOne.get(f'cmd=sharegame&subtype=6')
        for _ in range(8):
            for _ in range(11):
                # 开始挑战或挑战下一层
                DaLeDouOne.get('cmd=towerfight&type=0')
                time.sleep(0.5)
            # 挑战斗神塔层数为10的倍数boss  分享
            DaLeDouOne.get(f'cmd=sharegame&subtype=2&shareinfo=4')
            if '您今日的分享次数已达上限' in html:
                self.msg += DaLeDou.find_tuple(
                    r'</p><p>(.*?)&nbsp;(.*?)<br /><a.*?开通达人')
                # 自动挑战
                DaLeDouOne.get('cmd=towerfight&type=11')
                # 结束挑战
                DaLeDouOne.get('cmd=towerfight&type=7&confirm=1')
                break

        if self.week == '4':
            # 领取奖励
            DaLeDouOne.get('cmd=sharegame&subtype=3')
            text_list = DaLeDou.findall(r'sharenums=(\d+)')
            for s in text_list:
                # 领取
                DaLeDouOne.get(f'cmd=sharegame&subtype=4&sharenums={s}')
                self.msg += DaLeDou.findall(r'<p>【领取奖励】</p>(.*?)<p>')

    @deco
    def 乐斗(self):
        '''
        好友 大侠
        帮友 大侠
        侠侣 全部乐斗
        '''
        self.msg += DaLeDou.conversion('乐斗')

        # 武林 》设置 》乐斗助手
        DaLeDouOne.get('cmd=view&type=6')
        if '开启自动使用体力药水' in html:
            #  开启自动使用体力药水
            DaLeDouOne.get('cmd=set&type=0')

        # 好友首页 乐斗大侠
        DaLeDouOne.get('cmd=friendlist&page=1')
        text_list = DaLeDou.findall(r'侠：.*?B_UID=(\d+)')
        for B_UID in text_list:
            # 乐斗
            DaLeDouOne.get(f'cmd=fight&B_UID={B_UID}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                return
            self.msg += DaLeDou.findall(r'删</a><br />(.*?)。')

        # 帮友首页 乐斗大侠
        DaLeDouOne.get('cmd=viewmem')
        text_list = DaLeDou.findall(r'侠：.*?B_UID=(\d+)')
        for B_UID in text_list:
            # 乐斗
            DaLeDouOne.get(f'cmd=fight&B_UID={B_UID}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                return
            self.msg += DaLeDou.findall(r'侠侣</a><br />(.*?)。')

        # 侠侣 全部乐斗
        DaLeDouOne.get('cmd=viewxialv')
        text_list = DaLeDou.findall(r'：.*?B_UID=(\d+)')[1:]
        for B_UID in text_list:
            # 乐斗
            DaLeDouOne.get(f'cmd=fight&B_UID={B_UID}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                return
            self.msg += DaLeDou.findall(r'删</a><br />(.*?)。')

    @deco
    def 兵法(self):
        if self.week == '4':
            self.msg += DaLeDou.conversion('兵法')
            # 助威
            DaLeDouOne.get('cmd=brofight&subtype=13')
            text_list = DaLeDou.findall(r'.*?teamid=(\d+).*?助威</a>')
            teamid_random = random.choice(text_list)
            # 确定
            DaLeDouOne.get(
                f'cmd=brofight&subtype=13&teamid={teamid_random}&type=5&op=cheer')
            self.msg += DaLeDou.findall(r'领奖</a><br />(.*?)<br /><br />')

        elif self.week == '6':
            # 兵法 -> 助威 -> 领奖
            self.msg += DaLeDou.conversion('兵法')
            DaLeDouOne.get('cmd=brofight&subtype=13&op=draw')
            self.msg += DaLeDou.findall(r'领奖</a><br />(.*?)<br /><br />')

    @deco
    def 我要报名(self):
        self.msg += DaLeDou.conversion('我要报名')

        # 报名 武林大会
        DaLeDouOne.get('cmd=fastSignWulin&ifFirstSign=1')
        # 武林
        DaLeDouOne.get('cmd=showwulin')
        self.msg += DaLeDou.find_tuple(
            r'【冠军排行】</a><br />(.*?)<br />(.*?)<br />')

        if self.week in ['0', '2', '5']:
            # 报名 侠侣争霸
            DaLeDouOne.get('cmd=cfight&subtype=9')
            self.msg += DaLeDou.find_tuple(
                r'【侠侣争霸】<br />(.*?)<a.*?</a><br />(.*?)。.*查看')

        if self.week in ['6', '0']:
            # 报名 笑傲群侠
            DaLeDouOne.get('cmd=knightfight&op=signup')
            self.msg += DaLeDou.findall(r'【冠军排行】</a><br />(.*?)<br />.*?等级')

    @deco
    def 巅峰之战进行中(self):
        if self.week == '1':
            self.msg += DaLeDou.conversion('巅峰之战进行中')
            # 随机加入 -> 确定
            DaLeDouOne.get('cmd=gvg&sub=4&group=0&check=1')
            self.msg += DaLeDou.findall(r'【巅峰之战】</p>(.*?)<br /><p>')
            # 领奖
            DaLeDouOne.get('cmd=gvg&sub=1')
            self.msg += DaLeDou.findall(r'【巅峰之战】</p>(.*?)<br /><p>')

        elif self.week in ['3', '4', '5', '6', '0']:
            self.msg += DaLeDou.conversion('巅峰之战进行中')
            for _ in range(14):
                # 征战
                DaLeDouOne.get('cmd=gvg&sub=5')
                if '您今天' in html:
                    break
                elif '撒花祝贺' in html:
                    break
            self.msg += DaLeDou.findall(r'个人信息：<br />(.*?)</p>挑战书')

    @deco
    def 矿洞(self):
        self.msg += DaLeDou.conversion('矿洞')
        for _ in range(5):
            # 矿洞
            DaLeDouOne.get('cmd=factionmine')
            if '领取奖励' in html:
                # 领取奖励
                DaLeDouOne.get('cmd=factionmine&op=reward')
                self.msg += DaLeDou.findall(
                    r'【矿洞副本】<br /><br />(.*?)<br /><a.*?领取奖励')
            elif '开启副本' in html:
                # floor   1、2、3、4、5 对应 第一、二、三、四、五层
                # mode    1、2、3 对应 简单、普通、困难
                # 确认开启
                DaLeDouOne.get(f'cmd=factionmine&op=start&floor=5&mode=1')
                self.msg += DaLeDou.findall(r'矿石商店</a><br />(.*?)<br />')
            elif DaLeDou.findall(r'剩余次数：(\d+)/3<br />')[0] != '0':
                # 挑战
                DaLeDouOne.get('cmd=factionmine&op=fight')
                self.msg += DaLeDou.findall(r'矿石商店</a><br />(.*?)<br />')
            else:
                break

    @deco
    def 掠夺(self):
        if self.week == '3':
            self.msg += DaLeDou.conversion('掠夺')
            # 领取胜负奖励
            DaLeDouOne.get('cmd=forage_war&subtype=6')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    @deco
    def 踢馆(self):
        if self.week == '5':
            self.msg += DaLeDou.conversion('踢馆')
            for t in [2, 2, 2, 2, 2, 4]:
                # 试炼、高倍转盘
                DaLeDouOne.get(f'cmd=facchallenge&subtype={t}')
                self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')
            for _ in range(30):
                # 挑战
                DaLeDouOne.get('cmd=facchallenge&subtype=3')
                self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')
                if '您的挑战次数已用光' in html:
                    break

        elif self.week == '6':
            self.msg += DaLeDou.conversion('踢馆')
            # 领奖
            DaLeDouOne.get('cmd=facchallenge&subtype=7')
            self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')
            if '还未报名' in html:
                # 报名
                DaLeDouOne.get('cmd=facchallenge&subtype=1')
                self.msg += DaLeDou.findall(r'功勋商店</a><br />(.*?)<br />')

    @deco
    def 竞技场(self):
        '''
        每月26日结束
        '''
        if int(self.date) <= 25:
            self.msg += DaLeDou.conversion('竞技场')
            for _ in range(10):
                # 免费挑战 》开始挑战
                DaLeDouOne.get('cmd=arena&op=challenge')
                self.msg += DaLeDou.findall(r'更新提示</a><br />(.*?)。')
                if '免费挑战次数已用完' in html:
                    # 领取奖励
                    DaLeDouOne.get('cmd=arena&op=drawdaily')
                    self.msg += DaLeDou.findall(r'更新提示</a><br />(.*?)<br />')
                    break

            # 竞技点商店
            id = read_yaml('id', '竞技场.yaml')
            times = read_yaml('times', '竞技场.yaml')
            if id:
                # 兑换 or 兑换10个
                DaLeDouOne.get(f'cmd=arena&op=exchange&id={id}&times={times}')
                self.msg += DaLeDou.findall(r'竞技场</a><br />(.*?)<br />')

    @deco
    def 十二宫(self):
        '''
        扫荡 》请猴王扫荡
        '''
        self.msg += DaLeDou.conversion('十二宫')
        id = read_yaml('scene_id', '十二宫.yaml')
        # 请猴王扫荡
        DaLeDouOne.get(
            f'cmd=zodiacdungeon&op=autofight&scene_id={id}&pay_recover_times=0')
        if msg := DaLeDou.findall(r'<br />(.*?)<br /><br /></p>'):
            # 要么 扫荡
            self.msg += [msg[0].split('<br />')[-1]]
        else:
            # 要么 挑战次数不足 or 当前场景进度不足以使用自动挑战功能！
            self.msg += DaLeDou.findall(r'id="id"><p>(.*?)<br />')
        # 兑换奖励
        DaLeDouOne.get('cmd=zodiacdungeon&op=showexchange&type=2')
        self.msg += DaLeDou.findall(r'<p>兑换奖励<br />(.*?)<br /><br />')

    @deco
    def 许愿(self):
        '''
        领取许愿奖励 》许愿 》向xx上香许愿 》领取
        '''
        self.msg += DaLeDou.conversion('许愿')
        for sub in [5, 4, 1, 6]:
            DaLeDouOne.get(f'cmd=wish&sub={sub}')
            if sub != 4:
                self.msg += DaLeDou.findall(r'【每日许愿】<br />(.*?)<br />')

    @deco
    def 抢地盘(self):
        '''
        等级  30级以下 40级以下 ... 120级以下 无限制区
        type  1       2            10        11
        等级
        text_list = DaLeDou.findall(r'.*?等级:(\d+)\(.*?')
        无限制区
        '''
        self.msg += DaLeDou.conversion('抢地盘')
        DaLeDouOne.get('cmd=recommendmanor&type=11&page=1')
        text_list = DaLeDou.findall(r'manorid=(\d+)">攻占</a>')
        random_manorid = random.choice(text_list)
        # 攻占
        DaLeDouOne.get(f'cmd=manorfight&fighttype=1&manorid={random_manorid}')
        self.msg += DaLeDou.findall(r'】</p><p>(.*?)。')
        # 兑换武器
        DaLeDouOne.get('cmd=manor&sub=0')
        self.msg += DaLeDou.findall(r'【抢地盘】<br /><br />(.*?)<br /><br />')

    @deco
    def 历练(self):
        self.msg += DaLeDou.conversion('历练')
        npcid_list = read_yaml('npcid', '历练.yaml')
        for npcid in npcid_list:
            for _ in range(3):
                DaLeDouOne.get(
                    f'cmd=mappush&subtype=3&mapid=6&npcid={npcid}&pageid=2')
                if '活力不足' in html:
                    return
                self.msg += DaLeDou.findall(r'阅历值：\d+<br />(.*?)<br />')

    @deco
    def 镖行天下(self):
        self.msg += DaLeDou.conversion('镖行天下')
        for _ in range(5):
            # 刷新
            DaLeDouOne.get('cmd=cargo&op=3')
            text_list = DaLeDou.findall(r'passerby_uin=(\d+)">拦截')
            for uin in text_list:
                # 拦截
                DaLeDouOne.get(f'cmd=cargo&op=14&passerby_uin={uin}')
                if '恭喜你获得了' in html:
                    self.msg += DaLeDou.findall(r'商店</a><br />(.*?)<br />')
                elif '您今天已达拦截次数上限了' in html:
                    # 护送完成 》领取奖励 》护送押镖 》刷新押镖 》启程护送
                    for op in [3, 16, 7, 8, 6]:
                        DaLeDouOne.get(f'cmd=cargo&op={op}')
                        self.msg += DaLeDou.findall(r'商店</a><br />(.*?)<br />')
                    return

    @deco
    def 幻境(self):
        self.msg += DaLeDou.conversion('幻境')
        stage_id = read_yaml('stage_id', '幻境.yaml')
        DaLeDouOne.get(f'cmd=misty&op=start&stage_id={stage_id}')
        for _ in range(5):
            # 乐斗
            DaLeDouOne.get(f'cmd=misty&op=fight')
            self.msg += DaLeDou.findall(r'累积星数.*?<br />(.*?)<br /><br />')
        # 返回飘渺幻境
        DaLeDouOne.get('cmd=misty&op=return')

    @deco
    def 群雄逐鹿(self):
        if self.week == '6':
            self.msg += DaLeDou.conversion('群雄逐鹿')
            # 报名
            DaLeDouOne.get('cmd=thronesbattle&op=signup')
            self.msg += DaLeDou.findall(r'届群雄逐鹿<br />(.*?)<br />')
            # 领奖
            DaLeDouOne.get('cmd=thronesbattle&op=drawreward')
            self.msg += DaLeDou.findall(r'届群雄逐鹿<br />(.*?)<br />')

    @deco
    def 画卷迷踪(self):
        self.msg += DaLeDou.conversion('画卷迷踪')
        for _ in range(20):
            # 准备完成进入战斗
            DaLeDouOne.get('cmd=scroll_dungeon&op=fight&buff=0')
            if '没有挑战次数' in html:
                break
            elif '征战书不足' in html:
                break
            self.msg += DaLeDou.findall(r'选择</a><br /><br />(.*?)<br />')

    @deco
    def 门派(self):
        from daledou.menpai import MenPai
        self.msg += MenPai().main()

    @deco
    def 门派邀请赛(self):
        if self.week == '1':
            self.msg += DaLeDou.conversion('门派邀请赛')
            # 组队报名
            DaLeDouOne.get('cmd=secttournament&op=signup')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')
            # 领取奖励
            DaLeDouOne.get('cmd=secttournament&op=getrankandrankingreward')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')

        elif self.week not in ['1', '2']:
            self.msg += DaLeDou.conversion('门派邀请赛')
            for _ in range(6):
                # 开始挑战
                DaLeDouOne.get('cmd=secttournament&op=fight')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')

            # 兑换商店
            type = read_yaml('type', '门派邀请赛.yaml')
            times = read_yaml('times', '门派邀请赛.yaml')
            if type:
                # 兑换 or 兑换10个
                DaLeDouOne.get(
                    f'cmd=exchange&subtype=2&type={type}&times={times}&costtype=11')
                self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    @deco
    def 会武(self):
        if self.week in ['1', '2', '3']:
            self.msg += DaLeDou.conversion('会武')
            for _ in range(21):
                # 挑战
                DaLeDouOne.get('cmd=sectmelee&op=dotraining')
                self.msg += DaLeDou.findall(r'最高伤害：\d+<br />(.*?)<br />')
                if '你已达今日挑战上限' in html:
                    self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
                    break
                elif '你的试炼书不足' in html:
                    # 兑换 试炼书*10
                    DaLeDouOne.get(
                        'cmd=exchange&subtype=2&type=1265&times=10&costtype=13')

        elif self.week == '4':
            self.msg += DaLeDou.conversion('会武')
            # 冠军助威 丐帮
            DaLeDouOne.get('cmd=sectmelee&op=cheer&sect=1003')
            # 冠军助威
            DaLeDouOne.get('cmd=sectmelee&op=showcheer')
            self.msg += DaLeDou.findall(r'【冠军助威】<br />(.*?)<br /><br />')

        elif self.week == '6':
            self.msg += DaLeDou.conversion('会武')
            # 领奖
            DaLeDouOne.get('cmd=sectmelee&op=drawreward')
            self.msg += DaLeDou.findall(r'【领奖】<br />(.*?)<br />.*?领取')

            # 兑换 真黄金卷轴*10
            DaLeDouOne.get(
                'cmd=exchange&subtype=2&type=1263&times=10&costtype=13')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    @deco
    def 梦想之旅(self):
        self.msg += DaLeDou.conversion('梦想之旅')
        # 普通旅行
        DaLeDouOne.get('cmd=dreamtrip&sub=2')
        self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
        text_list = DaLeDou.findall(r'梦幻机票：(\d+)<br />')
        c = html.count('未去过')
        self.msg += [f'梦幻机票：{text_list[0]}', f'未去过：{c}']

    @deco
    def 帮派商会(self):
        self.msg += DaLeDou.conversion('帮派商会')

        # 帮派宝库
        DaLeDouOne.get('cmd=fac_corp&op=0')
        text_list = DaLeDou.findall(r'gift_id=(\d+).*?点击领取</a>')
        for id in text_list:
            DaLeDouOne.get(f'cmd=fac_corp&op=3&gift_id={id}&type=0')
            self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

        # 交易会所
        jiaoyi_dict = read_yaml('交易', '帮派商会.yaml')
        DaLeDouOne.get('cmd=fac_corp&op=1')
        for jiaoyi_name, params in jiaoyi_dict.items():
            if jiaoyi_name in html:
                DaLeDouOne.get(f'cmd=fac_corp&op=4&{params}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

        # 兑换商店
        DaLeDouOne.get('cmd=fac_corp&op=2')
        duihuan_dict = read_yaml('兑换', '帮派商会.yaml')
        for duihuan_name, type_id in duihuan_dict.items():
            if duihuan_name in html:
                DaLeDouOne.get(f'cmd=fac_corp&op=5&type_id={type_id}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    @deco
    def 帮派远征军(self):
        self.msg += DaLeDou.conversion('帮派远征军')
        while self.week != '0':
            # 帮派远征军
            DaLeDouOne.get('cmd=factionarmy&op=viewIndex&island_id=-1')
            point_list = DaLeDou.findall(r'point_id=(\d+)">参战')
            if not point_list:
                self.msg += ['已经全部通关了，周日领取奖励']
                return
            for point in point_list:
                # 参战
                DaLeDouOne.get(
                    f'cmd=factionarmy&op=viewpoint&point_id={point}')
                uin_list = DaLeDou.findall(r'opp_uin=(\d+)">攻击')
                for uin in uin_list:
                    # 攻击
                    DaLeDouOne.get(
                        f'cmd=factionarmy&op=fightWithUsr&point_id={point}&opp_uin={uin}')
                    if '参数错误' in html:
                        continue
                    elif '您的血量不足' in html:
                        self.msg += ['您的血量不足，请重生后在进行战斗']
                        # 帮派远征军
                        DaLeDouOne.get(
                            'cmd=factionarmy&op=viewIndex&island_id=-1')
                        self.msg += DaLeDou.findall(
                            r'排行榜</a><br />(.*?)<br />')
                        return

        if self.week == '0':
            # 领取奖励
            for id in range(15):
                DaLeDouOne.get(
                    f'cmd=factionarmy&op=getPointAward&point_id={id}')
                self.msg += DaLeDou.findall(r'【帮派远征军-领取奖励】<br />(.*?)<br />')
            # 领取岛屿宝箱
            for id in range(5):
                DaLeDouOne.get(
                    f'cmd=factionarmy&op=getIslandAward&island_id={id}')
                self.msg += DaLeDou.findall(r'【帮派远征军-领取奖励】<br />(.*?)<br />')

    @deco
    def 帮派黄金联赛(self):
        self.msg += DaLeDou.conversion('帮派黄金联赛')
        # 帮派黄金联赛
        DaLeDouOne.get('cmd=factionleague&op=0')
        if '休赛期' in html:
            self.msg += ['当前处于休赛期，没有可执行的操作']
            return
        if '领取奖励' in html:
            # 领取奖励
            DaLeDouOne.get('cmd=factionleague&op=5')
            self.msg += DaLeDou.findall(r'<p>(.*?)<br /><br />')
        if '领取帮派赛季奖励' in html:
            # 领取帮派赛季奖励
            DaLeDouOne.get('cmd=factionleague&op=7')
            self.msg += DaLeDou.findall(r'<p>(.*?)<br /><br />')
            # 参与防守
            DaLeDouOne.get('cmd=factionleague&op=1')
            self.msg += DaLeDou.findall(r'<p>(.*?)<br /><br />')
        if '参战</a>' in html:
            while True:
                # 参战
                DaLeDouOne.get('cmd=factionleague&op=2')
                text_list = DaLeDou.findall(r'&amp;opp_uin=(\d+)">攻击</a>')
                if not text_list:
                    self.msg += ['已经没有可攻击的对象']
                    break
                for uin in text_list:
                    # 攻击
                    DaLeDouOne.get(f'cmd=factionleague&op=4&opp_uin={uin}')
                    if '您已阵亡' in html:
                        self.msg += ['您已阵亡']
                        return

    @deco
    def 武林盟主(self):
        self.msg += DaLeDou.conversion('武林盟主')
        # 武林盟主
        DaLeDouOne.get('cmd=wlmz&op=view_index')
        if '领取奖励' in html:
            two_tuple_list = DaLeDou.findall(
                r'section_id=(\d+)&amp;round_id=(\d+)">')
            for s, r in two_tuple_list:
                DaLeDouOne.get(
                    f'cmd=wlmz&op=get_award&section_id={s}&round_id={r}')
                self.msg += DaLeDou.findall(r'【武林盟主】<br /><br />(.*?)</p>')
            # 武林盟主
            DaLeDouOne.get('cmd=wlmz&op=view_index')

        if self.week in ['1', '3', '5']:
            # 黄金赛场  1
            # 白银赛场  2
            # 青铜赛场  3
            DaLeDouOne.get(f'cmd=wlmz&op=signup&ground_id=1')
            self.msg += DaLeDou.findall(r'赛场】<br />(.*?)<br />')
        elif self.week in ['2', '4', '6']:
            for index in range(8):
                # 选择
                DaLeDouOne.get(f'cmd=wlmz&op=guess_up&index={index}')
            # 确定竞猜选择
            DaLeDouOne.get('cmd=wlmz&op=comfirm')
            self.msg += DaLeDou.findall(r'战报</a><br />(.*?)<br /><br />')

    @deco
    def 全民乱斗(self):
        '''
        大乱斗 领取
        六门会武 -> 武林盟主 -> 武林大会
        '''
        n = True
        msg = []
        for t in [2, 3, 4]:
            DaLeDouOne.get(f'cmd=luandou&op=0&acttype={t}')
            test_list = DaLeDou.findall(r'.*?id=(\d+)">领取</a>')
            for id in test_list:
                n = False
                # 领取
                DaLeDouOne.get(f'cmd=luandou&op=8&id={id}')
                msg += DaLeDou.findall(r'【全民乱斗】<br /><br />(.*?)<br />大乱斗')
        if not n:
            self.msg += DaLeDou.conversion('全民乱斗')
            self.msg += msg

    @deco
    def 江湖长梦(self):
        from daledou.jianghu import JiangHu
        self.msg += JiangHu().main()

    @deco
    def 任务(self):
        from daledou.missions import Missions
        self.msg += Missions().main()

    @deco
    def 我的帮派(self):
        from daledou.mygang import MyGang
        self.msg += MyGang().main()

    @deco
    def 帮派祭坛(self):
        self.msg += DaLeDou.conversion('帮派祭坛')
        # 帮派祭坛
        DaLeDouOne.get('cmd=altar')
        for _ in range(30):
            if '转转券不足' in html:
                break
            elif '转动轮盘' in html:
                # 转动轮盘
                DaLeDouOne.get('cmd=altar&op=spinwheel')
                self.msg += DaLeDou.findall(
                    r'积分兑换</a><br />(.*?)<br /><br />')
            elif '随机分配' in html:
                two_tuple_list = DaLeDou.findall(
                    r'op=(.*?)&amp;id=(\d+)">选择</a>')
                op, id = two_tuple_list[0]
                # 偷取|选择帮派
                DaLeDouOne.get(f'cmd=altar&op={op}&id={id}')
                if '选择路线' in html:
                    # 选择路线 向前、向左、向右
                    DaLeDouOne.get(f'cmd=altar&op=dosteal&id={id}')
                    if '该帮派已解散' in html:
                        # 偷取|选择帮派
                        _, id = two_tuple_list[1]
                        DaLeDouOne.get(f'cmd=altar&op=dosteal&id={id}')
            elif '领取奖励' in html:
                # 领取奖励
                DaLeDouOne.get('cmd=altar&op=drawreward')

    @deco
    def 飞升大作战(self):
        from daledou.feisheng import FeiSheng
        self.msg += FeiSheng().main()

    @deco
    def 活动(self):
        # 首页
        DaLeDouOne.get('cmd=index')
        if '幸运金蛋' in html:
            self.msg += DaLeDou.conversion('活动')
            self.msg += ['---幸运金蛋---']
            DaLeDouOne.get('cmd=newAct&subtype=110&op=1&index=0')
            self.msg += DaLeDou.findall(r'【幸运金蛋】<br /><br />(.*?)<br /><br />')

    @deco
    def 每日奖励(self):
        self.msg += DaLeDou.conversion('每日奖励')
        for key in ['login', 'meridian', 'daren', 'wuzitianshu']:
            # 每日奖励
            DaLeDouOne.get(f'cmd=dailygift&op=draw&key={key}')
            self.msg += DaLeDou.findall(r'【每日奖励】<br />(.*?)<br />')

    @deco
    def 今日活跃度(self):
        '''
        大桶可乐 移除 影魂1
        DaLeDouOne.get('cmd=upgradepearl&type=5&weapon_id=1184&hole_id=2&pearl_type=6')
        # 大桶可乐 镶嵌 影魂1
        DaLeDouOne.get('cmd=inlaypearl&subcmd=doinlay&weapon_id=1184&hole_id=2&pearl_id=4051')
        '''
        # 乐斗20次 任务
        # 好友第2页
        DaLeDouOne.get(f'cmd=friendlist&page=2')
        text_list = DaLeDou.findall(r'cmd=fight&amp;B_UID=(\d+)')
        for B_UID in text_list:
            # 乐斗 包括心魔
            DaLeDouOne.get(f'cmd=fight&B_UID={B_UID}')

        self.msg += DaLeDou.conversion('今日活跃度')
        # 今日活跃度
        DaLeDouOne.get('cmd=liveness')
        self.msg += DaLeDou.find_tuple(r'【(.*?)】.*?礼包</a><br />(.*?)<a')
        # 领取今日活跃度礼包
        for id in range(1, 5):
            DaLeDouOne.get(f'cmd=liveness_getgiftbag&giftbagid={id}&action=1')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<p>1.')
        # 领取帮派总活跃奖励
        DaLeDouOne.get('cmd=factionop&subtype=18')
        self.msg += DaLeDou.findall(r'<br />(.*?)</p><p>你的职位:')

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
