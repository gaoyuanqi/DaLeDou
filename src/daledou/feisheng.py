from src.daledou.daledou import DaLeDou


class FeiSheng(DaLeDou):
    '''飞升大作战'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 境界修为(self):
        # 境界修为
        FeiSheng.get('cmd=ascendheaven&op=showrealm')
        self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def 报名(self):
        '''
        优先单排模式，其次匹配模式
        '''
        for _ in range(2):
            # 报名单排模式
            FeiSheng.get('cmd=ascendheaven&op=signup&type=1')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />S'))
            if '时势造英雄' in html:
                break
            elif '还没有入场券玄铁令' in html:
                # 兑换 玄铁令*1
                FeiSheng.get('cmd=ascendheaven&op=exchange&id=2&times=1')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
                if '不足' not in html:
                    # 本赛季该道具库存不足
                    # 积分不足，快去参加飞升大作战吧~
                    continue
            elif '不在报名时间' in html:
                break
            # 当前为休赛期，报名匹配模式
            FeiSheng.get('cmd=ascendheaven&op=signup&type=2')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />S'))
            break

    def 领取奖励(self):
        '''
        周四 领取赛季结束奖励
        '''
        # 飞升大作战
        FeiSheng.get('cmd=ascendheaven')
        if ('赛季结算中' in html):
            # 境界修为
            FeiSheng.get('cmd=ascendheaven&op=showrealm')
            for s in DaLeDou.findall(r'season=(\d+)'):
                # 领取奖励
                FeiSheng.get(f'cmd=ascendheaven&op=getrealmgift&season={s}')
                self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def run(self) -> list:
        self.境界修为()
        self.报名()
        if self.week == '4':
            self.领取奖励()

        return self.msg
