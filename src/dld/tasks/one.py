"""
本模块为大乐斗第一轮任务

默认每天 13:01 定时运行

使用以下命令运行本模块任务：
    >>> # 立即运行第一轮任务
    >>> python main.py --one

    >>> # 立即运行某个函数
    >>> python main.py --one 邪神秘宝

    >>> # 立即运行多个函数
    >>> python main.py --one 邪神秘宝 矿洞
"""

import random
import re
import time
import traceback
from datetime import datetime, timedelta

from ..core.daledou import DaLeDou
from .common import (
    c_邪神秘宝,
    c_问鼎天下,
    c_帮派商会,
    c_任务派遣中心,
    c_侠士客栈,
    c_帮派巡礼,
    c_深渊秘境,
    c_龙凰论武,
    c_幸运金蛋,
    c_客栈同福,
    c_乐斗大笨钟,
)


def _run(d: DaLeDou, func_names: list):
    global D
    D = d
    for func in func_names:
        print("--" * 20)
        D.current_task = func
        D.append(f"\n【{func}】")
        try:
            globals()[func]()
        except Exception:
            D.log(f"{traceback.format_exc()}").append()


def run_one_args(d: DaLeDou, extra_args: list):
    """运行one模式携带的函数参数列表"""
    _run(d, extra_args)
    print("--" * 20)
    print(d.pushplus_content())
    print("--" * 20)


def run_one_all(d: DaLeDou, title: str):
    """运行one模式所有任务"""
    _run(d, d.func_names_one)
    print("--" * 20)
    d.pushplus_send(title)


# ============================================================


def get_exchange_config(config: list):
    """返回兑换名称、兑换id和兑换数量"""
    for item in config:
        name: str = item["name"]
        _id: int = item["id"]
        exchange_number: int = item["exchange_number"]
        if exchange_number > 0:
            yield name, _id, exchange_number


def is_target_date_reached(
    days_before: int, end_date_tuple: tuple[int, int, int]
) -> bool:
    """
    判断当前日期是否已达到或超过目标日期（结束日期的前N天）

    Args:
        days_before: 结束日期之前的天数（目标日期 = 结束日期 - days_before）
        end_date_tuple: 结束日期的年月日三元组，格式为 (年, 月, 日)

    Returns:
        bool: 如果当前日期大于等于目标日期返回True，否则返回False

    Examples:
        >>> # 判断当前日期是否为2024-11-7（2024-11-8的前1天）
        >>> is_target_date_reached(1, (2024, 11, 8))

        >>> # 判断当前日期是否为2024-11-2（2024-11-8的前6天）
        >>> is_target_date_reached(6, (2024, 11, 8))
    """
    end_year, end_month, end_day = end_date_tuple
    current_date = datetime.now().date()
    target_date = datetime(end_year, end_month, end_day).date() - timedelta(
        days=days_before
    )
    return current_date >= target_date


# ============================================================


def 邪神秘宝():
    c_邪神秘宝(D)


def 战阵调整() -> bool:
    """
    调整华山论剑出战侠士，仅替换耐久为0或未出战的位置

    Returns:
        bool: 调整是否成功完成
    """
    # 获取所有侠士id
    # 侠士页面
    D.get("cmd=knightarena&op=viewsetknightlist&pos=0")
    available_knight_ids = D.findall(r"knightid=(\d+)")
    if not available_knight_ids:
        D.log(D.find(r"<p>(.*?)</p>")).append()
        return False

    # 处理当前出战侠士
    # 战阵调整
    D.get("cmd=knightarena&op=viewteam")
    vacant_positions = D.findall(r'pos=(\d+)">选择侠士')
    deployed_knights = D.findall(r'耐久：(\d+).*?pos=(\d+)">更改侠士.*?id=(\d+)')

    positions_to_clear = []
    for durability, position, knight_id in deployed_knights:
        # 从可用列表中移除已出战的侠士
        if knight_id in available_knight_ids:
            available_knight_ids.remove(knight_id)

        # 记录需要清退的0耐久位置
        if durability == "0":
            positions_to_clear.append(position)
            # 下阵0耐久侠士
            D.get(f"cmd=knightarena&op=setknight&id={knight_id}&pos={position}&type=0")

    # 重新分配侠士
    all_vacant_positions = vacant_positions + positions_to_clear
    for position in all_vacant_positions:
        if not available_knight_ids:
            D.log("可用侠士已耗尽").append()
            break

        selected_knight = available_knight_ids.pop()
        # 上阵新侠士
        D.get(
            f"cmd=knightarena&op=setknight&id={selected_knight}&pos={position}&type=1"
        )
    return True


def 荣誉兑换():
    config: list[dict] = D.config["华山论剑"]
    if config is None:
        return

    for name, _id, exchange_number in get_exchange_config(config):
        count = 0
        for _ in range(exchange_number // 10):
            D.get(f"cmd=knightarena&op=exchange&id={_id}&times=10")
            D.log(D.find())
            if "成功" not in D.html:
                break
            count += 10
        for _ in range(exchange_number - count):
            D.get(f"cmd=knightarena&op=exchange&id={_id}&times=1")
            D.log(D.find())
            if "成功" not in D.html:
                break
            count += 1
        if count:
            D.append(f"兑换{name}*{count}")


def 侠士招募():
    # 侠士招募
    D.get("cmd=knightarena&op=viewlottery")
    number = int(D.find(r"（(\d+)）"))
    for _ in range(number // 100):
        # 招募十次
        D.get("cmd=knightarena&op=lottery&times=10")
        D.log(D.find()).append()


def 华山论剑():
    """
    免费挑战：每月1~25号每天挑战8次，耐久不足或者侠士未上阵时自动战阵调整
    赛季段位奖励：每月26号领取
    荣誉兑换：每月26号兑换，详见配置文件
    侠士招募：每月26号招募
    """
    if D.day == 26:
        # 领取赛季段位奖励
        D.get(r"cmd=knightarena&op=drawranking")
        D.log(D.find()).append()

        荣誉兑换()
        侠士招募()
        return

    for _ in range(10):
        # 华山论剑
        D.get("cmd=knightarena")
        if "免费挑战" not in D.html:
            D.log("没有免费挑战次数了").append()
            break
        # 免费挑战
        D.get("cmd=knightarena&op=challenge")
        D.log(D.find()).append()
        if "增加荣誉点数" in D.html:
            continue

        # 请先设置上阵侠士后再开始战斗
        # 耐久不足
        if not 战阵调整():
            break


def 斗豆月卡():
    """每天领取150斗豆"""
    # 领取150斗豆
    D.get("cmd=monthcard&sub=1")
    D.log(D.find(r"<p>(.*?)<br />")).append()


def 分享():
    """
    每天最多一键分享9次，斗神塔每次挑战11层以增加一次分享次数
    周四领取奖励，若全部已领取则重置分享
    """
    # 达人等级对应斗神塔CD时间
    cd = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 1,
        "9": 1,
        "10": 1,
    }
    # 乐斗达人
    D.get("cmd=ledouvip")
    if level := D.find(r"当前级别：(\d+)"):
        second = cd[level]
    else:
        # 还未成为达人
        second = 10

    end = False
    for _ in range(9):
        # 一键分享
        D.get("cmd=sharegame&subtype=6")
        D.log(D.find(r"】</p>(.*?)<p>"))
        if ("达到当日分享次数上限" in D.html) or end:
            D.log(D.find(r"</p><p>(.*?)<br />")).append()
            break

        for _ in range(11):
            # 开始挑战 or 挑战下一层
            D.get("cmd=towerfight&type=0")
            D.log(D.find(), "斗神塔")
            time.sleep(second)
            if "您战胜了" not in D.html:
                end = True
                break
            # 您败给了
            # 已经到了塔顶
            # 已经没有剩余的周挑战数
            # 您需要消耗斗神符才能继续挑战斗神塔

    # 自动挑战
    D.get("cmd=towerfight&type=11")
    D.log(D.find(), "斗神塔")
    time.sleep(second)
    if "结束挑战" in D.html:
        # 结束挑战
        D.get("cmd=towerfight&type=7")
        D.log(D.find(), "斗神塔")

    if D.week != 4:
        return

    # 领取奖励
    D.get("cmd=sharegame&subtype=3")
    for s in D.findall(r"sharenums=(\d+)"):
        # 领取
        D.get(f"cmd=sharegame&subtype=4&sharenums={s}")
        D.log(D.find(r"】</p>(.*?)<p>")).append()

    number = D.html.count("已领取")
    if number == 14:
        # 重置分享
        D.get("cmd=sharegame&subtype=7")
        D.log(D.find(r"】</p>(.*?)<p>")).append()


def 乐斗():
    """
    每天开启自动使用体力药水、使用4次贡献药水
    每天乐斗好友BOSS、帮友BOSS、侠侣页所有
    """
    # 乐斗助手
    D.get("cmd=view&type=6")
    if "开启自动使用体力药水" in D.html:
        # 开启自动使用体力药水
        D.get("cmd=set&type=0")
        D.log("开启自动使用体力药水").append()

    for _ in range(4):
        # 使用贡献药水*1
        D.get("cmd=use&id=3038&store_type=1&page=1")
        if "使用规则" in D.html:
            D.log(D.find(r"】</p><p>(.*?)<br />")).append()
            break
        D.log(D.find()).append()

    # 好友BOSS
    D.get("cmd=friendlist&page=1")
    for u in D.findall(r"侠：.*?B_UID=(\d+)"):
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}")
        D.log(D.find(r"删</a><br />(.*?)，")).append()
        if "体力值不足" in D.html:
            break

    # 帮友BOSS
    D.get("cmd=viewmem&page=1")
    for u in D.findall(r"侠：.*?B_UID=(\d+)"):
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}")
        D.log(D.find(r"侠侣</a><br />(.*?)，")).append()
        if "体力值不足" in D.html:
            break

    # 侠侣
    D.get("cmd=viewxialv&page=1")
    for u in D.findall(r"</a>\d+.*?B_UID=(\d+)"):
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}")
        if "使用规则" in D.html:
            D.log(D.find(r"】</p><p>(.*?)<br />")).append()
        elif "查看乐斗过程" in D.html:
            D.log(D.find(r"删</a><br />(.*?)！")).append()
        if "体力值不足" in D.html:
            break


def 武林():
    """每天报名武林大会"""
    # 报名
    D.get("cmd=fastSignWulin&ifFirstSign=1")
    if "使用规则" in D.html:
        D.log(D.find(r"】</p><p>(.*?)<br />")).append()
    else:
        D.log(D.find(r"升级。<br />(.*?) ")).append()


def 群侠():
    """每天报名笑傲群侠"""
    # 报名
    D.get("cmd=knightfight&op=signup")
    D.log(D.find(r"侠士侠号.*?<br />(.*?)<br />")).append()


def 侠侣():
    """周二、周五、周日报名侠侣争霸"""
    # 报名
    D.get("cmd=cfight&subtype=9")
    if "使用规则" in D.html:
        D.log(D.find(r"】</p><p>(.*?)<br />")).append()
    else:
        D.log(D.find(r"报名状态.*?<br />(.*?)<br />")).append()


def 结拜():
    """周一报名结拜（从低等级到高等级依次报名）"""
    for _id in [1, 2, 3, 5, 4]:
        # 报名
        D.get(f"cmd=brofight&subtype=1&gidIdx={_id}")
        D.log(D.find(r"排行</a><br />(.*?)<"))
        if "请换一个赛区报名" in D.html or "你们无法报名" in D.html:
            continue
        D.append()
        break


def 巅峰之战进行中():
    """
    领奖：周一领奖
    报名：周一报名，选择派别详见配置文件
    征战：周三~周日每天最多14次
    """
    if D.week == 1:
        # 领奖
        D.get("cmd=gvg&sub=1")
        D.log(D.find(r"】</p>(.*?)<br />")).append()

        config: int = D.config["巅峰之战进行中"]
        if config is None:
            return
        # 报名
        D.get(f"cmd=gvg&sub=4&group={config}&check=1")
        D.log(D.find(r"】</p>(.*?)<br />")).append()
        return

    for _ in range(14):
        # 征战
        D.get("cmd=gvg&sub=5")
        if "战线告急" in D.html:
            D.log(D.find(r"支援！<br />(.*?)<")).append()
        else:
            D.log(D.find(r"】</p>(.*?)<")).append()

        if "你在巅峰之战中" not in D.html:
            # 冷却时间
            # 撒花祝贺
            # 请您先报名再挑战
            # 您今天已经用完复活次数了
            break


