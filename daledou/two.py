"""
本模块为大乐斗第二轮任务

默认每天 20:01 定时运行

手动运行第二轮任务：
python main.py two
手动运行某个函数：
python main.py two -- 邪神秘宝
手动运行多个函数：
python main.py two -- 邪神秘宝 问鼎天下
"""

import random
import re

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


def run_two(unknown_args: list):
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


def 镖行天下():
    """
    每天领取押镖奖励
    """
    # 领取奖励
    D.get("cmd=cargo&op=16")
    D.msg_append(D.find())


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

    # 领取任务奖励
    for p2 in data:
        # 领取
        D.get(f"cmd=knight_island&op=getmissionreward&pos={p2}")
        D.msg_append(D.find(r"斗豆）<br />(.*?)<br />"))


def get_backpack_item_id(page: int) -> list:
    """
    获取背包物品id
    """
    _yaml: list = D.yaml["背包"]
    data = []
    for p in range(1, int(page) + 1):
        D.print_info(f"查找第 {p} 页id")
        # 下页
        D.get(f"cmd=store&store_type=0&page={p}")
        if "使用规则" in D.html:
            D.find(r"】</p><p>(.*?)<br />")
            continue
        _, _html = D.html.split("清理")
        D.html, _ = _html.split("商店")
        for _m in _yaml:
            # 查找物品id
            data += D.findall(rf"{_m}.*?</a>数量：.*?id=(\d+)")

    return data


def get_backpack_item_id_and_number(item_id: list) -> set:
    """
    获取背包物品id及数量
    """
    id_number = []
    for _id in item_id:
        # 物品详情
        D.get(f"cmd=owngoods&id={_id}")
        if "很抱歉" in D.html:
            D.find(r"】</p><p>(.*?)<br />", f"背包-{_id}-不存在")
        else:
            number = D.find(r"数量：(\d+)", f"背包-{_id}-数量")
            id_number.append((str(_id), int(number)))

    return set(id_number)


def 使用(id_and_number: set):
    """
    背包使用
    """
    for _id, number in id_and_number:
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
                D.find(r"】</p><p>(.*?)<br />", f"背包-{_id}-使用")
                break
            # 您使用了
            # 你打开
            D.msg_append(D.find())


def 背包():
    """
    背包物品使用，详见yaml配置文件
    """
    # 背包
    D.get("cmd=store&store_type=0")
    page = D.find(r"第1/(\d+)")
    if page is None:
        D.print_info("背包未找到页码")
        D.msg_append("背包未找到页码")
        return

    id_list = get_backpack_item_id(page)
    id_and_number: set = get_backpack_item_id_and_number(id_list)
    使用(id_and_number)


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


def 镶嵌():
    """
    周四镶嵌魂珠升级（碎 -> 1 -> 2 -> 3 -> 4）
    """
    for e in range(2000, 2007):
        for _ in range(50):
            # 魂珠碎片 -> 1
            D.get(f"cmd=upgradepearl&type=6&exchangetype={e}")
            _msg = D.find(r"魂珠升级</p><p>(.*?)</p>")
            if "不能合成该物品" in D.html:
                # 抱歉，您的xx魂珠碎片不足，不能合成该物品！
                break
            D.msg_append(_msg)

    for _id in get_p():
        for _ in range(50):
            # 1 -> 2 -> 3 -> 4
            D.get(f"cmd=upgradepearl&type=3&pearl_id={_id}")
            _msg = D.find(r"魂珠升级</p><p>(.*?)<")
            if "您拥有的魂珠数量不够" in D.html:
                break
            D.msg_append(_msg)


def 普通合成():
    """
    神匠坊-普通合成
    """
    data = []
    # 神匠坊背包
    for p in range(1, 20):
        D.print_info(f"背包第 {p} 页")
        # 下一页
        D.get(f"cmd=weapongod&sub=12&stone_type=0&quality=0&page={p}")
        data += D.findall(r"拥有：(\d+)/(\d+).*?stone_id=(\d+)")
        if "下一页" not in D.html:
            break
    for possess, number, _id in data:
        if int(possess) < int(number):
            # 符石碎片不足
            continue
        count = int(int(possess) / int(number))
        for _ in range(count):
            # 普通合成
            D.get(f"cmd=weapongod&sub=13&stone_id={_id}")
            D.msg_append(D.find(r"背包<br /></p>(.*?)!"))


