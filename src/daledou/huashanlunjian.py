'''
华山论剑
'''
from src.daledou.daledou import DaLeDou


class HuaShan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 战阵调整(self):
        '''
        选择/更改侠士
        '''
        # 战阵调整页面
        HuaShan.get('cmd=knightarena&op=viewsetknightlist&pos=0')
        knightid: list = DaLeDou.findall(r'knightid=(\d+)')

        # 出战侠士页面
        HuaShan.get('cmd=knightarena&op=viewteam')
        xuanze_pos: list = DaLeDou.findall(r'pos=(\d+)">选择侠士')
        genggai: list = DaLeDou.findall(
            r'耐久：(\d+)/.*?pos=(\d+)">更改侠士.*?id=(\d+)')

        genggai_pos: list = []
        for n, p, id in genggai:
            # 移除不可出战的侠士id
            knightid.remove(id)
            if n == '0':
                # 筛选耐久为 0 的侠士出战次序
                genggai_pos.append(p)

        # 选择/更改侠士
        for p in (xuanze_pos + genggai_pos):
            if not knightid:
                break
            id: str = knightid.pop()
            # 出战
            HuaShan.get(
                f'cmd=knightarena&op=setknight&id={id}&pos={p}&type=1')

    def 开始挑战(self):
        '''
        开始挑战 8 次
        战阵调整至多2次
        '''
        for _ in range(10):
            # 开始挑战
            HuaShan.get('cmd=knightarena&op=challenge')
            if '耐久不足' in html:
                self.战阵调整()
                continue
            self.msg += DaLeDou.findall(r'荣誉兑换</a><br />(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('华山论剑')

        self.战阵调整()
        self.开始挑战()

        return self.msg