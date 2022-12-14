'''
帮派祭坛
'''
from missions.daledou.daledou import DaLeDou


class BangPai(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 帮派祭坛(self):
        # 帮派祭坛
        BangPai.get('cmd=altar')
        for _ in range(30):
            if '转转券不足' in html:
                break
            elif '转动轮盘' in html:
                # 转动轮盘
                BangPai.get('cmd=altar&op=spinwheel')
                self.msg += DaLeDou.findall(
                    r'积分兑换</a><br />(.*?)<br /><br />')
            elif '随机分配' in html:
                two_tuple_list = DaLeDou.findall(
                    r'op=(.*?)&amp;id=(\d+)">选择</a>')
                op, id = two_tuple_list[0]
                # 偷取|选择帮派
                BangPai.get(f'cmd=altar&op={op}&id={id}')
                if '选择路线' in html:
                    # 选择路线 向前、向左、向右
                    BangPai.get(f'cmd=altar&op=dosteal&id={id}')
                    if '该帮派已解散' in html:
                        # 偷取|选择帮派
                        _, id = two_tuple_list[1]
                        BangPai.get(f'cmd=altar&op=dosteal&id={id}')
            elif '领取奖励' in html:
                # 领取奖励
                BangPai.get('cmd=altar&op=drawreward')

    def main(self) -> list:
        if DaLeDou.rank() >= 40:
            # 40级开启
            self.msg += DaLeDou.conversion('帮派祭坛')
            self.帮派祭坛()
            return self.msg

        return []