def 符石分解():
    """
    神匠坊-符石分解，详见yaml配置文件
    """
    _yaml: list[int] = D.yaml["神匠坊"]
    data = []

    # 符石分解
    for p in range(1, 10):
        D.print_info(f"符石分解第 {p} 页")
        # 下一页
        D.get(f"cmd=weapongod&sub=9&stone_type=0&page={p}")
        data += D.findall(r"数量:(\d+).*?stone_id=(\d+)")
        if "下一页" not in D.html:
            break
    for num, _id in data:
        if int(_id) not in _yaml:
            continue
        # 分解
        D.get(f"cmd=weapongod&sub=11&stone_id={_id}&num={num}&i_p_w=num%7C")
        D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))


def 符石打造():
    """
    神匠坊-符石打造
    """
    # 符石
    D.get("cmd=weapongod&sub=7")
    if _number := D.find(r"符石水晶：(\d+)"):
        quotient, remainder = divmod(int(_number), 60)
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
    周四普通合成、符石分解（默认仅I类）、符石打造
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
    每天查询商店积分，比如矿石商店、粮票商店、功勋商店等积分
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


def 猜单双():
    """
    随机单数、双数
    """
    # 猜单双
    D.get("cmd=oddeven")
    for _ in range(5):
        value = D.findall(r'value=(\d+)">.*?数')
        if not value:
            D.print_info("猜单双已经结束")
            D.msg_append("猜单双已经结束")
            break

        value = random.choice(value)
        # 单数1 双数2
        D.get(f"cmd=oddeven&value={value}")
        D.msg_append(D.find())


def 煮元宵():
    """
    成熟度>=96时赶紧出锅
    """
    # 煮元宵
    D.get("cmd=yuanxiao2014")
    for _ in range(4):
        # 开始烹饪
        D.get("cmd=yuanxiao2014&op=1")
        if "领取烹饪次数" in D.html:
            D.print_info("没有烹饪次数了")
            D.msg_append("没有烹饪次数了")
            break

        for _ in range(20):
            maturity = D.find(r"当前元宵成熟度：(\d+)")
            if int(maturity) < 96:
                # 继续加柴
                D.get("cmd=yuanxiao2014&op=2")
                continue
            # 赶紧出锅
            D.get("cmd=yuanxiao2014&op=3")
            D.msg_append(D.find(r"活动规则</a><br /><br />(.*?)。"))
            break


def 元宵节():
    """
    周四领取、领取月桂兔
    """
    # 领取
    D.get("cmd=newAct&subtype=101&op=1")
    D.msg_append(D.find(r"】</p>(.*?)<br />"))
    # 领取月桂兔
    D.get("cmd=newAct&subtype=101&op=2&index=0")
    D.msg_append(D.find(r"】</p>(.*?)<br />"))


def 神魔转盘():
    """
    幸运抽奖免费抽奖一次
    """
    # 神魔转盘
    D.get("cmd=newAct&subtype=88&op=0")
    if "免费抽奖一次" not in D.html:
        D.print_info("没有免费抽奖次数")
        D.msg_append("没有免费抽奖次数")
        return

    D.get("cmd=newAct&subtype=88&op=1")
    D.msg_append(D.find())


def 乐斗驿站():
    """
    免费领取淬火结晶*1
    """
    D.get("cmd=newAct&subtype=167&op=2")
    D.msg_append(D.find())


def 浩劫宝箱():
    """
    领取一次
    """
    D.get("cmd=newAct&subtype=152")
    D.msg_append(D.find(r"浩劫宝箱<br />(.*?)<br />"))


def 幸运转盘():
    """
    转动轮盘一次
    """
    D.get("cmd=newAct&subtype=57&op=roll")
    D.msg_append(D.find(r"0<br /><br />(.*?)<br />"))


