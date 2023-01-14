'''
武林盟主
'''
from src.daledou.daledou import DaLeDou


class WuLin(DaLeDou):

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
            two_tuple_list = DaLeDou.findall(
                r'section_id=(\d+)&amp;round_id=(\d+)">')
            for s, r in two_tuple_list:
                WuLin.get(
                    f'cmd=wlmz&op=get_award&section_id={s}&round_id={r}')
                self.msg += DaLeDou.findall(r'【武林盟主】<br /><br />(.*?)</p>')
            # 武林盟主
            WuLin.get('cmd=wlmz&op=view_index')

    def 报名(self):
        '''
        黄金赛场  1
        白银赛场  2
        青铜赛场  3
        '''
        if self.week in ['1', '3', '5']:
            WuLin.get(f'cmd=wlmz&op=signup&ground_id=1')
            self.msg += DaLeDou.findall(r'赛场】<br />(.*?)<br />')

    def 竞猜(self):
        if self.week in ['2', '4', '6']:
            for index in range(8):
                # 选择
                WuLin.get(f'cmd=wlmz&op=guess_up&index={index}')
            # 确定竞猜选择
            WuLin.get('cmd=wlmz&op=comfirm')
            self.msg += DaLeDou.findall(r'战报</a><br />(.*?)<br /><br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('武林盟主')

        self.领取奖励()
        self.报名()
        self.竞猜()

        return self.msg
