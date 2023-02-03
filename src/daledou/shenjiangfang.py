'''
神匠坊
'''
from src.daledou.daledou import DaLeDou


class ShenJiang(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 普通合成(self):
        data = []
        for p in range(1, 20):
            # 下一页
            ShenJiang.get(
                f'cmd=weapongod&sub=12&stone_type=0&quality=0&page={p}')
            data += DaLeDou.findall(r'拥有：(\d+)/(\d+).*?stone_id=(\d+)')
            if '下一页' not in html:
                break

        for remaining, amount, id in data:
            if int(remaining) >= int(amount):
                count: int = int(int(remaining) / int(amount))
                for _ in range(count):
                    # 普通合成
                    ShenJiang.get(f'cmd=weapongod&sub=13&stone_id={id}')
                    # self.msg += DaLeDou.findall(r'背包<br /></p>(.*?)!')

    def 符石分解(self):
        data_II = []
        data_all = []
        for p in range(1, 5):
            # 下一页
            ShenJiang.get(f'cmd=weapongod&sub=9&stone_type=0&page={p}')
            data_II += DaLeDou.findall(r'II \(数量:(\d+)\).*?stone_id=(\d+)')
            data_all += DaLeDou.findall(r'I \(数量:(\d+)\).*?stone_id=(\d+)')
            if '下一页' not in html:
                break

        data_I: set = set(data_all) - set(data_II)
        for num, id in data_I:
            # 分解
            ShenJiang.get(
                f'cmd=weapongod&sub=11&stone_id={id}&num={int(num)}&i_p_w=num%7C')
            # self.msg += DaLeDou.findall(r'背包</a><br /></p>(.*?)!')

    def 符石打造(self):
        # 符石
        ShenJiang.get('cmd=weapongod&sub=7')
        data: list = DaLeDou.findall(r'符石水晶：(\d+)')
        if data:
            amount: int = int(data[0])
            ten: int = int(amount / 60)
            one: int = int((amount - (ten * 60)) / 6)
            for _ in range(ten):
                # 打造十次
                ShenJiang.get('cmd=weapongod&sub=8&produce_type=1&times=10')
            for _ in range(one):
                # 打造一次
                ShenJiang.get('cmd=weapongod&sub=8&produce_type=1&times=1')

    def main(self) -> list:
        self.普通合成()
        self.符石分解()
        self.符石打造()

        return self.msg
