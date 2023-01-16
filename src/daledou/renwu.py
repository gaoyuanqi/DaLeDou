'''
任务
'''
import random
from os import getenv

from src.daledou.daledou import DaLeDou


class RenWu(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 查看好友资料(self):
        # 武林 》设置 》乐斗助手
        RenWu.get('cmd=view&type=6')
        if '开启查看好友信息和收徒' in html:
            #  开启查看好友信息和收徒
            RenWu.get('cmd=set&type=1')
        # 查看好友第2页
        RenWu.get(f'cmd=friendlist&page=2')
        B_UID: list = DaLeDou.findall(r'\d+：.*?B_UID=(\d+).*?级')
        for uin in B_UID:
            RenWu.get(f'cmd=totalinfo&B_UID={uin}')

    def 徽章进阶(self):
        '''
        勤劳徽章  1
        好友徽章  2
        等级徽章  3
        长者徽章  4
        时光徽章  5
        常胜徽章  6
        财富徽章  7
        达人徽章  8
        武林徽章  9
        分享徽章  10
        金秋徽章  11
        武器徽章  12
        金秋富豪  13
        佣兵徽章  14
        斗神徽章  15
        圣诞徽章  16
        春节徽章  17
        春节富豪  18
        技能徽章  19
        一掷千金  20
        劳动徽章  21
        周年富豪  22
        国旗徽章  23
        七周年徽章  24
        八周年徽章  25
        九周年徽章  26
        魅力徽章  27
        威望徽章  28
        十周年徽章  29
        十一周年徽章  30
        仙武徽章  31
        荣耀徽章  32
        十二周年徽章  33
        '''
        for id in range(1, 34):
            RenWu.get(
                f'cmd=achievement&op=upgradelevel&achievement_id={id}&times=1')
            if '进阶失败' in html:
                break
            elif '进阶成功' in html:
                break
            elif '物品不足' in html:
                break

    def 兵法研习(self):
        '''
        兵法      消耗     id       功能
        金兰之泽  孙子兵法  2544     增加生命
        雷霆一击  孙子兵法  2570     增加伤害
        残暴攻势  武穆遗书  21001    增加暴击几率
        不屈意志  武穆遗书  21032    降低受到暴击几率
        '''
        for id in [21001, 2570, 21032, 2544]:
            RenWu.get(f'cmd=brofight&subtype=12&op=practice&baseid={id}')
            if '研习成功' in html:
                break

    def 挑战陌生人(self):
        # 斗友
        RenWu.get('cmd=friendlist&type=1')
        B_UID: list = DaLeDou.findall(r'：.*?级.*?B_UID=(\d+).*?乐斗</a>')
        for uin in B_UID[:4]:
            # 乐斗
            RenWu.get(f'cmd=fight&B_UID={uin}&page=1&type=9')

    def 强化神装(self):
        '''
        神兵  0
        神铠  1
        神羽  2
        神兽  3
        神饰  4
        神履  5
        '''
        for id in range(6):
            # 进阶
            RenWu.get(f'cmd=outfit&op=1&magic_outfit_id={id}')
            if '进阶所需材料不足' in html:
                continue
            elif '已经满阶' in html:
                continue
            elif '很遗憾' in html:
                break
            else:
                # 升级成功
                break

    def 武器专精(self):
        '''
        武器专精
        投掷武器专精  0
        小型武器专精  1
        中型武器专精  2
        大型武器专精  3

        武器栏      投掷武器专精  小型武器专精  中型武器专精  大型武器专精
        专精·控制   1000         1003         1006         1009
        专精·吸血   1001         1004         1007         1010
        专精·凝神   1002         1005         1008         1011
        '''
        # 武器专精
        for tid in range(4):
            RenWu.get(f'cmd=weapon_specialize&op=2&type_id={tid}')
            if '升星所需材料不足' in html:
                continue
            elif '已经满阶' in html:
                continue
            elif '很遗憾' in html:
                break
            else:
                # 升级成功
                continue

        # 武器栏
        for sid in range(1000, 1012):
            RenWu.get(f'cmd=weapon_specialize&op=5&storage_id={sid}')
            if '升星所需材料不足' in html:
                continue
            elif '已经满阶' in html:
                continue
            elif '很遗憾' in html:
                break
            else:
                # 升级成功
                continue

    def 强化铭刻(self):
        '''
        技能      id  材料
        坚韧不拔  0   坚固的砥石
        嗜血如命  1   染血的羊皮
        坚定不移  2   稳固的磐石
        生存本能  3   沧桑的兽骨
        横扫千军  4   尖锐的铁器
        三魂之力  5   三彩水晶石
        四魂天功  6   四色补天石
        炙血战魂  7   破碎的铠甲
        百战之躯  8   粗壮的牛角
        攻无不克  9   锋利的狼牙
        魅影舞步  10
        '''
        idx = random.randint(0, 3)
        id = random.randint(0, 4)
        for id in range(11):
            RenWu.get(
                f'cmd=inscription&subtype=5&type_id={id}&weapon_idx={idx}&attr_id={id}')
            if '升级所需材料不足' in html:
                continue
            else:
                break

    def 增强经脉(self):
        # 20级开启
        # 经脉
        RenWu.get('cmd=intfmerid&sub=1')
        for _ in range(7):
            master_id: list = DaLeDou.findall(r'.*?master_id=(\d+)">传功</a>')
            for id in master_id:
                # 传功
                RenWu.get(f'cmd=intfmerid&sub=2&master_id={id}')
                if '请先' in html:
                    # 位置已满，请先将收入丹田！
                    # 丹田内力已经满了，请先合并！
                    # 一键合成
                    RenWu.get('cmd=intfmerid&sub=10&op=4')
                    # 一键拾取
                    RenWu.get('cmd=intfmerid&sub=5')

    def 助阵(self):
        '''
        助阵组合  id   dex
        毒光剑影  1    0（生命）
        正邪两立  2    0、1（投掷减免、投掷伤害）
        纵剑天下  3    0、1、2（小型减免、速度、小型伤害）
        致命一击  9    0、1、2（暴击伤害、暴击减免、生命）
        老谋深算  4    0、1、2、3（大型减免、大型伤害、速度、生命）
        智勇双全  5    0、1、2、3（中型减免、中型伤害、减暴、暴击）
        以柔克刚  6    0、1、2、3（技能减免、技能伤害、闪避、命中）
        雕心鹰爪  7    0、1、2、3（投掷和小型武器穿透、技能穿透、大型穿透、中型穿透）
        根骨奇特  8    0、1、2、3、4（空手减免、空手伤害、力量、敏捷、生命）
        '''
        tianshu = {
            1: [0],
            2: [0, 1],
            3: [0, 1, 2],
            9: [0, 1, 2],
            4: [0, 1, 2, 3],
            5: [0, 1, 2, 3],
            6: [0, 1, 2, 3],
            7: [0, 1, 2, 3],
            8: [0, 1, 2, 3, 4]
        }
        n = 0
        for id, dex_list in tianshu.items():
            for dex in dex_list:
                RenWu.get(
                    f'cmd=formation&type=4&formationid={id}&attrindex={dex}&times=1')
                if n == 2:
                    return
                elif '提升成功' in html:
                    n += 1
                    continue
                elif '经验值已经达到最大' in html:
                    continue
                elif '阅历不足' in html:
                    return
                elif '你还没有激活该属性' in html:
                    # 要么 没有激活该属性
                    # 要么 没有该属性
                    break

    def main(self) -> list:
        self.msg += DaLeDou.conversion('任务')

        # 日常任务
        RenWu.get('cmd=task&sub=1')
        daily_missions: str = html

        if '查看好友资料' in daily_missions:
            self.查看好友资料()

        if '徽章进阶' in daily_missions:
            self.徽章进阶()

        if '兵法研习' in daily_missions:
            self.兵法研习()

        if '挑战陌生人' in daily_missions:
            self.挑战陌生人()

        if '强化神装' in daily_missions:
            self.强化神装()

        if '武器专精' in daily_missions:
            self.武器专精()

        if '强化铭刻' in daily_missions:
            self.强化铭刻()

        if '增强经脉' in daily_missions:
            self.增强经脉()

        self.助阵()

        # 一键完成任务
        RenWu.get('cmd=task&sub=7')
        renwu: list[tuple] = DaLeDou.findall(r'id=\d+">(.*?)</a>.*?>(.*?)</a>')
        for k, v in renwu:
            self.msg.append(f'{k} {v}')

        return self.msg
