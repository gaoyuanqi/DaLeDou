'''
分享
'''
import time

from src.daledou.daledou import DaLeDou


class FenXiang(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 分享(self):
        # 一键分享
        FenXiang.get(f'cmd=sharegame&subtype=6')

        # 斗神塔
        FenXiang.get('cmd=towerfight&type=3')
        n = False
        if '结束挑战' in html:
            # 结束挑战
            FenXiang.get('cmd=towerfight&type=7')
            n = True
        for _ in range(8):
            for _ in range(11):
                # 开始挑战或挑战下一层
                FenXiang.get('cmd=towerfight&type=0')
                cooling: list = DaLeDou.findall(r'战斗剩余时间：(\d+)')
                time.sleep(int(cooling[0]))
                if '结束挑战' in html:
                    if n:
                        self.msg += DaLeDou.findall(r'【斗神塔】<br />(.*?)。<br />')
                        self.msg += DaLeDou.findall(r'</p><p>(.*?)<br />.*?开通')
                        return
                    # 结束挑战
                    FenXiang.get('cmd=towerfight&type=7')
                    n = True

            # 连续登录3天   分享
            FenXiang.get('cmd=sharegame&subtype=2&shareinfo=10')
            # 挑战斗神塔层数为10的倍数boss  分享
            FenXiang.get(f'cmd=sharegame&subtype=2&shareinfo=4')
            if '您今日的分享次数已达上限' in html:
                self.msg += DaLeDou.findall(r'</p><p>(.*?)<br />.*?开通达人')
                # 自动挑战
                FenXiang.get('cmd=towerfight&type=11')
                break

    def 领取奖励(self):
        '''
        周四领取奖励
        '''
        FenXiang.get('cmd=sharegame&subtype=3')
        sharenums: list = DaLeDou.findall(r'sharenums=(\d+)')
        for s in sharenums:
            # 领取
            FenXiang.get(f'cmd=sharegame&subtype=4&sharenums={s}')
            self.msg += DaLeDou.findall(r'<p>【领取奖励】</p>(.*?)<p>')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('分享')

        self.分享()
        if self.week == '4':
            self.领取奖励()

        return self.msg
