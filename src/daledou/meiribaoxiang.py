from src.daledou.daledou import DaLeDou


class MeiRi(DaLeDou):
    '''每日宝箱'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        # 每日宝箱
        MeiRi.get('cmd=dailychest')
        while type_list := DaLeDou.findall(r'type=(\d+)">打开'):
            # 打开
            MeiRi.get(f'cmd=dailychest&op=open&type={type_list[0]}')
            self.msg.append(DaLeDou.search(r'规则说明</a><br />(.*?)<br />'))

        return self.msg
