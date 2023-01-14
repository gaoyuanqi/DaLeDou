'''
我要报名
'''
from src.daledou.daledou import DaLeDou


class BaoMing(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 武林大会(self):
        # 报名 武林大会
        BaoMing.get('cmd=fastSignWulin&ifFirstSign=1')
        # 武林
        BaoMing.get('cmd=showwulin')
        self.msg += DaLeDou.find_tuple(
            r'【冠军排行】</a><br />(.*?)<br />(.*?)<br />武林技能')

    def 侠侣争霸(self):
        '''
        周二、周五、周日报名
        '''
        if self.week in ['0', '2', '5']:
            # 报名 侠侣争霸
            BaoMing.get('cmd=cfight&subtype=9')
            self.msg += DaLeDou.find_tuple(
                r'【侠侣争霸】<br />(.*?)<a.*?</a><br />(.*?)。.*查看')

    def 笑傲群侠(self):
        '''
        周六、周日报名
        '''
        if self.week in ['6', '0']:
            # 报名 笑傲群侠
            BaoMing.get('cmd=knightfight&op=signup')
            self.msg += DaLeDou.findall(r'【冠军排行】</a><br />(.*?)<br />开赛')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('我要报名')

        self.武林大会()
        self.侠侣争霸()
        self.笑傲群侠()

        return self.msg
