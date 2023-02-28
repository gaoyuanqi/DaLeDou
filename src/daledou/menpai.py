'''
门派
'''
from src.daledou.daledou import DaLeDou


class MenPai(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 万年寺(self):
        # 点燃 》点燃
        for op in ['fumigatefreeincense', 'fumigatepaidincense']:
            MenPai.get(f'cmd=sect&op={op}')
            self.msg += DaLeDou.findall(r'修行。<br />(.*?)<br />')

    def 八叶堂(self):
        # 进入木桩训练 》进入同门切磋
        for op in ['trainingwithnpc', 'trainingwithmember']:
            MenPai.get(f'cmd=sect&op={op}')
            self.msg += DaLeDou.findall(r'【八叶堂】<br />(.*?)<br />')

    def 五花堂(self):

        # 五花堂
        MenPai.get('cmd=sect_task')
        wuhuatang: str = html

        missions = {
            '进入华藏寺看一看': 'cmd=sect_art',
            '进入伏虎寺看一看': 'cmd=sect_trump',
            '进入金顶看一看': 'cmd=sect&op=showcouncil',
            '进入八叶堂看一看': 'cmd=sect&op=showtraining',
            '进入万年寺看一看': 'cmd=sect&op=showfumigate'
        }
        for name, url in missions.items():
            if name in wuhuatang:
                MenPai.get(url)

        if '进行一次武艺切磋' in wuhuatang:
            for rank in [1, 2, 3]:
                # 掌门 首座 堂主
                MenPai.get(
                    f'cmd=sect&op=trainingwithcouncil&rank={rank}&pos=1')

        if '查看一名' in wuhuatang:
            # 查看一名同门成员的资料 or 查看一名其他门派成员的资料
            for page in [2, 3]:
                # 好友第2、3页
                MenPai.get(f'cmd=friendlist&page={page}')
                B_UID: list = DaLeDou.findall(r'\d+：.*?B_UID=(\d+).*?级')
                for uin in B_UID:
                    # 查看好友
                    MenPai.get(f'cmd=totalinfo&B_UID={uin}')

        if '进行一次心法修炼' in wuhuatang:
            '''
            少林心法      峨眉心法    华山心法      丐帮心法    武当心法      明教心法
            101 法华经    104 斩情决  107 御剑术   110 醉拳    113 太极内力  116 圣火功
            102 金刚经    105 护心决  108 龟息术   111 烟雨行  114 绕指柔剑  117 五行阵
            103 达摩心经  106 观音咒  109 养心术   112 笑尘诀  115 金丹秘诀  118 日月凌天
            '''
            for id in range(101, 119):
                MenPai.get(f'cmd=sect_art&subtype=2&art_id={id}&times=1')
                if '修炼成功' in html:
                    self.msg += DaLeDou.findall(r'【心法修炼】<br />(.*?)<br />')
                    break
                elif '修炼失败' in html:
                    if '你的门派贡献不足无法修炼' in html:
                        break
                    elif ('你的心法已达顶级无需修炼' in html) and (id == 118):
                        self.msg += ['所有心法都已经顶级']

        # 五花堂
        MenPai.get('cmd=sect_task')
        task_id: list = DaLeDou.findall(r'task_id=(\d+)">完成')
        for id in task_id:
            # 完成
            MenPai.get(f'cmd=sect_task&subtype=2&task_id={id}')
            self.msg += DaLeDou.findall(r'【五花堂】<br />(.*?)<br /><br />')

    def run(self) -> list:
        self.msg += DaLeDou.conversion('门派')

        # 门派
        MenPai.get('cmd=sect')
        if '出师' in html:
            self.万年寺()
            self.八叶堂()
            self.五花堂()
            return self.msg

        self.msg += ['您还没有加入门派']
        return self.msg
