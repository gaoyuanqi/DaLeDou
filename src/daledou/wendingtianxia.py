from src.daledou.daledou import DaLeDou


class WenDingOne(DaLeDou):
    '''问鼎天下 第一轮'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        '''周一领取奖励'''
        WenDingOne.get('cmd=tbattle&op=drawreward')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

    def 攻占(self):
        '''周一~周五攻占东海倒数第一个

        至多攻占2次，直到大获全胜结束攻占
        '''
        # 问鼎天下
        WenDingOne.get('cmd=tbattle')
        if '你占领的领地已经枯竭' in html:
            # 领取
            WenDingOne.get('cmd=tbattle&op=drawreleasereward')
            self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))
        elif '放弃' in html:
            # 放弃
            WenDingOne.get('cmd=tbattle&op=abandon')
            self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

        for _ in range(2):
            # 1东海 2南荒   3西泽   4北寒
            WenDingOne.get(f'cmd=tbattle&op=showregion&region=1')
            # 攻占 倒数第一个
            if id := DaLeDou.findall(r'id=(\d+).*?攻占</a>'):
                WenDingOne.get(f'cmd=tbattle&op=occupy&id={id[-1]}&region=1')
                self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))
                if '大获全胜' in html:
                    break

    def 淘汰赛(self):
        '''神ㄨ阁丶 周六助威'''
        # 助威
        WenDingOne.get(f'cmd=tbattle&op=cheerregionbattle&id=10215')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

    def 排名赛(self):
        '''神ㄨ阁丶 周日助威'''
        WenDingOne.get(f'cmd=tbattle&op=cheerchampionbattle&id=10215')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

    def run(self) -> list:
        if self.week == '1':
            self.领取奖励()
        if self.week not in ['6', '0']:
            self.攻占()
        elif self.week == '6':
            self.淘汰赛()
        elif self.week == '0':
            self.排名赛()

        return self.msg


class WenDingTwo(DaLeDou):
    '''问鼎天下 第二轮'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 攻占(self):
        '''周一~周五攻占东海倒数第一个

        至多攻占3次，直到大获全胜结束攻占
        '''
        # 问鼎天下
        WenDingTwo.get('cmd=tbattle')
        if '你占领的领地已经枯竭' in html:
            # 领取
            WenDingTwo.get('cmd=tbattle&op=drawreleasereward')
            self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))
        elif '放弃' in html:
            # 放弃
            WenDingTwo.get('cmd=tbattle&op=abandon')
            self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

        for _ in range(3):
            # 1东海 2南荒   3西泽   4北寒
            WenDingTwo.get(f'cmd=tbattle&op=showregion&region=1')
            # 攻占 倒数第一个
            if id := DaLeDou.findall(r'id=(\d+).*?攻占</a>'):
                WenDingTwo.get(f'cmd=tbattle&op=occupy&id={id[-1]}&region=1')
                self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))
                if '大获全胜' in html:
                    break

    def run(self) -> list:
        if self.week not in ['6', '0']:
            self.攻占()

        return self.msg