def 冰雪企缘():
    """
    至多领取两次
    """
    # 冰雪企缘
    D.get("cmd=newAct&subtype=158&op=0")
    gift = D.findall(r"gift_type=(\d+)")
    if not gift:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")
        return

    for g in gift:
        # 领取
        D.get(f"cmd=newAct&subtype=158&op=2&gift_type={g}")
        D.msg_append(D.find())


def 甜蜜夫妻():
    """
    夫妻甜蜜好礼      至多领取3次
    单身鹅鼓励好礼    至多领取3次
    """
    # 甜蜜夫妻
    D.get("cmd=newAct&subtype=129")
    flag = D.findall(r"flag=(\d+)")
    if not flag:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")
        return

    for f in flag:
        # 领取
        D.get(f"cmd=newAct&subtype=129&op=1&flag={f}")
        D.msg_append(D.find(r"】</p>(.*?)<br />"))


def 乐斗菜单():
    """
    点单
    """
    # 乐斗菜单
    D.get("cmd=menuact")
    if gift := D.find(r"套餐.*?gift=(\d+).*?点单</a>"):
        # 点单
        D.get(f"cmd=menuact&sub=1&gift={gift}")
        D.msg_append(D.find(r"哦！<br /></p>(.*?)<br />"))
    else:
        D.print_info("没有可点单")
        D.msg_append("没有可点单")


def 客栈同福():
    """
    献酒三次
    """
    for _ in range(3):
        # 献酒
        D.get("cmd=newAct&subtype=155")
        D.msg_append(D.find(r"】<br /><p>(.*?)<br />"))
        if "黄酒不足" in D.html:
            break


def 周周礼包():
    """
    领取一次
    """
    # 周周礼包
    D.get("cmd=weekgiftbag&sub=0")
    if _id := D.find(r';id=(\d+)">领取'):
        # 领取
        D.get(f"cmd=weekgiftbag&sub=1&id={_id}")
        D.msg_append(D.find())
    else:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")


def 登录有礼():
    """
    领取登录奖励一次
    """
    # 登录有礼
    D.get("cmd=newAct&subtype=56")
    index = D.find(r"gift_index=(\d+)")
    if index is None:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")
        return

    # 领取
    D.get(f"cmd=newAct&subtype=56&op=draw&gift_type=1&gift_index={index}")
    D.msg_append(D.find())


def 活跃礼包():
    """
    领取两次
    """
    for p in ["1", "2"]:
        D.get(f"cmd=newAct&subtype=94&op={p}")
        D.msg_append(D.find(r"】.*?<br />(.*?)<br />"))


def 上香活动():
    """
    领取檀木香、龙涎香各两次
    """
    for _ in range(2):
        # 檀木香
        D.get("cmd=newAct&subtype=142&op=1&id=1")
        D.msg_append(D.find())
        # 龙涎香
        D.get("cmd=newAct&subtype=142&op=1&id=2")
        D.msg_append(D.find())


def 徽章战令():
    """
    领取每日礼包
    """
    # 每日礼包
    D.get("cmd=badge&op=1")
    D.msg_append(D.find())


def 好友赠卡():
    """
    生肖福卡-好友赠卡
    """
    # 好友赠卡
    D.get("cmd=newAct&subtype=174&op=4")
    for name, qq, card_id in D.findall(r"送您(.*?)\*.*?oppuin=(\d+).*?id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=174&op=6&oppuin={qq}&card_id={card_id}")
        D.find(name=f"生肖福卡-{name}")
        D.msg_append(f"好友赠卡：{name}")


def 分享福卡():
    """
    生肖福卡-分享福卡
    """
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    if qq := D.yaml["生肖福卡"]:
        pattern = "[子丑寅卯辰巳午未申酉戌亥][鼠牛虎兔龙蛇马羊猴鸡狗猪]"
        data = D.findall(rf"({pattern})\s+(\d+).*?id=(\d+)")
        name, max_number, _id = max(data, key=lambda x: int(x[1]))
        p = f"cmd=newAct&subtype=174&op=5&oppuin={qq}&card_id={_id}&confirm=1"
        if int(max_number) >= 2:
            # 分享福卡
            D.get(p)
            D.msg_append(D.find(r"~<br /><br />(.*?)<br />", f"生肖福卡-{name}福卡"))
        else:
            D.print_info("你的福卡数量不足2", "生肖福卡-取消分享")
            D.msg_append("你的福卡数量不足2")


