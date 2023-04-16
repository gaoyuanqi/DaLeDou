from src.daledou.daledou import DaLeDou


class LiLian(DaLeDou):
    '''历练'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 历练(self):
        for id in DaLeDou.read_yaml('历练'):
            for _ in range(3):
                LiLian.get(
                    f'cmd=mappush&subtype=3&mapid=6&npcid={id}&pageid=2')
                self.msg.append(DaLeDou.search(r'阅历值：\d+<br />(.*?)<br />'))
                if '您还没有打到该历练场景' in html:
                    self.msg.append(DaLeDou.search(r'介绍</a><br />(.*?)<br />'))
                    return
                elif '还不能挑战' in html:
                    return
                elif '活力不足' in html:
                    return

    def run(self) -> list:
        self.历练()

        return self.msg
