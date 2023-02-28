'''
帮派商会
'''
from src.daledou.daledou import DaLeDou


class BangPai(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 帮派宝库(self):
        # 帮派宝库
        BangPai.get('cmd=fac_corp&op=0')
        gift_id: list = DaLeDou.findall(r'gift_id=(\d+)&amp;type=(\d+)">点击领取')
        for id, t in gift_id:
            BangPai.get(f'cmd=fac_corp&op=3&gift_id={id}&type={t}')
            self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def 交易会所(self):
        # 交易会所
        BangPai.get('cmd=fac_corp&op=1')
        data: dict = DaLeDou.readyaml('帮派商会')
        jiaoyi: dict = data['交易会所']
        for jiaoyi_name, params in jiaoyi.items():
            if jiaoyi_name in html:
                BangPai.get(f'cmd=fac_corp&op=4&{params}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def 兑换商店(self):
        # 兑换商店
        BangPai.get('cmd=fac_corp&op=2')
        data: dict = DaLeDou.readyaml('帮派商会')
        duihuan: dict = data['兑换商店']
        for duihuan_name, type_id in duihuan.items():
            if duihuan_name in html:
                BangPai.get(f'cmd=fac_corp&op=5&type_id={type_id}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('帮派商会')

        self.帮派宝库()
        self.交易会所()
        self.兑换商店()

        return self.msg
