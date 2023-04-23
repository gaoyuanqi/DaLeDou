from src.daledou.daledou import DaLeDou


class ShenJiang(DaLeDou):
    '''神匠坊'''

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
                count = int(int(remaining) / int(amount))
                for _ in range(count):
                    # 普通合成
                    ShenJiang.get(f'cmd=weapongod&sub=13&stone_id={id}')
                    DaLeDou.search(r'背包<br /></p>(.*?)!')

    def 符石分解(self):
        if yaml := DaLeDou.read_yaml('神匠坊'):
            data = []
            for p in range(1, 10):
                # 下一页
                ShenJiang.get(f'cmd=weapongod&sub=9&stone_type=0&page={p}')
                data += DaLeDou.findall(r'数量:(\d+).*?stone_id=(\d+)')
                if '下一页' not in html:
                    break
            for num, id in data:
                if int(id) in yaml:
                    # 分解
                    ShenJiang.get(
                        f'cmd=weapongod&sub=11&stone_id={id}&num={num}&i_p_w=num%7C')
                    DaLeDou.search(r'背包</a><br /></p>(.*?)<')

    def 符石打造(self):
        # 符石
        ShenJiang.get('cmd=weapongod&sub=7')
        if data := DaLeDou.findall(r'符石水晶：(\d+)'):
            amount = int(data[0])
            ten = int(amount / 60)
            one = int((amount - (ten * 60)) / 6)
            for _ in range(ten):
                # 打造十次
                ShenJiang.get('cmd=weapongod&sub=8&produce_type=1&times=10')
                DaLeDou.search(r'背包</a><br /></p>(.*?)<')
            for _ in range(one):
                # 打造一次
                ShenJiang.get('cmd=weapongod&sub=8&produce_type=1&times=1')
                DaLeDou.search(r'背包</a><br /></p>(.*?)<')

    def run(self) -> list:
        self.普通合成()
        self.符石分解()
        self.符石打造()

        return self.msg
