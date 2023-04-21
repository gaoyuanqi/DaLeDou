from src.daledou.daledou import DaLeDou


class DianFeng(DaLeDou):
    '''巅峰之战进行中'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 报名(self):
        '''周一报名、领奖'''
        for c in ['cmd=gvg&sub=4&group=0&check=1', 'cmd=gvg&sub=1']:
            DianFeng.get(c)
            self.msg.append(DaLeDou.search(r'【巅峰之战】</p>(.*?)。'))

    def 征战(self):
        '''周三、四、五、六、日征战'''
        # 巅峰之战
        DianFeng.get('cmd=gvg&sub=0')
        if '战线告急' in html:
            mode = r'支援！<br />(.*?)。'
        else:
            mode = r'】</p>(.*?)。'
        for _ in range(14):
            # 征战
            DianFeng.get('cmd=gvg&sub=5')
            if '您今天' in html:
                break
            elif '撒花祝贺' in html:
                self.msg.append(DaLeDou.search(r'】</p>(.*?)<br />'))
                break
            self.msg.append(DaLeDou.search(mode))

    def 夺宝奇兵(self):
        '''
        周二夺宝奇兵 选择16倍太空探宝
        '''
        for _ in range(300):
            # 投掷
            DianFeng.get('cmd=element&subtype=7')
            DaLeDou.search(r'遥控骰子</a><br /><br />(.*?)。')
            if '当前操作非法' in html:
                # 太空探宝
                DianFeng.get('cmd=element&subtype=15&gameType=3')
                DaLeDou.search(r'当前地图：(.*?)')
                if text_list := DaLeDou.findall(r'拥有:(\d+)战功'):
                    if int(text_list[0]) < 200000:
                        self.msg.append(f'战功：{text_list[0]} 大于200000才会探宝')
                        break

    def run(self) -> list:
        if self.week == '1':
            self.报名()
        elif self.week == '2':
            self.夺宝奇兵()
        elif self.week in ['3', '4', '5', '6', '0']:
            self.征战()

        return self.msg
