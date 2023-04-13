from unicodedata import numeric

from src.daledou.daledou import DaLeDou


class ZhuanJing(DaLeDou):
    '''专精'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 祝福合集宝库(self):
        # 祝福合集宝库
        ZhuanJing.get('cmd=newAct&subtype=143')
        if '专精' in html:
            return True

    def biaoxingtianxia(self) -> int:
        '''
        镖行天下商店积分
        '''
        ZhuanJing.get('cmd=exchange&subtype=10&costtype=4')
        jifen = DaLeDou.findall(r'我的威望：(\d+)')
        return int(int(jifen[0]) / 40)

    def beibao(self):
        '''
        背包中的投掷、小型、中型、大型武器符文石数量
        '''
        list = ['3658', '3657', '3656', '3655']
        for index, id in enumerate(list):
            ZhuanJing.get(f'cmd=owngoods&id={id}')
            number = DaLeDou.findall(r'数量：(\d+)')
            if number:
                yield index, int(number[0])
            else:
                yield index, 0

    def find(self):
        for id, beibao_number in self.beibao():
            ZhuanJing.get(f'cmd=weapon_specialize&op=0&type_id={id}')
            jieduan: str = DaLeDou.findall(r'阶段：(.*?)阶')[0]
            # xingji: list = DaLeDou.findall(r'星级：(\d+)星')
            xiaohao: str = DaLeDou.findall(r'消耗：.*?(\d+)')[0]
            zhufuzhi: tuple = DaLeDou.findall(r'祝福值：(\d+)/(\d+)')[0]

            if numeric(jieduan) <= 4:
                # 四阶5星(含)前失败6点祝福值
                zhufuzhi_step = 6
            else:
                # 五阶5星(含)前失败5点祝福值
                zhufuzhi_step = 5

            yield xiaohao, zhufuzhi, zhufuzhi_step, beibao_number

    def calculate(self):
        jifen: int = self.biaoxingtianxia()
        for data in self.find():
            xiaohao, zhufuzhi, zhufuzhi_step, beibao_number = data
            # 计算材料数量
            now_jindu, max_jindu = zhufuzhi
            gap_jindu: int = int(max_jindu) - int(now_jindu)
            shengji_number: int = int(gap_jindu / zhufuzhi_step)
            calculate_number: int = (shengji_number + 1) * int(xiaohao)
            practical_number: int = jifen + beibao_number
            yield calculate_number, practical_number, zhufuzhi_step

    def run(self) -> list:
        if self.祝福合集宝库():
            self.msg.append('升级武器专精所需投掷、小型、中型、大型武器符文石数量')
            self.msg.append('需要  拥有（商店+背包）  失败祝福值')
            for data in self.calculate():
                calculate_number, practical_number, zhufuzhi_step = data
                self.msg.append(
                    f'{calculate_number}  {practical_number}  {zhufuzhi_step}')
        else:
            self.msg.append('祝福合集宝库没有该活动时不计算')

        return self.msg
