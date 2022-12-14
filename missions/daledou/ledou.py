'''
乐斗
'''
from missions.daledou.daledou import DaLeDou


class LeDou(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 乐斗助手(self):
        # 武林 》设置 》乐斗助手
        LeDou.get('cmd=view&type=6')
        if '开启自动使用体力药水' in html:
            #  开启自动使用体力药水
            LeDou.get('cmd=set&type=0')

    def 贡献药水(self):
        for _ in range(3):
            # 使用 贡献药水
            LeDou.get('cmd=use&id=3038&store_type=1&page=1')

    def 好友大侠(self):
        # 好友首页 乐斗大侠
        LeDou.get('cmd=friendlist&page=1')
        text_list = DaLeDou.findall(r'侠：.*?B_UID=(\d+)')
        for B_UID in text_list:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={B_UID}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                break

    def 帮友大侠(self):
        # 帮友首页 乐斗大侠
        LeDou.get('cmd=viewmem')
        text_list = DaLeDou.findall(r'侠：.*?B_UID=(\d+)')
        for B_UID in text_list:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={B_UID}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                break

    def 侠侣(self):
        # 侠侣 全部乐斗
        LeDou.get('cmd=viewxialv')
        text_list = DaLeDou.findall(r'：.*?B_UID=(\d+)')[1:]
        for B_UID in text_list:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={B_UID}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                break

    def 好友(self):
        '''
        乐斗20次 任务
        乐斗好友第2页
        '''
        LeDou.get(f'cmd=friendlist&page=2')
        text_list = DaLeDou.findall(r'cmd=fight&amp;B_UID=(\d+)')
        for B_UID in text_list:
            # 乐斗 包括心魔
            LeDou.get(f'cmd=fight&B_UID={B_UID}')

    def main(self) -> list:
        if DaLeDou.rank() >= 20:
            self.乐斗助手()
            self.贡献药水()
            self.好友大侠()
            self.帮友大侠()
            self.侠侣()
            self.好友()
            return self.msg
        
        return []
