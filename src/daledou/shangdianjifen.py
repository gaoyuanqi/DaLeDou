'''
商店积分
'''
from src.daledou.daledou import DaLeDou


class ShangDian(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 商店积分(self):
        '''
        查询商店积分
        比如矿石商店、粮票商店、功勋商店等中的积分

        1 踢馆
        2 掠夺
        3 矿洞
        4 镖行天下
        9 幻境
        10 群雄逐鹿
        11 门派邀请赛
        12 帮派祭坛
        13 会武
        14 问鼎天下
        '''
        for type in [1, 2, 3, 4, 9, 10, 11, 12, 13, 14]:
            ShangDian.get(f'cmd=exchange&subtype=10&costtype={type}')
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

        # 江湖长梦
        # 武林盟主
        # 飞升大作战
        # 深渊之潮
        urls = [
            'cmd=longdreamexchange',
            'cmd=wlmz&op=view_exchange',
            'cmd=ascendheaven&op=viewshop',
            'cmd=abysstide&op=viewabyssshop'
        ]
        for url in urls:
            ShangDian.get(url)
            self.msg += DaLeDou.findall(r'】<br />(.*?)<br />')

        # 竞技场
        ShangDian.get('cmd=arena&op=queryexchange')
        self.msg += DaLeDou.findall(r'竞技场</a><br />(.*?)<br /><br />')

        # 帮派商会
        ShangDian.get('cmd=fac_corp&op=2')
        self.msg += DaLeDou.findall(r'剩余刷新时间.*?秒&nbsp;(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('商店积分')

        self.商店积分()

        return self.msg
