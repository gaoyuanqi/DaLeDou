'''
许愿
'''
from src.daledou.daledou import DaLeDou


class XuYuan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 许愿(self):
        '''
        领取许愿奖励 》许愿 》向xx上香许愿 》领取
        '''
        for sub in [5, 4, 1, 6]:
            XuYuan.get(f'cmd=wish&sub={sub}')
            if sub != 4:
                self.msg += DaLeDou.findall(r'【每日许愿】<br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('许愿')

        self.许愿()

        return self.msg
