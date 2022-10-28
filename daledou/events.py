'''
大乐斗【活动】
'''
import random

from daledou.daledou import DaLeDou
from daledou.config import read_yaml


class Events(DaLeDou):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 浩劫宝箱(self):
        Events.get('cmd=newAct&subtype=152')
        self.msg += DaLeDou.findall(r'浩劫宝箱<br />(.*?)<br />')

    def 幸运金蛋(self):
        Events.get('cmd=newAct&subtype=110&op=1&index=1')
        self.msg += DaLeDou.findall(r'【幸运金蛋】<br /><br />(.*?)<br />')

    def 幸运转盘(self):
        Events.get('cmd=newAct&subtype=57&op=roll')
        self.msg += DaLeDou.findall(r'0<br /><br />(.*?)<br />')

    def 惊喜刮刮卡(self):
        for i in range(3):
            Events.get(f'cmd=newAct&subtype=148&op=2&id={i}')
            self.msg += DaLeDou.findall(
                r'奖池预览</a><br /><br />(.*?)<br /><br />')

    def 甜蜜夫妻(self):
        for i in range(1, 4):
            # 领取
            Events.get(f'cmd=newAct&subtype=129&op=1&flag={i}')

    def 乐斗菜单(self):
        Events.get('cmd=menuact')
        # 乐斗菜单
        text_list = DaLeDou.findall(r'套餐.*?gift=(\d+).*?点单</a>')
        if text_list:
            # 点单
            Events.get(f'cmd=menuact&sub=1&gift={text_list[0]}')
            self.msg += DaLeDou.findall(r'每日只能点取一份套餐哦！<br /></p>(.*?)<br />')
        else:
            self.msg += ['点单已领取完']

    def 客栈同福(self):
        for _ in range(3):
            # 献酒
            Events.get('cmd=newAct&subtype=155')
            self.msg += DaLeDou.findall(r'【客栈同福】<br /><p>(.*?)<br />')
            if '黄酒不足' in html:
                break

    def 周周礼包(self):
        # 周周礼包
        Events.get('cmd=weekgiftbag&sub=0')
        text_list = DaLeDou.findall(r';id=(\d+)">领取')
        if text_list:
            # 点单
            Events.get(f'cmd=weekgiftbag&sub=1&id={text_list[0]}')
            self.msg += DaLeDou.findall(r'【周周礼包】<br />(.*?)<br />')

    def 登录有礼(self):
        # 登录有礼
        Events.get('cmd=newAct&subtype=56')
        text_list = DaLeDou.findall(r'gift_index=(\d+)">领取')
        # 领取
        if text_list:
            Events.get(
                f'cmd=newAct&subtype=56&op=draw&gift_type=1&gift_index={text_list[-1]}')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    def 活跃礼包(self):
        Events.get('cmd=newAct&subtype=94&op=1')
        self.msg += DaLeDou.findall(r'【活跃礼包】.*?<br />(.*?)<br />')
        Events.get('cmd=newAct&subtype=94&op=2')
        self.msg += DaLeDou.findall(r'【活跃礼包】.*?<br />(.*?)<br />')

    def 猜单双(self):
        # 猜单双
        Events.get('cmd=oddeven')
        for _ in range(5):
            text_list = DaLeDou.findall(r'value=(\d+)">.*?数')
            if text_list:
                value = random.choice(text_list)
                # 单数1 双数2
                Events.get(f'cmd=oddeven&value={value}')
                self.msg += DaLeDou.findall(r'【猜单双】<br />(.*?)<br />')
            else:
                break

    def 上香活动(self):
        for _ in range(2):
            # 檀木香
            Events.get('cmd=newAct&subtype=142&op=1&id=1')
            self.msg += DaLeDou.findall(r'【缅怀金庸先生上香】<br />(.*?)<br />')
            # 龙涎香
            Events.get('cmd=newAct&subtype=142&op=1&id=2')
            self.msg += DaLeDou.findall(r'【缅怀金庸先生上香】<br />(.*?)<br />')

    def 徽章战令(self):
        # 每日礼包
        Events.get('cmd=badge&op=1')
        self.msg += DaLeDou.findall(r'【徽章战令】<br />(.*?)<br />')

    def 生肖福卡(self):
        # 领取
        Events.get('cmd=newAct&subtype=174&op=7&task_id=1')
        self.msg += DaLeDou.findall(r'~<br /><br />(.*?)<br />活跃度80')

    def 长安盛会(self):
        # 【盛会豪礼】 点击领取
        Events.get('cmd=newAct&subtype=118&op=1&id=1')
        self.msg += DaLeDou.findall(r'【长安盛会】<br />(.*?)<br />')
        # 【签到宝箱】 点击领取
        Events.get('cmd=newAct&subtype=118&op=1&id=2')
        self.msg += DaLeDou.findall(r'【长安盛会】<br />(.*?)<br />')
        # 点击参与
        for _ in range(3):
            Events.get('cmd=newAct&subtype=118&op=1&id=5')
            self.msg += DaLeDou.findall(r'【长安盛会】<br />(.*?)<br />')
            if '剩余次数不足' in html:
                break

    def 深渊秘宝(self):
        '''
        三魂秘宝 免费抽奖
        七魄秘宝 免费抽奖
        '''
        # 深渊秘宝
        Events.get('cmd=newAct&subtype=175')
        number = html.count('免费抽奖')
        if number == 2:
            for type in range(1, 3):
                Events.get(f'cmd=newAct&subtype=175&op=1&type={type}&times=1')
                self.msg += DaLeDou.findall(r'深渊秘宝<br />(.*?)<br />')
        else:
            self.msg += [f'免费抽奖次数为 {number}，不足两次时该任务不执行']

    def 登录商店(self):
        for _ in range(5):
            # 兑换5次 黄金卷轴*5
            Events.get('cmd=newAct&op=exchange&subtype=52&type=1223&times=5')
            self.msg += DaLeDou.findall(r'<br /><br />(.*?)<br /><br />')
        for _ in range(3):
            # 兑换3次 黄金卷轴*1
            Events.get('cmd=newAct&op=exchange&subtype=52&type=1223&times=1')
            self.msg += DaLeDou.findall(r'<br /><br />(.*?)<br /><br />')

    def 盛世巡礼(self):
        '''
        对话		cmd=newAct&subtype=150&op=3&itemId=0
        点击继续	cmd=newAct&subtype=150&op=4&itemId=0
        收下礼物	cmd=newAct&subtype=150&op=5&itemId=0
        '''
        for itemId in [0, 4, 6, 9, 11, 14, 17]:
            # 收下礼物
            Events.get(f'cmd=newAct&subtype=150&op=5&itemId={itemId}')
            self.msg += DaLeDou.findall(r'礼物<br />(.*?)<br />')

    def 十二周年生日祝福(self):
        for day in range(1, 8):
            Events.get(f'cmd=newAct&subtype=165&op=3&day={day}')
            self.msg += DaLeDou.findall(r'【乐斗生日祝福】<br />(.*?)<br />')

    def 中秋礼盒(self):
        for _ in range(3):
            # 中秋礼盒
            Events.get('cmd=midautumngiftbag&sub=0')
            id_list = DaLeDou.findall(r'amp;id=(\d+)')
            if not id_list:
                self.msg.append('没有可领取的了')
                break
            for id in id_list:
                # 领取
                Events.get(f'cmd=midautumngiftbag&sub=1&id={id}')
                if '已领取完该系列任务所有奖励' in html:
                    continue
                self.msg += DaLeDou.findall(r'【中秋礼盒】<br />(.*?)<br />')

    def 企鹅吉利兑(self):
        '''
        id  消耗
        1   180 泯灭·苍玉IV
        2   180 破坏·银光IV
        3   180 洞悉·异炎IV
        4   180 破坏·锦月IV
        5   20  V级万能碎片
        6   2   熔炼乌金
        7   2   玄铁令
        8   1   挑战书
        '''
        # 企鹅吉利兑
        Events.get('cmd=geelyexchange')
        self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br />')

        # 修炼任务 》每日任务
        id_list = DaLeDou.findall(r'id=(\d+)">领取</a>')
        for id in id_list:
            # 领取
            Events.get(f'cmd=geelyexchange&op=GetTaskReward&id={id}')
            self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br /><br />')

        # 限时兑换
        date = DaLeDou.findall(r'至\d+月(\d+)日')[0]
        if int(self.date) == int(date) - 1:
            name_list = read_yaml('企鹅吉利兑', '活动.yaml')
            for name in name_list:
                id = DaLeDou.findall(
                    f'{name}.*?op=ExchangeProps&amp;id=(\d+)')[0]
                # used/total 0/1
                used, total = DaLeDou.findall(f'{name}.*?(\d+)/(\d+)')[0]
                if used == total:
                    continue
                for _ in range(int(total)):
                    # 兑换
                    Events.get(f'cmd=geelyexchange&op=ExchangeProps&id={id}')
                    if '你的精魄不足，快去完成任务吧~' in html:
                        break
                    elif '该物品已达兑换上限~' in html:
                        break
                    self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br />')
                if DaLeDou.findall(r'当前精魄：(\d+)')[0] == '0':
                    break

        # 当前精魄
        self.msg += DaLeDou.findall(r'喔~<br />(.*?)<br /><br />')
        # 兑换详情
        msg = DaLeDou.find_tuple(
            r'兑换==<br />(.*?)&nbsp;&nbsp;&nbsp;&nbsp;(.*?)&')
        self.msg += [f'{msg[0]} {msg[1]}']
        self.msg += DaLeDou.findall_tuple(
            r'精魄兑换</a><br />(.*?)&nbsp;&nbsp;&nbsp;&nbsp;(.*?)&')

    def 乐斗游记(self):
        # 乐斗游记
        Events.get('cmd=newAct&subtype=176')

        # 今日游记任务
        text_list = DaLeDou.findall(r'task_id=(\d+)')
        for id in text_list:
            # 领取
            Events.get(f'cmd=newAct&subtype=176&op=1&task_id={id}')
            self.msg += DaLeDou.findall(r'积分。<br /><br />(.*?)<br />')

        if self.week == '4':
            # 一键领取
            Events.get('cmd=newAct&subtype=176&op=5')
            self.msg += DaLeDou.findall(r'积分。<br /><br />(.*?)<br />')
            self.msg += DaLeDou.findall(r'十次</a><br />(.*?)<br />乐斗')
            # 兑换
            text_list = DaLeDou.findall(r'溢出积分：(\d+)')
            if (num := int(text_list[0])) != 0:
                num10 = int(num / 10)
                num1 = num - (num10 * 10)
                for _ in range(num10):
                    # 兑换十次
                    Events.get('cmd=newAct&subtype=176&op=2&num=10')
                    self.msg += DaLeDou.findall(r'积分。<br /><br />(.*?)<br />')
                for _ in range(num1):
                    # 兑换一次
                    Events.get('cmd=newAct&subtype=176&op=2&num=1')
                    self.msg += DaLeDou.findall(r'积分。<br /><br />(.*?)<br />')

    def 万圣节(self):
        # 点亮南瓜灯
        Events.get('cmd=hallowmas&gb_id=1')
        for _ in range(20):
            text_list = DaLeDou.findall(f'cushaw_id=(\d+)')
            for id in text_list:
                Events.get(f'cmd=hallowmas&gb_id=4&cushaw_id={id}')
                self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')
                if '恭喜您' in html:
                    # 恭喜您获得10体力和南瓜灯一个！
                    # 恭喜您获得20体力和南瓜灯一个！南瓜灯已刷新
                    break
                elif '请领取' in html:
                    # 请领取今日的活跃度礼包来获得蜡烛吧！
                    return

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('活动')

        # 首页
        Events.get('cmd=index')
        events_missions = html

        missions = {
            '神魔转盘': 'cmd=newAct&subtype=88&op=1',
            '乐斗驿站': 'cmd=newAct&subtype=167&op=2',
            '双节签到': 'cmd=newAct&subtype=144',
            '圣诞有礼': 'cmd=newAct&subtype=145',
            '开心娃娃机': 'cmd=newAct&subtype=124&op=1',
            '好礼步步升': 'cmd=newAct&subtype=43&op=get',
        }
        for name, url in missions.items():
            if name in events_missions:
                Events.get(url)
                self.msg += [f'---{name}---']
                self.msg += DaLeDou.findall(f'【{name}】<br />(.*?)<br />')

        if '浩劫宝箱' in events_missions:
            self.msg += ['---浩劫宝箱---']
            self.浩劫宝箱()
        if '幸运金蛋' in events_missions:
            self.msg += ['---幸运金蛋---']
            self.幸运金蛋()
        if '幸运转盘' in events_missions:
            self.msg += ['---幸运转盘---']
            self.幸运转盘()
        if '惊喜刮刮卡' in events_missions:
            self.msg += ['---惊喜刮刮卡---']
            self.惊喜刮刮卡()
        if '甜蜜夫妻' in events_missions:
            self.msg += ['---甜蜜夫妻---']
            self.甜蜜夫妻()
        if '乐斗菜单' in events_missions:
            self.msg += ['---乐斗菜单---']
            self.乐斗菜单()
        if '客栈同福' in events_missions:
            self.msg += ['---客栈同福---']
            self.客栈同福()
        if '周周礼包' in events_missions:
            self.msg += ['---周周礼包---']
            self.周周礼包()
        if '登录有礼' in events_missions:
            self.msg += ['---登录有礼---']
            self.登录有礼()
        if '活跃礼包' in events_missions:
            self.msg += ['---活跃礼包---']
            self.活跃礼包()
        if '猜单双' in events_missions:
            self.msg += ['---猜单双---']
            self.猜单双()
        if '上香活动' in events_missions:
            self.msg += ['---上香活动---']
            self.上香活动()
        if '徽章战令' in events_missions:
            self.msg += ['---徽章战令---']
            self.徽章战令()
        if '生肖福卡' in events_missions:
            self.msg += ['---生肖福卡---']
            self.生肖福卡()
        if '长安盛会' in events_missions:
            self.msg += ['---长安盛会---']
            self.长安盛会()
        if '深渊秘宝' in events_missions:
            self.msg += ['---深渊秘宝---']
            self.深渊秘宝()
        if '中秋礼盒' in events_missions:
            self.msg += ['---中秋礼盒---']
            self.中秋礼盒()
        if '企鹅吉利兑' in events_missions:
            self.msg += ['---企鹅吉利兑---']
            self.企鹅吉利兑()
        if '乐斗游记' in events_missions:
            self.msg += ['---乐斗游记---']
            self.乐斗游记()
        if '万圣节' in events_missions:
            self.msg += ['---万圣节---']
            self.万圣节()

        if self.week == '4':
            if '登录商店' in events_missions:
                self.msg += ['---登录商店---']
                self.登录商店()
            if '盛世巡礼' in events_missions:
                self.msg += ['---盛世巡礼---']
                self.盛世巡礼()
            if '十二周年生日祝福' in events_missions:
                self.msg += ['---十二周年生日祝福---']
                self.十二周年生日祝福()

        # [2:] 表示切掉多余的 ['【开始时间】', '2022-10-22 21:26:34']
        return self.msg[2:]
