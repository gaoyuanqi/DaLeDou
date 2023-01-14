'''
帮派商会
'''
from src.daledou.daledou import DaLeDou
from src.daledou._set import _readyaml, _getenvqq


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
        gift_id: list = DaLeDou.findall(r'gift_id=(\d+).*?点击领取</a>')
        for id in gift_id:
            BangPai.get(f'cmd=fac_corp&op=3&gift_id={id}&type=0')
            self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def 交易会所(self):
        # 交易会所
        data: dict = _readyaml('帮派商会', _getenvqq())
        jiaoyi: dict = data['交易']
        BangPai.get('cmd=fac_corp&op=1')
        for jiaoyi_name, params in jiaoyi.items():
            if jiaoyi_name in html:
                BangPai.get(f'cmd=fac_corp&op=4&{params}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def 兑换商店(self):
        # 兑换商店
        data: dict = _readyaml('帮派商会', _getenvqq())
        duihuan: dict = data['兑换']
        for duihuan_name, type_id in duihuan.items():
            if duihuan_name in html:
                BangPai.get(f'cmd=fac_corp&op=5&type_id={type_id}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def main(self) -> list:
        self.msg += DaLeDou.conversion('帮派商会')

        self.帮派宝库()
        self.交易会所()
        self.兑换商店()

        return self.msg
