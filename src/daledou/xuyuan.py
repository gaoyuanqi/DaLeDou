from src.daledou.daledou import DaLeDou


class XuYuan(DaLeDou):
    '''许愿'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        '''
        领取许愿奖励 》许愿 》向xx上香许愿 》领取
        '''
        for sub in [5, 4, 1, 6]:
            XuYuan.get(f'cmd=wish&sub={sub}')
            if sub != 4:
                self.msg.append(DaLeDou.search(r'【每日许愿】<br />(.*?)<br />'))

        return self.msg
