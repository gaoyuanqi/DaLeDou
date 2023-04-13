from unicodedata import numeric

from src.daledou.daledou import DaLeDou


class AoYi(DaLeDou):
    '''奥义'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 祝福合集宝库(self):
        # 祝福合集宝库
        AoYi.get('cmd=newAct&subtype=143')
        if '奥义' in html:
            return True

    def bangpaijitan(self) -> int:
        '''
        帮派祭坛商店积分
        '''
        AoYi.get('cmd=exchange&subtype=10&costtype=12')
        jifen = DaLeDou.findall(r'我的祭祀积分：(\d+)')
        return int(int(jifen[0]) / 40)

    def calculate(self):
        jifen: int = self.bangpaijitan()
        # 奥义
        AoYi.get(f'cmd=skillEnhance&op=0')
        jieduan: str = DaLeDou.findall(r'阶段：(.*?)阶')[0]
        # xingji: list = DaLeDou.findall(r'星级：(\d+)星')
        xiaohao: tuple = DaLeDou.findall(r'消耗：.*?(\d+)（(\d+)）')[0]
        zhufuzhi: tuple = DaLeDou.findall(r'祝福值：(\d+)/(\d+)')[0]

        if numeric(jieduan) <= 5:
            # 五阶5星(含)前失败4点祝福值
            zhufuzhi_step = 4

        # 计算材料数量
        xiaohao, beibao_number = xiaohao
        now_jindu, max_jindu = zhufuzhi
        gap_jindu: int = int(max_jindu) - int(now_jindu)
        shengji_number: int = int(gap_jindu / zhufuzhi_step)
        calculate_number: int = (shengji_number + 1) * int(xiaohao)
        practical_number: int = jifen + int(beibao_number)
        return calculate_number, practical_number, zhufuzhi_step

    def run(self) -> list:
        if self.祝福合集宝库():
            self.msg.append('升级技能奥义所需奥秘元素数量')
            calculate_number, practical_number, zhufuzhi_step = self.calculate()
            self.msg.append(f'需要：{calculate_number}')
            self.msg.append(f'拥有（商店+背包）：{practical_number}')
            self.msg.append(f'五阶5星(含)前失败祝福值：{zhufuzhi_step}')
        else:
            self.msg.append('祝福合集宝库没有该活动时不计算')

        return self.msg
