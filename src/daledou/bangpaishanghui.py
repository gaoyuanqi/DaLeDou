from src.daledou.daledou import DaLeDou


class BangPai(DaLeDou):
    '''帮派商会'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 帮派宝库(self):
        # 帮派宝库
        BangPai.get('cmd=fac_corp&op=0')
        for id, t in DaLeDou.findall(r'gift_id=(\d+)&amp;type=(\d+)">点击领取'):
            BangPai.get(f'cmd=fac_corp&op=3&gift_id={id}&type={t}')
            self.msg.append(DaLeDou.search(r'【帮派商会】</p>(.*?)<br />'))

    def 交易会所(self):
        # 交易会所
        BangPai.get('cmd=fac_corp&op=1')
        data: dict = DaLeDou.read_yaml('帮派商会')
        jiaoyi: dict = data['交易会所']
        for jiaoyi_name, params in jiaoyi.items():
            if jiaoyi_name in html:
                BangPai.get(f'cmd=fac_corp&op=4&{params}')
                self.msg.append(DaLeDou.search(r'【帮派商会】</p>(.*?)<br />'))

    def 兑换商店(self):
        # 兑换商店
        BangPai.get('cmd=fac_corp&op=2')
        data: dict = DaLeDou.read_yaml('帮派商会')
        duihuan: dict = data['兑换商店']
        for duihuan_name, type_id in duihuan.items():
            if duihuan_name in html:
                BangPai.get(f'cmd=fac_corp&op=5&type_id={type_id}')
                self.msg.append(DaLeDou.search(r'【帮派商会】</p>(.*?)<br />'))

    def run(self) -> list:
        self.帮派宝库()
        self.交易会所()
        self.兑换商店()

        return self.msg
