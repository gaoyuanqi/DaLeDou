"""
本模块为大乐斗第二轮任务

默认每天 20:01 定时运行

手动运行第二轮任务：
python main.py --two
手动运行某个函数：
python main.py --two 邪神秘宝
手动运行多个函数：
python main.py --two 邪神秘宝 问鼎天下
"""

from daledou.utils import push, yield_dld_objects
from daledou.common import (
    c_邪神秘宝,
    c_问鼎天下,
    c_帮派商会,
    c_任务派遣中心,
    c_侠士客栈,
    c_帮派巡礼,
    c_深渊秘境,
    c_幸运金蛋,
    c_乐斗大笨钟,
)


def run_two(unknown_args: list = None):
    global D
    for D in yield_dld_objects():
        if unknown_args:
            func_name_list = unknown_args
            is_push = False
        else:
            func_name_list = D.func_map["two"]
            is_push = True

        for func_name in func_name_list:
            print("--" * 20)
            D.func_name = func_name
            D.msg_append(f"\n【{func_name}】")
            try:
                globals()[func_name]()
            except Exception as e:
                D.print_info(f"出现异常，本任务结束：{e}")
                D.msg_append("出现异常，本任务结束，详情查看日志")
        D.run_time()

        if is_push:
            print("--" * 20)
            # pushplus微信推送消息
            push(f"{D.qq} two", D.msg_join)
        else:
            print("--" * 20)
            print("--------------模拟微信信息--------------")
            print(D.msg_join)

        print("--" * 20)


# ============================================================


def 邪神秘宝():
    c_邪神秘宝(D)


def 问鼎天下():
    c_问鼎天下(D)


def 帮派商会():
    c_帮派商会(D)


def 任务派遣中心():
    c_任务派遣中心(D)


def 侠士客栈():
    c_侠士客栈(D)


def 深渊之潮():
    c_帮派巡礼(D)
    c_深渊秘境(D)


def 侠客岛():
    """
    侠客行至多领取3次任务奖励
    """
    # 侠客行
    D.get("cmd=knight_island&op=viewmissionindex")
    data = D.findall(r"getmissionreward&amp;pos=(\d+)")
    if not data:
        D.print_info("没有奖励领取")
        D.msg_append("没有奖励领取")
        return

    for p in data:
        # 领取
        D.get(f"cmd=knight_island&op=getmissionreward&pos={p}")
        D.msg_append(D.find(r"斗豆）<br />(.*?)<br />"))


def 背包():
    """
    背包物品使用
    """
    yaml: list = D.yaml["背包"]
    data = []

    # 背包
    D.get("cmd=store&store_type=0")
    page = int(D.find(r"第1/(\d+)"))
    for p in range(1, (page + 1)):
        D.get(f"cmd=store&store_type=0&page={p}")
        D.print_info(f"查找第 {p} 页")
        if "使用规则" in D.html:
            D.find(r"】</p><p>(.*?)<br />")
            continue
        _, _html = D.html.split("清理")
        D.html, _ = _html.split("商店")
        for _m in yaml:
            for number, _id in D.findall(rf"{_m}.*?</a>数量：(\d+).*?id=(\d+)"):
                data.append((_id, int(number)))

    for _id, number in set(data):
        if _id in ["3023", "3024", "3025"]:
            # xx洗刷刷，3103生命洗刷刷除外
            D.print_info("只能生命洗刷刷，其它洗刷刷不支持")
            D.msg_append("只能生命洗刷刷，其它洗刷刷不支持")
            continue
        for _ in range(number):
            # 使用
            D.get(f"cmd=use&id={_id}")
            if "使用规则" in D.html:
                # 该物品不能被使用
                # 该物品今天已经不能再使用了
                D.find(r"】</p><p>(.*?)<br />")
                break
            # 您使用了
            # 你打开
            D.msg_append(D.find())


def 镶嵌():
    """
    周四镶嵌魂珠升级（碎 -> 1 -> 2 -> 3 -> 4）
    """

    def get_p():
        for p_1 in range(4001, 4062, 10):
            # 魂珠1级
            yield p_1
        for p_2 in range(4002, 4063, 10):
            # 魂珠2级
            yield p_2
        for p_3 in range(4003, 4064, 10):
            # 魂珠3级
            yield p_3

    for _id in range(2000, 2007):
        for _ in range(50):
            # 魂珠碎片 -> 1
            D.get(f"cmd=upgradepearl&type=6&exchangetype={_id}")
            msg = D.find(r"魂珠升级</p><p>(.*?)</p>", f"镶嵌-{_id}")
            if "不能合成该物品" in D.html:
                # 抱歉，您的xx魂珠碎片不足，不能合成该物品！
                break
            D.msg_append(msg)

    n = 0
    for _id in get_p():
        for _ in range(50):
            # 1 -> 2 -> 3 -> 4
            D.get(f"cmd=upgradepearl&type=3&pearl_id={_id}")
            D.find(r"魂珠升级</p><p>(.*?)<", f"镶嵌-{_id}")
            if "您拥有的魂珠数量不够" in D.html:
                break
            n += 1
    if n:
        D.msg_append(f"升级成功*{n}")


