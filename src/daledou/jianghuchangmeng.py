'''
江湖长梦
'''
from src.daledou.daledou import DaLeDou


class JiangHu(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 玄铁令(self):
        # 【江湖长梦】兑换 玄铁令*10
        if self.week == '4':
            for _ in range(7):
                # 兑换 玄铁令*1
                JiangHu.get(
                    'cmd=longdreamexchange&op=exchange&key_id=5&page=1')
                # 兑换成功
                self.msg += DaLeDou.findall(r'侠士碎片</a><br />(.*?)<br />')
                if '该物品兑换次数已达上限' in html:
                    self.msg += ['玄铁令兑换次数已达上限']
                    break
                elif '剩余积分或兑换材料不足' in html:
                    self.msg += ['商店剩余积分或兑换材料不足']
                    break

    def 柒承的忙碌日常(self):
        for _ in range(2):
            # 柒承的忙碌日常
            JiangHu.get('cmd=jianghudream&op=showCopyInfo&id=1')
            # 开启副本
            JiangHu.get('cmd=jianghudream&op=beginInstance&ins_id=1')
            if '开启副本所需追忆香炉不足' in html:
                self.msg += DaLeDou.findall(r'【江湖长梦】<br />(.*?)<br /><a')
                break
            # 进入下一天
            JiangHu.get('cmd=jianghudream&op=goNextDay')
            if '进入下一天异常' in html:
                # 开启副本
                JiangHu.get('cmd=jianghudream&op=beginInstance&ins_id=1')
            for _ in range(7):
                msg1: list = DaLeDou.findall(r'event_id=(\d+)">战斗\(等级1\)')
                msg2: list = DaLeDou.findall(r'event_id=(\d+)">奇遇\(等级1\)')
                msg3: list = DaLeDou.findall(r'event_id=(\d+)">商店\(等级1\)')
                if msg1:  # 战斗
                    JiangHu.get(
                        f'cmd=jianghudream&op=chooseEvent&event_id={msg1[0]}')
                    # FIGHT!
                    JiangHu.get('cmd=jianghudream&op=doPveFight')
                    if '战败' in html:
                        break
                elif msg2:  # 奇遇
                    params: str = f'cmd=jianghudream&op=chooseEvent&event_id={msg2[0]}'
                    JiangHu.get(params)
                    # 视而不见
                    params: str = 'cmd=jianghudream&op=chooseAdventure&adventure_id=2'
                    JiangHu.get(params)
                elif msg3:  # 商店
                    params: str = f'cmd=jianghudream&op=chooseEvent&event_id={msg3[0]}'
                    JiangHu.get(params)
                # 进入下一天
                JiangHu.get('cmd=jianghudream&op=goNextDay')

            # 结束回忆
            JiangHu.get('cmd=jianghudream&op=endInstance')
            self.msg += DaLeDou.findall(r'【江湖长梦】<br />(.*?)<br /><a')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('江湖长梦')

        self.玄铁令()
        self.柒承的忙碌日常()

        return self.msg
