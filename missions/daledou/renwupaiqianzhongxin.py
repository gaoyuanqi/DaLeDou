'''
任务派遣中心
'''
from missions.daledou.daledou import DaLeDou


class RenWu(DaLeDou):

    def __init__(self):
        super().__init__()
        self.msg = []

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 领取奖励(self):
        # 任务派遣中心
        RenWu.get('cmd=missionassign&subtype=0')

        # 查看 》领取奖励
        text_list = DaLeDou.findall(r'0时0分.*?mission_id=(.*?)">查看')
        for id in text_list:
            RenWu.get(f'cmd=missionassign&subtype=5&mission_id={id}')
            self.msg += DaLeDou.findall(r'\[任务派遣中心\](.*?)<br />')

    def 派遣(self):
        # 任务派遣中心
        RenWu.get('cmd=missionassign&subtype=0')

        # 接受任务
        missions_dict = {
            '少女天团': '2',
            '闺蜜情深': '17',
            '男女搭配': '9',
            '鼓舞士气': '5',
            '仙人降临': '6',
            '雇佣军团': '11',
            '调整状态': '12',
            '防御工事': '10',
            '护送长老': '1',
            '坚持不懈': '4',
            '降妖除魔': '3',
            '深山隐士': '7',
            '抓捕小偷': '8',
            '小队巡逻': '13',
            '武艺切磋': '14',
            '哥俩好啊': '15',
            '协助村长': '16',
            '打扫房间': '18',
            '货物运送': '19',
            '消除虫害': '20',
            '帮助邻居': '21',
            '上山挑水': '22',
            '房屋维修': '23',
            '清理蟑螂': '24',
            '收割作物': '25',
            '炊烟袅袅': '26',
            '湖边垂钓': '27',
            '勤劳园丁': '29'
        }
        for _ in range(3):
            # 获取可接受任务id ['1', '2', '3']
            id_list = DaLeDou.findall(r'小时.*?mission_id=(.*?)">接受')
            for _, id in missions_dict.items():
                if id in id_list:
                    # 快速委派
                    RenWu.get(f'cmd=missionassign&subtype=7&mission_id={id}')
                    # 开始任务
                    RenWu.get(f'cmd=missionassign&subtype=8&mission_id={id}')
                    if '任务数已达上限' in html:
                        break
            # 任务派遣中心
            RenWu.get('cmd=missionassign&subtype=0')
            if '今日已领取了全部任务哦' in html:
                break
            elif html.count('查看') == 3:
                break
            elif '50斗豆' not in html:
                # 刷新任务
                RenWu.get('cmd=missionassign&subtype=3')

        self.msg += DaLeDou.findall(r'<br />(.*?)<a.*?查看')

    def main(self) -> list[str]:
        self.msg += DaLeDou.conversion('任务派遣中心')

        self.领取奖励()
        self.派遣()

        return self.msg
