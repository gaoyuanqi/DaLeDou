from src.daledou.daledou import DaLeDou


class HuaJuan(DaLeDou):
    '''画卷迷踪'''

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def get(params: str):
        global html
        html = DaLeDou.get(params)

    def run(self) -> list:
        for _ in range(20):
            # 准备完成进入战斗
            HuaJuan.get('cmd=scroll_dungeon&op=fight&buff=0')
            self.msg.append(DaLeDou.search(r'选择</a><br /><br />(.*?)<br />'))
            if '没有挑战次数' in html:
                break
            elif '征战书不足' in html:
                break

        return self.msg
