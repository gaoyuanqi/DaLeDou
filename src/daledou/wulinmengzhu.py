from src.daledou.daledou import DaLeDou


class WuLin(DaLeDou):
    '''武林盟主'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领奖(self):
        '''周三、五、日领取排行奖励和竞猜奖励'''
        # 武林盟主
        WuLin.get('cmd=wlmz&op=view_index')
        if data := DaLeDou.findall(r'section_id=(\d+)&amp;round_id=(\d+)">'):
            for s, r in data:
                WuLin.get(f'cmd=wlmz&op=get_award&section_id={s}&round_id={r}')
                self.msg.append(DaLeDou.search(r'【武林盟主】<br /><br />(.*?)</p>'))
        else:
            self.msg.append('没有可领取的排行奖励和竞猜奖励')

    def 报名(self):
        '''周一、三、五报名比赛

        分站赛报名黄金、白银、青铜，默认报名黄金
        总决赛不需报名
        '''
        if yaml := DaLeDou.read_yaml('武林盟主'):
            WuLin.get(f'cmd=wlmz&op=signup&ground_id={yaml}')
            if '总决赛周不允许报名' in html:
                self.msg.append(DaLeDou.search(r'战报</a><br />(.*?)<br />'))
                return
            self.msg.append(DaLeDou.search(r'赛场】<br />(.*?)<br />'))

    def 竞猜(self):
        '''周二、四、六竞猜'''
        for index in range(8):
            # 选择
            WuLin.get(f'cmd=wlmz&op=guess_up&index={index}')
            DaLeDou.search(r'规则</a><br />(.*?)<br />')
        # 确定竞猜选择
        WuLin.get('cmd=wlmz&op=comfirm')
        self.msg.append(DaLeDou.search(r'战报</a><br />(.*?)<br />'))

    def run(self) -> list:
        if self.week in ['3', '5', '0']:
            self.领奖()
        if self.week in ['1', '3', '5']:
            self.报名()
        elif self.week in ['2', '4', '6']:
            self.竞猜()

        return self.msg
