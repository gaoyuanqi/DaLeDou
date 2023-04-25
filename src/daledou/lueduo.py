from src.daledou.daledou import DaLeDou


class LueDuo(DaLeDou):
    '''掠夺'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 掠夺(self):
        '''周二掠夺一次、领奖一次'''
        # 掠夺首页
        LueDuo.get('cmd=forage_war')
        if '本轮轮空' in html:
            self.msg.append(DaLeDou.search(r'本届战况：(.*?)<br />'))
            return

        # 掠夺
        LueDuo.get('cmd=forage_war&subtype=3')
        if gra_id := DaLeDou.findall(r'gra_id=(\d+)">掠夺'):
            data = []
            for id in gra_id:
                LueDuo.get(f'cmd=forage_war&subtype=3&op=1&gra_id={id}')
                if zhanli := DaLeDou.findall(r'<br />1.*? (\d+)\.'):
                    data += [(int(zhanli[0]), id)]
            if data:
                _, id = min(data)
                LueDuo.get(f'cmd=forage_war&subtype=4&gra_id={id}')
                self.msg.append(DaLeDou.search(r'返回</a><br />(.*?)<br />'))

        # 领奖
        LueDuo.get('cmd=forage_war&subtype=5')
        self.msg.append(DaLeDou.search(r'返回</a><br />(.*?)<br />'))

    def 领取胜负奖励(self):
        '''周三领取胜负奖励'''
        LueDuo.get('cmd=forage_war&subtype=6')
        self.msg.append(DaLeDou.search(r'规则</a><br />(.*?)<br />'))

    def run(self) -> list:
        if self.week == '2':
            self.掠夺()
        elif self.week == '3':
            self.领取胜负奖励()

        return self.msg
