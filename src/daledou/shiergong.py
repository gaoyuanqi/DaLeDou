'''
十二宫
'''
from src.daledou.daledou import DaLeDou


class ShiErGong(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 扫荡(self):
        '''
        扫荡 》请猴王扫荡
        '''
        data: dict = DaLeDou.readyaml('十二宫')
        id: int = data['id']
        # 请猴王扫荡
        ShiErGong.get(
            f'cmd=zodiacdungeon&op=autofight&scene_id={id}&pay_recover_times=0')
        if msg := DaLeDou.findall(r'<br />(.*?)<br /><br /></p>'):
            # 要么 扫荡
            self.msg += [msg[0].split('<br />')[-1]]
        else:
            # 要么 挑战次数不足 or 当前场景进度不足以使用自动挑战功能！
            self.msg += DaLeDou.findall(r'id="id"><p>(.*?)<br />')

        # 查看兑换奖励
        ShiErGong.get('cmd=zodiacdungeon&op=showexchange&type=2')
        self.msg += DaLeDou.findall(r'<p>兑换奖励<br />(.*?)<br /><br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('十二宫')

        self.扫荡()

        return self.msg