def 领取福卡():
    """
    生肖福卡-领取
    """
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    for task_id in D.findall(r"task_id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=174&op=7&task_id={task_id}")
        D.msg_append(D.find(r"~<br /><br />(.*?)<br />", "生肖福卡-集卡"))


def 生肖福卡():
    """
    集卡：
        好友赠卡：领取好友赠卡
        分享福卡：向好友分享一次福卡（选择数量最多的，如果数量最大值为1则不分享）
        领取福卡：领取
    兑奖：
        周四合成周年福卡、分斗豆
    抽奖：
        周四抽奖：
            已合成周年福卡则抽奖
            已过合卡时间则继续抽奖
    """
    好友赠卡()
    分享福卡()
    领取福卡()

    if D.week != 4:
        return

    # 兑奖及抽奖
    # 合成周年福卡
    D.get("cmd=newAct&subtype=174&op=8")
    D.msg_append(D.find(r"。<br /><br />(.*?)<br />", "生肖福卡-兑奖"))
    # 分斗豆
    D.get("cmd=newAct&subtype=174&op=9")
    D.msg_append(D.find(r"。<br /><br />(.*?)<br />", "生肖福卡-兑奖"))

    # 合卡结束日期
    _month, _day = D.findall(r"合卡时间：.*?至(\d+)月(\d+)日")[0]

    # 抽奖
    D.get("cmd=newAct&subtype=174&op=2")
    for _id, data in D.findall(r"id=(\d+).*?<br />(.*?)<br />"):
        numbers = re.D.findall(r"\d+", data)
        min_number = min(numbers, key=lambda x: int(x))
        for _ in range(int(min_number)):
            # 春/夏/秋/冬宵抽奖
            D.get(f"cmd=newAct&subtype=174&op=10&id={_id}&confirm=1")
            if "您还未合成周年福卡" in D.html:
                if (D.month == int(_month)) and (D.day > int(_day)):
                    # 合卡时间已结束
                    # 继续抽奖
                    D.get(f"cmd=newAct&subtype=174&op=10&id={_id}")
                else:
                    D.print_info("合卡期间需先合成周年福卡才能抽奖", "生肖福卡-抽奖")
                    D.msg_append("合卡期间需先合成周年福卡才能抽奖")
                    return
            D.msg_append(D.find(r"幸运抽奖<br /><br />(.*?)<br />", "生肖福卡-抽奖"))


def 长安盛会():
    """
    盛会豪礼：点击领取  id  1
    签到宝箱：点击领取  id  2
    全民挑战：点击参与  id  3，4，5
    """
    s_id = D.yaml["长安盛会"]
    # 选择黄金卷轴类别
    D.get(f"cmd=newAct&subtype=118&op=2&select_id={s_id}")

    for _id in D.findall(r"op=1&amp;id=(\d+)"):
        if _id in ["1", "2"]:
            # 点击领取
            D.get(f"cmd=newAct&subtype=118&op=1&id={_id}")
            D.msg_append(D.find(name="长安盛会-点击领取"))
        else:
            turn_count = D.find(r"剩余转动次数：(\d+)", "长安盛会-转动次数")
            for _ in range(int(turn_count)):
                # 点击参与
                D.get(f"cmd=newAct&subtype=118&op=1&id={_id}")
                D.msg_append(D.find(name="长安盛会-点击参与"))


def 深渊秘宝():
    """
    三魂秘宝、七魄秘宝各免费抽奖一次
    """
    # 深渊秘宝
    D.get("cmd=newAct&subtype=175")
    t_list = D.findall(r'type=(\d+)&amp;times=1">免费抽奖')
    if not t_list:
        D.print_info("没有免费抽奖次数")
        D.msg_append("没有免费抽奖次数")
        return

    for t in t_list:
        D.get(f"cmd=newAct&subtype=175&op=1&type={t}&times=1")
        D.msg_append(D.find())


