from src.daledou.daledou import DaLeDou


class BaoMing(DaLeDou):
    '''报名'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 武林大会(self):
        '''武林大会 每天报名'''
        BaoMing.get('cmd=fastSignWulin&ifFirstSign=1')
        self.msg.append(DaLeDou.search(r'升级。<br />(.*?) '))

    def 侠侣争霸(self):
        '''侠侣争霸 周二、五、日报名'''
        BaoMing.get('cmd=cfight&subtype=9')
        self.msg.append(DaLeDou.search(r'报名状态.*?<br />(.*?)<br /></br>'))

    def 笑傲群侠(self):
        '''笑傲群侠 周六、日报名'''
        BaoMing.get('cmd=knightfight&op=signup')
        self.msg.append(DaLeDou.search(r'级<br />(.*?)<br />'))

    def run(self) -> list:
        self.武林大会()
        if self.week in ['2', '5', '0']:
            self.侠侣争霸()
        if self.week in ['6', '0']:
            self.笑傲群侠()

        return self.msg