def 普通合成():
    data = []
    # 神匠坊背包
    for p in range(1, 20):
        # 下一页
        D.get(f"cmd=weapongod&sub=12&stone_type=0&quality=0&page={p}")
        D.print_info(f"背包第 {p} 页")
        data += D.findall(r"拥有：(\d+)/(\d+).*?stone_id=(\d+)")
        if "下一页" not in D.html:
            break
    for possess, consume, _id in data:
        if int(possess) < int(consume):
            # 符石碎片不足
            continue
        count = int(possess) // int(consume)
        for _ in range(count):
            # 普通合成
            D.get(f"cmd=weapongod&sub=13&stone_id={_id}")
            D.msg_append(D.find(r"背包<br /></p>(.*?)!"))


def 符石分解():
    yaml: list[int] = D.yaml["神匠坊"]
    data = []

    # 符石分解
    for p in range(1, 10):
        # 下一页
        D.get(f"cmd=weapongod&sub=9&stone_type=0&page={p}")
        D.print_info(f"符石分解第 {p} 页")
        data += D.findall(r"数量:(\d+).*?stone_id=(\d+)")
        if "下一页" not in D.html:
            break
    for num, _id in data:
        if int(_id) not in yaml:
            continue
        # 分解
        D.get(f"cmd=weapongod&sub=11&stone_id={_id}&num={num}&i_p_w=num%7C")
        D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))


def 符石打造():
    # 符石
    D.get("cmd=weapongod&sub=7")
    number = int(D.find(r"符石水晶：(\d+)"))
    quotient, remainder = divmod(number, 60)
    for _ in range(quotient):
        # 打造十次
        D.get("cmd=weapongod&sub=8&produce_type=1&times=10")
        D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))
    for _ in range(remainder // 6):
        # 打造一次
        D.get("cmd=weapongod&sub=8&produce_type=1&times=1")
        D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))


def 神匠坊():
    """
    每月20号普通合成、符石分解（默认仅I类）、符石打造
    """
    普通合成()
    符石分解()
    符石打造()


def 每日宝箱():
    """
    每月20号打开所有的铜质、银质、金质宝箱
    """
    # 每日宝箱
    D.get("cmd=dailychest")
    while t := D.find(r'type=(\d+)">打开'):
        # 打开
        D.get(f"cmd=dailychest&op=open&type={t}")
        D.msg_append(D.find(r"说明</a><br />(.*?)<"))
        if "今日开宝箱次数已达上限" in D.html:
            break


def 商店():
    """
    每天查询商店积分
    """
    urls = [
        "cmd=longdreamexchange",  # 江湖长梦
        "cmd=wlmz&op=view_exchange",  # 武林盟主
        "cmd=arena&op=queryexchange",  # 竞技场
        "cmd=ascendheaven&op=viewshop",  # 飞升大作战
        "cmd=abysstide&op=viewabyssshop",  # 深渊之潮
        "cmd=exchange&subtype=10&costtype=1",  # 踢馆
        "cmd=exchange&subtype=10&costtype=2",  # 掠夺
        "cmd=exchange&subtype=10&costtype=3",  # 矿洞
        "cmd=exchange&subtype=10&costtype=4",  # 镖行天下
        "cmd=exchange&subtype=10&costtype=9",  # 幻境
        "cmd=exchange&subtype=10&costtype=10",  # 群雄逐鹿
        "cmd=exchange&subtype=10&costtype=11",  # 门派邀请赛
        "cmd=exchange&subtype=10&costtype=12",  # 帮派祭坛
        "cmd=exchange&subtype=10&costtype=13",  # 会武
        "cmd=exchange&subtype=10&costtype=14",  # 问鼎天下
    ]
    for url in urls:
        D.get(url)
        D.msg_append(D.find())


def 幸运金蛋():
    c_幸运金蛋(D)


def 新春拜年():
    """
    收取礼物
    """
    # 新春拜年
    D.get("cmd=newAct&subtype=147")
    if "op=3" not in D.html:
        D.print_info("没有礼物收取")
        D.msg_append("没有礼物收取")
        return

    # 收取礼物
    D.get("cmd=newAct&subtype=147&op=3")
    D.msg_append(D.find(r"祝您：.*?<br /><br />(.*?)<br />"))


def 乐斗大笨钟():
    c_乐斗大笨钟(D)
