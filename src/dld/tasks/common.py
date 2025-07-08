"""
本模块抽离了 one.py 和 two.py 两个模块的公共任务函数
"""

import random

from ..core.daledou import DaLeDou


def c_邪神秘宝(D: DaLeDou):
    """高级秘宝和极品秘宝免费一次或者抽奖一次"""
    for i in [0, 1]:
        # 免费一次 或 抽奖一次
        D.get(f"cmd=tenlottery&op=2&type={i}")
        D.log(D.find(r"】</p>(.*?)<br />")).append()


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
    """
    领取奖励：每天最多3次
    接受：每天最多3次；优先S、A级，如果S、A已尝试且没有免费刷新次数则选择B级
    """
    base_name = "任务派遣中心"
    # 任务派遣中心
    D.get("cmd=missionassign&subtype=0")
    for _id in D.findall(r'0时0分.*?mission_id=(.*?)">查看'):
        # 查看
        D.get(f"cmd=missionassign&subtype=1&mission_id={_id}")
        mission_name = f"{base_name}-{D.find(r'任务名称：(.*?)<')}"
        # 领取奖励
        D.get(f"cmd=missionassign&subtype=5&mission_id={_id}")
        D.log(D.find(r"\[任务派遣中心\](.*?)<br />"), mission_name).append()

    fail_ids = []
    is_maximums = False
    is_no_free_refresh = False
    for _ in range(5):
        # 任务派遣中心
        D.get("cmd=missionassign&subtype=0")
        S_ids = D.findall(r'-S&nbsp;所需时间.*?_id=(\d+)">接受')
        A_ids = D.findall(r'-A&nbsp;所需时间.*?_id=(\d+)">接受')
        B_ids = D.findall(r'-B&nbsp;所需时间.*?_id=(\d+)">接受')

        _ids = S_ids + A_ids

        if is_no_free_refresh:
            _ids = B_ids
            if set(_ids).issubset(fail_ids):
                break

        for _id in _ids:
            # 接受
            D.get(f"cmd=missionassign&subtype=2&mission_id={_id}")
            mission_name = f"{base_name}-{D.find(r'任务名称：(.*?)<')}"

            # 快速委派
            D.get(f"cmd=missionassign&subtype=7&mission_id={_id}")
            if "设置佣兵成功" not in D.html:
                D.log(D.find(r"】<br /><br />(.*?)<"), mission_name)
                fail_ids.append(_id)
                continue
            D.log(D.find(r"】</p>(.*?)<"), mission_name)

            # 开始任务
            D.get(f"cmd=missionassign&subtype=8&mission_id={_id}")
            if "当前可执行任务数已达上限" in D.html:
                D.log(D.find(r"】<br /><br />(.*?)<"), mission_name)
                is_maximums = True
                break
            D.log(D.find(r"】</p>(.*?)<"), mission_name)

            if D.html.count("查看") == 3 or "今天已领取了全部任务" in D.html:
                is_maximums = True
                break

        if is_maximums:
            break

        if is_no_free_refresh:
            continue

        # 任务派遣中心
        D.get("cmd=missionassign&subtype=0")
        if "本次消耗：0斗豆" in D.html:
            # 刷新任务
            D.get("cmd=missionassign&subtype=3")
            D.log("免费刷新成功", "任务派遣中心-刷新任务")
        else:
            D.log("没有免费刷新次数了", "任务派遣中心-刷新任务")
            is_no_free_refresh = True

    # 任务派遣中心
    D.get("cmd=missionassign&subtype=0")
    for info in D.findall(r"<br />(.*?)&nbsp;<a.*?查看"):
        D.log(info, "任务派遣中心-当前任务").append()


def c_侠士客栈(D: DaLeDou):
    """
    领取奖励：每天3次
    客栈奇遇：
        前来捣乱的xx：与TA理论
        黑市商人：物品交换，详见配置文件
    """
    # 侠士客栈
    D.get("cmd=warriorinn")
    for t, n in D.findall(r"type=(\d+)&amp;num=(\d+)"):
        # 领取奖励
        D.get(f"cmd=warriorinn&op=getlobbyreward&type={t}&num={n}")
        D.log(D.find(r"侠士客栈<br />(.*?)<br />")).append()

    for p in D.findall(r'pos=(\d+)">前来捣乱的'):
        # 与TA理论
        D.get(f"cmd=warriorinn&op=exceptadventure&pos={p}")
        D.log(D.find(r"侠士客栈<br />(.*?)<")).append()

    config: list[str] = D.config["侠士客栈"]
    if config is None:
        return
    for p in D.findall(r'pos=(\d+)">黑市商人'):
        # 与TA交换
        D.get(f"cmd=warriorinn&op=confirmadventure&pos={p}&type=0")
        for text in config:
            if text in D.html:
                D.log(D.find(r"物品交换<br /><br />(.*?)<br />")).append()
                # 确认
                D.get(f"cmd=warriorinn&op=exceptadventure&pos={p}")
                D.log(D.find(r"侠士客栈<br />(.*?)<br />")).append()


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
    exchange_count: int = config["exchange_count"]

    if _id is None:
        D.log("你没有配置深渊秘境副本").append()
        return

    for _ in range(exchange_count):
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


def c_龙凰论武(D: DaLeDou):
    """每月4~25号每天随机挑战，挑战次数详见配置文件"""
    # 龙凰之境
    D.get("cmd=dragonphoenix&op=lunwu")
    if "已报名" in D.html:
        D.log("系统已随机报名，次日才能挑战").append()
        return
    elif "论武榜" not in D.html:
        D.log("进入论武异常，无法挑战").append()
        return

    challenge_count: int = D.config["龙凰之境"]["龙凰论武"]["challenge_count"]
    for _ in range(challenge_count):
        data = D.findall(r"uin=(\d+).*?idx=(\d+)")
        uin, _idx = random.choice(data)
        # 挑战
        D.get(f"cmd=dragonphoenix&op=pk&zone=1&uin={uin}&idx={_idx}")
        D.log(D.find(r"/\d+</a><br /><br />(.*?)<")).append()
        if "挑战次数不足" in D.html:
            break
        elif "冷却中" in D.html:
            break


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
            # 客栈同福
            D.get("cmd=newAct&subtype=154")
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