def 中秋礼盒():
    """
    领取
    """
    # 中秋礼盒
    D.get("cmd=midautumngiftbag&sub=0")
    ids = D.findall(r"amp;id=(\d+)")
    if not ids:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")
        return

    for _id in ids:
        # 领取
        D.get(f"cmd=midautumngiftbag&sub=1&id={_id}")
        D.msg_append(D.find())
        if "已领取完该系列任务所有奖励" in D.html:
            continue


def 双节签到():
    """
    每天领取签到奖励
    活动截止日的前一天领取奖励金
    """
    # 领取签到奖励
    D.get("cmd=newAct&subtype=144&op=1")
    D.msg_append(D.find())

    month, day = D.findall(r"至(\d+)月(\d+)日")[0]
    if (D.month == int(month)) and (D.day == (int(day) - 1)):
        # 奖励金
        D.get("cmd=newAct&subtype=144&op=3")
        D.msg_append(D.find())


def 乐斗游记():
    """
    每天领取积分
    每周四一键领取、兑换十次、兑换一次
    """
    # 乐斗游记
    D.get("cmd=newAct&subtype=176")

    # 今日游记任务
    for _id in D.findall(r"task_id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=176&op=1&task_id={_id}")
        D.msg_append(D.find(r"积分。<br /><br />(.*?)<br />"))

    if D.week != 4:
        return

    # 一键领取
    D.get("cmd=newAct&subtype=176&op=5")
    D.msg_append(D.find(r"积分。<br /><br />(.*?)<br />"))
    D.msg_append(D.find(r"十次</a><br />(.*?)<br />乐斗"))

    # 兑换
    if num := D.find(r"溢出积分：(\d+)"):
        quotient, remainder = divmod(int(num), 10)
        for _ in range(quotient):
            # 兑换十次
            D.get("cmd=newAct&subtype=176&op=2&num=10")
            D.msg_append(D.find(r"积分。<br /><br />(.*?)<br />"))
        for _ in range(remainder):
            # 兑换一次
            D.get("cmd=newAct&subtype=176&op=2&num=1")
            D.msg_append(D.find(r"积分。<br /><br />(.*?)<br />"))


def 斗境探秘():
    """
    领取每日探秘奖励、累计探秘奖励
    """
    # 斗境探秘
    D.get("cmd=newAct&subtype=177")
    # 领取每日探秘奖励
    for _id in D.findall(r"id=(\d+)&amp;type=2"):
        # 领取
        D.get(f"cmd=newAct&subtype=177&op=2&id={_id}&type=2")
        D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))

    # 领取累计探秘奖励
    for _id in D.findall(r"id=(\d+)&amp;type=1"):
        # 领取
        D.get(f"cmd=newAct&subtype=177&op=2&id={_id}&type=1")
        D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))


def 幸运金蛋():
    c_幸运金蛋(D)


