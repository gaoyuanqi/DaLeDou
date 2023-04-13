import time

from src.daledou.daledou import DaLeDou


class FenXiang(DaLeDou):
    '''分享'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 斗神塔(self):
        # 斗神塔
        FenXiang.get('cmd=towerfight&type=3')
        n = False
        if '结束挑战' in html:
            # 结束挑战
            FenXiang.get('cmd=towerfight&type=7')
            n = True
        for _ in range(11):
            # 开始挑战 or 挑战下一层
            FenXiang.get('cmd=towerfight&type=0')
            msg = DaLeDou.search(r'【斗神塔】<br />(.*?)。<br />')
            cooling = DaLeDou.findall(r'战斗剩余时间：(\d+)')
            if cooling:
                time.sleep(int(cooling[0]))
            if '结束挑战' in html:
                if n:
                    self.msg.append(msg)
                    return True
                # 结束挑战
                FenXiang.get('cmd=towerfight&type=7')
                n = True

    def 分享(self):
        for _ in range(9):
            # 一键分享
            FenXiang.get(f'cmd=sharegame&subtype=6')
            msg = DaLeDou.search(r'</p><p>(.*?)<br />.*?开通达人')
            if ('上限' in html) or (self.斗神塔()):
                self.msg.append(msg)
                # 自动挑战
                FenXiang.get('cmd=towerfight&type=11')
                # 结束挑战
                FenXiang.get('cmd=towerfight&type=7')
                break

    def 领取奖励(self):
        '''
        周四领取奖励
        '''
        # 领取奖励
        FenXiang.get('cmd=sharegame&subtype=3')
        sharenums = DaLeDou.findall(r'sharenums=(\d+)')
        for s in sharenums:
            # 领取
            FenXiang.get(f'cmd=sharegame&subtype=4&sharenums={s}')
            self.msg.append(DaLeDou.search(r'<p>【领取奖励】</p>(.*?)<p>'))

    def run(self) -> list:
        self.分享()
        if self.week == '4':
            self.领取奖励()

        return self.msg
