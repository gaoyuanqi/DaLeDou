'''
大乐斗第二轮
默认每天 20:01 执行
'''
from daledou.deco import deco
from daledou.daledou import DaLeDou
from daledou.config import read_yaml


class DaLeDouTwo(DaLeDou):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    @deco
    def 每日宝箱(self):
        if self.date == '20':
            self.msg += DaLeDou.conversion('每日宝箱')
            # 每日宝箱
            DaLeDouTwo.get('cmd=dailychest')
            while text_list := DaLeDou.findall(r'type=(\d+)">打开'):
                # 打开
                DaLeDouTwo.get(f'cmd=dailychest&op=open&type={text_list[0]}')
                self.msg += DaLeDou.findall(r'规则说明</a><br />(.*?)<br />')

    @deco
    def 仙武修真(self):
        self.msg += DaLeDou.conversion('仙武修真')
        for id in range(1, 4):
            # 领取
            DaLeDouTwo.get(f'cmd=immortals&op=getreward&taskid={id}')
            self.msg += DaLeDou.findall(r'帮助</a><br />(.*?)<br />')
        for _ in range(5):
            # 寻访
            DaLeDouTwo.get('cmd=immortals&op=visitimmortals&mountainId=1')
            if '你的今日寻访挑战次数已用光' in html:
                break
            # 挑战
            DaLeDouTwo.get('cmd=immortals&op=fightimmortals')
            self.msg += DaLeDou.findall(r'帮助</a><br />(.*?)<a')

    @deco
    def 大侠回归三重好礼(self):
        if self.week == '4':
            # 大侠回归三重好礼
            DaLeDouTwo.get('cmd=newAct&subtype=173&op=1')
            self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br />')
            two_tuple_list = DaLeDou.findall(r'subtype=(\d+).*?taskid=(\d+)')
            if two_tuple_list:
                self.msg += DaLeDou.conversion('大侠回归三重好礼')
            for s, t in two_tuple_list:
                # 领取
                DaLeDouTwo.get(f'cmd=newAct&subtype={s}&op=2&taskid={t}')
                self.msg += DaLeDou.findall(r'】<br /><br />(.*?)<br />')

    @deco
    def 乐斗黄历(self):
        '''
        乐斗好友10次
        今日活跃度达到60
        今日活跃度达到90
        '''
        self.msg += DaLeDou.conversion('乐斗黄历')
        # 乐斗黄历
        DaLeDouTwo.get('cmd=calender&op=0')
        self.msg += DaLeDou.findall(r'今日任务：(.*?)<br />')
        # 领取
        DaLeDouTwo.get('cmd=calender&op=2')
        self.msg += DaLeDou.findall(r'【乐斗黄历】<br /><br />(.*?)<br />')
        if '任务未完成' in html:
            return
        # 占卜
        DaLeDouTwo.get('cmd=calender&op=4')
        self.msg += DaLeDou.findall(r'【运势占卜】<br /><br />(.*?)<br />')

    @deco
    def 夺宝奇兵(self):
        if self.date == '21':
            self.msg += DaLeDou.conversion('夺宝奇兵')
            # 夺宝奇兵
            DaLeDouTwo.get('cmd=element&subtype=6')
            if '【选择场景】' in html:
                # 太空探宝
                DaLeDouTwo.get('cmd=element&subtype=15&gameType=3')
            while True:
                # 投掷
                DaLeDouTwo.get('cmd=element&subtype=7')
                if '【选择场景】' in html:
                    # 太空探宝
                    DaLeDouTwo.get('cmd=element&subtype=15&gameType=3')
                    text_list = DaLeDou.findall(r'<br />拥有:(.*?)战功<br />')
                    if int(text_list[0]) < 200000:
                        self.msg += [f'战功：{text_list[0]}', '只有大于200000才会探宝']
                        break

    @deco
    def 活动(self):
        from daledou.events import Events
        self.msg += Events().main()

    @deco
    def 背包(self):
        # 武林 》设置 》乐斗助手
        DaLeDouTwo.get('cmd=view&type=6')
        if '开启背包里的提前按钮' in html:
            #  开启背包里的提前按钮
            DaLeDouTwo.get('cmd=set&type=12')

        # 锦囊
        DaLeDouTwo.get('cmd=store&store_type=5&page=1')
        two_tuple_list = DaLeDou.findall(r'数量：(\d+).*?id=(\d+).*?使用')
        for number, id in two_tuple_list:
            if id in ['3023', '3024', '3025', '3103']:
                # xx洗刷刷
                continue
                # 提前
                # DaLeDouTwo.get(f'cmd=topgoods&id={id}&type=2&page=1')
            else:
                for _ in range(int(number)):
                    # 使用
                    DaLeDouTwo.get(f'cmd=use&id={id}&store_type=2&page=1')

        # 属性
        DaLeDouTwo.get('cmd=store&store_type=2&page=1')
        two_tuple_list = DaLeDou.findall(r'数量：(\d+).*?id=(\d+).*?使用')
        for number, id in two_tuple_list:
            for _ in range(int(number)):
                # 使用
                DaLeDouTwo.get(f'cmd=use&id={id}&store_type=2&page=1')

        # 指定物品使用一次
        shiyong_dict = read_yaml('使用', '背包.yaml')
        for id in shiyong_dict:
            # 使用
            DaLeDouTwo.get(f'cmd=use&id={shiyong_dict[id]}&store_type=0')

        # 指定物品提前一次
        if self.week == '4':
            tiqian_dict = read_yaml('提前', '背包.yaml')
            for id in tiqian_dict:
                # 提前
                DaLeDouTwo.get(f'cmd=topgoods&id={tiqian_dict[id]}')

    def 商店积分(self):
        '''
        查询商店积分
        比如矿石商店、粮票商店、功勋商店等中的积分

        1 踢馆
        2 掠夺
        3 矿洞
        4 镖行天下
        9 幻境
        10 群雄逐鹿
        11 门派邀请赛
        12 帮派祭坛
        13 会武
        14 问鼎天下
        '''
        self.msg += DaLeDou.conversion('商店积分')
        for type in [1, 2, 3, 4, 9, 10, 11, 12, 13, 14]:
            DaLeDouTwo.get(f'cmd=exchange&subtype=10&costtype={type}')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

        # 江湖长梦
        # 武林盟主
        # 飞升大作战
        # 深渊之潮
        urls = [
            'cmd=longdreamexchange',
            'cmd=wlmz&op=view_exchange',
            'cmd=ascendheaven&op=viewshop',
            'cmd=abysstide&op=viewabyssshop'
        ]
        for url in urls:
            DaLeDouTwo.get(url)
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

        # 竞技场
        DaLeDouTwo.get('cmd=arena&op=queryexchange')
        self.msg += DaLeDou.findall(r'竞技场</a><br />(.*?)<br /><br />')

        # 帮派商会
        DaLeDouTwo.get('cmd=fac_corp&op=2')
        self.msg += DaLeDou.findall(r'剩余刷新时间.*?秒&nbsp;(.*?)<br />')

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
        self.夺宝奇兵()
        self.活动()
        self.背包()
        self.商店积分()