def 春联大赛():
    """
    选择、领取斗币各三次
    """
    # 开始答题
    D.get("cmd=newAct&subtype=146&op=1")
    if "您的活跃度不足" in D.html:
        D.print_info("您的活跃度不足50")
        D.msg_append("您的活跃度不足50")
        return
    elif "今日答题已结束" in D.html:
        D.print_info("今日答题已结束")
        D.msg_append("今日答题已结束")
        return

    _data = {
        "虎年腾大步": "兔岁展宏图",
        "虎辟长安道": "兔开大吉春",
        "虎跃前程去": "兔携好运来",
        "虎去雄风在": "兔来喜气浓",
        "虎带祥云去": "兔铺锦绣来",
        "虎蹄留胜迹": "兔角搏青云",
        "虎留英雄气": "兔会世纪风",
        "金虎辞旧岁": "银兔贺新春",
        "虎威惊盛世": "兔翰绘新春",
        "虎驰金世界": "兔唤玉乾坤",
        "虎声传捷报": "兔影抖春晖",
        "虎嘶飞雪里": "兔舞画图中",
        "兔归皓月亮": "花绽春光妍",
        "兔俊千山秀": "春暖万水清",
        "兔毫抒壮志": "燕梭织春光",
        "玉兔迎春至": "黄莺报喜来",
        "玉兔迎春到": "红梅祝福来",
        "玉兔蟾宫笑": "红梅五岭香",
        "卯时春入户": "兔岁喜盈门",
        "卯门生紫气": "兔岁报拜年",
        "卯来四季美": "兔献百家福",
        "红梅迎春笑": "玉兔出月欢",
        "红梅赠虎岁": "彩烛耀兔年",
        "红梅迎雪放": "玉兔踏春来",
        "丁年歌盛世": "卯兔耀中华",
        "寅年春锦绣": "卯序业辉煌",
        "燕舞春光丽": "兔奔曙光新",
        "笙歌辞旧岁": "兔酒庆新春",
        "瑞雪兆丰年": "迎得玉兔归",
        "雪消狮子瘦": "月满兔儿肥",
    }
    for _ in range(3):
        for s in D.findall(r"上联：(.*?) 下联："):
            if x := _data.D.get(s):
                xialian = D.find(rf"{x}<a.*?index=(\d+)")
            else:
                # 上联在字库中不存在，将随机选择
                xialian = [random.choice(range(3))]

            # 选择
            # index 0 1 2
            D.get(f"cmd=newAct&subtype=146&op=3&index={xialian[0]}")
            D.msg_append(D.find(r"剩余\d+题<br />(.*?)<br />"))
            # 确定选择
            D.get("cmd=newAct&subtype=146&op=2")
            D.msg_append(D.find())

    for _id in range(1, 4):
        # 领取
        D.get(f"cmd=newAct&subtype=146&op=4&id={_id}")
        D.msg_append(D.find())


def 新春拜年():
    """
    收取礼物
    """
    # 新春拜年
    D.get("cmd=newAct&subtype=147")
    if "op=3" in D.html:
        # 收取礼物
        D.get("cmd=newAct&subtype=147&op=3")
        D.msg_append(D.find(r"祝您：.*?<br /><br />(.*?)<br />"))


def 喜从天降():
    """
    每天至多点燃烟花10次，活动时间20.00-22.00
    """
    for _ in range(10):
        D.get("cmd=newAct&subtype=137&op=1")
        D.msg_append(D.find())
        if "燃放烟花次数不足" in D.html:
            break


def 五一礼包():
    """
    周四领取三次劳动节礼包
    """
    for _id in range(3):
        D.get(f"cmd=newAct&subtype=113&op=1&id={_id}")
        D.msg_append(D.find(r"】<br /><br />(.*?)<"))


def 端午有礼():
    """
    周四兑换礼包：2次礼包4、1次礼包3
    活动期间最多可以得到 4x7=28 个粽子

    index
    3       礼包4：消耗10粽子得到 淬火结晶*5+真黄金卷轴*5+徽章符文石*5+修为丹*5+境界丹*5+元婴飞仙果*5
    2       礼包3：消耗8粽子得到 2级日曜石*1+2级玛瑙石*1+2级迅捷石*1+2级月光石*1+2级紫黑玉*1
    1       礼包2：消耗6粽子得到 阅历羊皮卷*5+无字天书*5+河图洛书*5+还童天书*1
    0       礼包1：消耗4粽子得到 中体力*2+挑战书*2+斗神符*2
    """
    for _ in range(2):
        # 礼包4
        D.get("cmd=newAct&subtype=121&op=1&index=3")
        D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))
        if "您的端午香粽不足" in D.html:
            break

    # 礼包3
    D.get("cmd=newAct&subtype=121&op=1&index=2")
    D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))


def 圣诞有礼():
    """
    周四领取点亮奖励和连线奖励
    """
    # 圣诞有礼
    D.get("cmd=newAct&subtype=145")
    for _id in D.findall(r"task_id=(\d+)"):
        # 任务描述：领取奖励
        D.get(f"cmd=newAct&subtype=145&op=1&task_id={_id}")
        D.msg_append(D.find())

    # 连线奖励
    for i in D.findall(r"index=(\d+)"):
        D.get(f"cmd=newAct&subtype=145&op=2&index={i}")
        D.msg_append(D.find())