def 矿洞():
    """
    挑战：每天3次
    通关奖励：有就领取
    开启副本：详见配置文件
    """
    config: str = D.config["矿洞"]

    # 矿洞
    D.get("cmd=factionmine")
    for _ in range(5):
        if "副本挑战中" in D.html:
            # 挑战
            D.get("cmd=factionmine&op=fight")
            D.log(D.find()).append()
            if "挑战次数不足" in D.html:
                break
        elif "开启副本" in D.html:
            if config is None:
                D.log("你没有配置开启副本").append()
                return
            # 确认开启
            D.get(f"cmd=factionmine&op=start&{config}")
            D.log(D.find()).append()
            if "当前不能开启此副本" in D.html:
                return
        elif "领取奖励" in D.html:
            D.get("cmd=factionmine&op=reward")
            D.log(D.find()).append()


def 掠夺():
    """
    周二掠夺一次战力最低的成员、领奖
    周三领取胜负奖励、报名
    """
    if D.week == 3:
        # 领取胜负奖励
        D.get("cmd=forage_war&subtype=6")
        D.log(D.find()).append()
        # 报名
        D.get("cmd=forage_war&subtype=1")
        D.log(D.find()).append()
        return

    # 掠夺
    D.get("cmd=forage_war")
    if ("本轮轮空" in D.html) or ("未报名" in D.html):
        D.log(D.find(r"本届战况：(.*?)<br />")).append()
        return

    data = []
    # 掠夺
    D.get("cmd=forage_war&subtype=3")
    if gra_id := D.findall(r'gra_id=(\d+)">掠夺'):
        for _id in gra_id:
            D.get(f"cmd=forage_war&subtype=3&op=1&gra_id={_id}")
            if zhanli := D.find(r"<br />1.*? (\d+)\."):
                data.append((int(zhanli), _id))
        if data:
            _, _id = min(data)
            D.get(f"cmd=forage_war&subtype=4&gra_id={_id}")
            D.log(D.find()).append()
    else:
        D.log("已占领对方全部粮仓").append()

    # 领奖
    D.get("cmd=forage_war&subtype=5")
    D.log(D.find()).append()


def 踢馆():
    """
    周五试炼5次、高倍转盘一次、最多挑战30次
    周六报名、领奖
    """
    if D.week == 6:
        # 报名
        D.get("cmd=facchallenge&subtype=1")
        D.log(D.find()).append()
        # 领奖
        D.get("cmd=facchallenge&subtype=7")
        D.log(D.find()).append()
        return

    def generate_sequence():
        # 试炼、高倍转盘序列
        for t in [2, 2, 2, 2, 2, 4]:
            yield t
        # 挑战序列
        for _ in range(30):
            yield 3

    for t in generate_sequence():
        D.get(f"cmd=facchallenge&subtype={t}")
        D.log(D.find()).append()
        if "您的复活次数已耗尽" in D.html:
            break
        elif "您的挑战次数已用光" in D.html:
            break
        elif "你们帮没有报名参加这次比赛" in D.html:
            break


def 竞技场():
    """
    兑换10个河图洛书：每月1~25号每天兑换，详见配置文件
    挑战：每月1~25号每天最多10次
    领取奖励：每月1~25号每天领取
    """
    config: bool = D.config["竞技场"]
    if config:
        # 兑换10个河图洛书
        D.get("cmd=arena&op=exchange&id=5435&times=10")
        D.log(D.find()).append()

    for _ in range(10):
        # 免费挑战 or 开始挑战
        D.get("cmd=arena&op=challenge")
        D.log(D.find()).append()
        if "免费挑战次数已用完" in D.html:
            break

    # 领取奖励
    D.get("cmd=arena&op=drawdaily")
    D.log(D.find()).append()


def 十二宫():
    """每天自动选择最高场景请猴王扫荡"""
    # 十二宫
    D.get("cmd=zodiacdungeon")
    if scene_id := D.findall(r"scene_id=(\d+)\">扫荡"):
        _id = scene_id[-1]
        # 请猴王扫荡
        D.get(f"cmd=zodiacdungeon&op=autofight&scene_id={_id}")
        if "恭喜你" in D.html:
            D.log(D.find(r"恭喜你，(.*?)！")).append()
            return
        elif "是否复活再战" in D.html:
            D.log(D.find(r"<br.*>(.*?)，")).append()
            return
        # 你已经不幸阵亡，请复活再战！
        # 挑战次数不足
        # 当前场景进度不足以使用自动挑战功能
        D.log(D.find(r"<p>(.*?)<br />")).append()


def 许愿():
    """每天领取许愿奖励、上香许愿、领取魂珠碎片宝箱"""
    for sub in [5, 1, 6]:
        D.get(f"cmd=wish&sub={sub}")
        D.log(D.find()).append()


def 抢地盘():
    """
    每天无限制区随机攻占一次

    等级  30级以下 40级以下 ... 120级以下 无限制区
    type  1       2            10        11
    """
    D.get("cmd=recommendmanor&type=11&page=1")
    if manorid := D.findall(r'manorid=(\d+)">攻占</a>'):
        _id = random.choice(manorid)
        # 攻占
        D.get(f"cmd=manorfight&fighttype=1&manorid={_id}")
        D.log(D.find(r"</p><p>(.*?)。")).append()
    # 兑换武器
    D.get("cmd=manor&sub=0")
    D.log(D.find(r"<br /><br />(.*?)<br /><br />")).append()


def 历练():
    """每天乐斗BOSS一次，最多乐斗5个BOSS"""
    config: list = D.config["历练"]
    if config is None:
        D.log("你没有配置历练BOSS").append()
        return

    # 乐斗助手
    D.get("cmd=view&type=6")
    if "取消自动使用活力药水" in D.html:
        # 取消自动使用活力药水
        D.get("cmd=set&type=11")
        D.log("取消自动使用活力药水").append()

    for _id in config:
        D.get(f"cmd=mappush&subtype=3&mapid=6&npcid={_id}&pageid=2")
        if "您还没有打到该历练场景" in D.html:
            D.log(D.find(r"介绍</a><br />(.*?)<br />")).append()
            continue

        D.log(D.find(r"阅历值：\d+<br />(.*?)<br />")).append()
        if "活力不足" in D.html:
            break
        elif "BOSS" not in D.html:
            # 你今天和xx挑战次数已经达到上限了，请明天再来挑战吧
            # 还不能挑战
            continue


def 镖行天下():
    """
    领取奖励：每天一次
    刷新押镖：当镖师是蔡八斗时刷新，最多免费两次
    启程护送：每天一次
    拦截：每天3次
    """
    # 镖行天下
    D.get("cmd=cargo")
    if "护送完成" in D.html:
        # 领取奖励
        D.get("cmd=cargo&op=16")
        D.log(D.find()).append()
    if "剩余护送次数：1" in D.html:
        # 护送押镖
        D.get("cmd=cargo&op=7")
        count = int(D.find(r"免费刷新次数：(\d+)"))
        for _ in range(count):
            if "蔡八斗" not in D.html:
                break
            # 刷新押镖
            D.get("cmd=cargo&op=8")
            D.log(D.find()).append()
        D.log("当前镖师：" + D.find(r"当前镖师：(.*?)<")).append()
        # 启程护送
        D.get("cmd=cargo&op=6")
        D.log(D.find()).append()

    for _ in range(5):
        # 刷新
        D.get("cmd=cargo&op=3")
        for uin in D.findall(r'passerby_uin=(\d+)">拦截'):
            # 拦截
            D.get(f"cmd=cargo&op=14&passerby_uin={uin}")
            D.log(D.find())
            if "系统繁忙" in D.html:
                continue
            elif "这个镖车在保护期内" in D.html:
                continue
            elif "您今天已达拦截次数上限了" in D.html:
                return
            D.append()


def 幻境():
    """
    每天自动选择最高场景最多乐斗5次
    领取奖励
    """
    # 幻境
    D.get("cmd=misty")
    if "【飘渺幻境】" not in D.html:
        # 返回飘渺幻境
        D.get("cmd=misty&op=return")
    if stage_id := D.findall(r"op=start&amp;stage_id=(\d+)"):
        D.get(f"cmd=misty&op=start&stage_id={stage_id[-1]}")
        if "您的挑战次数已用完" in D.html:
            D.log(D.find(r"0/1<br />(.*?)<")).append()
            return
        for _ in range(5):
            # 乐斗
            D.get("cmd=misty&op=fight")
            D.log(D.find(r"星数.*?<br />(.*?)<br />")).append()
            if "尔等之才" in D.html:
                break

        # 领取奖励
        while _id := D.find(r"box_id=(\d+)"):
            D.get(f"cmd=misty&op=reward&box_id={_id}")
            D.log(D.find(r"星数.*?<br />(.*?)<br />")).append()
        # 返回飘渺幻境
        D.get("cmd=misty&op=return")


def 群雄逐鹿():
    """周六报名、领奖"""
    for op in ["signup", "drawreward"]:
        D.get(f"cmd=thronesbattle&op={op}")
        D.log(D.find(r"届群雄逐鹿<br />(.*?)<br />")).append()


def 画卷迷踪():
    """每天最多挑战20次"""
    for _ in range(20):
        # 准备完成进入战斗
        D.get("cmd=scroll_dungeon&op=fight&buff=0")
        D.log(D.find(r"</a><br /><br />(.*?)<br />")).append()
        if "没有挑战次数" in D.html:
            break
        elif "征战书不足" in D.html:
            break


def 门派():
    """
    万年寺：每天点燃普通香炉、点燃高香香炉
    八叶堂：每天一次进入木桩训练、一次进入同门切磋
    五花堂：每天最多完成任务3次
    """
    # 点燃普通香炉、点燃高香香炉
    for op in ["fumigatefreeincense", "fumigatepaidincense"]:
        D.get(f"cmd=sect&op={op}")
        D.log(D.find(r"修行。<br />(.*?)<br />")).append()

    # 进入木桩训练、进入同门切磋
    for op in ["trainingwithnpc", "trainingwithmember"]:
        D.get(f"cmd=sect&op={op}")
        D.log(D.find()).append()

    # 五花堂
    wuhuatang = D.get("cmd=sect_task")
    missions = {
        "进入华藏寺看一看": "cmd=sect_art",
        "进入伏虎寺看一看": "cmd=sect_trump",
        "进入金顶看一看": "cmd=sect&op=showcouncil",
        "进入八叶堂看一看": "cmd=sect&op=showtraining",
        "进入万年寺看一看": "cmd=sect&op=showfumigate",
        "与掌门人进行一次武艺切磋": "cmd=sect&op=trainingwithcouncil&rank=1&pos=1",
        "与首座进行一次武艺切磋": "cmd=sect&op=trainingwithcouncil&rank=2&pos=1",
        "与堂主进行一次武艺切磋": "cmd=sect&op=trainingwithcouncil&rank=3&pos=1",
    }
    for name, url in missions.items():
        if name in wuhuatang:
            D.get(url)
            D.log(name)
    if "查看一名" in wuhuatang:
        # 查看一名同门成员的资料 or 查看一名其他门派成员的资料
        D.log("查看好友第二页所有成员")
        # 好友第2页
        D.get("cmd=friendlist&page=2")
        for uin in D.findall(r"</a>\d+.*?B_UID=(\d+)"):
            # 查看好友
            D.get(f"cmd=totalinfo&B_UID={uin}")
            D.log(f"查看好友{uin}")
    if "进行一次心法修炼" in wuhuatang:
        for _id in range(101, 119):
            # 修炼
            D.get(f"cmd=sect_art&subtype=2&art_id={_id}&times=1")
            D.log(D.find())
            if "修炼成功" in D.html:
                break

    # 五花堂
    D.get("cmd=sect_task")
    for task_id in D.findall(r'task_id=(\d+)">完成'):
        # 完成
        D.get(f"cmd=sect_task&subtype=2&task_id={task_id}")
        D.log(D.find()).append()


