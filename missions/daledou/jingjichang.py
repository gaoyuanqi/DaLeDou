'''
竞技场
'''
from missions.daledou.daledou import DaLeDou
from missions.daledou.config import read_yaml


class JingJiChang(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 挑战(self):
        '''
        每月26日结束
        '''
        if int(self.date) <= 25:
            self.msg += DaLeDou.conversion('竞技场')
            for _ in range(10):
                # 免费挑战 》开始挑战
                JingJiChang.get('cmd=arena&op=challenge')
                self.msg += DaLeDou.findall(r'更新提示</a><br />(.*?)。')
                if '免费挑战次数已用完' in html:
                    # 领取奖励
                    JingJiChang.get('cmd=arena&op=drawdaily')
                    self.msg += DaLeDou.findall(r'更新提示</a><br />(.*?)<br />')
                    break

    def 兑换(self):
        if int(self.date) <= 25:
            # 竞技点商店
            id = read_yaml('id', '竞技场.yaml')
            times = read_yaml('times', '竞技场.yaml')
            if id:
                # 兑换 or 兑换10个
                JingJiChang.get(f'cmd=arena&op=exchange&id={id}&times={times}')
                self.msg += DaLeDou.findall(r'竞技场</a><br />(.*?)<br />')

    def main(self) -> list:
        # 大乐斗首页
        JingJiChang.get('cmd=index')
        if '竞技场' in html:
            self.挑战()
            self.兑换()
            return self.msg

        return []
