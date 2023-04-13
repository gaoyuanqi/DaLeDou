from src.daledou.daledou import DaLeDou


class WuLin(DaLeDou):
    '''武林盟主'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        # 武林盟主
        WuLin.get('cmd=wlmz&op=view_index')
        if '领取奖励' in html:
            for s, r in DaLeDou.findall(r'section_id=(\d+)&amp;round_id=(\d+)">'):
                WuLin.get(
                    f'cmd=wlmz&op=get_award&section_id={s}&round_id={r}')
                self.msg.append(DaLeDou.search(r'【武林盟主】<br /><br />(.*?)</p>'))
            # 武林盟主
            WuLin.get('cmd=wlmz&op=view_index')

    def 报名(self):
        '''
        黄金赛场  1
        白银赛场  2
        青铜赛场  3
        '''
        data = DaLeDou.read_yaml('武林盟主')
        WuLin.get(f'cmd=wlmz&op=signup&ground_id={data}')
        self.msg.append(DaLeDou.search(r'赛场】<br />(.*?)<br />'))

    def 竞猜(self):
        for index in range(8):
            # 选择
            WuLin.get(f'cmd=wlmz&op=guess_up&index={index}')
            DaLeDou.search(r'规则</a><br />(.*?)<br />')
        # 确定竞猜选择
        WuLin.get('cmd=wlmz&op=comfirm')
        self.msg.append(DaLeDou.search(r'战报</a><br />(.*?)<br /><br />'))

    def run(self) -> list:
        self.领取奖励()
        if self.week in ['1', '3', '5']:
            self.报名()
        elif self.week in ['2', '4', '6']:
            self.竞猜()

        return self.msg
