'''
华山论剑
乐斗等级需 >= 40
'''
from src.daledou.daledou import DaLeDou
from src.daledou._set import _readyaml


class HuaShan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 战阵调整(self):
        '''
        选择出战侠士
        '''
        id_list = _readyaml('id', '华山论剑.yaml')
        # 战阵调整
        HuaShan.get('cmd=knightarena&op=viewteam')
        for id, p in zip(id_list, range(3)):
            # 第一、二、三战侠士
            HuaShan.get(f'cmd=knightarena&op=setknight&id={id}&pos={p}&type=1')
            if '您没有该侠士' in html:
                self.msg += [f'您没有该侠士：{id}']

    def 开始挑战(self):
        '''
        开始挑战 8 次
        '''
        for _ in range(8):
            # 开始挑战
            HuaShan.get('cmd=knightarena&op=challenge')
            self.msg += DaLeDou.findall(r'荣誉兑换</a><br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('华山论剑')

        self.战阵调整()
        self.开始挑战()

        return self.msg
