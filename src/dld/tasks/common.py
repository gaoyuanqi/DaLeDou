"""
本模块抽离了 one.py 和 two.py 两个模块的公共任务函数
"""

from ..core.daledou import DaLeDou


def c_邪神秘宝(D: DaLeDou):
    """高级秘宝和极品秘宝免费一次或者抽奖一次"""
    for i in [0, 1]:
        # 免费一次 或 抽奖一次
        D.get(f"cmd=tenlottery&op=2&type={i}")
        D.log(D.find(r"】</p>(.*?)<br />")).append()


def c_问鼎天下(D: DaLeDou):
    # 问鼎天下
    D.get("cmd=tbattle")
    if "你占领的领地已经枯竭" in D.html:
        # 领取
        D.get("cmd=tbattle&op=drawreleasereward")
        D.log(D.find()).append()
    elif "放弃" in D.html:
        # 放弃
        D.get("cmd=tbattle&op=abandon")
        D.log(D.find()).append()

    # 1东海 2南荒 3西泽 4北寒
    D.get("cmd=tbattle&op=showregion&region=1")
    # 攻占 倒数第一个
    if _ids := D.findall(r"id=(\d+).*?攻占</a>"):
        D.get(f"cmd=tbattle&op=occupy&id={_ids[-1]}&region=1")
        D.log(D.find()).append()


def 帮派宝库(D: DaLeDou):
    # 帮派宝库
    D.get("cmd=fac_corp&op=0")
    data = D.findall(r'gift_id=(\d+)&amp;type=(\d+)">点击领取')
    if not data:
        D.log("帮派宝库没有礼包领取", "帮派商会-帮派宝库").append()
        return

    for _id, t in data:
        D.get(f"cmd=fac_corp&op=3&gift_id={_id}&type={t}")
        D.log(D.find(r"</p>(.*?)<br />"), "帮派商会-帮派宝库").append()
        if "入帮24小时才能领取商会礼包" in D.html:
            break


def 交易会所(D: DaLeDou):
    config: dict = D.config["帮派商会"]["交易会所"]
    if config is None:
        return

    # 交易会所
    D.get("cmd=fac_corp&op=1")
    if "已交易" in D.html:
        return

    data = []
    for mode in config:
        data += D.findall(rf"{mode}.*?type=(\d+)&amp;goods_id=(\d+)")
    for t, _id in data:
        # 兑换
        D.get(f"cmd=fac_corp&op=4&type={t}&goods_id={_id}")
        D.log(D.find(r"</p>(.*?)<br />"), f"帮派商会-交易-{_id}").append()


def 兑换商店(D: DaLeDou):
    config: dict = D.config["帮派商会"]["兑换商店"]
    if config is None:
        return

    # 兑换商店
    D.get("cmd=fac_corp&op=2")
    if "已兑换" in D.html:
        return

    data = []
    for mode in config:
        data += D.findall(rf"{mode}.*?type_id=(\d+)")
    for t in data:
        # 兑换
        D.get(f"cmd=fac_corp&op=5&type_id={t}")
        D.log(D.find(r"</p>(.*?)<br />"), f"帮派商会-兑换-{t}").append()


def c_帮派商会(D: DaLeDou):
    """
    帮派宝库：每天领取礼包
    交易会所：每天交易物品
    兑换商店：每天兑换物品
    """
    帮派宝库(D)
    交易会所(D)
    兑换商店(D)


def c_任务派遣中心(D: DaLeDou):
    """至多领取奖励、接受任务3次"""
    # 任务派遣中心
    D.get("cmd=missionassign&subtype=0")
    for _id in D.findall(r'mission_id=(.*?)">查看'):
        # 领取奖励
        D.get(f"cmd=missionassign&subtype=5&mission_id={_id}")
        D.log(D.find(r"\[任务派遣中心\](.*?)<br />")).append()

    # 接受任务
    missions_dict = {
        "少女天团": "2",
        "闺蜜情深": "17",
        "男女搭配": "9",
        "鼓舞士气": "5",
        "仙人降临": "6",
        "雇佣军团": "11",
        "调整状态": "12",
        "防御工事": "10",
        "护送长老": "1",
        "坚持不懈": "4",
        "降妖除魔": "3",
        "深山隐士": "7",
        "抓捕小偷": "8",
        "小队巡逻": "13",
        "武艺切磋": "14",
        "哥俩好啊": "15",
        "协助村长": "16",
        "打扫房间": "18",
        "货物运送": "19",
        "消除虫害": "20",
        "帮助邻居": "21",
        "上山挑水": "22",
        "房屋维修": "23",
        "清理蟑螂": "24",
        "收割作物": "25",
        "炊烟袅袅": "26",
        "湖边垂钓": "27",
        "勤劳园丁": "29",
    }
    # 任务派遣中心
    D.get("cmd=missionassign&subtype=0")
    for _ in range(3):
        mission_id = D.findall(r'mission_id=(\d+)">接受')
        for _, _id in missions_dict.items():
            if _id in mission_id:
                # 快速委派
                D.get(f"cmd=missionassign&subtype=7&mission_id={_id}")
                # 开始任务
                D.get(f"cmd=missionassign&subtype=8&mission_id={_id}")
                if "任务数已达上限" in D.html:
                    break
        # 任务派遣中心
        D.get("cmd=missionassign&subtype=0")
        if "今日已领取了全部任务哦" in D.html:
            break
        elif D.html.count("查看") == 3:
            break
        elif "50斗豆" not in D.html:
            # 刷新任务
            D.get("cmd=missionassign&subtype=3")

    # 任务派遣中心
    D.get("cmd=missionassign&subtype=0")
    for info in D.findall(r"<br />(.*?)&nbsp;<a.*?查看"):
        D.log(info).append()


