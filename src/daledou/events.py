from src.daledou.daledou import DaLeDou
from random import choice, sample


class EventsOne(DaLeDou):
    '''活动'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 神魔转盘(self):
        EventsOne.get('cmd=newAct&subtype=88&op=1')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 乐斗驿站(self):
        EventsOne.get('cmd=newAct&subtype=167&op=2')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 开心娃娃机(self):
        EventsOne.get('cmd=newAct&subtype=124&op=1')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 好礼步步升(self):
        EventsOne.get('cmd=newAct&subtype=43&op=get')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 浩劫宝箱(self):
        EventsOne.get('cmd=newAct&subtype=152')
        self.msg.append(DaLeDou.search(r'浩劫宝箱<br />(.*?)<br />'))

    def 幸运金蛋(self):
        # 幸运金蛋
        EventsOne.get('cmd=newAct&subtype=110&op=0')
        for i in DaLeDou.findall(r'index=(\d+)'):
            # 砸金蛋
            EventsOne.get(f'cmd=newAct&subtype=110&op=1&index={i}')
            self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)<br />'))

    def 幸运转盘(self):
        EventsOne.get('cmd=newAct&subtype=57&op=roll')
        self.msg.append(DaLeDou.search(r'0<br /><br />(.*?)<br />'))

    def 惊喜刮刮卡(self):
        for i in range(3):
            EventsOne.get(f'cmd=newAct&subtype=148&op=2&id={i}')
            self.msg.append(DaLeDou.search(r'奖池预览</a><br /><br />(.*?)<br />'))

    def 甜蜜夫妻(self):
        for i in range(1, 4):
            # 领取
            EventsOne.get(f'cmd=newAct&subtype=129&op=1&flag={i}')

    def 乐斗菜单(self):
        # 乐斗菜单
        EventsOne.get('cmd=menuact')
        if gift := DaLeDou.findall(r'套餐.*?gift=(\d+).*?点单</a>'):
            # 点单
            EventsOne.get(f'cmd=menuact&sub=1&gift={gift[0]}')
            self.msg.append(DaLeDou.search(r'哦！<br /></p>(.*?)<br />'))
        else:
            self.msg.append('点单已领取完')

    def 客栈同福(self):
        for _ in range(3):
            # 献酒
            EventsOne.get('cmd=newAct&subtype=155')
            self.msg.append(DaLeDou.search(r'】<br /><p>(.*?)<br />'))
            if '黄酒不足' in html:
                break

    def 周周礼包(self):
        # 周周礼包
        EventsOne.get('cmd=weekgiftbag&sub=0')
        if id := DaLeDou.findall(r';id=(\d+)">领取'):
            # 点单
            EventsOne.get(f'cmd=weekgiftbag&sub=1&id={id[0]}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 登录有礼(self):
        # 登录有礼
        EventsOne.get('cmd=newAct&subtype=56')
        # 领取
        if index := DaLeDou.findall(r'gift_index=(\d+)">领取'):
            EventsOne.get(
                f'cmd=newAct&subtype=56&op=draw&gift_type=1&gift_index={index[-1]}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 活跃礼包(self):
        for p in ['1', '2']:
            EventsOne.get(f'cmd=newAct&subtype=94&op={p}')
            self.msg.append(DaLeDou.search(r'】.*?<br />(.*?)<br />'))

    def 猜单双(self):
        # 猜单双
        EventsOne.get('cmd=oddeven')
        for _ in range(5):
            if value := DaLeDou.findall(r'value=(\d+)">.*?数'):
                value = choice(value)
                # 单数1 双数2
                EventsOne.get(f'cmd=oddeven&value={value}')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
            else:
                break

    def 上香活动(self):
        for _ in range(2):
            # 檀木香
            EventsOne.get('cmd=newAct&subtype=142&op=1&id=1')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
            # 龙涎香
            EventsOne.get('cmd=newAct&subtype=142&op=1&id=2')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 徽章战令(self):
        # 每日礼包
        EventsOne.get('cmd=badge&op=1')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 生肖福卡(self):
        # 领取
        EventsOne.get('cmd=newAct&subtype=174&op=7&task_id=1')
        self.msg.append(DaLeDou.search(r'~<br /><br />(.*?)<br />活跃度80'))

    def 长安盛会(self):
        '''
        id
        1           盛会豪礼点击领取
        2           签到宝箱点击领取
        3、4、5     点击参与
        '''
        for _ in range(3):
            # 长安盛会
            DaLeDou.get('cmd=newAct&subtype=118&op=0')
            for id in DaLeDou.findall(r'op=1&amp;id=(\d+)'):
                if id == 3:
                    # 选择奖励内容 3036黄金卷轴 or 5089黄金卷轴
                    EventsOne.get('cmd=newAct&subtype=118&op=2&select_id=3036')
                EventsOne.get(f'cmd=newAct&subtype=118&op=1&id={id}')
                if '【周年嘉年华】' in html:
                    self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)</p>'))
                    return
                else:
                    self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 深渊秘宝(self):
        '''
        三魂秘宝 免费抽奖
        七魄秘宝 免费抽奖
        '''
        # 深渊秘宝
        EventsOne.get('cmd=newAct&subtype=175')
        number: int = html.count('免费抽奖')
        if number == 2:
            for type in range(1, 3):
                EventsOne.get(
                    f'cmd=newAct&subtype=175&op=1&type={type}&times=1')
                self.msg.append(DaLeDou.search(r'深渊秘宝<br />(.*?)<br />'))
        else:
            self.msg.append(f'免费抽奖次数为 {number}，不足两次时该任务不执行')

    def 登录商店(self):
        for _ in range(5):
            # 兑换5次 黄金卷轴*5
            EventsOne.get(
                'cmd=newAct&op=exchange&subtype=52&type=1223&times=5')
            self.msg.append(DaLeDou.search(r'<br /><br />(.*?)<br /><br />'))
        for _ in range(3):
            # 兑换3次 黄金卷轴*1
            EventsOne.get(
                'cmd=newAct&op=exchange&subtype=52&type=1223&times=1')
            self.msg.append(DaLeDou.search(r'<br /><br />(.*?)<br /><br />'))

    def 盛世巡礼(self):
        '''
        对话		cmd=newAct&subtype=150&op=3&itemId=0
        点击继续	cmd=newAct&subtype=150&op=4&itemId=0
        收下礼物	cmd=newAct&subtype=150&op=5&itemId=0
        '''
        for itemId in [0, 4, 6, 9, 11, 14, 17]:
            # 收下礼物
            EventsOne.get(f'cmd=newAct&subtype=150&op=5&itemId={itemId}')
            self.msg.append(DaLeDou.search(r'礼物<br />(.*?)<br />'))

    def 十二周年生日祝福(self):
        for day in range(1, 8):
            EventsOne.get(f'cmd=newAct&subtype=165&op=3&day={day}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 中秋礼盒(self):
        for _ in range(3):
            # 中秋礼盒
            EventsOne.get('cmd=midautumngiftbag&sub=0')
            ids = DaLeDou.findall(r'amp;id=(\d+)')
            if not ids:
                self.msg.append('没有可领取的了')
                break
            for id in ids:
                # 领取
                EventsOne.get(f'cmd=midautumngiftbag&sub=1&id={id}')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
                if '已领取完该系列任务所有奖励' in html:
                    continue

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
        EventsOne.get('cmd=geelyexchange')

        # 修炼任务 》每日任务
        for id in DaLeDou.findall(r'id=(\d+)">领取</a>'):
            # 领取
            EventsOne.get(f'cmd=geelyexchange&op=GetTaskReward&id={id}')
            self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)<br /><br />'))

        # 限时兑换
        date: str = DaLeDou.findall(r'至\d+月(\d+)日')[0]
        if int(self.date) == int(date) - 1:
            data: dict = DaLeDou.read_yaml('活动')
            duihuan_name: list = data['企鹅吉利兑']
            for name in duihuan_name:
                id = DaLeDou.findall(
                    f'{name}.*?op=ExchangeProps&amp;id=(\d+)')[0]
                # used/total 0/1
                used, total = DaLeDou.findall(f'{name}.*?(\d+)/(\d+)')[0]
                if used == total:
                    continue
                for _ in range(int(total)):
                    # 兑换
                    EventsOne.get(
                        f'cmd=geelyexchange&op=ExchangeProps&id={id}')
                    if '你的精魄不足，快去完成任务吧~' in html:
                        break
                    elif '该物品已达兑换上限~' in html:
                        break
                    self.msg.append(DaLeDou.search(
                        r'】<br /><br />(.*?)<br />'))
                if DaLeDou.findall(r'当前精魄：(\d+)')[0] == '0':
                    break

        # 当前精魄
        self.msg.append(DaLeDou.search(r'喔~<br />(.*?)<br /><br />'))

    def 乐斗游记(self):
        # 乐斗游记
        EventsOne.get('cmd=newAct&subtype=176')

        # 今日游记任务
        for id in DaLeDou.findall(r'task_id=(\d+)'):
            # 领取
            EventsOne.get(f'cmd=newAct&subtype=176&op=1&task_id={id}')
            self.msg.append(DaLeDou.search(r'积分。<br /><br />(.*?)<br />'))

        if self.week == '4':
            # 一键领取
            EventsOne.get('cmd=newAct&subtype=176&op=5')
            self.msg.append(DaLeDou.search(r'积分。<br /><br />(.*?)<br />'))
            self.msg.append(DaLeDou.search(r'十次</a><br />(.*?)<br />乐斗'))
            # 兑换
            num_list: list = DaLeDou.findall(r'溢出积分：(\d+)')
            if (num := int(num_list[0])) != 0:
                num10 = int(num / 10)
                num1 = num - (num10 * 10)
                for _ in range(num10):
                    # 兑换十次
                    EventsOne.get('cmd=newAct&subtype=176&op=2&num=10')
                    self.msg.append(DaLeDou.search(
                        r'积分。<br /><br />(.*?)<br />'))
                for _ in range(num1):
                    # 兑换一次
                    EventsOne.get('cmd=newAct&subtype=176&op=2&num=1')
                    self.msg.append(DaLeDou.search(
                        r'积分。<br /><br />(.*?)<br />'))

    def 万圣节(self):
        # 点亮南瓜灯
        EventsOne.get('cmd=hallowmas&gb_id=1')
        while True:
            if cushaw_id := DaLeDou.findall(r'cushaw_id=(\d+)'):
                id = choice(cushaw_id)
                # 南瓜
                EventsOne.get(f'cmd=hallowmas&gb_id=4&cushaw_id={id}')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
            # 恭喜您获得10体力和南瓜灯一个！
            # 恭喜您获得20体力和南瓜灯一个！南瓜灯已刷新
            # 请领取今日的活跃度礼包来获得蜡烛吧！
            if '请领取' in html:
                break

        # 兑换奖励
        EventsOne.get('cmd=hallowmas&gb_id=0')
        date: str = DaLeDou.findall(r'~\d+月(\d+)日')[0]
        if int(self.date) == int(date) - 1:
            num: str = DaLeDou.findall(r'南瓜灯：(\d+)个')[0]
            B = int(num) / 40
            A = (int(num) - int(B) * 40) / 20
            for _ in range(int(B)):
                # 礼包B 消耗40个南瓜灯
                EventsOne.get('cmd=hallowmas&gb_id=6')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
            for _ in range(int(A)):
                # 礼包A 消耗20个南瓜灯
                EventsOne.get('cmd=hallowmas&gb_id=5')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 双节签到(self):
        # 双节签到
        EventsOne.get('cmd=newAct&subtype=144')
        date: str = DaLeDou.findall(r'至\d+月(\d+)日')[0]
        if 'op=1' in html:
            # 领取
            EventsOne.get('cmd=newAct&subtype=144&op=1')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
        if int(self.date) == int(date) - 1:
            # 奖励金
            EventsOne.get('cmd=newAct&subtype=144&op=3')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 圣诞有礼(self):
        # 圣诞有礼
        EventsOne.get('cmd=newAct&subtype=145')
        for id in DaLeDou.findall(r'task_id=(\d+)'):
            # 任务描述：领取奖励
            EventsOne.get(f'cmd=newAct&subtype=145&op=1&task_id={id}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
        # 连线奖励
        for index in DaLeDou.findall(r'index=(\d+)'):
            EventsOne.get(f'cmd=newAct&subtype=145&op=2&index={index}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 乐斗回忆录(self):
        for id in [1, 3, 5, 7, 9]:
            # 回忆礼包
            EventsOne.get(f'cmd=newAct&subtype=171&op=3&id={id}')
            self.msg.append(DaLeDou.search(r'6点<br />(.*?)<br />'))

    def 新春礼包(self):
        # 新春礼包
        EventsOne.get('cmd=xinChunGift&subtype=1')
        date_list = DaLeDou.findall(r'~\d+月(\d+)日')
        giftid = DaLeDou.findall(r'giftid=(\d+)')
        for date, id in zip(date_list, giftid):
            if int(self.date) == int(date) - 1:
                EventsOne.get(f'cmd=xinChunGift&subtype=2&giftid={id}')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 乐斗大笨钟(self):
        # 领取
        EventsOne.get('cmd=newAct&subtype=18')
        self.msg.append(DaLeDou.search(r'<br /><br /><br />(.*?)<br />'))

    def 新春拜年(self):
        # 新春拜年
        EventsOne.get('cmd=newAct&subtype=147')
        if 'op=1' in html:
            for index in sample(range(5), 3):
                # 选中
                EventsOne.get(f'cmd=newAct&subtype=147&op=1&index={index}')
            # 赠礼
            EventsOne.get('cmd=newAct&subtype=147&op=2')
            self.msg.append('已赠礼')

    def 新春登录礼(self):
        # 新春登录礼
        EventsOne.get('cmd=newAct&subtype=99&op=0')
        for day in DaLeDou.findall(r'day=(\d+)'):
            # 领取
            EventsOne.get(f'cmd=newAct&subtype=99&op=1&day={day}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 喜从天降(self):
        # 点燃烟花
        EventsOne.get('cmd=newAct&subtype=137&op=1')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 春联大赛(self):
        # 开始答题
        EventsOne.get('cmd=newAct&subtype=146&op=1')
        if '您的活跃度不足' in html:
            self.msg.append('您的活跃度不足50')
            return
        elif '今日答题已结束' in html:
            self.msg.append('今日答题已结束')
            return

        chunlian = {
            '虎年腾大步': '兔岁展宏图',
            '虎辟长安道': '兔开大吉春',
            '虎跃前程去': '兔携好运来',
            '虎去雄风在': '兔来喜气浓',
            '虎带祥云去': '兔铺锦绣来',
            '虎蹄留胜迹': '兔角搏青云',
            '虎留英雄气': '兔会世纪风',
            '金虎辞旧岁': '银兔贺新春',
            '虎威惊盛世': '兔翰绘新春',
            '虎驰金世界': '兔唤玉乾坤',
            '虎声传捷报': '兔影抖春晖',
            '虎嘶飞雪里': '兔舞画图中',
            '兔归皓月亮': '花绽春光妍',
            '兔俊千山秀': '春暖万水清',
            '兔毫抒壮志': '燕梭织春光',
            '玉兔迎春至': '黄莺报喜来',
            '玉兔迎春到': '红梅祝福来',
            '玉兔蟾宫笑': '红梅五岭香',
            '卯时春入户': '兔岁喜盈门',
            '卯门生紫气': '兔岁报新春',
            '卯来四季美': '兔献百家福',
            '红梅迎春笑': '玉兔出月欢',
            '红梅赠虎岁': '彩烛耀兔年',
            '红梅迎雪放': '玉兔踏春来',
            '丁年歌盛世': '卯兔耀中华',
            '寅年春锦绣': '卯序业辉煌',
            '燕舞春光丽': '兔奔曙光新',
            '笙歌辞旧岁': '兔酒庆新春',
            '瑞雪兆丰年': '迎得玉兔归',
            '雪消狮子瘦': '月满兔儿肥',
        }
        for _ in range(3):
            for s in DaLeDou.findall(r'上联：(.*?) 下联：'):
                x = chunlian.get(s)
                if x is None:
                    # 上联在字库中不存在，将随机选择
                    xialian = [choice(range(3))]
                else:
                    xialian = DaLeDou.findall(f'{x}<a.*?index=(\d+)')
                if xialian:
                    # 选择
                    # index 0 1 2
                    EventsOne.get(
                        f'cmd=newAct&subtype=146&op=3&index={xialian[0]}')
                    self.msg.append(DaLeDou.search(r'剩余\d+题<br />(.*?)<br />'))
                    # 确定选择
                    EventsOne.get('cmd=newAct&subtype=146&op=2')
                    self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

        for id in range(1, 4):
            # 领取
            EventsOne.get(f'cmd=newAct&subtype=146&op=4&id={id}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 年兽大作战(self):
        # 年兽大作战
        EventsOne.get('cmd=newAct&subtype=170&op=0')
        if '等级不够' in html:
            self.msg.append('等级不够，还未开启年兽大作战哦！')
            return
        for _ in DaLeDou.findall(r'剩余免费随机次数：(\d+)'):
            # 随机武技库 免费一次
            EventsOne.get('cmd=newAct&subtype=170&op=6')
            self.msg.append(DaLeDou.search(r'帮助</a><br />(.*?)<br />'))

        # 自选武技库
        # 从大、中、小、投、技各随机选择一个
        if '暂未选择' in html:
            for t in range(5):
                EventsOne.get(f'cmd=newAct&subtype=170&op=4&type={t}')
                if '取消选择' in html:
                    continue
                if ids := DaLeDou.findall(r'id=(\d+)">选择'):
                    # 选择
                    EventsOne.get(
                        f'cmd=newAct&subtype=170&op=7&id={choice(ids)}')
                    if '自选武技列表已满' in html:
                        break

        for _ in range(3):
            # 挑战
            EventsOne.get('cmd=newAct&subtype=170&op=8')
            self.msg.append(DaLeDou.search(r'帮助</a><br />(.*?)。'))

    def 冰雪企缘(self):
        # 冰雪企缘
        EventsOne.get('cmd=newAct&subtype=158&op=0')
        for t in DaLeDou.findall(r'gift_type=(\d+)'):
            # 领取
            EventsOne.get(f'cmd=newAct&subtype=158&op=2&gift_type={t}')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 煮元宵(self):
        # 煮元宵
        EventsOne.get('cmd=yuanxiao2014')
        # number: list = DaLeDou.findall(r'今日剩余烹饪次数：(\d+)')
        for _ in range(4):
            # 开始烹饪
            EventsOne.get('cmd=yuanxiao2014&op=1')
            if '领取烹饪次数' in html:
                self.msg.append('没有烹饪次数了')
                break
            for _ in range(20):
                maturity = DaLeDou.findall(r'当前元宵成熟度：(\d+)')
                if int(maturity[0]) >= 96:
                    # 赶紧出锅
                    EventsOne.get('cmd=yuanxiao2014&op=3')
                    self.msg.append(DaLeDou.search(
                        r'活动规则</a><br /><br />(.*?)。'))
                    break
                # 继续加柴
                EventsOne.get('cmd=yuanxiao2014&op=2')

    def 元宵节(self):
        # 领取
        EventsOne.get('cmd=newAct&subtype=101&op=1')
        self.msg.append(DaLeDou.search(r'】</p>(.*?)<br />'))
        # 领取月桂兔
        EventsOne.get('cmd=newAct&subtype=101&op=2&index=0')
        self.msg.append(DaLeDou.search(r'】</p>(.*?)<br />'))

    def 五一礼包(self):
        for id in range(3):
            EventsOne.get(f'cmd=newAct&subtype=113&op=1&id={id}')
            if '【劳动节礼包】' in html:
                mode = r'】<br /><br />(.*?)</p>'
            else:
                mode = r'】<br /><br />(.*?)<br />'
            self.msg.append(DaLeDou.search(mode))

    def run(self) -> list:
        # 首页
        EventsOne.get('cmd=index')
        events_missions = html

        # 每天要执行的任务
        daily_func_name = {
            '神魔转盘': '神魔转盘',
            '乐斗驿站': '乐斗驿站',
            '开心娃娃机': '开心娃娃机',
            '好礼步步升': '好礼步步升',
            '浩劫宝箱': '浩劫宝箱',
            '幸运金蛋': '幸运金蛋',
            '幸运转盘': '幸运转盘',
            '惊喜刮刮卡': '惊喜刮刮卡',
            '甜蜜夫妻': '甜蜜夫妻',
            '乐斗菜单': '乐斗菜单',
            '客栈同福': '客栈同福',
            '周周礼包': '周周礼包',
            '登录有礼': '登录有礼',
            '活跃礼包': '活跃礼包',
            '猜单双': '猜单双',
            '上香活动': '上香活动',
            '徽章战令': '徽章战令',
            '生肖福卡': '生肖福卡',
            '长安盛会': '长安盛会',
            '深渊秘宝': '深渊秘宝',
            '中秋礼盒': '中秋礼盒',
            '企鹅吉利兑': '企鹅吉利兑',
            '乐斗游记': '乐斗游记',
            '万圣节': '万圣节',
            '双节签到': '双节签到',
            '乐斗大笨钟': '乐斗大笨钟',
            '新春拜年': '新春拜年',
            '新春登录礼': '新春登录礼',
            '喜从天降': '喜从天降',
            '春联大赛': '春联大赛',
            '年兽大作战': '年兽大作战',
            '冰雪企缘': '冰雪企缘',
            '煮元宵': '煮元宵',
        }

        # 周四要执行的任务
        thursday_func_name = {
            '登录商店': '登录商店',
            '盛世巡礼': '盛世巡礼',
            '十二周年生日祝福': '十二周年生日祝福',
            '圣诞有礼': '圣诞有礼',
            '乐斗回忆录': '乐斗回忆录',
            '新春礼包': '新春礼包',
            '元宵节': '元宵节',
            '5.1礼包': '五一礼包',
        }

        if self.week == '4':
            func_name = daily_func_name | thursday_func_name
        else:
            func_name = daily_func_name

        for missions, func in func_name.items():
            if missions in events_missions:
                self.msg.append(f'\n【{missions}】')
                getattr(self, func)()

        return self.msg


class EventsTwo(DaLeDou):
    '''活动'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 幸运金蛋(self):
        # 幸运金蛋
        EventsTwo.get('cmd=newAct&subtype=110&op=0')
        for i in DaLeDou.findall(r'index=(\d+)'):
            # 砸金蛋
            EventsTwo.get(f'cmd=newAct&subtype=110&op=1&index={i}')
            self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)<br />'))

    def 乐斗大笨钟(self):
        # 领取
        EventsTwo.get('cmd=newAct&subtype=18')
        self.msg.append(DaLeDou.search(r'<br /><br /><br />(.*?)<br />'))

    def 新春拜年(self):
        # 新春拜年
        EventsTwo.get('cmd=newAct&subtype=147')
        if 'op=3' in html:
            # 收取礼物
            EventsTwo.get('cmd=newAct&subtype=147&op=3')
            self.msg.append(DaLeDou.search(r'祝您：.*?<br /><br />(.*?)<br />'))

    def run(self) -> list:
        # 首页
        EventsTwo.get('cmd=index')
        events_missions = html

        func_name = {
            '幸运金蛋': "幸运金蛋",
            '乐斗大笨钟': '乐斗大笨钟',
            '新春拜年': '新春拜年',
        }

        for missions, func in func_name.items():
            if missions in events_missions:
                self.msg.append(f'\n【{missions}】')
                getattr(self, func)()

        return self.msg
