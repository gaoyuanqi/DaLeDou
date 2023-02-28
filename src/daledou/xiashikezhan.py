'''
侠士客栈
'''
from src.daledou.daledou import DaLeDou


class XiaShi(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        # 侠士客栈
        XiaShi.get('cmd=warriorinn')

        type: list = DaLeDou.findall(r'type=(\d+).*?领取奖励</a>')
        if type:
            for n in range(1, 4):
                # 领取奖励
                XiaShi.get(
                    f'cmd=warriorinn&op=getlobbyreward&type={type[0]}&num={n}')
                self.msg += DaLeDou.findall(r'侠士客栈<br />(.*?)<br />')

    def 客栈奇遇(self):
        # 侠士客栈
        DaLeDou.get('cmd=warriorinn')

        # 黑市商人 -> 你去别人家问问吧 -> 确定
        for rejectadventure in ['黑市商人', '老乞丐']:
            if rejectadventure in html:
                for pos in range(2):
                    XiaShi.get(
                        f'cmd=warriorinn&op=rejectadventure&pos={pos}')
                    self.msg += DaLeDou.findall(r'侠士客栈<br />(.*?)，<a')

        # 前来捣乱的柒承 -> 与TA理论 -> 确定
        for exceptadventure in ['前来捣乱的柒承', '前来捣乱的洪七公', '前来捣乱的欧阳锋', '前来捣乱的燕青', '前来捣乱的圣诞老鹅', '前来捣乱的断亦']:
            if exceptadventure in html:
                for pos in range(2):
                    XiaShi.get(
                        f'cmd=warriorinn&op=exceptadventure&pos={pos}')
                    self.msg += DaLeDou.findall(r'侠士客栈<br />(.*?)，<a')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('侠士客栈')

        self.领取奖励()
        self.客栈奇遇()

        return self.msg