def c_侠士客栈(D: DaLeDou):
    """领取奖励3次、客栈奇遇"""
    # 侠士客栈
    D.get("cmd=warriorinn")
    if t := D.find(r"type=(\d+).*?领取奖励</a>"):
        for n in range(1, 4):
            # 领取奖励
            D.get(f"cmd=warriorinn&op=getlobbyreward&type={t}&num={n}")
            D.log(D.find(r"侠士客栈<br />(.*?)<br />")).append()

    # 奇遇
    for p in D.findall(r"pos=(\d+)"):
        D.get(f"cmd=warriorinn&op=showAdventure&pos={p}")
        if "前来捣乱的" in D.html:
            # 前来捣乱的xx -> 与TA理论 -> 确认
            D.get(f"cmd=warriorinn&op=exceptadventure&pos={p}")
            if "战斗" in D.html:
                D.log(D.find(r"侠士客栈<br />(.*?) ，")).append()
                continue
            D.log(D.find(r"侠士客栈<br />(.*?)<br />")).append()
        else:
            # 黑市商人、老乞丐 -> 你去别人家问问吧、拯救世界的任务还是交给别人把 -> 确认
            D.get(f"cmd=warriorinn&op=rejectadventure&pos={p}")


def c_帮派巡礼(D: DaLeDou):
    """每天领取巡游赠礼"""
    # 领取巡游赠礼
    D.get("cmd=abysstide&op=getfactiongift")
    D.log(D.find()).append()


def c_深渊秘境(D: DaLeDou):
    """
    每天兑换副本，兑换次数详见配置文件
    每天通关副本，副本次数有多少就通关多少次，副本详见配置文件
    """
    config: dict = D.config["深渊之潮"]["深渊秘境"]
    _id: int = config["id"]
    exchange_number: int = config["exchange_number"]

    if _id is None:
        D.log("你没有配置深渊秘境副本").append()
        return

    for _ in range(exchange_number):
        # 兑换
        D.get("cmd=abysstide&op=addaccess")
        D.log(D.find()).append()
        if "无法继续兑换挑战次数" in D.html:
            break

    # 深渊秘境
    D.get("cmd=abysstide&op=viewallabyss")
    count = D.find(r"副本次数：(\d+)")
    for _ in range(int(count)):
        D.get(f"cmd=abysstide&op=enterabyss&id={_id}")
        if "开始挑战" not in D.html:
            # 暂无可用挑战次数
            # 该副本需要顺序通关解锁
            D.log(D.find()).append()
            break

        for _ in range(5):
            # 开始挑战
            D.get("cmd=abysstide&op=beginfight")
            D.log(D.find())
            if "憾负于" in D.html:
                break

        # 退出副本
        D.get("cmd=abysstide&op=endabyss")
        D.log(D.find()).append()


def c_客栈同福(D: DaLeDou):
    """
    献酒：每天当有匹配项时献酒，详见配置文件
    """
    config: list = D.config["客栈同福"]
    if config is None:
        D.log("你没有配置匹配").append()
        return

    # 客栈同福
    D.get("cmd=newAct&subtype=154")
    count: str = D.find(r"现有黄酒数量：(\d+)")
    if count == "0":
        D.log("黄酒数量不足，本次无操作").append()
        return

    is_libation = False
    for _ in range(int(count)):
        for pattern in config:
            if pattern not in D.html:
                continue
            is_libation = True
            # 献酒
            D.get("cmd=newAct&subtype=155")
            D.log(D.find(r"】<br /><p>(.*?)<br />")).append()
            if "黄酒不足" in D.html:
                return
        if not is_libation:
            D.log("没有找到匹配，本次无操作").append()
            break


def c_幸运金蛋(D: DaLeDou):
    """砸金蛋一次"""
    # 幸运金蛋
    D.get("cmd=newAct&subtype=110&op=0")
    if i := D.find(r"index=(\d+)"):
        # 砸金蛋
        D.get(f"cmd=newAct&subtype=110&op=1&index={i}")
        D.log(D.find(r"】<br /><br />(.*?)<br />")).append()
    else:
        D.log("没有砸蛋次数了").append()


def c_乐斗大笨钟(D: DaLeDou):
    """领取一次"""
    # 领取
    D.get("cmd=newAct&subtype=18")
    D.log(D.find(r"<br /><br /><br />(.*?)<br />")).append()
