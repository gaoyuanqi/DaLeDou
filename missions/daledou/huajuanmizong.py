'''
画卷迷踪
'''
from missions.daledou.daledou import DaLeDou


class HuaJuan(DaLeDou):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def 画卷迷踪(self):
        for _ in range(20):
            # 准备完成进入战斗
            HuaJuan.get('cmd=scroll_dungeon&op=fight&buff=0')
            self.msg += DaLeDou.findall(r'选择</a><br /><br />(.*?)<br />')
            if '没有挑战次数' in html:
                break
            elif '征战书不足' in html:
                break

    def main(self) -> list:
        # 大乐斗首页
        HuaJuan.get('cmd=index')
        if '画卷迷踪' in html:
            self.msg += DaLeDou.conversion('画卷迷踪')
            self.画卷迷踪()
            return self.msg

        return []
