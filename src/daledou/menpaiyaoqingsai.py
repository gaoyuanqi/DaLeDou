'''
门派邀请赛
'''
from src.daledou.daledou import DaLeDou


class MenPai(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 报名(self):
        if self.week == '1':
            # 组队报名
            MenPai.get('cmd=secttournament&op=signup')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')
            # 领取奖励
            MenPai.get('cmd=secttournament&op=getrankandrankingreward')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')

    def 开始挑战(self):
        if self.week not in ['1', '2']:
            for _ in range(6):
                # 开始挑战
                MenPai.get('cmd=secttournament&op=fight')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')

    def 兑换(self):
        if self.week not in ['1', '2']:
            data: dict = DaLeDou.readyaml('门派邀请赛')
            id: int = data['id']
            times: int = data['times']
            if id:
                # 兑换 or 兑换10个
                MenPai.get(
                    f'cmd=exchange&subtype=2&type={id}&times={times}&costtype=11')
                self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('门派邀请赛')

        # 门派
        MenPai.get('cmd=sect')
        if '出师' in html:
            self.报名()
            self.开始挑战()
            self.兑换()
            return self.msg

        self.msg += ['您还没有加入门派']
        return self.msg