def 新春礼包():
    """
    周四领取礼包
    """
    for _id in [280, 281, 282]:
        # 领取
        D.get(f"cmd=xinChunGift&subtype=2&giftid={_id}")
        D.msg_append(D.find())


def 登录商店():
    """
    周四兑换材料
    """
    t: int = D.yaml["登录商店"]
    for _ in range(5):
        # 兑换5次
        D.get(f"cmd=newAct&op=exchange&subtype=52&type={t}&times=5")
        D.msg_append(D.find(r"<br /><br />(.*?)<br /><br />"))
    for _ in range(3):
        # 兑换1次
        D.get(f"cmd=newAct&op=exchange&subtype=52&type={t}&times=1")
        D.msg_append(D.find(r"<br /><br />(.*?)<br /><br />"))


def 盛世巡礼():
    """
    周四收下礼物
    """
    for s in range(1, 8):
        # 点击进入
        D.get(f"cmd=newAct&subtype=150&op=2&sceneId={s}")
        if "他已经给过你礼物了" in D.html:
            D.print_info("礼物已领取", f"盛世巡礼-地点{s}")
            D.msg_append(f"地点{s}礼物已领取")
        elif s == 7 and ("点击继续" not in D.html):
            D.print_info("礼物已领取", f"盛世巡礼-地点{s}")
            D.msg_append(f"地点{s}礼物已领取")
        elif item := D.find(r"itemId=(\d+)", f"盛世巡礼-地点{s}-itemId"):
            # 收下礼物
            D.get(f"cmd=newAct&subtype=150&op=5&itemId={item}")
            _msg = D.find(r"礼物<br />(.*?)<br />", f"盛世巡礼-地点{s}-收下礼物")
            D.msg_append(f"地点{s}领取{_msg}")


def 新春登录礼():
    """
    每天至多领取七次
    """
    # 新春登录礼
    D.get("cmd=newAct&subtype=99&op=0")
    day = D.findall(r"day=(\d+)")
    if not day:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")
        return

    for d in day:
        # 领取
        D.get(f"cmd=newAct&subtype=99&op=1&day={d}")
        D.msg_append(D.find())


def 年兽大作战():
    """
    随机武技库免费一次
    自选武技库从大、中、小、投、技各随机选择一个补位
    挑战3次
    """
    # 年兽大作战
    D.get("cmd=newAct&subtype=170&op=0")
    if "等级不够" in D.html:
        D.print_info("等级不够，还未开启年兽大作战哦！")
        D.msg_append("等级不够，还未开启年兽大作战哦！")
        return

    for _ in D.find(r"剩余免费随机次数：(\d+)"):
        # 随机武技库 免费一次
        D.get("cmd=newAct&subtype=170&op=6")
        D.msg_append(D.find(r"帮助</a><br />(.*?)<br />"))

    # 自选武技库
    # 从大、中、小、投、技各随机选择一个
    if "暂未选择" in D.html:
        for t in range(5):
            D.get(f"cmd=newAct&subtype=170&op=4&type={t}")
            if "取消选择" in D.html:
                continue
            if ids := D.findall(r'id=(\d+)">选择'):
                # 选择
                D.get(f"cmd=newAct&subtype=170&op=7&id={random.choice(ids)}")
                if "自选武技列表已满" in D.html:
                    break

    for _ in range(3):
        # 挑战
        D.get("cmd=newAct&subtype=170&op=8")
        D.msg_append(D.find(r"帮助</a><br />(.*?)。"))


def 惊喜刮刮卡():
    """
    每天至多领取三次、点击刮卡二十次
    """
    # 领取
    for _id in range(3):
        D.get(f"cmd=newAct&subtype=148&op=2&id={_id}")
        D.msg_append(D.find(r"奖池预览</a><br /><br />(.*?)<br />"))

    # 刮卡
    for _ in range(20):
        D.get("cmd=newAct&subtype=148&op=1")
        D.msg_append(D.find(r"奖池预览</a><br /><br />(.*?)<br />"))
        if "您没有刮刮卡了" in D.html:
            break
        elif "不在刮奖时间不能刮奖" in D.html:
            break


