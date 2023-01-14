'''
巅峰之战进行中
'''
from src.daledou.daledou import DaLeDou


class DianFeng(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 报名(self):
        '''
        周一报名
        '''
        if self.week == '1':
            self.msg += DaLeDou.conversion('巅峰之战进行中')
            # 随机加入 -> 确定
            DianFeng.get('cmd=gvg&sub=4&group=0&check=1')
            self.msg += DaLeDou.findall(r'【巅峰之战】</p>(.*?)<br /><p>')
            # 领奖
            DianFeng.get('cmd=gvg&sub=1')
            self.msg += DaLeDou.findall(r'【巅峰之战】</p>(.*?)<br /><p>')

    def 征战(self):
        '''
        周三、四、五、六、日征战
        '''
        if self.week in ['3', '4', '5', '6', '0']:
            self.msg += DaLeDou.conversion('巅峰之战进行中')
            for _ in range(14):
                # 征战
                DianFeng.get('cmd=gvg&sub=5')
                if '您今天' in html:
                    break
                elif '撒花祝贺' in html:
                    break
            self.msg += DaLeDou.findall(r'个人信息：<br />(.*?)</p>挑战书')

    def 夺宝奇兵(self):
        if self.date == '21':
            if self.week == '2':
                self.msg += DaLeDou.conversion('巅峰之战进行中')
            # 夺宝奇兵
            DianFeng.get('cmd=element&subtype=6')
            if '【选择场景】' in html:
                # 太空探宝
                DianFeng.get('cmd=element&subtype=15&gameType=3')
            while True:
                # 投掷
                DianFeng.get('cmd=element&subtype=7')
                if '【选择场景】' in html:
                    # 太空探宝
                    DianFeng.get('cmd=element&subtype=15&gameType=3')
                    text_list = DaLeDou.findall(r'<br />拥有:(.*?)战功<br />')
                    if int(text_list[0]) < 200000:
                        self.msg += [f'战功：{text_list[0]}', '只有大于200000才会探宝']
                        break

    def main(self) -> list:
        self.报名()
        self.征战()
        self.夺宝奇兵()

        return self.msg
