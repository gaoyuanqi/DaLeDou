'''
镖行天下
'''
from src.daledou.daledou import DaLeDou


class BiaoXing(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 拦截(self):
        for _ in range(5):
            # 刷新
            BiaoXing.get('cmd=cargo&op=3')
            passerby_uin: list = DaLeDou.findall(r'passerby_uin=(\d+)">拦截')
            for uin in passerby_uin:
                # 拦截
                BiaoXing.get(f'cmd=cargo&op=14&passerby_uin={uin}')
                self.msg += DaLeDou.findall(r'商店</a><br />(.*?)<br />')
                if '您今天已达拦截次数上限了' in html:
                    return

    def 护送(self):
        '''
        护送完成 》领取奖励 》护送押镖 》刷新押镖 》启程护送
        '''
        for op in [3, 16, 7, 8, 6]:
            BiaoXing.get(f'cmd=cargo&op={op}')
            self.msg += DaLeDou.findall(r'商店</a><br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('镖行天下')

        self.拦截()
        self.护送()

        return self.msg
