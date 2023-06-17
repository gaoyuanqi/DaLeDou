from src.daledou.daledou import DaLeDou


class BangPai(DaLeDou):
    '''帮派祭坛'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        # 帮派祭坛
        BangPai.get('cmd=altar')
        for _ in range(30):
            if '转转券不足' in html:
                break
            elif '转动轮盘' in html:
                BangPai.get('cmd=altar&op=spinwheel')
                self.msg.append(DaLeDou.search(r'兑换</a><br />(.*?)<br />'))
            elif '随机分配' in html:
                for op, id in DaLeDou.findall(r'op=(.*?)&amp;id=(\d+)">选择</a>'):
                    # 偷取|选择帮派
                    BangPai.get(f'cmd=altar&op={op}&id={id}')
                    if '选择路线' in html:
                        # 选择路线 向前、向左、向右
                        BangPai.get(f'cmd=altar&op=dosteal&id={id}')
                        if '该帮派已解散' in html:
                            continue
                    break
            elif '领取奖励' in html:
                BangPai.get('cmd=altar&op=drawreward')
                if '当前没有累积奖励可以领取' in html:
                    self.msg.append(DaLeDou.search(r'<br /><br />(.*?)</p>'))
                else:
                    self.msg.append(DaLeDou.search(r'兑换</a><br />(.*?)<br />'))

        return self.msg
