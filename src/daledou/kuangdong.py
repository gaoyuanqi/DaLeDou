'''
矿洞
'''
from src.daledou.daledou import DaLeDou


class KuangDong(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 矿洞(self):
        for _ in range(5):
            # 矿洞
            KuangDong.get('cmd=factionmine')
            if '领取奖励' in html:
                # 领取奖励
                KuangDong.get('cmd=factionmine&op=reward')
                self.msg += DaLeDou.findall(
                    r'【矿洞副本】<br /><br />(.*?)<br /><a.*?领取奖励')
            elif '开启副本' in html:
                # floor   1、2、3、4、5 对应 第一、二、三、四、五层
                # mode    1、2、3 对应 简单、普通、困难
                # 确认开启
                KuangDong.get(f'cmd=factionmine&op=start&floor=5&mode=1')
                self.msg += DaLeDou.findall(r'矿石商店</a><br />(.*?)<br />')
            elif DaLeDou.findall(r'剩余次数：(\d+)/3<br />')[0] != '0':
                # 挑战
                KuangDong.get('cmd=factionmine&op=fight')
                self.msg += DaLeDou.findall(r'矿石商店</a><br />(.*?)<br />')
            else:
                break

    def main(self) -> list:
        self.msg += DaLeDou.conversion('矿洞')

        self.矿洞()

        return self.msg
