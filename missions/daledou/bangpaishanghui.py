'''
帮派商会
'''
from missions.daledou.daledou import DaLeDou
from missions.daledou.config import read_yaml


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
        text_list = DaLeDou.findall(r'gift_id=(\d+).*?点击领取</a>')
        for id in text_list:
            BangPai.get(f'cmd=fac_corp&op=3&gift_id={id}&type=0')
            self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def 交易会所(self):
        # 交易会所
        jiaoyi_dict = read_yaml('交易', '帮派商会.yaml')
        BangPai.get('cmd=fac_corp&op=1')
        for jiaoyi_name, params in jiaoyi_dict.items():
            if jiaoyi_name in html:
                BangPai.get(f'cmd=fac_corp&op=4&{params}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def 兑换商店(self):
        # 兑换商店
        BangPai.get('cmd=fac_corp&op=2')
        duihuan_dict = read_yaml('兑换', '帮派商会.yaml')
        for duihuan_name, type_id in duihuan_dict.items():
            if duihuan_name in html:
                BangPai.get(f'cmd=fac_corp&op=5&type_id={type_id}')
                self.msg += DaLeDou.findall(r'【帮派商会】</p>(.*?)<br />')

    def main(self) -> list:
        # 大乐斗首页
        BangPai.get('cmd=index')
        if '帮派商会' in html:
            self.msg += DaLeDou.conversion('帮派商会')
            self.帮派宝库()
            self.交易会所()
            self.兑换商店()
            return self.msg

        return []
