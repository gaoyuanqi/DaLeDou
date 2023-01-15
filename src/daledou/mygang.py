'''
我的帮派
'''
from src.daledou.daledou import DaLeDou


class MyGang(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 供奉(self):
        '''
        【背包】部分靠前物品会被供奉
        '''
        for _ in range(5):
            # 供奉守护神
            MyGang.get('cmd=viewolbation')
            id: list = DaLeDou.findall(r'数量：.*?id=(\d+).*?供奉</a>')
            # 供奉
            MyGang.get(f'cmd=oblation&id={id[0]}&page=1')
            self.msg += DaLeDou.findall(r'【供奉守护神】<br />(.*?)<br />')

    def 帮战(self):
        '''
        周日 领取奖励 》报名帮派战争 》激活祝福
        '''
        if self.week == '0':
            for sub in [4, 9, 6]:
                MyGang.get(f'cmd=facwar&sub={sub}')
                self.msg += DaLeDou.findall(r'</p>(.*?)<br /><a.*?查看上届')

    def 帮派任务(self):
        '''
        2727  紫霞秘籍
        2758  逍遥心法
        2505  铁砂掌
        2536  真元护体
        2437  九阳神功
        2442  金钟罩
        2377  北冥神功
        2399  乾坤大挪移
        2429  养生之道
        '''
        # 帮派任务
        MyGang.get('cmd=factiontask&sub=1')
        faction_missions: str = html

        missions = {
            '帮战冠军': 'cmd=facwar&sub=4',
            '查看帮战': 'cmd=facwar&sub=4',
            '查看帮贡': 'cmd=factionhr&subtype=14',
            '查看祭坛': 'cmd=altar',
            '查看踢馆': 'cmd=facchallenge&subtype=0',
            '查看要闻': 'cmd=factionop&subtype=8&pageno=1&type=2',
            # '加速贡献': 'cmd=use&id=3038&store_type=1&page=1',
            '粮草掠夺': 'cmd=forage_war',
        }
        for name, url in missions.items():
            if name in faction_missions:
                MyGang.get(url)

        if '帮派修炼' in faction_missions:
            n = 0
            for id in [2727, 2758, 2505, 2536, 2437, 2442, 2377, 2399, 2429]:
                for _ in range(4):
                    MyGang.get(
                        f'cmd=factiontrain&type=2&id={id}&num=1&i_p_w=num%7C')
                    if '你需要提升帮派等级来让你进行下一步的修炼' in html:
                        if id == 2429:
                            self.msg += ['所有武功秘籍已满级']
                        break
                    elif '技能经验增加' in html:
                        # 技能经验增加20！
                        n += 1
                if n == 4:
                    break

        # 帮派任务
        MyGang.get('cmd=factiontask&sub=1')
        ids: list = DaLeDou.findall(r'id=(\d+)">领取奖励</a>')
        for id in ids:
            # 领取奖励
            MyGang.get(f'cmd=factiontask&sub=3&id={id}')
        self.msg += DaLeDou.findall_tuple(r'id=\d+">(.*?)</a>(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('我的帮派')

        # 我的帮派
        MyGang.get('cmd=factionop&subtype=3&facid=0')
        if '你的职位' in html:
            self.供奉()
            self.帮战()
            self.帮派任务()
            return self.msg

        self.msg += ['您还没有加入帮派']
        return self.msg
