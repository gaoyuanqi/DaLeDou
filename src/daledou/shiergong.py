from src.daledou.daledou import DaLeDou


class ShiErGong(DaLeDou):
    '''十二宫'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        '''请猴王扫荡'''
        if yaml := DaLeDou.read_yaml('十二宫'):
            # 请猴王扫荡
            ShiErGong.get(f'cmd=zodiacdungeon&op=autofight&scene_id={yaml}')
            if msg := DaLeDou.search(r'<br />(.*?)<br /><br /></p>'):
                # 要么 扫荡
                self.msg.append(msg.split('<br />')[-1])
            else:
                # 要么 挑战次数不足 or 当前场景进度不足以使用自动挑战功能！
                self.msg.append(DaLeDou.search(r'id="id"><p>(.*?)<br />'))

        return self.msg
