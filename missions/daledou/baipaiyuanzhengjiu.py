'''
帮派远征军
'''
from missions.daledou.daledou import DaLeDou


class BangPai(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 参战(self):
        while self.week != '0':
            # 帮派远征军
            BangPai.get('cmd=factionarmy&op=viewIndex&island_id=-1')
            point_list = DaLeDou.findall(r'point_id=(\d+)">参战')
            if not point_list:
                self.msg += ['已经全部通关了，周日领取奖励']
                return
            for point in point_list:
                # 参战
                BangPai.get(
                    f'cmd=factionarmy&op=viewpoint&point_id={point}')
                uin_list = DaLeDou.findall(r'opp_uin=(\d+)">攻击')
                for uin in uin_list:
                    # 攻击
                    BangPai.get(
                        f'cmd=factionarmy&op=fightWithUsr&point_id={point}&opp_uin={uin}')
                    if '参数错误' in html:
                        continue
                    elif '您的血量不足' in html:
                        self.msg += ['您的血量不足，请重生后在进行战斗']
                        # 帮派远征军
                        BangPai.get(
                            'cmd=factionarmy&op=viewIndex&island_id=-1')
                        self.msg += DaLeDou.findall(
                            r'排行榜</a><br />(.*?)<br />')
                        return

    def 领取奖励(self):
        if self.week == '0':
            # 领取奖励
            for id in range(15):
                BangPai.get(
                    f'cmd=factionarmy&op=getPointAward&point_id={id}')
                self.msg += DaLeDou.findall(r'【帮派远征军-领取奖励】<br />(.*?)<br />')
            # 领取岛屿宝箱
            for id in range(5):
                BangPai.get(
                    f'cmd=factionarmy&op=getIslandAward&island_id={id}')
                self.msg += DaLeDou.findall(r'【帮派远征军-领取奖励】<br />(.*?)<br />')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('帮派远征军')

        self.参战()
        self.领取奖励()

        return self.msg
