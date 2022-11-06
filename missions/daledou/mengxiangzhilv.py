'''
梦想之旅
'''
from missions.daledou.daledou import DaLeDou


class MengXiang(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 梦想之旅(self):
        # 普通旅行
        MengXiang.get('cmd=dreamtrip&sub=2')
        self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
        text_list = DaLeDou.findall(r'梦幻机票：(\d+)<br />')
        c = html.count('未去过')
        self.msg += [f'梦幻机票：{text_list[0]}', f'未去过：{c}']

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('梦想之旅')

        self.梦想之旅()

        return self.msg
