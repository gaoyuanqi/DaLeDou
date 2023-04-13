from src.daledou.daledou import DaLeDou


class BangPai(DaLeDou):
    '''帮派远征军'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 参战(self):
        while True:
            # 帮派远征军
            BangPai.get('cmd=factionarmy&op=viewIndex&island_id=-1')
            point_id = DaLeDou.findall(r'point_id=(\d+)">参战')
            if not point_id:
                self.msg.append('已经全部通关了，周日领取奖励')
                break
            for p in point_id:
                # 参战
                BangPai.get(f'cmd=factionarmy&op=viewpoint&point_id={p}')
                for uin in DaLeDou.findall(r'opp_uin=(\d+)">攻击'):
                    # 攻击
                    BangPai.get(
                        f'cmd=factionarmy&op=fightWithUsr&point_id={p}&opp_uin={uin}')
                    if '参数错误' in html:
                        continue
                    elif '您的血量不足' in html:
                        self.msg.append('您的血量不足，请重生后在进行战斗')
                        return

    def 领取奖励(self):
        # 领取奖励
        for id in range(15):
            BangPai.get(
                f'cmd=factionarmy&op=getPointAward&point_id={id}')
            self.msg.append(DaLeDou.search(r'领取奖励】<br />(.*?)<br />'))
        # 领取岛屿宝箱
        for id in range(5):
            BangPai.get(
                f'cmd=factionarmy&op=getIslandAward&island_id={id}')
            self.msg.append(DaLeDou.search(r'领取奖励】<br />(.*?)<br />'))

    def run(self) -> list:
        if self.week != '0':
            self.参战()
        else:
            self.领取奖励()

        return self.msg
