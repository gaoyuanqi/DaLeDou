from src.daledou.daledou import DaLeDou


class JinRi(DaLeDou):
    '''今日活跃度'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        # 今日活跃度
        JinRi.get('cmd=liveness')
        self.msg.append(DaLeDou.search(r'【(.*?)】'))
        if 'factionop' in html:
            self.msg.append(DaLeDou.search(r'礼包</a><br />(.*?)<a'))
        else:
            self.msg.append(DaLeDou.search(r'礼包</a><br />(.*?)<br />'))
        # 领取今日活跃度礼包
        for id in range(1, 5):
            JinRi.get(f'cmd=liveness_getgiftbag&giftbagid={id}&action=1')
            self.msg.append(DaLeDou.search(r'】<br />(.*?)<p>1.'))
        # 领取帮派总活跃奖励
        JinRi.get('cmd=factionop&subtype=18')
        self.msg.append(DaLeDou.search(r'<br />(.*?)</p><p>你的职位:'))

    def run(self) -> list:
        self.领取奖励()

        return self.msg