def 开心娃娃机():
    """
    每天免费抓取一次
    """
    # 开心娃娃机
    D.get("cmd=newAct&subtype=124&op=0")
    if "1/1" not in D.html:
        D.print_info("没有免费抓取次数")
        D.msg_append("没有免费抓取次数")
        return

    # 抓取一次
    D.get("cmd=newAct&subtype=124&op=1")
    D.msg_append(D.find())


def 好礼步步升():
    """
    每天领取一次
    """
    D.get("cmd=newAct&subtype=43&op=get")
    D.msg_append(D.find())


def 企鹅吉利兑_兑换():
    _yaml: dict = D.yaml["企鹅吉利兑"]
    for name, number in _yaml.items():
        _id = D.find(rf"{name}.*?id=(\d+)")
        for _ in range(number):
            D.get(f"cmd=geelyexchange&op=ExchangeProps&id={_id}")
            msg = D.find(r"】<br /><br />(.*?)<br />")
            if "你的精魄不足，快去完成任务吧~" in D.html:
                break
            elif "该物品已达兑换上限~" in D.html:
                break
            D.msg_append(msg)
        if "当前精魄：0" in D.html:
            D.print_info("当前精魄：0")
            D.msg_append("当前精魄：0")
            break


def 企鹅吉利兑():
    """
    每天领取、活动截止日的前一天兑换材料，详见yaml配置文件
    """
    # 企鹅吉利兑
    D.get("cmd=geelyexchange")
    data = D.findall(r'id=(\d+)">领取</a>')
    if not data:
        D.print_info("没有礼包领取")
        D.msg_append("没有礼包领取")

    for _id in data:
        # 领取
        D.get(f"cmd=geelyexchange&op=GetTaskReward&id={_id}")
        D.msg_append(D.find(r"】<br /><br />(.*?)<br /><br />"))

    _year = D.year
    _month = D.findall(r"至(\d+)月")[0]
    _day = D.findall(r"至\d+月(\d+)日")[0]
    # 判断当前日期是否到达结束日期的前一天
    if D.is_arrive_date(1, (int(_year), int(_month), int(_day))):
        企鹅吉利兑_兑换()


def 乐斗大笨钟():
    c_乐斗大笨钟(D)


def 乐斗激运牌():
    """
    每天领取激运牌、翻牌
    """
    for _id in [0, 1]:
        # 领取
        D.get(f"cmd=realgoods&op=getTaskReward&id={_id}")
        D.msg_append(D.find(r"<br /><br />(.*?)<br />"))

    number = D.find(r"我的激运牌：(\d+)")
    for _ in range(int(number)):
        # 我要翻牌
        D.get("cmd=realgoods&op=lotteryDraw")
        D.msg_append(D.find(r"<br /><br />(.*?)<br />"))


def 乐斗回忆录():
    """
    周四领取回忆礼包、进阶礼包
    """
    for _id in range(1, 11):
        # 领取
        D.get(f"cmd=newAct&subtype=171&op=3&id={_id}")
        D.msg_append(D.find(r"6点<br />(.*?)<br />"))


def 爱的同心结():
    """
    依次兑换礼包5、4、3、2、1
    """
    data = {
        4016: 20,
        4015: 16,
        4014: 10,
        4013: 4,
        4012: 2,
    }
    for _id, count in data.items():
        for _ in range(count):
            # 兑换
            D.get(f"cmd=loveknot&sub=2&id={_id}")
            D.msg_append(D.find())
            if "恭喜您兑换成功" not in D.html:
                break


def 周年生日祝福():
    """
    周四领取
    """
    for day in range(1, 8):
        D.get(f"cmd=newAct&subtype=165&op=3&day={day}")
        D.msg_append(D.find())


def 重阳太白诗会():
    """
    每天领取重阳礼包
    不支持赋诗奖赏礼包
    """
    D.get("cmd=newAct&subtype=168&op=2")
    D.msg_append(D.find(r"<br /><br />(.*?)<br />"))
