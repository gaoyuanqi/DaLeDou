from src.daledou.daledou import DaLeDou


class BangPai(DaLeDou):
    '''帮派黄金联赛'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def get_data(self) -> list:
        '''获取对方防守列表所有战力和uin'''
        # 参战
        BangPai.get('cmd=factionleague&op=2')
        if pages := DaLeDou.findall(r'pages=(\d+)">末页'):
            uin = []
            for p in range(1, int(pages[0]) + 1):
                BangPai.get(f'cmd=factionleague&op=2&pages={p}')
                uin += DaLeDou.findall(r'%&nbsp;&nbsp;(\d+).*?opp_uin=(\d+)')
            # 按战力排序
            uin.sort()
            return uin
        self.msg.append('没有可攻击的敌人')
        return []

    def 帮派黄金联赛(self):
        # 帮派黄金联赛
        BangPai.get('cmd=factionleague&op=0')
        data: bool = DaLeDou.read_yaml('帮派黄金联赛')
        if '休赛期' in html:
            self.msg.append('当前处于休赛期，没有可执行的操作')
            return
        if '领取奖励' in html:
            # 领取奖励
            BangPai.get('cmd=factionleague&op=5')
            self.msg.append(DaLeDou.search(r'<p>(.*?)<br /><br />'))
        if '领取帮派赛季奖励' in html:
            # 领取帮派赛季奖励
            BangPai.get('cmd=factionleague&op=7')
            self.msg.append(DaLeDou.search(r'<p>(.*?)<br /><br />'))
            if data:
                # 参与防守
                BangPai.get('cmd=factionleague&op=1')
                self.msg.append(DaLeDou.search(r'<p>(.*?)<br /><br />'))
        if ('参战</a>' in html) and data:
            for _, uin in self.get_data():
                # 攻击
                BangPai.get(f'cmd=factionleague&op=4&opp_uin={uin}')
                if '不幸战败' in html:
                    self.msg.append(DaLeDou.search(r'】<br />(.*?)<br />'))
                    break
                elif '您已阵亡' in html:
                    self.msg.append(DaLeDou.search(r'】<br /><br />(.*?)</p>'))
                    break
                DaLeDou.search(r'】<br />(.*?)<br />')

    def run(self) -> list:
        self.帮派黄金联赛()

        return self.msg