def 门派邀请赛_商店兑换():
    config: list[dict] = D.config["门派邀请赛"]
    if config is None:
        return

    for name, _id, exchange_number in get_exchange_config(config):
        count = 0
        for _ in range(exchange_number // 10):
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=10")
            D.log(D.find())
            if "成功" not in D.html:
                break
            count += 10
        for _ in range(exchange_number - count):
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=1")
            D.log(D.find())
            if "成功" not in D.html:
                break
            count += 1
        if count:
            D.append(f"兑换{name}*{count}")


def 门派邀请赛():
    """
    报名：周一报名
    领取奖励：周一领取
    商店兑换：周一兑换
    开始挑战：周三~周日每天最多10次
    """
    if D.week == 1:
        # 组队报名
        D.get("cmd=secttournament&op=signup")
        D.log(D.find()).append()
        # 领取奖励
        D.get("cmd=secttournament&op=getrankandrankingreward")
        D.log(D.find()).append()

        门派邀请赛_商店兑换()
        return

    for _ in range(10):
        # 开始挑战
        D.get("cmd=secttournament&op=fight")
        D.log(D.find()).append()
        if "已达最大挑战上限" in D.html:
            break
        elif "门派战书不足" in D.html:
            break


def 会武_商店兑换():
    config: list[dict] = D.config["会武"]
    if config is None:
        return

    for name, _id, exchange_number in get_exchange_config(config):
        count = 0
        for _ in range(exchange_number // 10):
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=10")
            D.log(D.find())
            if "成功" not in D.html:
                break
            count += 10
        for _ in range(exchange_number - count):
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=1")
            D.log(D.find())
            if "成功" not in D.html:
                break
            count += 1
        if count:
            D.append(f"兑换{name}*{count}")


def 会武():
    """
    初、中、高级试炼场：周一、周二、周三挑战
    助威：周四助威丐帮
    商店兑换：周四兑换
    领奖：周六领奖
    """
    if D.week in [1, 2, 3]:
        for _ in range(21):
            # 挑战
            D.get("cmd=sectmelee&op=dotraining")
            if "试炼场】" in D.html:
                D.log(D.find(r"最高伤害：\d+<br />(.*?)<br />")).append()
                continue
            D.log(D.find(r"规则</a><br />(.*?)<br />")).append()
            if "你已达今日挑战上限" in D.html:
                break
            elif "你的试炼书不足" in D.html:
                break
    elif D.week == 4:
        # 冠军助威 丐帮
        D.get("cmd=sectmelee&op=cheer&sect=1003")
        # 冠军助威
        D.get("cmd=sectmelee&op=showcheer")
        D.log(D.find()).append()
        会武_商店兑换()
    elif D.week == 6:
        # 领奖
        D.get("cmd=sectmelee&op=showreward")
        D.log(D.find(r"<br />(.*?)。")).append()
        D.log(D.find(r"。<br />(.*?)。")).append()
        # 领取
        D.get("cmd=sectmelee&op=drawreward")
        if "本届已领取奖励" in D.html:
            D.log(D.find(r"规则</a><br />(.*?)<br />")).append()
        else:
            D.log(D.find()).append()


def 梦幻旅行():
    if D.html.count("已去过") < 5:
        return

    # 获取当前区域所有未去过的目的地
    if place := D.findall(r"([\u4e00-\u9fa5\s\-]+)(?=\s未去过)"):
        bmapid = D.find(r'bmapid=(\d+)">梦幻旅行')
    for name in place:
        # 梦幻旅行
        D.get(f"cmd=dreamtrip&sub=3&bmapid={bmapid}")
        s = D.find(rf"{name}.*?smapid=(\d+)")
        # 去这里
        D.get(f"cmd=dreamtrip&sub=2&smapid={s}")
        D.log(D.find()).append()

    # 领取礼包
    for _ in range(2):
        if b := D.findall(r"sub=4&amp;bmapid=(\d+)"):
            # 区域礼包 1 or 2 or 3 or 4
            # 超级礼包 0
            D.get(f"cmd=dreamtrip&sub=4&bmapid={b[0]}")
            D.log(D.find()).append()


def 梦想之旅():
    """
    普通旅行：每天一次
    梦幻旅行：周四且需已去过至少5个区域时
    区域礼包：有就周四领取
    超级礼包：有就周四领取
    """
    # 普通旅行
    D.get("cmd=dreamtrip&sub=2")
    D.log(D.find()).append()
    if D.week == 4:
        梦幻旅行()


def 问鼎天下_商店兑换():
    """仅兑换宝物碎片（仅当神魔录古阵篇中的宝物可升级且碎片数量不足时兑换）"""

    def get_number():
        """获取背包物品数量"""
        # 背包物品详情
        D.get(f"cmd=owngoods&id={backpack_id}")
        if "很抱歉" in D.html:
            number = 0
        else:
            number = D.find(r"数量：(\d+)")
            D.log(number, f"{name}背包数量")
        return int(number)

    def exchange():
        """问鼎天下商店兑换"""
        q, r = divmod((consume_number - possess_number), 10)
        if q:
            # 兑换10个
            D.get(f"cmd=exchange&subtype=2&type={t}&times=10&costtype=14")
            D.log(D.find(), f"{name}兑换").append()
            return
        for _ in range(r):
            # 兑换1个
            D.get(f"cmd=exchange&subtype=2&type={t}&times=1&costtype=14")
            D.log(D.find(), f"{name}兑换").append()

    data = {
        "夔牛碎片": {
            "id": 1,
            "t": 1270,
            "backpack_id": 5154,
            "name": "夔牛鼓",
        },
        "饕餮碎片": {
            "id": 2,
            "t": 1271,
            "backpack_id": 5155,
            "name": "饕餮鼎",
        },
        "烛龙碎片": {
            "id": 3,
            "t": 1268,
            "backpack_id": 5156,
            "name": "烛龙印",
        },
        "黄鸟碎片": {
            "id": 4,
            "t": 1269,
            "backpack_id": 5157,
            "name": "黄鸟伞",
        },
    }
    for name, _dict in data.items():
        _id = _dict["id"]
        t = _dict["t"]
        backpack_id = _dict["backpack_id"]
        _name = _dict["name"]
        possess_number = get_number()

        # 神魔录古阵篇宝物详情
        D.get(f"cmd=ancient_gods&op=4&id={_id}")
        # 当前等级
        now_level = D.find(r"等级：(\d+)")
        D.log(now_level, f"{_name}当前等级")
        # 最高等级
        max_level = D.find(r"最高提升至(\d+)")
        D.log(max_level, f"{_name}最高等级")
        if now_level == max_level:
            continue
        # 碎片消耗数量
        consume_number = int(D.find(r"碎片\*(\d+)"))
        D.log(consume_number, f"{_name}碎片消耗数量")
        if consume_number > possess_number:
            exchange()


def 问鼎天下():
    """
    领取奖励：周一领取
    领取帮资：周一~周五有就领取
    放弃资源点：周一~周五有就放弃
    东海：周一~周五攻占倒数第一个
    淘汰赛：周六助威，详见配置文件
    排名赛：周日助威，详见配置文件
    商店兑换：周六周日兑换
    """
    if D.week == 6:
        # 淘汰赛助威
        _id = D.config["问鼎天下"]["淘汰赛"]
        if _id is None:
            D.log("你没有配置淘汰赛助威帮派id").append()
            return
        D.get(f"cmd=tbattle&op=cheerregionbattle&id={_id}")
        D.log(D.find()).append()
    elif D.week == 7:
        # 排名赛助威
        _id = D.config["问鼎天下"]["排名赛"]
        if _id is None:
            D.log("你没有配置排名赛助威帮派id").append()
            return
        D.get(f"cmd=tbattle&op=cheerchampionbattle&id={_id}")
        D.log(D.find()).append()

    if D.week in [6, 7]:
        问鼎天下_商店兑换()
        return

    if D.week == 1:
        # 领取奖励
        D.get("cmd=tbattle&op=drawreward")
        D.log(D.find()).append()

    c_问鼎天下(D)


def 帮派商会():
    c_帮派商会(D)


def 帮派远征军_攻击(p_id: str, u: str) -> bool:
    # 攻击
    D.get(f"cmd=factionarmy&op=fightWithUsr&point_id={p_id}&opp_uin={u}")
    if "加入帮派第一周不能参与帮派远征军" in D.html:
        return False
    if "【帮派远征军-征战结束】" in D.html:
        D.log(D.find())
        if "您未能战胜" in D.html:
            D.append()
            return False
    elif "【帮派远征军】" in D.html:
        D.log(D.find(r"<br /><br />(.*?)</p>")).append()
        if "您的血量不足" in D.html:
            return False
    return True


def 帮派远征军_领取():
    point_ids = []
    land_ids = []
    for _id in range(5):
        D.get(f"cmd=factionarmy&op=viewIndex&island_id={_id}")
        point_ids += D.findall(r'point_id=(\d+)">领取奖励')
        if "未解锁" in D.html:
            break
        land_ids += D.findall(r'island_id=(\d+)">领取岛屿宝箱')

    # 领取奖励
    for p_id in point_ids:
        D.get(f"cmd=factionarmy&op=getPointAward&point_id={p_id}")
        D.log(D.find()).append()

    # 领取岛屿宝箱
    for i_id in land_ids:
        D.get(f"cmd=factionarmy&op=getIslandAward&island_id={i_id}")
        D.log(D.find()).append()


def 帮派远征军():
    """
    攻击：周一~周日按战力从低到高攻击
    领取奖励：阵亡或者全部通关则领取
    """
    while True:
        # 帮派远征军
        D.get("cmd=factionarmy&op=viewIndex&island_id=-1")
        p_id = D.find(r'point_id=(\d+)">参战')
        if p_id is None:
            D.log("已经全部通关了").append()
            帮派远征军_领取()
            break
        # 参战
        D.get(f"cmd=factionarmy&op=viewpoint&point_id={p_id}")

        data = []
        for _ in range(20):
            data += D.findall(r'(\d+)\.\d+<a.*?opp_uin=(\d+)">攻击')
            pages = D.find(r'pages=(\d+)">下一页')
            if not data or pages is None:
                break
            # 下一页
            D.get(f"cmd=factionarmy&op=viewpoint&point_id={p_id}&page={pages}")

        for _, u in sorted(data, key=lambda x: int(x[0])):
            if not 帮派远征军_攻击(p_id, u):
                帮派远征军_领取()
                return


def 帮派黄金联赛_参战():
    # 参战
    D.get("cmd=factionleague&op=2")
    if "opp_uin" not in D.html:
        D.log("敌人已全部阵亡").append()
        return

    data = []
    if pages := D.find(r'pages=(\d+)">末页'):
        _pages = int(pages)
    else:
        _pages = 1
    for p in range(1, _pages + 1):
        D.get(f"cmd=factionleague&op=2&pages={p}")
        data += D.findall(r"%&nbsp;&nbsp;(\d+).*?opp_uin=(\d+)")

    for _, u in sorted(data, key=lambda x: int(x[0])):
        # 攻击
        D.get(f"cmd=factionleague&op=4&opp_uin={u}")
        if "不幸战败" in D.html:
            D.log(D.find()).append()
            break
        elif "您已阵亡" in D.html:
            D.log(D.find(r"<br /><br />(.*?)</p>")).append()
            break
        D.log(D.find())


def 帮派黄金联赛():
    """每天领取奖励、领取帮派赛季奖励、参与防守、参战攻击"""
    # 帮派黄金联赛
    D.get("cmd=factionleague&op=0")
    if "领取奖励" in D.html:
        # 领取轮次奖励
        D.get("cmd=factionleague&op=5")
        D.log(D.find(r"<p>(.*?)<br /><br />")).append()
    elif "领取帮派赛季奖励" in D.html:
        # 领取帮派赛季奖励
        D.get("cmd=factionleague&op=7")
        D.log(D.find(r"<p>(.*?)<br /><br />")).append()
    elif "已参与防守" not in D.html:
        # 参与防守
        D.get("cmd=factionleague&op=1")
        D.log(D.find(r"<p>(.*?)<br /><br />")).append()
    elif "休赛期" in D.html:
        D.log("休赛期无任何操作").append()

    if "op=2" in D.html:
        帮派黄金联赛_参战()


def 任务派遣中心():
    c_任务派遣中心(D)


def 武林盟主():
    """
    周三、五、日领取排行奖励和竞猜奖励
    周一、三、五分站赛报名
    周二、四、六竞猜所有
    """
    if D.week in [3, 5, 7]:
        # 武林盟主
        D.get("cmd=wlmz&op=view_index")
        if data := D.findall(r'section_id=(\d+)&amp;round_id=(\d+)">'):
            for s, r in data:
                D.get(f"cmd=wlmz&op=get_award&section_id={s}&round_id={r}")
                D.log(D.find(r"<br /><br />(.*?)</p>")).append()
        else:
            D.log("没有奖励领取").append()

    if D.week in [1, 3, 5]:
        _id: int = D.config["武林盟主"]
        if _id is None:
            D.log("你没有配置报名赛场id").append()
            return
        D.get(f"cmd=wlmz&op=signup&ground_id={_id}")
        if "总决赛周不允许报名" in D.html or "您的战力不足" in D.html:
            D.log(D.find(r"战报</a><br />(.*?)<br />")).append()
        elif "您已报名" in D.html:
            D.log(D.find(r"赛场】<br />(.*?)<br />")).append()
    elif D.week in [2, 4, 6]:
        for index in range(8):
            # 选择
            D.get(f"cmd=wlmz&op=guess_up&index={index}")
            D.log(D.find(r"规则</a><br />(.*?)<br />"))
        # 确定竞猜选择
        D.get("cmd=wlmz&op=comfirm")
        D.log(D.find(r"战报</a><br />(.*?)<br />")).append()


def 全民乱斗():
    """每天乱斗竞技任务列表领取、乱斗任务领取"""
    collect_status = False
    for t in [2, 3, 4]:
        D.get(f"cmd=luandou&op=0&acttype={t}")
        for _id in D.findall(r'.*?id=(\d+)">领取</a>'):
            collect_status = True
            # 领取
            D.get(f"cmd=luandou&op=8&id={_id}")
            D.log(D.find(r"斗】<br /><br />(.*?)<br />")).append()
    if not collect_status:
        D.log("没有礼包领取").append()


def 侠士客栈():
    c_侠士客栈(D)


def 大侠回归三重好礼():
    """周四领取奖励"""
    # 大侠回归三重好礼
    D.get("cmd=newAct&subtype=173&op=1")
    if data := D.findall(r"subtype=(\d+).*?taskid=(\d+)"):
        for s, t in data:
            # 领取
            D.get(f"cmd=newAct&subtype={s}&op=2&taskid={t}")
            D.log(D.find(r"】<br /><br />(.*?)<br />")).append()
    else:
        D.log("没有礼包领取").append()


def 飞升大作战():
    """
    每天兑换玄铁令*1、优先报名单排模式，玄铁令不足或者休赛期时选择匹配模式
    周四领取赛季结束奖励
    """
    # 兑换 玄铁令*1
    D.get("cmd=ascendheaven&op=exchange&id=2&times=1")
    D.log(D.find()).append()

    # 报名单排模式
    D.get("cmd=ascendheaven&op=signup&type=1")
    D.log(D.find()).append()
    if "时势造英雄" not in D.html:
        # 当前为休赛期，不在报名时间、还没有入场券玄铁令、你已经报名参赛
        # 报名匹配模式
        D.get("cmd=ascendheaven&op=signup&type=2")
        D.log(D.find()).append()

    if (D.week != 4) or ("赛季结算中" not in D.html):
        return

    # 境界修为
    D.get("cmd=ascendheaven&op=showrealm")
    for s in D.findall(r"season=(\d+)"):
        # 领取奖励
        D.get(f"cmd=ascendheaven&op=getrealmgift&season={s}")
        D.log(D.find()).append()


def 许愿帮铺():
    config: list[dict] = D.config["深渊之潮"]["许愿帮铺"]
    if config is None:
        return

    for name, _id, exchange_number in get_exchange_config(config):
        count = 0
        if "之书" in name:
            quotient = exchange_number // 25
        else:
            quotient = 0
        for _ in range(quotient):
            D.get(f"cmd=abysstide&op=wishexchangetimes&id={_id}&times=25")
            D.log(D.find(), name)
            if "成功" not in D.html:
                break
            count += 25
        for _ in range(exchange_number - count):
            D.get(f"cmd=abysstide&op=wishexchange&id={_id}")
            D.log(D.find(), name)
            if "成功" not in D.html:
                break
            count += 1
        if count:
            D.append(f"兑换{name}*{count}")


def 深渊之潮():
    """每月26号许愿帮铺兑换，详见配置文件"""
    c_帮派巡礼(D)
    c_深渊秘境(D)
    if D.day == 26:
        许愿帮铺()


def 侠客岛():
    """侠客行最多接受任务3次（免费次数为0时不再刷新）"""
    count = "4"
    mission_success = False
    # 侠客行
    D.get("cmd=knight_island&op=viewmissionindex")
    for _ in range(4):
        view_mission_detail_pos = D.findall(r"viewmissiondetail&amp;pos=(\d+)")
        if not view_mission_detail_pos:
            break
        for p in view_mission_detail_pos:
            # 接受
            D.get(f"cmd=knight_island&op=viewmissiondetail&pos={p}")
            name = D.find(r"侠客行<br /><br />(.*?)（")
            D.log(name, "侠客行-任务名称")
            # 快速委派
            D.get(f"cmd=knight_island&op=autoassign&pos={p}")
            D.log(D.find(r"）<br />(.*?)<br />"), f"侠客行-{name}")
            if "快速委派成功" in D.html:
                mission_success = True
                # 开始任务
                D.get(f"cmd=knight_island&op=begin&pos={p}")
                html = D.find(r"斗豆）<br />(.*?)<br />")
                D.log(html, f"侠客行-{name}")
                D.append(f"{name}：{html}")
            elif "符合条件侠士数量不足" in D.html:
                # 侠客行
                D.get("cmd=knight_island&op=viewmissionindex")
                # 免费刷新次数
                count = D.find(r"剩余：(\d+)次")
                D.log(count, "侠客行-免费刷新次数")
                if count != "0":
                    # 刷新
                    D.get(f"cmd=knight_island&op=refreshmission&pos={p}")
                    D.log(D.find(r"斗豆）<br />(.*?)<br />"), f"侠客行-{name}")
                else:
                    D.log("没有免费次数，取消刷新", f"侠客行-{name}")

        if count == "0":
            break

    if not mission_success:
        D.log("没有可接受的任务").append()


def 八卦迷阵():
    _data = {
        "离": 1,
        "坤": 2,
        "兑": 3,
        "乾": 4,
        "坎": 5,
        "艮": 6,
        "震": 7,
        "巽": 8,
    }
    # 八卦迷阵
    D.get("cmd=spacerelic&op=goosip")
    result = D.find(r"([乾坤震巽坎离艮兑]{4})")
    if not result:
        D.log("首通没有八卦提示", "时空遗迹-八卦迷阵").append()
        return

    for i in result:
        # 点击八卦
        D.get(f"cmd=spacerelic&op=goosip&id={_data[i]}")
        D.log(D.find(r"分钟<br /><br />(.*?)<br />"), "时空遗迹-八卦迷阵")
        if "恭喜您" not in D.html:
            # 你被迷阵xx击败，停留在了本层
            # 耐力不足，无法闯关
            # 你被此门上附着的阵法传送回了第一层
            # 请遵循迷阵规则进行闯关
            break
        # 恭喜您进入到下一层
        # 恭喜您已通关迷阵，快去领取奖励吧
    D.append()

    if "恭喜您已通关迷阵" in D.html:
        # 领取通关奖励
        D.get("cmd=spacerelic&op=goosipgift")
        D.log(D.find(r"分钟<br /><br />(.*?)<br />"), "时空遗迹-八卦迷阵").append()


def 遗迹商店():
    config: dict = D.config["时空遗迹"]["遗迹商店"]
    if config is None:
        return

    for t, _list in config.items():
        for name, _id, exchange_number in get_exchange_config(_list):
            count = 0
            for _ in range(exchange_number // 10):
                # 兑换十次
                D.get(f"cmd=spacerelic&op=buy&type={t}&id={_id}&num=10")
                D.log(
                    D.find(r"售卖区.*?<br /><br /><br />(.*?)<"),
                    name,
                )
                if "兑换成功" not in D.html:
                    break
                count += 10
            for _ in range(exchange_number - count):
                # 兑换一次
                D.get(f"cmd=spacerelic&op=buy&type={t}&id={_id}&num=1")
                D.log(
                    D.find(r"售卖区.*?<br /><br /><br />(.*?)<"),
                    name,
                )
                if "兑换成功" not in D.html:
                    break
                count += 1
            if count:
                D.append(f"兑换{name}*{count}")


def 异兽洞窟():
    _ids: list = D.config["时空遗迹"]["异兽洞窟"]
    if _ids is None:
        D.log("你没有配置异兽洞窟id").append()
        return

    for _id in _ids:
        D.get(f"cmd=spacerelic&op=monsterdetail&id={_id}")
        if "剩余挑战次数：0" in D.html:
            D.log("异兽洞窟没有挑战次数", "时空遗迹-异兽洞窟").append()
            break
        if "剩余血量：0" in D.html:
            # 扫荡
            D.get(f"cmd=spacerelic&op=saodang&id={_id}")
        else:
            # 挑战
            D.get(f"cmd=spacerelic&op=monsterfight&id={_id}")
        D.log(D.find(r"次数.*?<br /><br />(.*?)&"), "时空遗迹-异兽洞窟")
        if "请按顺序挑战异兽" in D.html:
            continue
        D.append()
        break


def 悬赏任务():
    data = []
    for t in [1, 2]:
        D.get(f"cmd=spacerelic&op=task&type={t}")
        data += D.findall(r"type=(\d+)&amp;id=(\d+)")
    for t, _id in data:
        D.get(f"cmd=spacerelic&op=task&type={t}&id={_id}")
        D.log(D.find(r"赛季任务</a><br /><br />(.*?)<"), "时空遗迹-悬赏任务")
        if "您未完成该任务" in D.html:
            continue
        D.append()


def 遗迹征伐():
    # 遗迹征伐
    D.get("cmd=spacerelic&op=relicindex")
    year = int(D.find(r"(\d+)年"))
    month = int(D.find(r"(\d+)月"))
    day = int(D.find(r"(\d+)日"))

    # 判断当前日期是否到达结束日期的前一天
    if is_target_date_reached(1, (year, month, day)):
        # 悬赏任务-登录奖励
        D.get("cmd=spacerelic&op=task&type=1&id=1")
        D.log(D.find(r"赛季任务</a><br /><br />(.*?)<"), "时空遗迹-悬赏任务").append()
        # 排行奖励
        D.get("cmd=spacerelic&op=getrank")
        D.log(D.find(r"奖励</a><br /><br />(.*?)<"), "时空遗迹-赛季排行").append()

        遗迹商店()
        return

    # 判断当前日期是否到达第八周
    if is_target_date_reached(7, (year, month, day)):
        D.log("当前处于休赛期，结束前一天领取赛季奖励和悬赏商店兑换").append()
        return

    异兽洞窟()

    # 联合征伐挑战
    D.get("cmd=spacerelic&op=bossfight")
    D.log(D.find(r"挑战</a><br />(.*?)&"), "时空遗迹-联合征伐").append()

    悬赏任务()


def 时空遗迹():
    """
    八卦迷阵：
        八卦门：每天根据首通提示通关
        领取通关奖励：通关八卦后领取
    遗迹征伐：
        第七周的最后一个周三（含）之前执行：
            异兽洞窟：优先扫荡，否则挑战
            联合征伐：每天挑战一次
            悬赏任务：每天领取
        赛季结束日期的前一天执行：
            领取悬赏任务登录奖励
            领取赛季排行奖励
            悬赏商店兑换
    """
    八卦迷阵()
    遗迹征伐()


def 世界树():
    """每天一键领取经验奖励、免费温养（无武器时自动选择武器）"""
    # 世界树
    D.get("cmd=worldtree")
    # 一键领取经验奖励
    D.get("cmd=worldtree&op=autoget&id=1")
    D.log(D.find(r"福宝<br /><br />(.*?)<br />")).append()

    def get_id() -> str | None:
        # 温养武器选择
        for t in range(4):
            D.get(f"cmd=worldtree&op=viewweaponpage&type={t}")
            for _id in D.findall(r"weapon_id=(\d+)"):
                # 选择
                D.get(f"cmd=worldtree&op=setweapon&weapon_id={_id}&type={t}")
                D.log(D.find(r"当前武器：(.*?)<"))
                return _id

    # 源宝树
    D.get("cmd=worldtree&op=viewexpandindex")
    if "免费温养" not in D.html:
        D.log("没有免费温养次数").append()
        return

    if "weapon_id=0" in D.html and not get_id():
        D.log("没有武器可选择").append()
        return

    # 源宝树
    D.get("cmd=worldtree&op=viewexpandindex")
    _id = D.find(r"weapon_id=(\d+)")
    # 免费温养
    D.get(f"cmd=worldtree&op=dostrengh&times=1&weapon_id={_id}")
    D.log(D.find(r"规则</a><br />(.*?)<br />")).append()
    D.log("当前进度：" + D.find(r"当前进度:(.*?)<")).append()


def 龙凰论武():
    if D.day > 25:
        return

    if D.day == 1:
        zone: int = D.config["龙凰之境"]["龙凰论武"]["zone"]
        # 报名
        D.get(f"cmd=dragonphoenix&op=sign&zone={zone}")
        D.log(D.find()).append()
        return

    c_龙凰论武(D)

    # 每日领奖
    D.get("cmd=dragonphoenix&op=gift")
    D.log(D.find(r"/5</a><br /><br />(.*?)<")).append()


def 龙凰云集():
    if D.day != 27:
        return

    # 龙凰云集
    D.get("cmd=dragonphoenix&op=yunji")
    for _id in D.findall(r"idx=(\d+)"):
        # 领奖
        D.get(f"cmd=dragonphoenix&op=reward&idx={_id}")
        D.log(D.find(r"<br /><br /><br />(.*?)<")).append()
        if "当前无可领取奖励" in D.html:
            break

    config: list[dict] = D.config["龙凰之境"]["龙凰云集"]
    if config is None:
        return

    for name, _id, exchange_number in get_exchange_config(config):
        count = 0
        for _ in range(exchange_number // 10):
            D.get(f"cmd=dragonphoenix&op=buy&id={_id}&num=10")
            D.log(D.find(r"<br /><br /><br />(.*?)<"), name)
            if "成功" not in D.html:
                break
            count += 10
        for _ in range(exchange_number - count):
            D.get(f"cmd=dragonphoenix&op=buy&id={_id}&num=1")
            D.log(D.find(r"<br /><br /><br />(.*?)<"), name)
            if "成功" not in D.html:
                break
            count += 1
        if count:
            D.append(f"兑换{name}*{count}")


def 龙吟破阵():
    if D.day != 1:
        return
    # 领取
    D.get("cmd=dragonphoenix&op=getlastreward")
    D.log(D.find(r"领取<br /><br />(.*?)<")).append()


def 龙凰之境():
    """
    龙凰论武：
        报名：每月1号报名，选择赛区详见配置文件
        挑战：每月4~25号每天随机挑战，挑战次数详见配置文件
        每日领奖：每月4~25号每天一次
    龙凰云集：
        领奖：每月27号领取赛季论武次数奖励
        商店兑换：每月27号兑换，兑换次数详见配置文件
    龙吟破阵：
        领取：每月1号阵法库领取
    """
    龙凰论武()
    龙凰云集()
    龙吟破阵()


def 增强经脉():
    """每天最多传功12次"""
    # 关闭传功符不足用斗豆代替
    D.get("cmd=intfmerid&sub=21&doudou=0")
    if "关闭" in D.html:
        # 关闭合成两次确认
        D.get("cmd=intfmerid&sub=19")

    for _ in range(12):
        # 增强经脉
        D.get("cmd=intfmerid&sub=1")
        _id = D.find(r'master_id=(\d+)">传功</a>')
        # 传功
        D.get(f"cmd=intfmerid&sub=2&master_id={_id}")
        D.log(D.find(r"</p>(.*?)<p>"), "任务-增强经脉")
        if "传功符不足！" in D.html:
            return

        # 一键拾取
        D.get("cmd=intfmerid&sub=5")
        D.log(D.find(r"</p>(.*?)<p>"), "任务-增强经脉")
        # 一键合成
        D.get("cmd=intfmerid&sub=10&op=4")
        D.log(D.find(r"</p>(.*?)<p>"), "任务-增强经脉")


def 助阵():
    """无字天书或者河图洛书提升3次"""
    data = {
        1: [0],
        2: [0, 1],
        3: [0, 1, 2],
        9: [0, 1, 2],
        4: [0, 1, 2, 3],
        5: [0, 1, 2, 3],
        6: [0, 1, 2, 3],
        7: [0, 1, 2, 3],
        8: [0, 1, 2, 3, 4],
        10: [0, 1, 2, 3],
        11: [0, 1, 2, 3],
        12: [0, 1, 2, 3],
        13: [0, 1, 2, 3],
        14: [0, 1, 2, 3],
        15: [0, 1, 2, 3],
        16: [0, 1, 2, 3],
        17: [0, 1, 2, 3],
        18: [0, 1, 2, 3, 4],
    }

    def get_id_index():
        for f_id, index_list in data.items():
            for index in index_list:
                yield (f_id, index)

    count = 0
    for _id, i in get_id_index():
        if count == 3:
            break
        p = f"cmd=formation&type=4&formationid={_id}&attrindex={i}&times=1"
        for _ in range(3):
            # 提升
            D.get(p)
            if "助阵组合所需佣兵不满足条件，不能提升助阵属性经验" in D.html:
                D.log(D.find(r"<br /><br />(.*?)。"), "任务-助阵")
                return
            elif "阅历不足" in D.html:
                D.log(D.find(r"<br /><br />(.*?)，"), "任务-助阵")
                return

            D.log(D.find(), "任务-助阵")
            if "提升成功" in D.html:
                count += 1
            elif "经验值已经达到最大" in D.html:
                break
            elif "你还没有激活该属性" in D.html:
                return


def 查看好友资料():
    """查看第2页所有好友"""
    # 乐斗助手
    D.get("cmd=view&type=6")
    if "开启查看好友信息和收徒" in D.html:
        #  开启查看好友信息和收徒
        D.get("cmd=set&type=1")
        D.log("开启查看好友信息和收徒").append()
    # 好友第2页
    D.get("cmd=friendlist&page=2")
    for uin in D.findall(r"</a>\d+.*?B_UID=(\d+)"):
        D.get(f"cmd=totalinfo&B_UID={uin}")


def 徽章进阶():
    """进阶一次"""
    # 关闭道具不足自动购买
    D.get("cmd=achievement&op=setautobuy&enable=0&achievement_id=12")
    for _id in range(1, 41):
        D.get(f"cmd=achievement&op=upgradelevel&achievement_id={_id}&times=1")
        if "【徽章馆】" not in D.html:
            D.log(D.find(), "任务-徽章进阶")
            break
        D.log(D.find("<br /><br />(.*?)<"), "任务-徽章进阶")


def 兵法研习():
    """
    兵法      消耗     id    功能
    金兰之泽  孙子兵法  2544  增加生命
    雷霆一击  孙子兵法  2570  增加伤害
    残暴攻势  武穆遗书  21001 增加暴击几率
    不屈意志  武穆遗书  21032 降低受到暴击几率
    """
    for _id in [21001, 2570, 21032, 2544]:
        D.get(f"cmd=brofight&subtype=12&op=practice&baseid={_id}")
        D.log(D.find(r"武穆遗书：\d+个<br />(.*?)<br />"), "任务-兵法研习")
        if "研习成功" in D.html:
            break


def 挑战陌生人():
    """乐斗陌生人4次"""
    # 斗友
    D.get("cmd=friendlist&type=1")
    for u in D.findall(r"</a>\d+.*?B_UID=(\d+)")[:4]:
        D.get(f"cmd=fight&B_UID={u}&page=1&type=9")
        D.log(D.find(r"删</a><br />(.*?)！"), "任务-挑战陌生人")


def 任务():
    """增强经脉、助阵每天必做"""
    增强经脉()
    助阵()

    # 日常任务
    missions = D.get("cmd=task&sub=1")
    if "查看好友资料" in missions:
        查看好友资料()
    if "徽章进阶" in missions:
        徽章进阶()
    if "兵法研习" in missions:
        兵法研习()
    if "挑战陌生人" in missions:
        挑战陌生人()

    # 一键完成任务
    D.get("cmd=task&sub=7")
    for k, v in D.findall(r'id=\d+">(.*?)</a>.*?>(.*?)</a>'):
        D.log(f"{k} {v}").append()


def 帮派供奉():
    _ids: list = D.config["我的帮派"]
    if _ids is None:
        D.log("你没有配置帮派供奉物品id").append()
        return

    for _id in _ids:
        for _ in range(5):
            # 供奉
            D.get(f"cmd=oblation&id={_id}&page=1")
            if "供奉成功" in D.html:
                D.log(D.find()).append()
                continue
            D.log(D.find(r"】</p><p>(.*?)<br />"))
            break
        if "每天最多供奉5次" in D.html:
            break


def 帮派任务():
    # 帮派任务
    faction_missions = D.get("cmd=factiontask&sub=1")
    missions = {
        "帮战冠军": "cmd=facwar&sub=4",
        "查看帮战": "cmd=facwar&sub=4",
        "查看帮贡": "cmd=factionhr&subtype=14",
        "查看祭坛": "cmd=altar",
        "查看踢馆": "cmd=facchallenge&subtype=0",
        "查看要闻": "cmd=factionop&subtype=8&pageno=1&type=2",
        # '加速贡献': 'cmd=use&id=3038&store_type=1&page=1',
        "粮草掠夺": "cmd=forage_war",
    }
    for name, url in missions.items():
        if name in faction_missions:
            D.get(url)
            D.log(name)
    if "帮派修炼" in faction_missions:
        count = 0
        for _id in [2727, 2758, 2505, 2536, 2437, 2442, 2377, 2399, 2429]:
            for _ in range(4):
                # 修炼
                D.get(f"cmd=factiontrain&type=2&id={_id}&num=1&i_p_w=num%7C")
                D.log(D.find(r"规则说明</a><br />(.*?)<br />"))
                if "技能经验增加" in D.html:
                    count += 1
                    continue
                # 帮贡不足
                # 你今天获得技能升级经验已达到最大！
                # 你需要提升帮派等级来让你进行下一步的修炼
                break
            if count == 4:
                break
    # 帮派任务
    D.get("cmd=factiontask&sub=1")
    for _id in D.findall(r'id=(\d+)">领取奖励</a>'):
        # 领取奖励
        D.get(f"cmd=factiontask&sub=3&id={_id}")
        D.log(D.find(r"日常任务</a><br />(.*?)<br />")).append()


def 我的帮派():
    """
    每天供奉5次、帮派任务最多领取奖励3次
    周日领取奖励、报名帮战、激活祝福
    """
    # 我的帮派
    D.get("cmd=factionop&subtype=3&facid=0")
    if "你的职位" not in D.html:
        D.log("您还没有加入帮派").append()
        return

    帮派供奉()
    帮派任务()

    if D.week != 7:
        return
    # 领取奖励 》报名帮战 》激活祝福
    for sub in [4, 9, 6]:
        D.get(f"cmd=facwar&sub={sub}")
        D.log(D.find(r"</p>(.*?)<br /><a.*?查看上届")).append()


def 帮派祭坛():
    """
    转动轮盘：每天最多30次
    领取奖励：有就领取
    """
    # 帮派祭坛
    D.get("cmd=altar")
    for _ in range(30):
        if "转动轮盘" in D.html:
            # 转动轮盘
            D.get("cmd=altar&op=spinwheel")
            if "转动轮盘" in D.html:
                D.log(D.find()).append()
            if "转转券不足" in D.html or "已达转转券转动次数上限" in D.html:
                return
        if "【随机分配】" in D.html:
            all_disbanded = True
            data = D.findall(r"op=(.*?)&amp;id=(\d+)")
            for op, _id in data:
                # 选择
                D.get(f"cmd=altar&op={op}&id={_id}")
                if "选择路线" in D.html:
                    # 向前|向左|向右
                    D.get(f"cmd=altar&op=dosteal&id={_id}")
                if "该帮派已解散" in D.html or "系统繁忙" in D.html:
                    D.log(D.find(r"<br /><br />(.*?)<br />"))
                    continue
                all_disbanded = False
                if "转动轮盘" in D.html:
                    D.log(D.find()).append()
                    break
            if all_disbanded and data:
                D.append()
                return
        if "领取奖励" in D.html:
            D.get("cmd=altar&op=drawreward")
            D.log(D.find()).append()


def 每日奖励():
    """每天领取每日礼包、传功符礼包、达人礼包、无字天书礼包"""
    for key in ["login", "meridian", "daren", "wuzitianshu"]:
        # 每日奖励
        D.get(f"cmd=dailygift&op=draw&key={key}")
        D.log(D.find()).append()


def 领取徒弟经验():
    """每天领取一次"""
    # 领取徒弟经验
    D.get("cmd=exp")
    D.log(D.find(r"每日奖励</a><br />(.*?)<br />")).append()


def 今日活跃度():
    """每天领取活跃度礼包、帮派总活跃礼包"""
    # 今日活跃度
    D.get("cmd=liveness")
    D.log(D.find(r"【(.*?)】")).append()
    if "帮派总活跃" in D.html:
        D.log(D.find(r"礼包</a><br />(.*?)<")).append()

    # 领取今日活跃度礼包
    for giftbag_id in range(1, 5):
        D.get(f"cmd=liveness_getgiftbag&giftbagid={giftbag_id}&action=1")
        D.log(D.find(r"】<br />(.*?)<p>")).append()

    # 领取帮派总活跃奖励
    D.get("cmd=factionop&subtype=18")
    if "创建帮派" in D.html:
        D.log(D.find(r"帮派</a><br />(.*?)<br />")).append()
    else:
        D.log(D.find()).append()


def 仙武修真():
    """每天领取3次任务、长留山最多挑战5次"""
    for task_id in range(1, 4):
        # 领取
        D.get(f"cmd=immortals&op=getreward&taskid={task_id}")
        D.log(D.find(r"帮助</a><br />(.*?)<br />")).append()

    for _ in range(5):
        # 寻访 长留山
        D.get("cmd=immortals&op=visitimmortals&mountainId=1")
        D.log(D.find(r"帮助</a><br />(.*?)<br />"))
        if "你的今日寻访挑战次数已用光" in D.html:
            D.append()
            break
        # 挑战
        D.get("cmd=immortals&op=fightimmortals")
        D.log(D.find(r"帮助</a><br />(.*?)<a")).append()


def 乐斗黄历():
    """每天领取、占卜一次"""
    # 领取
    D.get("cmd=calender&op=2")
    D.log(D.find(r"<br /><br />(.*?)<br />")).append()
    # 占卜
    D.get("cmd=calender&op=4")
    D.log(D.find(r"<br /><br />(.*?)<br />")).append()


def 器魂附魔():
    """附魔任务领取3次"""
    for _id in range(1, 4):
        # 领取
        D.get(f"cmd=enchant&op=gettaskreward&task_id={_id}")
        D.log(D.find()).append()


def 兵法():
    """
    周四随机助威
    周六领奖、领取斗币（需要活跃度满50）
    """
    if D.week == 4:
        # 助威
        D.get("cmd=brofight&subtype=13")
        _id = D.find(r"teamid=(\d+).*?助威</a>")
        # 确定
        D.get(f"cmd=brofight&subtype=13&teamid={_id}&type=5&op=cheer")
        D.log(D.find(r"领奖</a><br />(.*?)<br />")).append()

    if D.week != 6:
        return

    # 领奖
    D.get("cmd=brofight&subtype=13&op=draw")
    D.log(D.find(r"领奖</a><br />(.*?)<br />")).append()

    for t in range(1, 6):
        D.get(f"cmd=brofight&subtype=10&type={t}")
        for remainder, u in D.findall(r"50000.*?(\d+).*?champion_uin=(\d+)"):
            if remainder == "0":
                continue
            # 领斗币
            D.get(f"cmd=brofight&subtype=10&op=draw&champion_uin={u}&type={t}")
            D.log(D.find(r"排行</a><br />(.*?)<br />")).append()
            return


# ============================================================


def get_boss_id():
    """返回历练高等级到低等级场景每关最后两个BOSS的id"""
    for _id in range(6394, 6013, -20):
        yield _id
        yield (_id - 1)


def 猜单双():
    """随机单数、双数"""
    # 猜单双
    D.get("cmd=oddeven")
    for _ in range(5):
        value = D.findall(r'value=(\d+)">.*?数')
        if not value:
            D.log("猜单双已经结束").append()
            break

        value = random.choice(value)
        # 单数1 双数2
        D.get(f"cmd=oddeven&value={value}")
        D.log(D.find()).append()


def 煮元宵():
    """成熟度>=96时赶紧出锅"""
    # 煮元宵
    D.get("cmd=yuanxiao2014")
    for _ in range(4):
        # 开始烹饪
        D.get("cmd=yuanxiao2014&op=1")
        if "领取烹饪次数" in D.html:
            D.log("没有烹饪次数了").append()
            break

        for _ in range(20):
            maturity = D.find(r"当前元宵成熟度：(\d+)")
            if int(maturity) < 96:
                # 继续加柴
                D.get("cmd=yuanxiao2014&op=2")
                continue
            # 赶紧出锅
            D.get("cmd=yuanxiao2014&op=3")
            D.log(D.find(r"活动规则</a><br /><br />(.*?)。")).append()
            break


def 点亮() -> bool:
    # 点亮南瓜灯
    D.get("cmd=hallowmas&gb_id=1")
    while True:
        if cushaw_id := D.findall(r"cushaw_id=(\d+)"):
            c_id = random.choice(cushaw_id)
            # 南瓜
            D.get(f"cmd=hallowmas&gb_id=4&cushaw_id={c_id}")
            D.log(D.find()).append()
            if "活力" in D.html:
                return True
        if "请领取今日的活跃度礼包来获得蜡烛吧" in D.html:
            break
    return False


def 点亮南瓜灯():
    """万圣节-点亮南瓜灯"""
    # 乐斗助手
    D.get("cmd=view&type=6")
    if "取消自动使用活力药水" in D.html:
        # 取消自动使用活力药水
        D.get("cmd=set&type=11")
        D.log("取消自动使用活力药水")
    for _id in get_boss_id():
        count = 3
        while count:
            D.get(f"cmd=mappush&subtype=3&npcid={_id}&pageid=2")
            if "您还没有打到该历练场景" in D.html:
                D.log(D.find(r"介绍</a><br />(.*?)<br />"), "历练").append()
                break
            D.log(D.find(r"\d+<br />(.*?)<"), "历练").append()
            if "活力不足" in D.html:
                if not 点亮():
                    return
                continue
            elif "BOSS" not in D.html:
                # 你今天和xx挑战次数已经达到上限了，请明天再来挑战吧
                # 还不能挑战
                break
            count -= 1


def 万圣节():
    """
    点亮南瓜灯，获得的活力将乐斗历练BOSS
    活动截止日的前一天优先兑换礼包B，最后兑换礼包A
    """
    点亮南瓜灯()

    # 万圣节
    D.get("cmd=hallowmas")
    year = D.year
    month = int(D.find(r"~(\d+)月"))
    day = int(D.find(r"~\d+月(\d+)日"))
    # 判断当前日期是否到达结束日期的前一天
    if not is_target_date_reached(1, (year, month, day)):
        return

    number = int(D.find(r"南瓜灯：(\d+)个"))
    b = number // 40
    a = (number - b * 40) // 20
    for _ in range(b):
        # 兑换礼包B 消耗40个南瓜灯
        D.get("cmd=hallowmas&gb_id=6")
        D.log(D.find()).append()
    for _ in range(a):
        # 兑换礼包A 消耗20个南瓜灯
        D.get("cmd=hallowmas&gb_id=5")
        D.log(D.find()).append()


def 元宵节():
    """周四领取、领取生肖限定形象卡"""
    # 领取
    D.get("cmd=newAct&subtype=101&op=1")
    D.log(D.find(r"】</p>(.*?)<br />")).append()
    # 领取形象卡
    D.get("cmd=newAct&subtype=101&op=2&index=0")
    D.log(D.find(r"】</p>(.*?)<br />")).append()


def 神魔转盘():
    """幸运抽奖免费抽奖一次"""
    # 神魔转盘
    D.get("cmd=newAct&subtype=88&op=0")
    if "免费抽奖一次" not in D.html:
        D.log("没有免费抽奖次数了").append()
        return

    # 幸运抽奖
    D.get("cmd=newAct&subtype=88&op=1")
    D.log(D.find()).append()


def 乐斗驿站():
    """免费领取淬火结晶*1"""
    D.get("cmd=newAct&subtype=167&op=2")
    D.log(D.find()).append()


def 幸运转盘():
    """转动轮盘一次"""
    D.get("cmd=newAct&subtype=57&op=roll")
    D.log(D.find(r"0<br /><br />(.*?)<br />")).append()


def 冰雪企缘():
    """最多领取两次"""
    # 冰雪企缘
    D.get("cmd=newAct&subtype=158&op=0")
    gift = D.findall(r"gift_type=(\d+)")
    if not gift:
        D.log("没有礼包领取").append()
        return

    for _id in gift:
        # 领取
        D.get(f"cmd=newAct&subtype=158&op=2&gift_type={_id}")
        D.log(D.find()).append()


def 甜蜜夫妻():
    """
    夫妻甜蜜好礼   最多领取3次
    单身鹅鼓励好礼 最多领取3次
    """
    # 甜蜜夫妻
    D.get("cmd=newAct&subtype=129")
    flag = D.findall(r"flag=(\d+)")
    if not flag:
        D.log("没有礼包领取").append()
        return

    for f in flag:
        # 领取
        D.get(f"cmd=newAct&subtype=129&op=1&flag={f}")
        D.log(D.find(r"】</p>(.*?)<br />")).append()


def 乐斗菜单():
    """点单一次"""
    # 乐斗菜单
    D.get("cmd=menuact")
    if gift := D.find(r"套餐.*?gift=(\d+).*?点单</a>"):
        # 点单
        D.get(f"cmd=menuact&sub=1&gift={gift}")
        D.log(D.find(r"哦！<br /></p>(.*?)<br />")).append()
    else:
        D.log("没有点单次数了").append()


def 客栈同福():
    c_客栈同福(D)


def 周周礼包():
    """领取一次"""
    # 周周礼包
    D.get("cmd=weekgiftbag&sub=0")
    if _id := D.find(r';id=(\d+)">领取'):
        # 领取
        D.get(f"cmd=weekgiftbag&sub=1&id={_id}")
        D.log(D.find()).append()
    else:
        D.log("没有礼包领取").append()


def 登录有礼():
    """
    登录奖励：每天领取一次
    额外奖励：每天领取一次
    """
    # 登录有礼
    D.get("cmd=newAct&subtype=56")
    if g := D.find(r"gift_type=1.*?gift_index=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=56&op=draw&gift_type=1&gift_index={g}")
        D.log(D.find()).append()
    if g := D.find(r"gift_type=2.*?gift_index=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=56&op=draw&gift_type=2&gift_index={g}")
        D.log(D.find()).append()


def 活跃礼包():
    """领取50活跃礼包、80活跃礼包"""
    for p in ["1", "2"]:
        D.get(f"cmd=newAct&subtype=94&op={p}")
        D.log(D.find(r"】.*?<br />(.*?)<br />")).append()


def 上香活动():
    """领取檀木香、龙涎香各两次"""
    for _ in range(2):
        # 檀木香
        D.get("cmd=newAct&subtype=142&op=1&id=1")
        D.log(D.find()).append()
        # 龙涎香
        D.get("cmd=newAct&subtype=142&op=1&id=2")
        D.log(D.find()).append()


def 徽章战令():
    """领取每日礼包"""
    # 每日礼包
    D.get("cmd=badge&op=1")
    D.log(D.find()).append()


def 生肖福卡_好友赠卡():
    # 好友赠卡
    D.get("cmd=newAct&subtype=174&op=4")
    for name, qq, card_id in D.findall(r"送您(.*?)\*.*?oppuin=(\d+).*?id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=174&op=6&oppuin={qq}&card_id={card_id}")
        D.log(D.find()).append()


def 生肖福卡_分享福卡():
    qq: int = D.config["生肖福卡"]
    if qq is None:
        return

    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    pattern = "[子丑寅卯辰巳午未申酉戌亥][鼠牛虎兔龙蛇马羊猴鸡狗猪]"
    data = D.findall(rf"({pattern})\s+(\d+).*?id=(\d+)")
    _, max_number, _id = max(data, key=lambda x: int(x[1]))
    if int(max_number) >= 2:
        # 分享福卡
        D.get(f"cmd=newAct&subtype=174&op=5&oppuin={qq}&card_id={_id}&confirm=1")
        D.log(D.find(r"~<br /><br />(.*?)<br />")).append()


def 生肖福卡_领取福卡():
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    for _id in D.findall(r"task_id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=174&op=7&task_id={_id}")
        D.log(D.find(r"~<br /><br />(.*?)<br />")).append()


def 生肖福卡_合卡():
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    # 合卡结束日期
    month, day = D.findall(r"合卡时间：.*?至(\d+)月(\d+)日")[0]
    if D.month == int(month) and D.day == int(day):
        return

    # 合成周年福卡
    D.get("cmd=newAct&subtype=174&op=8")
    D.log(D.find(r"。<br /><br />(.*?)<br />")).append()


def 生肖福卡_抽奖():
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    # 兑奖开始日期
    month, day = D.findall(r"兑奖时间：(\d+)月(\d+)日")[0]
    if not (D.month == int(month) and D.day >= int(day)):
        return

    # 分斗豆
    D.get("cmd=newAct&subtype=174&op=9")
    D.log(D.find(r"。<br /><br />(.*?)<br />")).append()

    # 抽奖
    D.get("cmd=newAct&subtype=174&op=2")
    for _id, data in D.findall(r"id=(\d+).*?<br />(.*?)<br />"):
        numbers = re.findall(r"\d+", data)
        min_number = min(numbers, key=lambda x: int(x))
        for _ in range(int(min_number)):
            # 春/夏/秋/冬宵抽奖
            D.get(f"cmd=newAct&subtype=174&op=10&id={_id}&confirm=1")
            if "您还未合成周年福卡" in D.html:
                # 继续抽奖
                D.get(f"cmd=newAct&subtype=174&op=10&id={_id}")
            D.log(D.find(r"幸运抽奖<br /><br />(.*?)<br />")).append()


def 生肖福卡():
    """
    集卡：
        好友赠卡：领取好友赠卡
        分享福卡：向指定好友分享一次福卡（单类福卡数量至少为2）
        领取福卡：领取
    合卡：
        合卡时间内每天一次合成周年福卡
    抽奖：
        兑奖时间内周四分斗豆、抽奖（未合成周年福卡则继续抽奖）
    """
    生肖福卡_好友赠卡()
    生肖福卡_分享福卡()
    生肖福卡_领取福卡()

    if D.week != 4:
        return

    生肖福卡_合卡()
    生肖福卡_抽奖()


def 长安盛会():
    """
    盛会豪礼：点击领取  id  1
    签到宝箱：点击领取  id  2
    全民挑战：点击参与  id  3，4，5
    """
    # 5089真黄金卷轴 3036黄金卷轴
    D.get("cmd=newAct&subtype=118&op=2&select_id=5089")
    for _id in D.findall(r"op=1&amp;id=(\d+)"):
        if _id in ["1", "2"]:
            # 点击领取
            D.get(f"cmd=newAct&subtype=118&op=1&id={_id}")
            D.log(D.find()).append()
        else:
            turn_count = D.find(r"剩余转动次数：(\d+)")
            for _ in range(int(turn_count)):
                # 点击参与
                D.get(f"cmd=newAct&subtype=118&op=1&id={_id}")
                D.log(D.find()).append()


def 深渊秘宝():
    """
    三魂秘宝：免费抽奖
    七魄秘宝：免费抽奖
    """
    # 深渊秘宝
    D.get("cmd=newAct&subtype=175")
    t_list = D.findall(r'type=(\d+)&amp;times=1">免费抽奖')
    if not t_list:
        D.log("没有免费抽奖次数了").append()
        return

    for t in t_list:
        # 领取
        D.get(f"cmd=newAct&subtype=175&op=1&type={t}&times=1")
        D.log(D.find()).append()


def 中秋礼盒():
    """领取"""
    # 中秋礼盒
    D.get("cmd=midautumngiftbag&sub=0")
    _ids = D.findall(r"amp;id=(\d+)")
    if not _ids:
        D.log("没有礼包领取").append()
        return

    for _id in _ids:
        # 领取
        D.get(f"cmd=midautumngiftbag&sub=1&id={_id}")
        D.log(D.find()).append()
        if "已领取完该系列任务所有奖励" in D.html:
            continue


def 双节签到():
    """
    签到奖励：每天领取
    奖励金：活动截止日的前一天领取
    """
    # 领取签到奖励
    D.get("cmd=newAct&subtype=144&op=1")
    D.log(D.find()).append()

    month, day = D.findall(r"至(\d+)月(\d+)日")[0]
    if (D.month == int(month)) and (D.day == (int(day) - 1)):
        # 奖励金
        D.get("cmd=newAct&subtype=144&op=3")
        D.log(D.find()).append()


def 乐斗游记():
    """
    每天领取积分
    周四一键领取、兑换
    """
    # 乐斗游记
    D.get("cmd=newAct&subtype=176")
    # 今日游记任务
    for _id in D.findall(r"task_id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=176&op=1&task_id={_id}")
        D.log(D.find(r"积分。<br /><br />(.*?)<br />")).append()

    if D.week != 4:
        return

    # 一键领取
    D.get("cmd=newAct&subtype=176&op=5")
    D.log(D.find(r"积分。<br /><br />(.*?)<br />")).append()
    D.log(D.find(r"十次</a><br />(.*?)<br />乐斗")).append()

    # 兑换
    number = int(D.find(r"溢出积分：(\d+)"))
    quotient, remainder = divmod(number, 10)
    for _ in range(quotient):
        # 兑换十次
        D.get("cmd=newAct&subtype=176&op=2&num=10")
        D.log(D.find(r"积分。<br /><br />(.*?)<br />"))
    for _ in range(remainder):
        # 兑换一次
        D.get("cmd=newAct&subtype=176&op=2&num=1")
        D.log(D.find(r"积分。<br /><br />(.*?)<br />"))
    D.append(f"消耗{number}溢出积分兑换传功符*{number}")


def 斗境探秘():
    """领取每日探秘奖励、累计探秘奖励"""
    # 斗境探秘
    D.get("cmd=newAct&subtype=177")
    # 领取每日探秘奖励
    for _id in D.findall(r"id=(\d+)&amp;type=2"):
        # 领取
        D.get(f"cmd=newAct&subtype=177&op=2&id={_id}&type=2")
        D.log(D.find(r"】<br /><br />(.*?)<br />")).append()

    # 领取累计探秘奖励
    for _id in D.findall(r"id=(\d+)&amp;type=1"):
        # 领取
        D.get(f"cmd=newAct&subtype=177&op=2&id={_id}&type=1")
        D.log(D.find(r"】<br /><br />(.*?)<br />")).append()


def 幸运金蛋():
    c_幸运金蛋(D)


def 春联大赛():
    """
    答题：每天最多3次（字库中不存在春联则结束）
    斗币：每天领取3次
    """
    # 开始答题
    D.get("cmd=newAct&subtype=146&op=1")
    if "您的活跃度不足" in D.html:
        D.log("您的活跃度不足50").append()
        return
    elif "今日答题已结束" in D.html:
        D.log("今日答题已结束").append()
        return

    couplets_dict = {
        "爆竹传吉语": "腊梅报新春",
        "爆竹欣祝福": "银蛇喜迎春",
        "爆竹欣祝褔": "银蛇乐报春",
        "春呈丰稔景": "酒贺小龙年",
        "春到田畴绿": "蛇来淑景新",
        "春归蛇起舞": "福到鸟争鸣",
        "春来千野绿": "蛇舞四时新",
        "除牙难捕鼠": "添足便成龙",
        "国强民幸福": "蛇舞世升平",
        "花放山河丽": "蛇迎世纪春",
        "花开四季馥": "蛇舞九州春",
        "花柳春风绿": "蛇年瑞气盈",
        "虎辟长安道": "兔开大吉春",
        "虎驰金世界": "兔唤玉乾坤",
        "虎带祥云去": "兔铺锦绣来",
        "虎年腾大步": "兔岁展宏图",
        "虎去雄风在": "兔来喜气浓",
        "虎声传捷报": "兔影抖春晖",
        "虎嘶飞雪里": "兔舞画图中",
        "虎蹄留胜迹": "兔角搏青云",
        "虎威惊盛世": "兔翰绘新春",
        "虎跃前程去": "兔携好运来",
        "虎留英雄气": "兔会世纪风",
        "捷报飞新宇": "春潮促小龙",
        "捷报书宏志": "春风乐小龙",
        "金虎辞旧岁": "银兔贺新春",
        "金蛇含瑞草": "紫燕报新春",
        "金蛇狂舞日": "紫燕报春时",
        "金蛇盘玉兔": "赤帜舞神州",
        "睛点龙飞去": "珠还蛇舞来",
        "龙去神威在": "蛇来紫气生",
        "龙蛇交替舞": "岁月又更新",
        "龙腾传捷报": "蛇舞兆丰年",
        "龙腾丰稔岁": "蛇舞吉庆年",
        "龙舞山河壮": "蛇盘世纪新",
        "龙吟山海壮": "蛇舞国民欢",
        "龙展强邦志": "蛇生富国情",
        "卯来四季美": "兔献百家福",
        "卯门生紫气": "兔岁报拜年",
        "卯时春入户": "兔岁喜盈门",
        "民逢大有岁": "国正小龙年",
        "瑞雪兆丰年": "迎得玉兔归",
        "山舞银蛇景": "梅香瑞雪春",
        "山舞银蛇日": "地披红杏时",
        "蛇酿新年酒": "花开盛世春",
        "蛇舞升平世": "莺歌富贵春",
        "笙歌辞旧岁": "兔酒庆新春",
        "兔归皓月亮": "花绽春光妍",
        "兔毫抒壮志": "燕梭织春光",
        "兔俊千山秀": "春暖万水清",
        "雪消狮子瘦": "月满兔儿肥",
        "燕舞春光丽": "兔奔曙光新",
        "寅年春锦绣": "卯序业辉煌",
        "玉兔蟾宫笑": "红梅五岭香",
        "玉兔迎春到": "红梅祝福来",
        "玉兔迎春至": "黄莺报喜来",
        "红梅迎春笑": "玉兔出月欢",
        "红梅迎雪放": "玉兔踏春来",
        "红梅赠虎岁": "彩烛耀兔年",
        "喜迎新世纪": "欢庆小龙年",
        "丁年歌盛世": "卯兔耀中华",
    }

    for _ in range(3):
        shang_lian = D.find(r"上联：(.*?) ")
        D.log(shang_lian)
        options_A, index_A = D.findall(r"<br />A.(.*?)<.*?index=(\d+)")[0]
        options_B, index_B = D.findall(r"<br />B.(.*?)<.*?index=(\d+)")[0]
        options_C, index_C = D.findall(r"<br />C.(.*?)<.*?index=(\d+)")[0]
        options_dict = {
            options_A: index_A,
            options_B: index_B,
            options_C: index_C,
        }

        if xia_lian := couplets_dict.get(shang_lian):
            index = options_dict[xia_lian]
            # 选择
            D.get(f"cmd=newAct&subtype=146&op=3&index={index}")
            D.log(D.find(r"剩余\d+题<br />(.*?)<br />")).append()
            # 确定选择
            D.get("cmd=newAct&subtype=146&op=2")
            D.log(D.find()).append()
        else:
            D.log("字库未找到春联，请手动答题").append()
            break

    for _id in range(1, 4):
        # 领取
        D.get(f"cmd=newAct&subtype=146&op=4&id={_id}")
        D.log(D.find()).append()


def 新春拜年():
    """随机赠礼3个礼物"""
    # 新春拜年
    D.get("cmd=newAct&subtype=147")
    if "op=1" in D.html:
        for i in random.sample(range(5), 3):
            # 选中
            D.get(f"cmd=newAct&subtype=147&op=1&index={i}")
        # 赠礼
        D.get("cmd=newAct&subtype=147&op=2")
        D.log("已赠礼").append()


def 喜从天降():
    """每天最多点燃烟花10次，活动时间20.00-22.00"""
    for _ in range(10):
        D.get("cmd=newAct&subtype=137&op=1")
        D.log(D.find()).append()
        if "燃放烟花次数不足" in D.html:
            break


def 节日福利_历练():
    # 乐斗助手
    D.get("cmd=view&type=6")
    if "开启自动使用活力药水" in D.html:
        # 开启自动使用活力药水
        D.get("cmd=set&type=11")
        D.log("开启自动使用活力药水")

    for _id in get_boss_id():
        for _ in range(3):
            D.get(f"cmd=mappush&subtype=3&mapid=6&npcid={_id}&pageid=2")
            if "您还没有打到该历练场景" in D.html:
                D.log(D.find(r"介绍</a><br />(.*?)<br />"), "节日福利-历练").append()
                break
            D.log(D.find(r"阅历值：\d+<br />(.*?)<br />"), "节日福利-历练").append()
            if "活力不足" in D.html:
                return
            elif "活力药水使用次数已达到每日上限" in D.html:
                return
            elif "BOSS" not in D.html:
                # 你今天和xx挑战次数已经达到上限了，请明天再来挑战吧
                # 还不能挑战
                break


def 节日福利_斗神塔():
    # 达人等级对应斗神塔CD时间
    cd = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 1,
        "9": 1,
        "10": 1,
    }
    # 乐斗达人
    D.get("cmd=ledouvip")
    if level := D.find(r"当前级别：(\d+)"):
        second = cd[level]
    else:
        # 还未成为达人
        second = 10

    count = 0
    for _ in range(16):
        # 自动挑战
        D.get("cmd=towerfight&type=11")
        D.log(D.find(), "节日福利-斗神塔")
        if "结束挑战" in D.html:
            time.sleep(second)
            # 结束挑战
            D.get("cmd=towerfight&type=7")
            D.log(D.find(), "节日福利-斗神塔")
        else:
            D.append()
            break
        count += 1
    D.append(f"斗神塔自动挑战*{count}")


def 节日福利():
    """
    历练：每天从高等级到低等级依次乐斗BOSS（自动使用活力药水）
    斗神塔：周四自动挑战（次数耗尽或到不了顶层结束）
    """
    节日福利_历练()
    if D.week == 4:
        节日福利_斗神塔()


def 预热礼包():
    """每天领取一次礼包"""
    # 领取
    D.get("cmd=newAct&subtype=117&op=1")
    D.log(D.find(r"<br /><br />(.*?)<")).append()


def 五一礼包():
    """周四领取3次劳动节礼包"""
    for _id in range(3):
        D.get(f"cmd=newAct&subtype=113&op=1&id={_id}")
        D.log(D.find(r"】<br /><br />(.*?)<")).append()


def 浩劫宝箱():
    """周四领取一次"""
    D.get("cmd=newAct&subtype=152")
    D.log(D.find(r"浩劫宝箱<br />(.*?)<br />")).append()


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
        D.log(D.find(r"】<br /><br />(.*?)<br />")).append()
        if "您的端午香粽不足" in D.html:
            break

    # 礼包3
    D.get("cmd=newAct&subtype=121&op=1&index=2")
    D.log(D.find(r"】<br /><br />(.*?)<br />")).append()


def 圣诞有礼():
    """周四领取点亮奖励和连线奖励"""
    # 圣诞有礼
    D.get("cmd=newAct&subtype=145")
    for _id in D.findall(r"task_id=(\d+)"):
        # 任务描述：领取奖励
        D.get(f"cmd=newAct&subtype=145&op=1&task_id={_id}")
        D.log(D.find()).append()

    # 连线奖励
    for i in D.findall(r"index=(\d+)"):
        D.get(f"cmd=newAct&subtype=145&op=2&index={i}")
        D.log(D.find()).append()


def 新春礼包():
    """周四领取礼包"""
    for _id in [280, 281, 282]:
        # 领取
        D.get(f"cmd=xinChunGift&subtype=2&giftid={_id}")
        D.log(D.find()).append()


def 登录商店():
    """周四兑换"""
    t: int = D.config["登录商店"]
    if t is None:
        D.log("你没有配置兑换物品id").append()
        return

    for _ in range(5):
        # 兑换5次
        D.get(f"cmd=newAct&op=exchange&subtype=52&type={t}&times=5")
        D.log(D.find(r"<br /><br />(.*?)<br /><br />")).append()
    for _ in range(3):
        # 兑换1次
        D.get(f"cmd=newAct&op=exchange&subtype=52&type={t}&times=1")
        D.log(D.find(r"<br /><br />(.*?)<br /><br />")).append()


def 盛世巡礼():
    """周四收下礼物"""
    for s in range(1, 8):
        # 点击进入
        D.get(f"cmd=newAct&subtype=150&op=2&sceneId={s}")
        if "他已经给过你礼物了" in D.html:
            D.log(f"地点{s}礼物已领取").append()
        elif s == 7 and ("点击继续" not in D.html):
            D.log(f"地点{s}礼物已领取").append()
        elif _id := D.find(r"itemId=(\d+)"):
            # 收下礼物
            D.get(f"cmd=newAct&subtype=150&op=5&itemId={_id}")
            D.log(D.find(r"礼物<br />(.*?)<br />")).append()


def 新春登录礼():
    """最多领取7次"""
    # 新春登录礼
    D.get("cmd=newAct&subtype=99&op=0")
    day = D.findall(r"day=(\d+)")
    if not day:
        D.log("没有礼包领取").append()
        return

    for d in day:
        # 领取
        D.get(f"cmd=newAct&subtype=99&op=1&day={d}")
        D.log(D.find()).append()


def 年兽大作战():
    """
    随机武技库免费一次
    自选武技库从大、中、小、投、技各随机选择一个补位
    挑战3次
    """
    # 年兽大作战
    D.get("cmd=newAct&subtype=170&op=0")
    if "等级不够" in D.html:
        D.log("等级不够，还未开启年兽大作战哦！").append()
        return

    for _ in D.find(r"剩余免费随机次数：(\d+)"):
        # 随机武技库 免费一次
        D.get("cmd=newAct&subtype=170&op=6")
        D.log(D.find(r"帮助</a><br />(.*?)<br />")).append()

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
        D.log(D.find(r"帮助</a><br />(.*?)。")).append()


def 惊喜刮刮卡():
    """最多领取3次、点击刮卡20次"""
    # 领取
    for _id in range(3):
        D.get(f"cmd=newAct&subtype=148&op=2&id={_id}")
        D.log(D.find(r"奖池预览</a><br /><br />(.*?)<br />")).append()

    # 刮卡
    for _ in range(20):
        D.get("cmd=newAct&subtype=148&op=1")
        D.log(D.find(r"奖池预览</a><br /><br />(.*?)<br />")).append()
        if "您没有刮刮卡了" in D.html:
            break
        elif "不在刮奖时间不能刮奖" in D.html:
            break


def 开心娃娃机():
    """免费抓取一次"""
    # 开心娃娃机
    D.get("cmd=newAct&subtype=124&op=0")
    if "1/1" not in D.html:
        D.log("没有免费抓取次数").append()
        return

    # 抓取一次
    D.get("cmd=newAct&subtype=124&op=1")
    D.log(D.find()).append()


def 好礼步步升():
    """每天领取一次"""
    D.get("cmd=newAct&subtype=43&op=get")
    D.log(D.find()).append()


def 企鹅吉利兑_兑换():
    config: list[dict] = D.config["企鹅吉利兑"]
    if config is None:
        D.log("你没有配置兑换物品").append()
        return

    for name, _id, exchange_number in get_exchange_config(config):
        count = 0
        for _ in range(exchange_number):
            D.get(f"cmd=geelyexchange&op=ExchangeProps&id={_id}")
            D.log(D.find(r"】<br /><br />(.*?)<br />"), name)
            if "你的精魄不足，快去完成任务吧~" in D.html:
                break
            elif "该物品已达兑换上限~" in D.html:
                break
            count += 1
        if count:
            D.append(f"兑换{name}*{count}")


def 企鹅吉利兑():
    """
    领取：每天领取
    兑换：截止日前一天兑换材料，详见配置文件
    """
    # 企鹅吉利兑
    D.get("cmd=geelyexchange")
    if _ids := D.findall(r'id=(\d+)">领取</a>'):
        for _id in _ids:
            # 领取
            D.get(f"cmd=geelyexchange&op=GetTaskReward&id={_id}")
            D.log(D.find(r"】<br /><br />(.*?)<br /><br />")).append()
    else:
        D.log("没有礼包领取").append()

    year = D.year
    month = int(D.find(r"至(\d+)月"))
    day = int(D.find(r"至\d+月(\d+)日"))
    # 判断当前日期是否到达结束日期的前一天
    if is_target_date_reached(1, (year, month, day)):
        企鹅吉利兑_兑换()


def 乐斗大笨钟():
    c_乐斗大笨钟(D)


def 乐斗激运牌():
    """每天领取激运牌两次、翻牌"""
    for _id in [0, 1]:
        # 领取
        D.get(f"cmd=realgoods&op=getTaskReward&id={_id}")
        D.log(D.find(r"<br /><br />(.*?)<br />")).append()

    number = int(D.find(r"我的激运牌：(\d+)"))
    for _ in range(number):
        # 我要翻牌
        D.get("cmd=realgoods&op=lotteryDraw")
        D.log(D.find(r"<br /><br />(.*?)<br />")).append()


def 乐斗能量棒():
    """最多领取3次能量棒，获得的活力将乐斗历练BOSS"""
    # 乐斗能量棒
    D.get("cmd=newAct&subtype=108&op=0")
    data = D.findall(r"id=(\d+)")
    if not data:
        D.log("没有可领取的能量棒").append()
        return

    # 乐斗助手
    D.get("cmd=view&type=6")
    if "取消自动使用活力药水" in D.html:
        # 取消自动使用活力药水
        D.get("cmd=set&type=11")
        D.log("取消自动使用活力药水")
    for _id in get_boss_id():
        count = 3
        while count:
            D.get(f"cmd=mappush&subtype=3&npcid={_id}&pageid=2")
            if "您还没有打到该历练场景" in D.html:
                D.log(D.find(r"介绍</a><br />(.*?)<br />"), "历练").append()
                break
            D.log(D.find(r"\d+<br />(.*?)<"), "历练").append()
            if "活力不足" in D.html:
                if not data:
                    return
                # 领取活力能量棒
                D.get(f"cmd=newAct&subtype=108&op=1&id={data.pop()}")
                D.log(D.find(r"<br /><br />(.*?)<")).append()
                continue
            elif "BOSS" not in D.html:
                # 你今天和xx挑战次数已经达到上限了，请明天再来挑战吧
                # 还不能挑战
                break
            count -= 1


def 乐斗回忆录():
    """周四领取回忆礼包、进阶礼包"""
    for _id in range(1, 11):
        # 领取
        D.get(f"cmd=newAct&subtype=171&op=3&id={_id}")
        D.log(D.find(r"6点<br />(.*?)<br />")).append()


def 爱的同心结():
    """依次兑换礼包5、4、3、2、1"""
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
            D.log(D.find()).append()
            if "恭喜您兑换成功" not in D.html:
                break


def 乐斗儿童节():
    """周四领取选择奖励"""
    # 乐斗儿童节
    D.get("cmd=newAct&subtype=130")
    if "取消返回" in D.html:
        # 取消返回
        D.get("cmd=newAct&subtype=130&op=6")

    if "op=2" not in D.html:
        D.log("你已经领取过了").append()
        return

    config: str = D.config["乐斗儿童节"]
    if config in None:
        D.log("你没有配置选择").append()
        return

    t, s = D.findall(r"type=(\d+)&sub_type=(\d+)", config)[0]
    # 选择分类
    D.get(f"cmd=newAct&subtype=130&op=2&type={t}")
    # 选择
    D.get(f"cmd=newAct&subtype=130&op=3&type={t}&sub_type={s}")
    D.log(D.find(r"】</p>(.*?)<")).append()


def 周年生日祝福():
    """周四领取"""
    for day in range(1, 8):
        D.get(f"cmd=newAct&subtype=165&op=3&day={day}")
        D.log(D.find()).append()


def 重阳太白诗会():
    """
    重阳礼包：每天领取一次
    不支持赋诗奖赏礼包
    """
    D.get("cmd=newAct&subtype=168&op=2")
    D.log(D.find(r"<br /><br />(.*?)<br />")).append()


def 五一预订礼包():
    """每天领取登录礼包"""
    # 5.1预订礼包
    D.get("cmd=lokireservation")
    if _id := D.find(r"idx=(\d+)"):
        # 领取
        D.get(f"cmd=lokireservation&op=draw&idx={_id}")
        D.log(D.find(r"<br /><br />(.*?)<")).append()
    else:
        D.log("没有登录礼包领取").append()
