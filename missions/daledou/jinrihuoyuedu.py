'''
今日活跃度
'''
from missions.daledou.daledou import DaLeDou


class JinRi(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        # 今日活跃度
        JinRi.get('cmd=liveness')
        self.msg += DaLeDou.find_tuple(r'【(.*?)】.*?礼包</a><br />(.*?)<a')
        # 领取今日活跃度礼包
        for id in range(1, 5):
            JinRi.get(f'cmd=liveness_getgiftbag&giftbagid={id}&action=1')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<p>1.')
        # 领取帮派总活跃奖励
        JinRi.get('cmd=factionop&subtype=18')
        self.msg += DaLeDou.findall(r'<br />(.*?)</p><p>你的职位:')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('今日活跃度')

        self.领取奖励()

        return self.msg
