from src.daledou.daledou import DaLeDou


class JingJiChang(DaLeDou):
    '''竞技场'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 挑战(self):
        '''
        至多挑战10次（免费挑战和开始挑战）
        '''
        for _ in range(10):
            # 免费挑战 or 开始挑战
            JingJiChang.get('cmd=arena&op=challenge')
            self.msg.append(DaLeDou.search(r'更新提示</a><br />(.*?)。'))
            if '免费挑战次数已用完' in html:
                # 领取奖励
                JingJiChang.get('cmd=arena&op=drawdaily')
                self.msg.append(DaLeDou.search(r'更新提示</a><br />(.*?)<br />'))
                break

    def 兑换(self):
        '''商店兑换材料'''
        if yaml := DaLeDou.read_yaml('竞技场'):
            # 兑换10个
            JingJiChang.get(f'cmd=arena&op=exchange&id={yaml}&times=10')
            self.msg.append(DaLeDou.search(r'竞技场</a><br />(.*?)<br />'))

    def run(self) -> list:
        self.挑战()
        self.兑换()

        return self.msg
