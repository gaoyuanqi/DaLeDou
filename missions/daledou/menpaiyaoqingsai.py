'''
门派邀请赛
'''
from missions.daledou.daledou import DaLeDou
from missions.daledou.config import read_yaml


class MenPai(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 报名(self):
        if self.week == '1':
            self.msg += DaLeDou.conversion('门派邀请赛')
            # 组队报名
            MenPai.get('cmd=secttournament&op=signup')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')
            # 领取奖励
            MenPai.get('cmd=secttournament&op=getrankandrankingreward')
            self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')

    def 开始挑战(self):
        if self.week not in ['1', '2']:
            self.msg += DaLeDou.conversion('门派邀请赛')
            for _ in range(6):
                # 开始挑战
                MenPai.get('cmd=secttournament&op=fight')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br /><br />')

    def 兑换(self):
        if self.week not in ['1', '2']:
            type = read_yaml('type', '门派邀请赛.yaml')
            times = read_yaml('times', '门派邀请赛.yaml')
            if type:
                # 兑换 or 兑换10个
                MenPai.get(
                    f'cmd=exchange&subtype=2&type={type}&times={times}&costtype=11')
                self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

    def main(self) -> list:
        if DaLeDou.rank() > 40:
            # 40级以上且加入门派开启
            # 门派
            MenPai.get('cmd=sect')
            if '出师' in html:
                self.报名()
                self.开始挑战()
                self.兑换()
                return self.msg

            self.msg += DaLeDou.conversion('门派邀请赛')
            self.msg += ['您需手动加入门派']
            return self.msg
        return []
