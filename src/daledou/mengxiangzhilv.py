'''
梦想之旅
'''
from src.daledou.daledou import DaLeDou


class MengXiang(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 梦想之旅(self) -> bool:
        '''
        查看下一个区域是否存在 已去过
        '''
        bmapid = {
            '空桑山': 2,
            '鹊山': 3,
            '鹿蜀': 4,
            '昆仑之丘': 1
        }
        # 梦想之旅
        MengXiang.get('cmd=dreamtrip')
        for k, v in bmapid.items():
            if k in html:
                # 下一个区域
                MengXiang.get(f'cmd=dreamtrip&sub=0&bmapid={v}')
                if '已去过' in html:
                    return True
                return False

    def 普通旅行(self):
        # 普通旅行
        MengXiang.get('cmd=dreamtrip&sub=2')
        self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
        text_list = DaLeDou.findall(r'梦幻机票：(\d+)<br />')
        c: int = html.count('未去过')
        self.msg += [f'梦幻机票：{text_list[0]}', f'未去过：{c}']

    def 梦幻旅行(self):
        if self.梦想之旅():
            # 梦想之旅
            MengXiang.get('cmd=dreamtrip')
            text_list = DaLeDou.findall(r'梦幻旅行</a><br />(.*?)<br /><br />')
            if not text_list:
                return

            # 查找未去过的目的地
            id_list = []
            list = text_list[0].split('<br />')
            for i, v in enumerate(list):
                if '未去过' in v:
                    id_list.append(i + 1)

            # 消耗梦幻机票去目的地
            for id in id_list:
                # 去这里
                MengXiang.get(f'cmd=dreamtrip&sub=2&smapid={id}')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')
                if '当前没有梦幻机票' in html:
                    break

    def 领取(self):
        # 梦想之旅
        MengXiang.get('cmd=dreamtrip')
        for _ in range(2):
            bmapid: list = DaLeDou.findall(r'sub=4&amp;bmapid=(\d+)')
            if bmapid:
                # 礼包     1 or 2 or 3 or 4
                # 超级礼包 0
                MengXiang.get(f'cmd=dreamtrip&sub=4&bmapid={bmapid[0]}')
                self.msg += DaLeDou.findall(r'规则</a><br />(.*?)<br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('梦想之旅')

        self.普通旅行()
        if self.week == '4':
            self.梦幻旅行()
            self.领取()

        return self.msg
