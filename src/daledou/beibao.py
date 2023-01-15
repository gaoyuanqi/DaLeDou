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
        # 指定物品使用一次
        data: dict = DaLeDou.readyaml('背包')
        shiyong: dict = data['使用']
        for id in shiyong:
            # 使用
            BeiBao.get(f'cmd=use&id={shiyong[id]}&store_type=0')

    def 提前(self):
        # 指定物品提前一次
        if self.week == '4':
            data: dict = DaLeDou.readyaml('背包')
            tiqian: dict = data['提前']
            for key in tiqian:
                # 提前
                BeiBao.get(f'cmd=topgoods&id={tiqian[key]}')

    def main(self) -> list:
        self.乐斗助手()
        self.锦囊()
        self.属性()
        self.使用()
        self.提前()

        return self.msg
