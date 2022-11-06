'''
帮派黄金联赛
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

    def 帮派黄金联赛(self):
        # 帮派黄金联赛
        BangPai.get('cmd=factionleague&op=0')
        if '休赛期' in html:
            self.msg += ['当前处于休赛期，没有可执行的操作']
            return
        if '领取奖励' in html:
            # 领取奖励
            BangPai.get('cmd=factionleague&op=5')
            self.msg += DaLeDou.findall(r'<p>(.*?)<br /><br />')
        if '领取帮派赛季奖励' in html:
            # 领取帮派赛季奖励
            BangPai.get('cmd=factionleague&op=7')
            self.msg += DaLeDou.findall(r'<p>(.*?)<br /><br />')
            # 参与防守
            BangPai.get('cmd=factionleague&op=1')
            self.msg += DaLeDou.findall(r'<p>(.*?)<br /><br />')
        if '参战</a>' in html:
            while True:
                # 参战
                BangPai.get('cmd=factionleague&op=2')
                text_list = DaLeDou.findall(r'&amp;opp_uin=(\d+)">攻击</a>')
                if not text_list:
                    self.msg += ['已经没有可攻击的对象']
                    break
                for uin in text_list:
                    # 攻击
                    BangPai.get(f'cmd=factionleague&op=4&opp_uin={uin}')
                    if '您已阵亡' in html:
                        self.msg += ['您已阵亡']
                        return

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('帮派黄金联赛')

        self.帮派黄金联赛()

        return self.msg
