from src.daledou.daledou import DaLeDou


class MenPai(DaLeDou):
    '''门派邀请赛'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 报名(self):
        # 组队报名
        MenPai.get('cmd=secttournament&op=signup')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))
        # 领取奖励
        MenPai.get('cmd=secttournament&op=getrankandrankingreward')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

    def 开始挑战(self):
        for _ in range(6):
            # 开始挑战
            MenPai.get('cmd=secttournament&op=fight')
            self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

    def 兑换(self):
        if t := DaLeDou.read_yaml('门派邀请赛'):
            # 兑换10个
            MenPai.get(f'cmd=exchange&subtype=2&type={t}&times=10&costtype=11')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))

    def run(self) -> list:
        if self.week == '1':
            self.报名()
        elif self.week not in ['1', '2']:
            self.开始挑战()
            self.兑换()

        return self.msg
