from src.daledou.daledou import DaLeDou


class HuanJing(DaLeDou):
    '''幻境'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        if data := DaLeDou.read_yaml('幻境'):
            HuanJing.get(f'cmd=misty&op=start&stage_id={data}')
            for _ in range(5):
                # 乐斗
                HuanJing.get(f'cmd=misty&op=fight')
                self.msg.append(DaLeDou.search(r'星数.*?<br />(.*?)<br />'))
            # 返回飘渺幻境
            HuanJing.get('cmd=misty&op=return')

        return self.msg
