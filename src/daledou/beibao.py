'''
背包
'''
from src.daledou.daledou import DaLeDou


class BeiBao(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 乐斗助手(self):
        # 武林 》设置 》乐斗助手
        BeiBao.get('cmd=view&type=6')
        if '开启背包里的提前按钮' in html:
            #  开启背包里的提前按钮
            BeiBao.get('cmd=set&type=12')

    def 锦囊(self):
        # 锦囊
        BeiBao.get('cmd=store&store_type=5&page=1')
        two_tuple_list: list = DaLeDou.findall(r'数量：(\d+).*?id=(\d+).*?使用')
        for number, id in two_tuple_list:
            if id in ['3023', '3024', '3025', '3103']:
                # xx洗刷刷
                continue
                # 提前
                # BeiBao.get(f'cmd=topgoods&id={id}&type=2&page=1')
            else:
                for _ in range(int(number)):
                    # 使用
                    BeiBao.get(f'cmd=use&id={id}&store_type=2&page=1')

    def 属性(self):
        # 属性
        BeiBao.get('cmd=store&store_type=2&page=1')
        two_tuple_list: list = DaLeDou.findall(r'数量：(\d+).*?id=(\d+).*?使用')
        for number, id in two_tuple_list:
            for _ in range(int(number)):
                # 使用
                BeiBao.get(f'cmd=use&id={id}&store_type=2&page=1')

    def 使用(self):
        data = []
        # 背包
        BeiBao.get('cmd=store')
        page: list = DaLeDou.findall(r'第1/(\d+)')
        for p in range(1, int(page[0])+1):
            # 下页
            BeiBao.get(f'cmd=store&store_type=0&page={p}')
            data += DaLeDou.findall(r'宝箱</a>数量：(\d+).*?id=(\d+).*?使用')

        # 使用
        for k, v in data:
            for _ in range(int(k)):
                BeiBao.get(f'cmd=use&id={v}&store_type=0')

    def run(self) -> list:
        self.乐斗助手()
        self.锦囊()
        self.属性()
        if self.week == '4':
            self.使用()

        return self.msg
