'''
飞升大作战
'''
from daledou.daledou import DaLeDou


class FeiSheng(DaLeDou):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 境界修为(self):
        # 境界修为
        FeiSheng.get('cmd=ascendheaven&op=showrealm')
        self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    def 报名(self):
        '''
        优先单排模式，其次匹配模式
        '''
        for _ in range(2):
            # 报名单排模式
            FeiSheng.get('cmd=ascendheaven&op=signup&type=1')
            if '时势造英雄' in html:
                break
            elif '还没有入场券玄铁令' in html:
                # 兑换 玄铁令*1
                FeiSheng.get('cmd=ascendheaven&op=exchange&id=2&times=1')
                if '不足' not in html:
                    # 本赛季该道具库存不足
                    # 积分不足，快去参加飞升大作战吧~
                    continue
            # 当前为休赛期，报名匹配模式
            FeiSheng.get('cmd=ascendheaven&op=signup&type=2')
            break
        self.msg += DaLeDou.findall(r'【飞升大作战】<br />(.*?)<br />S')

    def 领取奖励(self):
        '''
        周四 领取赛季结束奖励
        '''
        # 飞升大作战
        FeiSheng.get('cmd=ascendheaven')
        if ('赛季结算中' in html) and (self.week == '4'):
            # 境界修为
            FeiSheng.get('cmd=ascendheaven&op=showrealm')
            text_list = DaLeDou.findall(r'season=(\d+)')
            for s in text_list:
                # 领取奖励
                FeiSheng.get(f'cmd=ascendheaven&op=getrealmgift&season={s}')
                self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('飞升大作战')

        self.境界修为()
        self.报名()
        self.领取奖励()

        # [2:] 表示切掉多余的 ['【开始时间】', '2022-10-22 21:26:34']
        return self.msg[2:]
