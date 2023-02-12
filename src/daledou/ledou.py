'''
乐斗
'''
from src.daledou.daledou import DaLeDou


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
        for _ in range(4):
            # 使用 贡献药水
            LeDou.get('cmd=use&id=3038&store_type=1&page=1')

    def 好友大侠(self):
        # 好友首页 乐斗大侠
        LeDou.get('cmd=friendlist&page=1')
        B_UID: list = DaLeDou.findall(r'侠：.*?B_UID=(\d+)')
        for uin in B_UID:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={uin}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                break

    def 帮友大侠(self):
        # 帮友首页 乐斗大侠
        LeDou.get('cmd=viewmem')
        B_UID: list = DaLeDou.findall(r'侠：.*?B_UID=(\d+)')
        for uin in B_UID:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={uin}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                break

    def 侠侣(self):
        # 侠侣 全部乐斗
        LeDou.get('cmd=viewxialv')
        B_UID: list = DaLeDou.findall(r'：.*?B_UID=(\d+)')[1:]
        for uin in B_UID:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={uin}')
            if '体力值不足' in html:
                self.msg += ['体力值不足']
                break

    def 好友(self):
        '''
        乐斗20次 任务
        好友乐斗从末页开始向前乐斗至多20好友，不包括首页
        '''
        # 好友
        LeDou.get('cmd=friendlist')
        page: list = DaLeDou.findall(r'第\d+/(\d+)页')
        if not page:
            return
        elif page[0] == '1':
            return
        data = []
        p: int = int(page[0])
        for i in range(p, p - 2, -1):
            if i == 1:
                break
            LeDou.get(f'cmd=friendlist&page={i}')
            data += DaLeDou.findall(r'cmd=fight&amp;B_UID=(\d+)')[:-1]
        for uin in data:
            # 乐斗
            LeDou.get(f'cmd=fight&B_UID={uin}')

    def main(self) -> list:
        self.乐斗助手()
        self.贡献药水()
        self.好友大侠()
        self.帮友大侠()
        self.侠侣()
        self.好友()

        return self.msg
