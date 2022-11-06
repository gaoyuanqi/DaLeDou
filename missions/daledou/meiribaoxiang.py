'''
每日宝箱
'''
from missions.daledou.daledou import DaLeDou


class MeiRi(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 打开(self):
        if self.date == '20':
            self.msg += DaLeDou.conversion('每日宝箱')
            # 每日宝箱
            MeiRi.get('cmd=dailychest')
            while text_list := DaLeDou.findall(r'type=(\d+)">打开'):
                # 打开
                MeiRi.get(f'cmd=dailychest&op=open&type={text_list[0]}')
                self.msg += DaLeDou.findall(r'规则说明</a><br />(.*?)<br />')

    def main(self) -> list[str]:
        self.打开()

        return self.msg
