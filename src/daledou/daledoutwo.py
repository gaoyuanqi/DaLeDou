from os import environ

from src.daledou.daledou import DaLeDou


class DaLeDouTwo(DaLeDou):
    '''大乐斗第二轮'''

    def __init__(self) -> None:
        super().__init__()
        self.modulepath = [
            ['邪神秘宝', True, 'xieshenmibao.XieShen'],
            ['每日宝箱', (self.date == '20'), 'meiribaoxiang.MeiRi'],
            ['问鼎天下', (self.week not in ['6', '0']),
             'wendingtianxia.WenDingTwo'],
            ['任务派遣中心', True, 'renwupaiqianzhongxin.RenWu'],
            ['侠士客栈', True, 'xiashikezhan.XiaShi'],
            ['深渊之潮', True, 'shenyuanzhichao.ShenYuan'],
            ['镶嵌', (self.week == '4'), 'xiangqian.XiangQian'],
            ['神匠坊', (self.week == '4'), 'shenjiangfang.ShenJiang'],
            ['专精', True, 'zhuanjing.ZhuanJing'],
            ['奥义', True, 'aoyi.AoYi'],
            ['兵法', (self.week in ['4', '6']), 'bingfa.BingFa'],
            ['活动', True, 'events.EventsTwo'],
            ['背包', True, 'beibao.BeiBao'],
            ['商店', True, 'shangdian.ShangDian'],
        ]

    def run(self):
        if mission := DaLeDou.is_dld():
            for name, bool, path in self.modulepath:
                if (name in mission) and bool:
                    if name not in ['背包', '活动']:
                        self.msg.append(f'\n【{name}】')
                    environ['DLD_MISSIONS'] = name
                    self.msg += DaLeDou.load_object(f'{self.path}{path}')
        # print(self.msg)
        return self.msg
