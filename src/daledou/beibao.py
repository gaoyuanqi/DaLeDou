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
        if page:
            for p in range(1, int(page[0]) + 1):
                # 下页
                BeiBao.get(f'cmd=store&store_type=0&page={p}')
                data += DaLeDou.findall(r'宝箱</a>数量：(\d+).*?id=(\d+).*?使用')

            # 使用
            for k, v in data:
                for _ in range(int(k)):
                    BeiBao.get(f'cmd=use&id={v}&store_type=0')

        id_list = [
            3030,  # 神来拳套(赠)
            3176,  # 阅历羊皮卷
            3356,  # 贡献小笼包
            3381,  # 阅历卷宗
            3487,  # 巅峰之战二等勋章
            3488,  # 巅峰之战一等勋章
            3503,  # 贡献叉烧包
            3671,  # 资源补给箱
            5392,  # 3级星石礼盒
            6779,  # 惊喜锦囊
        ]

        for id in id_list:
            for _ in range(70):
                BeiBao.get(f'cmd=use&id={id}')
                if '您使用了' not in html:
                    break

    def run(self) -> list:
        self.乐斗助手()
        self.锦囊()
        self.属性()
        if self.week == '4':
            self.使用()

        return self.msg
