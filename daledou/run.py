import argparse
import random
import re
import time
from datetime import datetime, timedelta

from schedule import every, repeat, run_pending

from daledou.utils import push, yield_dld_objects


@repeat(every(2).hours)
def job_timing():
    # 每隔 2 小时检测Cookie有效期
    _run_func("check")


@repeat(every().day.at("13:10"))
def job_one():
    # 每天 13:10 运行第一轮
    _run_func("one")


@repeat(every().day.at("20:01"))
def job_two():
    # 每天 20:01 运行第二轮
    _run_func("two")


def _get_parse_args() -> tuple[str, list[str]]:
    """
    解析命令行参数，返回运行模式和额外参数列表
    """
    parser = argparse.ArgumentParser(description="处理命令行参数")
    parser.add_argument("mode", nargs="?", default="", help="运行模式")
    parser.add_argument("--extra", help="额外的参数")

    args, unknown_args = parser.parse_known_args()
    return args.mode, unknown_args


def run_serve():
    mode, unknown_args = _get_parse_args()

    if mode not in ["", "timing", "one", "two", "check", "dev"]:
        print(f"不存在 {mode} 运行模式")
        return

    if mode in ["", "timing"]:
        _run_func("check")
        print("脚本将在 13:10 和 20:01 定时运行...")
        while True:
            run_pending()
            time.sleep(1)
    else:
        _run_func(mode, unknown_args)


def _run_func(mode: str, unknown_args=None):
    global D
    print("--" * 20)
    for D in yield_dld_objects():
        print("--" * 20)
        if mode == "check":
            continue

        if mode == "dev":
            func_name_list = unknown_args
        elif mode in ["one", "two"]:
            func_name_list = D.func_map[mode]

        for func_name in func_name_list:
            D.func_name = func_name
            D.msg_append(f"\n【{func_name}】")
            result = globals()[func_name]()
        D.run_time()
        print("--" * 20)

        if (mode == "dev") and (result is None):
            print("--------------模拟微信信息--------------")
            print(D.msg_join)
        elif mode in ["one", "two"]:
            # pushplus微信推送消息
            push(f"{D.qq} {mode}", D.msg_join)

        print("--" * 20)


# ============================================================


def get_backpack_item_count(item_id: str | int) -> int:
    """
    返回背包物品id数量
    """
    # 背包物品详情
    D.get(f"cmd=owngoods&id={item_id}")
    if "很抱歉" in D.html:
        D.find(r"】</p><p>(.*?)<br />", f"背包-{item_id}-不存在")
        result = 0
    else:
        result = D.find(r"数量：(\d+)", f"背包-{item_id}-数量")
    return int(result)


def get_store_points(params: str) -> int:
    """
    返回商店积分
    """
    # 商店
    D.get(params)
    result = D.find(name="商店积分")
    _, store_points = result.split("：")
    return int(store_points)


def 邪神秘宝():
    """
    每天高级秘宝和极品秘宝免费一次或者抽奖一次
    """
    for i in [0, 1]:
        # 免费一次 or 抽奖一次
        D.get(f"cmd=tenlottery&op=2&type={i}")
        D.msg_append(D.find(r"】</p>(.*?)<br />"))


def 华山论剑():
    """
    每月1~25号每天免费挑战8次，侠士耐久为0时取消出战并更换侠士
    每月26号领取赛季段位奖励
    """

    def 战阵调整() -> bool:
        """
        选择侠士、0耐久侠士取消出战后更改侠士
        """
        # 点击第一战选择侠士/更改侠士
        D.get("cmd=knightarena&op=viewsetknightlist&pos=0")
        # 获取所有侠士id
        knightid = D.findall(r"knightid=(\d+)")
        if not knightid:
            D.msg_append(D.find(r"<p>(.*?)</p>"))
            return False

        # 点击战阵调整
        D.get("cmd=knightarena&op=viewteam")
        # 获取所有选择侠士pos(即第一、二、三战未出战的pos)
        choose_knight_pos = D.findall(r'pos=(\d+)">选择侠士')
        # 获取所有更改侠士的耐久、pos、id
        change_knight = D.findall(r'耐久：(\d+)/.*?pos=(\d+)">更改侠士.*?id=(\d+)')

        knight_durable_0_pos = []
        for d, p, _id in change_knight:
            # 移除更改侠士id
            knightid.remove(_id)
            if d == "0":
                # 筛选0耐久侠士pos
                knight_durable_0_pos.append(p)
                # 0耐久侠士取消出战
                D.get(f"cmd=knightarena&op=setknight&id={_id}&pos={p}&type=0")

        # 选择/更改侠士
        for p in choose_knight_pos + knight_durable_0_pos:
            # 判断还有没有可用的侠士
            if not knightid:
                D.print_info("没有可用的侠士")
                D.msg_append("没有可用的侠士")
                break
            _id: str = knightid.pop()
            # 出战
            D.get(f"cmd=knightarena&op=setknight&id={_id}&pos={p}&type=1")
        return True

    # 每月26号领取赛季段位奖励
    if D.day == 26:
        # 赛季段位奖励
        D.get(r"cmd=knightarena&op=drawranking")
        D.msg_append(D.find())
        return

    # 每月1~25号挑战
    for _ in range(10):
        # 华山论剑
        D.get("cmd=knightarena")
        if "免费挑战" not in D.html:
            D.print_info("免费挑战次数已用完")
            D.msg_append("免费挑战次数已用完")
            break
        # 免费挑战
        D.get("cmd=knightarena&op=challenge")
        D.msg_append(D.find())
        if "增加荣誉点数" in D.html:
            continue

        # 请先设置上阵侠士后再开始战斗
        # 耐久不足
        if not 战阵调整():
            break


def 斗豆月卡():
    """
    每天领取150斗豆:
    """
    # 领取150斗豆
    D.get("cmd=monthcard&sub=1")
    D.msg_append(D.find(r"<p>(.*?)<br />"))


def 分享():
    """
    每天一键分享，斗神塔每次挑战11层以增加一次分享次数
    周四领取奖励
    """
    _end = False
    # 达人等级对应斗神塔CD时间
    data = {
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
    if grade := D.find(r"当前级别：(\d+)", "达人等级"):
        second = data[grade]
    else:
        # 还未成为达人
        second = 10

    for _ in range(9):
        # 一键分享
        D.get("cmd=sharegame&subtype=6")
        D.find(r"】</p>(.*?)<p>")
        if ("达到当日分享次数上限" in D.html) or _end:
            D.msg_append(D.find(r"</p><p>(.*?)<br />.*?开通达人"))
            break

        for _ in range(11):
            # 开始挑战 or 挑战下一层
            D.get("cmd=towerfight&type=0")
            D.find(name="斗神塔-挑战")
            time.sleep(second)
            if "您" in D.html:
                # 您败给了
                # 您战胜了
                continue

            # 系统繁忙
            # 已经到了塔顶
            # 已经没有剩余的周挑战数
            # 您需要消耗斗神符才能继续挑战斗神塔
            _end = True

    # 自动挑战
    D.get("cmd=towerfight&type=11")
    D.find(name="斗神塔-自动挑战")
    for _ in range(10):
        time.sleep(second)
        if "结束挑战" in D.html:
            # 结束挑战
            D.get("cmd=towerfight&type=7")
            D.find(name="斗神塔-结束挑战")
            break
        # 挑战下一层
        D.get("cmd=towerfight&type=0")
        D.find(name="斗神塔-挑战")

    if D.week == 4:
        # 领取奖励
        D.get("cmd=sharegame&subtype=3")
        for s in D.findall(r"sharenums=(\d+)"):
            # 领取
            D.get(f"cmd=sharegame&subtype=4&sharenums={s}")
            D.msg_append(D.find(r"】</p>(.*?)<p>"))


def 乐斗():
    """
    每天开启自动使用体力药水、使用四次贡献药水
    每天乐斗好友BOSS、帮友BOSS以及侠侣页所有
    """
    # 乐斗助手
    D.get("cmd=view&type=6")
    if "开启自动使用体力药水" in D.html:
        #  开启自动使用体力药水
        D.get("cmd=set&type=0")
        D.print_info("开启自动使用体力药水")
        D.msg_append("开启自动使用体力药水")

    for _ in range(4):
        # 使用贡献药水*1
        D.get("cmd=use&id=3038&store_type=1&page=1")
        if "使用规则" in D.html:
            D.msg_append(D.find(r"】</p><p>(.*?)<br />"))
            break
        D.msg_append(D.find())

    # 好友BOSS
    D.get("cmd=friendlist&page=1")
    for u in D.findall(r"侠：.*?B_UID=(\d+)"):
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}")
        D.msg_append(D.find(r"删</a><br />(.*?)，"))
        if "体力值不足" in D.html:
            break

    # 帮友BOSS
    D.get("cmd=viewmem&page=1")
    for u in D.findall(r"侠：.*?B_UID=(\d+)"):
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}")
        D.msg_append(D.find(r"侠侣</a><br />(.*?)，"))
        if "体力值不足" in D.html:
            break

    # 侠侣
    D.get("cmd=viewxialv&page=1")
    uin = D.findall(r"：.*?B_UID=(\d+)")
    if not uin:
        D.print_info("侠侣未找到uin")
        D.msg_append("侠侣未找到uin")
        return
    for u in uin[1:]:
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}")
        if "使用规则" in D.html:
            D.msg_append(D.find(r"】</p><p>(.*?)<br />"))
        elif "查看乐斗过程" in D.html:
            D.msg_append(D.find(r"删</a><br />(.*?)！"))
        if "体力值不足" in D.html:
            break


def 报名():
    """
    每天报名武林大会、笑傲群侠
    周二、五、日报名侠侣争霸
    """
    # 武林大会
    D.get("cmd=fastSignWulin&ifFirstSign=1")
    if "使用规则" in D.html:
        D.msg_append(D.find(r"】</p><p>(.*?)<br />"))
    else:
        D.msg_append(D.find(r"升级。<br />(.*?) "))

    # 侠侣争霸
    if D.week in [2, 5, 7]:
        D.get("cmd=cfight&subtype=9")
        if "使用规则" in D.html:
            D.msg_append(D.find(r"】</p><p>(.*?)<br />"))
        else:
            D.msg_append(D.find(r"报名状态.*?<br />(.*?)<br />"))

    # 笑傲群侠
    D.get("cmd=knightfight&op=signup")
    D.msg_append(D.find(r"侠士侠号.*?<br />(.*?)<br />"))


def 巅峰之战进行中():
    """
    周一、二随机加入及领奖
    周三、四、五、六、日征战
    """
    if D.week in [1, 2]:
        # 随机加入
        D.get("cmd=gvg&sub=4&group=0&check=1")
        D.msg_append(D.find(r"】</p>(.*?)<br />"))
        # 领奖
        D.get("cmd=gvg&sub=1")
        D.msg_append(D.find(r"】</p>(.*?)<br />"))
        return

    for _ in range(14):
        # 征战
        D.get("cmd=gvg&sub=5")
        if "你在巅峰之战中" in D.html:
            if "战线告急" in D.html:
                D.msg_append(D.find(r"支援！<br />(.*?)。"))
            else:
                D.msg_append(D.find(r"】</p>(.*?)。"))
            continue

        # 冷却时间
        # 撒花祝贺
        # 请您先报名再挑战
        # 您今天已经用完复活次数了
        if "战线告急" in D.html:
            D.msg_append(D.find(r"支援！<br />(.*?)<br />"))
        else:
            D.msg_append(D.find(r"】</p>(.*?)<br />"))
        break


def 矿洞():
    """
    每天挑战三次
    领取通关领取
    开启副本
    """
    _yaml: dict = D.yaml["矿洞"]
    f = _yaml["floor"]
    m = _yaml["mode"]

    # 矿洞
    D.get("cmd=factionmine")
    for _ in range(5):
        if "副本挑战中" in D.html:
            # 挑战
            D.get("cmd=factionmine&op=fight")
            D.msg_append(D.find())
            if "挑战次数不足" in D.html:
                break
            time.sleep(1)
        elif "开启副本" in D.html:
            # 确认开启
            D.get(f"cmd=factionmine&op=start&floor={f}&mode={m}")
            D.msg_append(D.find())
            if "当前不能开启此副本" in D.html:
                break
        elif "领取奖励" in D.html:
            D.get("cmd=factionmine&op=reward")
            D.msg_append(D.find())


def 掠夺():
    """
    周二掠夺一次（各粮仓中第一个最低战斗力的成员）、领奖
    周三领取胜负奖励、报名
    """
    if D.week == 3:
        # 领取胜负奖励
        D.get("cmd=forage_war&subtype=6")
        D.msg_append(D.find())
        # 报名
        D.get("cmd=forage_war&subtype=1")
        D.msg_append(D.find())
        return

    # 掠夺
    D.get("cmd=forage_war")
    if "本轮轮空" in D.html:
        D.msg_append(D.find(r"本届战况：(.*?)<br />"))
        return
    elif "未报名" in D.html:
        D.msg_append(D.find(r"本届战况：(.*?)<br />"))
        return

    # 掠夺
    D.get("cmd=forage_war&subtype=3")
    data = []
    if gra_id := D.findall(r'gra_id=(\d+)">掠夺'):
        for _id in gra_id:
            D.get(f"cmd=forage_war&subtype=3&op=1&gra_id={_id}")
            if zhanli := D.find(r"<br />1.*? (\d+)\."):
                data.append((int(zhanli), _id))
        if data:
            _, _id = min(data)
            D.get(f"cmd=forage_war&subtype=4&gra_id={_id}")
            D.msg_append(D.find())
    else:
        D.print_info("已占领对方全部粮仓")
        D.msg_append("已占领对方全部粮仓")

    # 领奖
    D.get("cmd=forage_war&subtype=5")
    D.msg_append(D.find())


def 踢馆():
    """
    周五试炼5次、高倍转盘一次、挑战至多30次
    周六报名及领奖
    """
    if D.week == 6:
        # 报名
        D.get("cmd=facchallenge&subtype=1")
        D.msg_append(D.find())
        # 领奖
        D.get("cmd=facchallenge&subtype=7")
        D.msg_append(D.find())
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
        D.msg_append(D.find())
        if "您的复活次数已耗尽" in D.html:
            break
        elif "您的挑战次数已用光" in D.html:
            break
        elif "你们帮没有报名参加这次比赛" in D.html:
            break


def 竞技场():
    """
    每天兑换10个河图洛书
    每月1~25号每天挑战至多10次、领取奖励
    """
    # 兑换10个河图洛书
    D.get("cmd=arena&op=exchange&id=5435&times=10")
    D.msg_append(D.find())

    if D.day > 25:
        return

    for _ in range(10):
        # 免费挑战 or 开始挑战
        D.get("cmd=arena&op=challenge")
        D.msg_append(D.find())
        if "免费挑战次数已用完" in D.html:
            break

    # 领取奖励
    D.get("cmd=arena&op=drawdaily")
    D.msg_append(D.find())


def 十二宫():
    """
    每天请猴王扫荡yaml配置的关卡
    """
    _id: int = D.yaml["十二宫"]
    # 请猴王扫荡
    D.get(f"cmd=zodiacdungeon&op=autofight&scene_id={_id}")
    if "恭喜你" in D.html:
        D.msg_append(D.find(r"恭喜你，(.*?)！"))
        return
    elif "是否复活再战" in D.html:
        D.msg_append(D.find(r"<br.*>(.*?)，"))
        return

    # 你已经不幸阵亡，请复活再战！
    # 挑战次数不足
    # 当前场景进度不足以使用自动挑战功能
    D.msg_append(D.find(r"<p>(.*?)<br />"))


def 许愿():
    """
    每天领取许愿奖励、上香许愿、领取魂珠碎片宝箱
    """
    for sub in [5, 1, 6]:
        D.get(f"cmd=wish&sub={sub}")
        D.msg_append(D.find())


def 抢地盘():
    """
    每天无限制区攻占一次第10位

    等级  30级以下 40级以下 ... 120级以下 无限制区
    type  1       2            10        11
    """
    D.get("cmd=recommendmanor&type=11&page=1")
    if manorid := D.findall(r'manorid=(\d+)">攻占</a>'):
        # 攻占
        D.get(f"cmd=manorfight&fighttype=1&manorid={manorid[-1]}")
        D.msg_append(D.find(r"</p><p>(.*?)。"))
    # 兑换武器
    D.get("cmd=manor&sub=0")
    D.msg_append(D.find(r"<br /><br />(.*?)<br /><br />"))


def 历练():
    """
    取消自动使用活力药水
    每天乐斗yaml配置指定的关卡BOSS3次
    """
    _yaml: list = D.yaml["历练"]

    # 乐斗助手
    D.get("cmd=view&type=6")
    if "取消自动使用活力药水" in D.html:
        #  取消自动使用活力药水
        D.get("cmd=set&type=11")
        D.print_info("取消自动使用活力药水")
        D.msg_append("取消自动使用活力药水")

    for _id in _yaml:
        for _ in range(3):
            D.get(f"cmd=mappush&subtype=3&mapid=6&npcid={_id}&pageid=2")
            if "您还没有打到该历练场景" in D.html:
                D.msg_append(D.find(r"介绍</a><br />(.*?)<br />"))
                break
            D.msg_append(D.find(r"阅历值：\d+<br />(.*?)<br />"))
            if "活力不足" in D.html:
                return
            elif "挑战次数已经达到上限了，请明天再来挑战吧" in D.html:
                break
            elif "还不能挑战" in D.html:
                break


def 镖行天下():
    """
    每天拦截3次、领取奖励、刷新押镖并启程护送
    """
    for op in [16, 8, 6]:
        # 领取奖励 》刷新押镖 》启程护送
        D.get(f"cmd=cargo&op={op}")
        D.msg_append(D.find())

    for _ in range(5):
        # 刷新
        D.get("cmd=cargo&op=3")
        for uin in D.findall(r'passerby_uin=(\d+)">拦截'):
            # 拦截
            D.get(f"cmd=cargo&op=14&passerby_uin={uin}")
            _msg = D.find()
            if "系统繁忙" in D.html:
                continue
            elif "这个镖车在保护期内" in D.html:
                continue
            elif "您今天已达拦截次数上限了" in D.html:
                return
            D.msg_append(_msg)


def 幻境():
    """
    每天乐斗yaml配置的关卡
    """
    stage_id: int = D.yaml["幻境"]
    D.get(f"cmd=misty&op=start&stage_id={stage_id}")
    for _ in range(5):
        # 乐斗
        D.get("cmd=misty&op=fight")
        D.msg_append(D.find(r"星数.*?<br />(.*?)<br />"))
        if "尔等之才" in D.html:
            break
    # 返回飘渺幻境
    D.get("cmd=misty&op=return")


def 群雄逐鹿():
    """
    周六报名、领奖
    """
    for op in ["signup", "drawreward"]:
        D.get(f"cmd=thronesbattle&op={op}")
        D.msg_append(D.find(r"届群雄逐鹿<br />(.*?)<br />"))


def 画卷迷踪():
    """
    每天至多挑战20次
    """
    for _ in range(20):
        # 准备完成进入战斗
        D.get("cmd=scroll_dungeon&op=fight&buff=0")
        D.msg_append(D.find(r"选择</a><br /><br />(.*?)<br />"))
        if "没有挑战次数" in D.html:
            break
        elif "征战书不足" in D.html:
            break


def 门派():
    """
    万年寺：点燃普通香炉 》点燃高香香炉
    八叶堂：进入木桩训练 》进入同门切磋 》进入同门切磋
    五花堂：至多完成任务3次
    """
    # 点燃普通香炉 》点燃高香香炉
    for op in ["fumigatefreeincense", "fumigatepaidincense"]:
        D.get(f"cmd=sect&op={op}")
        D.msg_append(D.find(r"修行。<br />(.*?)<br />"))

    # 进入木桩训练 》进入同门切磋 》进入同门切磋
    for op in ["trainingwithnpc", "trainingwithmember", "trainingwithmember"]:
        D.get(f"cmd=sect&op={op}")
        D.msg_append(D.find())

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
            D.print_info(name)
            D.get(url)
    if "查看一名" in wuhuatang:
        # 查看一名同门成员的资料 or 查看一名其他门派成员的资料
        D.print_info("查看好友第二页所有成员")
        # 好友第2页
        D.get("cmd=friendlist&page=2")
        for uin in D.findall(r"\d+：.*?B_UID=(\d+).*?级"):
            # 查看好友
            D.get(f"cmd=totalinfo&B_UID={uin}")
    if "进行一次心法修炼" in wuhuatang:
        """
        少林心法      峨眉心法    华山心法      丐帮心法    武当心法      明教心法
        101 法华经    104 斩情决  107 御剑术   110 醉拳    113 太极内力  116 圣火功
        102 金刚经    105 护心决  108 龟息术   111 烟雨行  114 绕指柔剑  117 五行阵
        103 达摩心经  106 观音咒  109 养心术   112 笑尘诀  115 金丹秘诀  118 日月凌天
        """
        for art_id in range(101, 119):
            D.get(f"cmd=sect_art&subtype=2&art_id={art_id}&times=1")
            D.find()
            if "你的心法已达顶级无需修炼" in D.html:
                continue
            # 修炼成功
            # 你的门派贡献不足无法修炼
            break

    # 五花堂
    D.get("cmd=sect_task")
    for task_id in D.findall(r'task_id=(\d+)">完成'):
        # 完成
        D.get(f"cmd=sect_task&subtype=2&task_id={task_id}")
        D.msg_append(D.find())


def 门派邀请赛():
    """
    周一、二报名、领取奖励
    周三~周日开始挑战至多10次（消耗门派战书*5）
    商店兑换详见yaml配置文件
    """
    _yaml: dict = D.yaml["门派邀请赛"]

    # 门派邀请赛商店兑换
    for _id, _dict in _yaml.items():
        _week: list = _dict["week"]
        _number: int = _dict["number"]
        if (D.week not in _week) or (_number == 0):
            continue
        quotient, remainder = divmod(_number, 10)
        for _ in range(quotient):
            # 兑换10个
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=10")
            D.msg_append(D.find())
            if "达到当日兑换上限" in D.html:
                break
            elif "积分不足" in D.html:
                break
        for _ in range(remainder):
            # 兑换1个
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=1")
            D.msg_append(D.find())
            if "达到当日兑换上限" in D.html:
                break
            elif "积分不足" in D.html:
                break

    if D.week in [1, 2]:
        # 组队报名
        D.get("cmd=secttournament&op=signup")
        D.msg_append(D.find())
        # 领取奖励
        D.get("cmd=secttournament&op=getrankandrankingreward")
        D.msg_append(D.find())
        return

    for _ in range(10):
        # 开始挑战
        D.get("cmd=secttournament&op=fight")
        D.msg_append(D.find())
        if "已达最大挑战上限" in D.html:
            break
        elif "门派战书不足" in D.html:
            break


def 会武():
    """
    周一、二、三初、中、高级试炼场挑战至多21次
    周四助威丐帮
    周六、日领奖
    商店兑换详见yaml配置文件
    """
    _yaml: dict[int, dict] = D.yaml["会武"]

    # 会武商店兑换
    for _id, _dict in _yaml.items():
        _week: list = _dict["week"]
        _number: int = _dict["number"]
        if (D.week not in _week) or (_number == 0):
            continue
        quotient, remainder = divmod(_number, 10)
        for _ in range(quotient):
            # 兑换10个
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=10")
            D.msg_append(D.find())
            if "达到当日兑换上限" in D.html:
                break
            elif "积分不足" in D.html:
                break
        for _ in range(remainder):
            # 兑换1个
            D.get(f"cmd=exchange&subtype=2&type={_id}&times=1")
            D.msg_append(D.find())
            if "达到当日兑换上限" in D.html:
                break
            elif "积分不足" in D.html:
                break

    if D.week in [1, 2, 3]:
        for _ in range(21):
            # 挑战
            D.get("cmd=sectmelee&op=dotraining")
            if "试炼场】" in D.html:
                D.msg_append(D.find(r"最高伤害：\d+<br />(.*?)<br />"))
                continue
            D.msg_append(D.find(r"规则</a><br />(.*?)<br />"))
            if "你已达今日挑战上限" in D.html:
                break
            elif "你的试炼书不足" in D.html:
                break
    elif D.week == 4:
        # 冠军助威 丐帮
        D.get("cmd=sectmelee&op=cheer&sect=1003")
        # 冠军助威
        D.get("cmd=sectmelee&op=showcheer")
        D.msg_append(D.find())
    elif D.week in [6, 7]:
        # 领奖
        D.get("cmd=sectmelee&op=showreward")
        D.msg_append(D.find(r"<br />(.*?)。"))
        D.msg_append(D.find(r"。<br />(.*?)。"))
        # 领取
        D.get("cmd=sectmelee&op=drawreward")
        if "本届已领取奖励" in D.html:
            D.msg_append(D.find(r"规则</a><br />(.*?)<br />"))
        else:
            D.msg_append(D.find())


def 梦想之旅():
    """
    每天一次普通旅行
    周四如果当前区域已去过至少7个目的地，那么消耗梦幻机票解锁剩下所有未去过的目的地
    周四领取区域礼包、超级礼包
    """
    # 普通旅行
    D.get("cmd=dreamtrip&sub=2")
    D.msg_append(D.find())

    if D.week != 4:
        return

    if (count := D.html.count("已去过")) < 7:
        _msg = f"已去过 {count} （大于等于7才会消耗梦幻机票）"
        D.print_info(_msg)
        D.msg_append(_msg)
        return

    # 获取当前区域所有未去过的目的地
    place = D.findall(r"([\u4e00-\u9fa5\s\-]+)(?=\s未去过)")
    if not place:
        D.print_info("当前区域全部已去过")
        D.msg_append("当前区域全部已去过")
    else:
        bmapid = D.find(r'bmapid=(\d+)">梦幻旅行')
    for name in place:
        # 梦幻旅行
        D.get(f"cmd=dreamtrip&sub=3&bmapid={bmapid}")
        s = D.find(rf"{name}.*?smapid=(\d+)")
        # 去这里
        D.get(f"cmd=dreamtrip&sub=2&smapid={s}")
        D.msg_append(D.find())

    # 领取礼包
    for _ in range(2):
        if b := D.findall(r"sub=4&amp;bmapid=(\d+)"):
            # 区域礼包 1 or 2 or 3 or 4
            # 超级礼包 0
            D.get(f"cmd=dreamtrip&sub=4&bmapid={b[0]}")
            D.msg_append(D.find())


def 问鼎天下():
    """
    周一领取奖励
    周一、二、三、四、五领取帮资或放弃资源点、东海攻占倒数第一个
    周六淘汰赛助威yaml配置的帮派
    周日排名赛助威yaml配置的帮派
    """
    if D.week == 6:
        # 淘汰赛助威
        _id = D.yaml["问鼎天下"]["淘汰赛"]
        D.get(f"cmd=tbattle&op=cheerregionbattle&id={_id}")
        D.msg_append(D.find())
    elif D.week == 7:
        # 排名赛助威
        _id = D.yaml["问鼎天下"]["排名赛"]
        D.get(f"cmd=tbattle&op=cheerchampionbattle&id={_id}")
        D.msg_append(D.find())

    if D.week in [6, 7]:
        return

    if D.week == 1:
        # 领取奖励
        D.get("cmd=tbattle&op=drawreward")
        D.msg_append(D.find())

    # 问鼎天下
    D.get("cmd=tbattle")
    if "你占领的领地已经枯竭" in D.html:
        # 领取
        D.get("cmd=tbattle&op=drawreleasereward")
        D.msg_append(D.find())
    elif "放弃" in D.html:
        # 放弃
        D.get("cmd=tbattle&op=abandon")
        D.msg_append(D.find())

    # 1东海 2南荒 3西泽 4北寒
    D.get("cmd=tbattle&op=showregion&region=1")
    # 攻占 倒数第一个
    if _id := D.findall(r"id=(\d+).*?攻占</a>"):
        D.get(f"cmd=tbattle&op=occupy&id={_id[-1]}&region=1")
        D.msg_append(D.find())


def 帮派商会():
    """
    每天帮派宝库领取礼包、交易会所交易物品、兑换商店兑换物品
    """
    _yaml: dict = D.yaml["帮派商会"]
    jiaoyi = _yaml["交易会所"]
    duihuan = _yaml["兑换商店"]
    data_1 = []
    data_2 = []

    for _ in range(10):
        # 帮派宝库
        D.get("cmd=fac_corp&op=0")
        if mode := D.findall(r'gift_id=(\d+)&amp;type=(\d+)">点击领取'):
            for _id, t in mode:
                D.get(f"cmd=fac_corp&op=3&gift_id={_id}&type={t}")
                D.msg_append(D.find(r"</p>(.*?)<br />", "帮派商会-帮派宝库"))
        else:
            D.print_info("没有礼包领取", "帮派商会-帮派宝库")
            D.msg_append("没有礼包领取")
            break

    # 交易会所
    D.get("cmd=fac_corp&op=1")
    if "已交易" not in D.html:
        for mode in jiaoyi:
            data_1 += D.findall(rf"{mode}.*?type=(\d+)&amp;goods_id=(\d+)")
        for t, _id in data_1:
            # 兑换
            D.get(f"cmd=fac_corp&op=4&type={t}&goods_id={_id}")
            D.msg_append(D.find(r"</p>(.*?)<br />", f"帮派商会-交易-{_id}"))

    # 兑换商店
    D.get("cmd=fac_corp&op=2")
    if "已兑换" not in D.html:
        for mode in duihuan:
            data_2 += D.findall(rf"{mode}.*?type_id=(\d+)")
        for t in data_2:
            D.get(f"cmd=fac_corp&op=5&type_id={t}")
            D.msg_append(D.find(r"</p>(.*?)<br />", f"帮派商会-兑换-{t}"))


def 帮派远征军():
    """
    周一、二、三、四、五、六、日参战攻击
    周日领取奖励
    """

    def attack(p: str, u: str) -> bool:
        # 攻击
        D.get(f"cmd=factionarmy&op=fightWithUsr&point_id={p}&opp_uin={u}")
        if "【帮派远征军-征战结束】" in D.html:
            _msg = D.find()
            if "您未能战胜" in D.html:
                D.msg_append(_msg)
                return True
        elif "【帮派远征军】" in D.html:
            D.msg_append(D.find(r"<br /><br />(.*?)</p>"))
            if "您的血量不足" in D.html:
                return True
        return False

    _end = False
    while True:
        # 帮派远征军
        D.get("cmd=factionarmy&op=viewIndex&island_id=-1")
        point_id = D.findall(r'point_id=(\d+)">参战')
        if not point_id:
            D.print_info("已经全部通关了，周日领取奖励")
            D.msg_append("已经全部通关了，周日领取奖励")
            break
        for p in point_id:
            # 参战
            D.get(f"cmd=factionarmy&op=viewpoint&point_id={p}")
            for u in D.findall(r'opp_uin=(\d+)">攻击'):
                if attack(p, u):
                    _end = True
                    break
        if _end:
            break

    if D.week != 7:
        return

    # 领取奖励
    for p_id in range(15):
        D.get(f"cmd=factionarmy&op=getPointAward&point_id={p_id}")
        if "【帮派远征军】" in D.html:
            D.msg_append(D.find(r"<br /><br />(.*?)</p>"))
            if "点尚未攻占下来" in D.html:
                break
            continue
        D.msg_append(D.find())

    # 领取岛屿宝箱
    for i_id in range(5):
        D.get(f"cmd=factionarmy&op=getIslandAward&island_id={i_id}")
        if "【帮派远征军】" in D.html:
            D.msg_append(D.find(r"<br /><br />(.*?)</p>"))
            if "岛尚未攻占下来" in D.html:
                break
            continue
        D.msg_append(D.find())


def 帮派黄金联赛():
    """
    领取奖励、领取帮派赛季奖励、参与防守、参战攻击
    """
    # 帮派黄金联赛
    D.get("cmd=factionleague&op=0")
    if "领取奖励" in D.html:
        # 领取轮次奖励
        D.get("cmd=factionleague&op=5")
        D.msg_append(D.find(r"<p>(.*?)<br /><br />"))
    elif "领取帮派赛季奖励" in D.html:
        # 领取帮派赛季奖励
        D.get("cmd=factionleague&op=7")
        D.msg_append(D.find(r"<p>(.*?)<br /><br />"))
    elif "已参与防守" not in D.html:
        # 参与防守
        D.get("cmd=factionleague&op=1")
        D.msg_append(D.find(r"<p>(.*?)<br /><br />"))
    elif "休赛期" in D.html:
        D.print_info("休赛期无任何操作")
        D.msg_append("休赛期无任何操作")

    if "op=2" not in D.html:
        return

    # 参战
    D.get("cmd=factionleague&op=2")
    if "opp_uin" not in D.html:
        D.print_info("没有可攻击的敌人")
        D.msg_append("没有可攻击的敌人")
        return

    uin = []
    if pages := D.find(r'pages=(\d+)">末页'):
        _pages = pages
    else:
        _pages = 1
    for p in range(1, int(_pages) + 1):
        D.get(f"cmd=factionleague&op=2&pages={p}")
        uin += D.findall(r"%&nbsp;&nbsp;(\d+).*?opp_uin=(\d+)")

    # 按战力从低到高排序
    uins = sorted(uin, key=lambda x: float(x[0]))
    for _, u in uins:
        # 攻击
        D.get(f"cmd=factionleague&op=4&opp_uin={u}")
        if "不幸战败" in D.html:
            D.msg_append(D.find())
            break
        elif "您已阵亡" in D.html:
            D.msg_append(D.find(r"<br /><br />(.*?)</p>"))
            break
        D.find()


def 任务派遣中心():
    """
    每天领取奖励、接受任务
    """
    # 任务派遣中心
    D.get("cmd=missionassign&subtype=0")
    for _id in D.findall(r'mission_id=(.*?)">查看'):
        # 领取奖励
        D.get(f"cmd=missionassign&subtype=5&mission_id={_id}")
        D.msg_append(D.find(r"\[任务派遣中心\](.*?)<br />"))

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
    for _msg in D.findall(r"<br />(.*?)&nbsp;<a.*?查看"):
        D.msg_append(_msg)


def 武林盟主():
    """
    周三、五、日领取排行奖励和竞猜奖励
    周一、三、五分站赛报名yaml配置的赛场
    周二、四、六竞猜
    """
    if D.week in [3, 5, 7]:
        # 武林盟主
        D.get("cmd=wlmz&op=view_index")
        if data := D.findall(r'section_id=(\d+)&amp;round_id=(\d+)">'):
            for s, r in data:
                D.get(f"cmd=wlmz&op=get_award&section_id={s}&round_id={r}")
                D.msg_append(D.find(r"<br /><br />(.*?)</p>"))
        else:
            D.print_info("没有可领取的排行奖励和竞猜奖励")
            D.msg_append("没有可领取的排行奖励和竞猜奖励")

    if D.week in [1, 3, 5]:
        g_id: int = D.yaml["武林盟主"]
        D.get(f"cmd=wlmz&op=signup&ground_id={g_id}")
        if "总决赛周不允许报名" in D.html:
            D.msg_append(D.find(r"战报</a><br />(.*?)<br />"))
            return
        D.msg_append(D.find(r"赛场】<br />(.*?)<br />"))
    elif D.week in [2, 4, 6]:
        for index in range(8):
            # 选择
            D.get(f"cmd=wlmz&op=guess_up&index={index}")
            D.find(r"规则</a><br />(.*?)<br />")
        # 确定竞猜选择
        D.get("cmd=wlmz&op=comfirm")
        D.msg_append(D.find(r"战报</a><br />(.*?)<br />"))


def 全民乱斗():
    """
    乱斗竞技任务列表领取、乱斗任务领取
    """
    n = True
    for t in [2, 3, 4]:
        D.get(f"cmd=luandou&op=0&acttype={t}")
        for _id in D.findall(r'.*?id=(\d+)">领取</a>'):
            n = False
            # 领取
            D.get(f"cmd=luandou&op=8&id={_id}")
            D.msg_append(D.find(r"斗】<br /><br />(.*?)<br />"))
    if n:
        D.print_info("没有可领取的")
        D.msg_append("没有可领取的")


def 侠士客栈():
    """
    每天领取奖励3次、客栈奇遇
    """
    # 侠士客栈
    D.get("cmd=warriorinn")
    if t := D.find(r"type=(\d+).*?领取奖励</a>"):
        for n in range(1, 4):
            # 领取奖励
            D.get(f"cmd=warriorinn&op=getlobbyreward&type={t}&num={n}")
            D.msg_append(D.find(r"侠士客栈<br />(.*?)<br />"))

    # 奇遇
    for p in D.findall(r"pos=(\d+)"):
        D.get(f"cmd=warriorinn&op=showAdventure&pos={p}")
        if "前来捣乱的" in D.html:
            # 前来捣乱的xx -> 与TA理论 -> 确认
            D.get(f"cmd=warriorinn&op=exceptadventure&pos={p}")
            if "战斗" in D.html:
                D.msg_append(D.find(r"侠士客栈<br />(.*?) ，"))
                continue
            D.msg_append(D.find(r"侠士客栈<br />(.*?)<br />"))
        else:
            # 黑市商人、老乞丐 -> 你去别人家问问吧、拯救世界的任务还是交给别人把 -> 确认
            D.get(f"cmd=warriorinn&op=rejectadventure&pos={p}")


def 增强经脉():
    """
    每天传功至多12次
    """
    # 关闭传功符不足用斗豆代替
    D.get("cmd=intfmerid&sub=21&doudou=0")
    if "关闭" in D.html:
        # 关闭合成两次确认
        D.get("cmd=intfmerid&sub=19")

    for _ in range(12):
        # 增强经脉
        D.get("cmd=intfmerid&sub=1")
        _id = D.find(r'master_id=(\d+)">传功</a>', "任务-增强经脉")
        # 传功
        D.get(f"cmd=intfmerid&sub=2&master_id={_id}")
        D.find(r"</p>(.*?)<p>", "任务-增强经脉")
        if "传功符不足!" in D.html:
            return

        # 一键拾取
        D.get("cmd=intfmerid&sub=5")
        D.find(r"</p>(.*?)<p>", "任务-增强经脉")
        # 一键合成
        D.get("cmd=intfmerid&sub=10&op=4")
        D.find(r"</p>(.*?)<p>", "任务-增强经脉")


def 助阵():
    """
    无字天书、河洛图书提升3次
    """
    _data = {
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
        for f_id, index_list in _data.items():
            for index in index_list:
                yield (f_id, index)

    n = 0
    for _id, _index in get_id_index():
        if n == 3:
            break
        for _ in range(3):
            # 提升
            D.get(f"cmd=formation&type=4&formationid={_id}&attrindex={_index}&times=1")
            if "助阵组合所需佣兵不满足条件，不能提升助阵属性经验" in D.html:
                D.find(r"<br /><br />(.*?)。", "任务-助阵")
                return
            elif "阅历不足" in D.html:
                D.find(r"<br /><br />(.*?)，", "任务-助阵")
                return

            D.find(name="任务-助阵")
            if "提升成功" in D.html:
                n += 1
            elif "经验值已经达到最大" in D.html:
                break
            elif "你还没有激活该属性" in D.html:
                return


def 查看好友资料():
    """
    查看好友第二页
    """
    # 武林 》设置 》乐斗助手
    D.get("cmd=view&type=6")
    if "开启查看好友信息和收徒" in D.html:
        #  开启查看好友信息和收徒
        D.get("cmd=set&type=1")
    # 查看好友第2页
    D.get("cmd=friendlist&page=2")
    for uin in D.findall(r"\d+：.*?B_UID=(\d+).*?级"):
        D.get(f"cmd=totalinfo&B_UID={uin}")


def 徽章进阶():
    """
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
    """
    for _id in range(1, 34):
        D.get(f"cmd=achievement&op=upgradelevel&achievement_id={_id}&times=1")
        D.find(r";<br />(.*?)<br />", "任务-徽章进阶")
        if "进阶失败" in D.html:
            break
        elif "进阶成功" in D.html:
            break
        elif "物品不足" in D.html:
            break


def 兵法研习():
    """
    兵法      消耗     id       功能
    金兰之泽  孙子兵法  2544     增加生命
    雷霆一击  孙子兵法  2570     增加伤害
    残暴攻势  武穆遗书  21001    增加暴击几率
    不屈意志  武穆遗书  21032    降低受到暴击几率
    """
    for _id in [21001, 2570, 21032, 2544]:
        D.get(f"cmd=brofight&subtype=12&op=practice&baseid={_id}")
        D.find(r"武穆遗书：\d+个<br />(.*?)<br />", "任务-兵法研习")
        if "研习成功" in D.html:
            break


def 挑战陌生人():
    """
    斗友乐斗四次
    """
    # 斗友
    D.get("cmd=friendlist&type=1")
    uin = D.findall(r"：.*?级.*?B_UID=(\d+).*?乐斗</a>")
    if not uin:
        D.print_info("未找到斗友")
        return

    for u in uin[:4]:
        # 乐斗
        D.get(f"cmd=fight&B_UID={u}&page=1&type=9")
        D.find(r"删</a><br />(.*?)！", "任务-挑战陌生人")


def 任务():
    """
    增强经脉、助阵每天必做
    """
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
        D.msg_append(f"{k} {v}")


def 我的帮派():
    """
    每天供奉5次、帮派任务至多领取奖励3次
    周日领取奖励、报名帮派战争、激活祝福
    """
    # 我的帮派
    D.get("cmd=factionop&subtype=3&facid=0")
    if "你的职位" not in D.html:
        D.print_info("您还没有加入帮派")
        D.msg_append("您还没有加入帮派")
        return

    _yaml: list = D.yaml["我的帮派"]
    for _id in _yaml:
        for _ in range(5):
            # 供奉
            D.get(f"cmd=oblation&id={_id}&page=1")
            if "供奉成功" in D.html:
                D.msg_append(D.find())
                continue
            D.find(r"】</p><p>(.*?)<br />")
            break
        if "每天最多供奉5次" in D.html:
            break

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
            D.print_info(name)
            D.get(url)
    if "帮派修炼" in faction_missions:
        n = 0
        for _id in [2727, 2758, 2505, 2536, 2437, 2442, 2377, 2399, 2429]:
            for _ in range(4):
                # 修炼
                D.get(f"cmd=factiontrain&type=2&id={_id}&num=1&i_p_w=num%7C")
                D.find(r"规则说明</a><br />(.*?)<br />")
                if "技能经验增加" in D.html:
                    n += 1
                    continue
                # 帮贡不足
                # 你今天获得技能升级经验已达到最大！
                # 你需要提升帮派等级来让你进行下一步的修炼
                break
            if n == 4:
                break
    # 帮派任务
    D.get("cmd=factiontask&sub=1")
    for _id in D.findall(r'id=(\d+)">领取奖励</a>'):
        # 领取奖励
        D.get(f"cmd=factiontask&sub=3&id={_id}")
        D.msg_append(D.find(r"日常任务</a><br />(.*?)<br />"))

    if D.week != 7:
        return

    # 周日 领取奖励 》报名帮派战争 》激活祝福
    for sub in [4, 9, 6]:
        D.get(f"cmd=facwar&sub={sub}")
        D.msg_append(D.find(r"</p>(.*?)<br /><a.*?查看上届"))


def 帮派祭坛():
    """
    每天转动轮盘至多30次、领取通关奖励
    """
    # 帮派祭坛
    D.get("cmd=altar")
    for _ in range(30):
        if "【祭坛轮盘】" in D.html:
            # 转动轮盘
            D.get("cmd=altar&op=spinwheel")
            if "【祭坛轮盘】" in D.html:
                D.msg_append(D.find())
            if "转转券不足" in D.html:
                break
            elif "已达转转券转动次数上限" in D.html:
                break
        if "【随机分配】" in D.html:
            for op, _id in D.findall(r"op=(.*?)&amp;id=(\d+)"):
                # 选择
                D.get(f"cmd=altar&op={op}&id={_id}")
                if "选择路线" in D.html:
                    # 选择路线
                    D.get(f"cmd=altar&op=dosteal&id={_id}")
                if "【随机分配】" in D.html:
                    # 该帮派已解散，无法操作！
                    # 系统繁忙
                    D.find(r"<br /><br />(.*?)<br />")
                    continue
                if "【祭坛轮盘】" in D.html:
                    D.msg_append(D.find())
                    break
        if "领取奖励" in D.html:
            D.get("cmd=altar&op=drawreward")
            D.msg_append(D.find())


def 飞升大作战():
    """
    每天兑换玄铁令*1、优先报名单排模式，玄铁令不足或者休赛期时选择匹配模式
    周四领取赛季结束奖励
    """
    # 兑换 玄铁令*1
    D.get("cmd=ascendheaven&op=exchange&id=2&times=1")
    D.msg_append(D.find())

    # 报名单排模式
    D.get("cmd=ascendheaven&op=signup&type=1")
    D.msg_append(D.find())
    if "时势造英雄" not in D.html:
        # 当前为休赛期，不在报名时间、还没有入场券玄铁令、你已经报名参赛
        # 报名匹配模式
        D.get("cmd=ascendheaven&op=signup&type=2")
        D.msg_append(D.find())

    if (D.week != 4) or ("赛季结算中" not in D.html):
        return

    # 境界修为
    D.get("cmd=ascendheaven&op=showrealm")
    for s in D.findall(r"season=(\d+)"):
        # 领取奖励
        D.get(f"cmd=ascendheaven&op=getrealmgift&season={s}")
        D.msg_append(D.find())


def 深渊之潮():
    """
    每天帮派巡礼领取巡游赠礼、深渊秘境至多挑战3次，yaml配置关卡
    """
    _id: int = D.yaml["深渊之潮"]

    # 领取巡游赠礼
    D.get("cmd=abysstide&op=getfactiongift")
    D.msg_append(D.find())

    for _ in range(5):
        D.get(f"cmd=abysstide&op=enterabyss&id={_id}")
        if "开始挑战" not in D.html:
            # 暂无可用挑战次数
            # 该副本需要顺序通关解锁
            D.msg_append(D.find())
            break

        for _ in range(5):
            # 开始挑战
            D.get("cmd=abysstide&op=beginfight")
            D.find()
            if "憾负于" in D.html:
                break

        # 退出副本
        D.get("cmd=abysstide&op=endabyss")
        D.msg_append(D.find())


def 每日奖励():
    """
    每天领取4次
    """
    for key in ["login", "meridian", "daren", "wuzitianshu"]:
        # 每日奖励
        D.get(f"cmd=dailygift&op=draw&key={key}")
        D.msg_append(D.find())


def 领取徒弟经验():
    """
    每天一次
    """
    # 领取徒弟经验
    D.get("cmd=exp")
    D.msg_append(D.find(r"每日奖励</a><br />(.*?)<br />"))


def 今日活跃度():
    """
    每天领取活跃度礼包、帮派总活跃礼包
    """
    # 今日活跃度
    D.get("cmd=liveness")
    D.msg_append(D.find(r"【(.*?)】"))
    if "帮派总活跃" in D.html:
        D.msg_append(D.find(r"礼包</a><br />(.*?)<"))

    # 领取今日活跃度礼包
    for giftbag_id in range(1, 5):
        D.get(f"cmd=liveness_getgiftbag&giftbagid={giftbag_id}&action=1")
        D.msg_append(D.find(r"】<br />(.*?)<p>"))

    # 领取帮派总活跃奖励
    D.get("cmd=factionop&subtype=18")
    if "创建帮派" in D.html:
        D.msg_append(D.find(r"帮派</a><br />(.*?)<br />"))
    else:
        D.msg_append(D.find())


def 仙武修真():
    """
    每天领取3次任务、寻访长留山挑战至多5次
    """
    for task_id in range(1, 4):
        # 领取
        D.get(f"cmd=immortals&op=getreward&taskid={task_id}")
        D.msg_append(D.find(r"帮助</a><br />(.*?)<br />"))

    for _ in range(5):
        # 寻访 长留山
        D.get("cmd=immortals&op=visitimmortals&mountainId=1")
        _msg = D.find(r"帮助</a><br />(.*?)<br />")
        if "你的今日寻访挑战次数已用光" in D.html:
            D.msg_append(_msg)
            break
        # 挑战
        D.get("cmd=immortals&op=fightimmortals")
        D.msg_append(D.find(r"帮助</a><br />(.*?)<a"))


def 大侠回归三重好礼():
    """
    周四领取奖励
    """
    # 大侠回归三重好礼
    D.get("cmd=newAct&subtype=173&op=1")
    if _data := D.findall(r"subtype=(\d+).*?taskid=(\d+)"):
        for s, t in _data:
            # 领取
            D.get(f"cmd=newAct&subtype={s}&op=2&taskid={t}")
            D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))
    else:
        D.print_info("没有可领取的奖励")
        D.msg_append("没有可领取的奖励")


def 乐斗黄历():
    """
    每天占卜一次
    """
    # 乐斗黄历
    D.get("cmd=calender&op=0")
    D.msg_append(D.find(r"今日任务：(.*?)<br />"))
    # 领取
    D.get("cmd=calender&op=2")
    D.msg_append(D.find(r"<br /><br />(.*?)<br />"))
    if "任务未完成" in D.html:
        return
    # 占卜
    D.get("cmd=calender&op=4")
    D.msg_append(D.find(r"<br /><br />(.*?)<br />"))


def 器魂附魔():
    """
    附魔任务领取（50、80、115）
    """
    # 器魂附魔
    D.get("cmd=enchant")
    for task_id in range(1, 4):
        # 领取
        D.get(f"cmd=enchant&op=gettaskreward&task_id={task_id}")
        D.msg_append(D.find())


def 侠客岛():
    """
    侠客行接受任务、领取奖励至多3次，刷新至多4次（即免费次数为0时不再刷新）
    第一轮及第二轮均执行
    """
    count: str = "4"
    mission_success: bool = False
    # 侠客行
    D.get("cmd=knight_island&op=viewmissionindex")
    for _ in range(4):
        view_mission_detail_pos = D.findall(r"viewmissiondetail&amp;pos=(\d+)")
        if not view_mission_detail_pos:
            break
        for p in view_mission_detail_pos:
            # 接受
            D.get(f"cmd=knight_island&op=viewmissiondetail&pos={p}")
            mission_name = D.find(r"侠客行<br /><br />(.*?)（", "侠客行-任务名称")
            # 快速委派
            D.get(f"cmd=knight_island&op=autoassign&pos={p}")
            D.find(r"）<br />(.*?)<br />", f"侠客行-{mission_name}")
            if "快速委派成功" in D.html:
                mission_success = True
                # 开始任务
                D.get(f"cmd=knight_island&op=begin&pos={p}")
                _html = D.find(r"斗豆）<br />(.*?)<br />", f"侠客行-{mission_name}")
                D.msg_append(f"{mission_name}：{_html}")
            elif "符合条件侠士数量不足" in D.html:
                # 侠客行
                D.get("cmd=knight_island&op=viewmissionindex")
                # 免费刷新次数
                count = D.find(r"剩余：(\d+)次", "侠客行-免费刷新次数")
                if count != "0":
                    # 刷新
                    D.get(f"cmd=knight_island&op=refreshmission&pos={p}")
                    D.find(r"斗豆）<br />(.*?)<br />", f"侠客行-{mission_name}")
                else:
                    D.print_info("没有免费次数，取消刷新", f"侠客行-{mission_name}")

        if count == "0":
            break

    # 领取任务奖励
    for p2 in D.findall(r"getmissionreward&amp;pos=(\d+)"):
        mission_success = True
        # 领取
        D.get(f"cmd=knight_island&op=getmissionreward&pos={p2}")
        D.msg_append(D.find(r"斗豆）<br />(.*?)<br />"))

    if not mission_success:
        D.msg_append("没有可接受或可领取的任务（符合条件侠士数量不足、执行中、已完成）")


def 八卦迷阵():
    """
    根据首通提示通关并领取奖励
    """
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
        D.print_info("首通没有八卦提示", "时空遗迹-八卦迷阵")
        D.msg_append("首通没有八卦提示")
        return

    for i in result:
        # 点击八卦
        D.get(f"cmd=spacerelic&op=goosip&id={_data[i]}")
        D.msg_append(D.find(r"分钟<br /><br />(.*?)<br />", "时空遗迹-八卦迷阵"))
        if "恭喜您" not in D.html:
            # 你被迷阵xx击败，停留在了本层
            # 耐力不足，无法闯关
            # 你被此门上附着的阵法传送回了第一层
            # 请遵循迷阵规则进行闯关
            break
        # 恭喜您进入到下一层
        # 恭喜您已通关迷阵，快去领取奖励吧

    if "恭喜您已通关迷阵" in D.html:
        # 领取通关奖励
        D.get("cmd=spacerelic&op=goosipgift")
        D.msg_append(D.find(r"分钟<br /><br />(.*?)<br />", "时空遗迹-八卦迷阵"))


def 遗迹商店():
    """
    遗迹征伐-遗迹商店特惠区兑换，只能10的倍数兑换
    """
    _yaml: dict = D.yaml["时空遗迹"]

    n = 0
    for k, _dict in _yaml.items():
        name: str = _dict["name"]
        number: int = _dict["number"]
        number, _ = divmod(number, 10)
        for _ in range(number):
            D.get(f"cmd=spacerelic&op=buy&type=1&id={k}&num=10")
            D.find(
                r"售卖区</a><br /><br /><br />(.*?)<",
                f"时空遗迹-遗迹商店-{name}",
            )
            if "兑换成功" in D.html:
                n += 10
            elif "上限" in D.html:
                break
            elif "积分不足" in D.html:
                break
        D.msg_append(f"{name}兑换*{n}")

    # 遗迹商店积分
    D.msg_append(D.find(r"规则</a><br />(.*?)<br />", "时空遗迹-遗迹商店"))


def 遗迹征伐():
    """
    第七周的最后一个周三（含）之前：
        异兽洞窟：按照异兽母巢到异兽幼崽顺序优先扫荡，否则挑战
        联合征伐：每天挑战一次
        悬赏任务：每天领取
    第八周：
        赛季排行：每天领取一次排行奖励
        遗迹商店：每天特惠区兑换，详见yaml配置文件
    """
    # 遗迹征伐
    D.get("cmd=spacerelic&op=relicindex")
    # 赛季结束年
    _year = D.find(r"(\d+)年", "时空遗迹-遗迹征伐-结束年")
    # 赛季结束月
    _month = D.find(r"(\d+)月", "时空遗迹-遗迹征伐-结束月")
    # 赛季结束日
    _day = D.find(r"(\d+)日", "时空遗迹-遗迹征伐-结束日")

    end_date = datetime(int(_year), int(_month), int(_day))
    # 计算第七周的最后一天（周三），即结束日期的前8天
    seventh_week_last_day = (end_date - timedelta(days=8)).date()
    # 获取当前日期
    current_date = datetime.now().date()

    # 判断当前日期是否在第八周
    if current_date > seventh_week_last_day:
        # 排行奖励
        D.get("cmd=spacerelic&op=getrank")
        D.msg_append(D.find(r"奖励</a><br /><br />(.*?)<", "时空遗迹-赛季排行"))

        遗迹商店()
        return

    # 异兽洞窟挑战
    for _id in [5, 4, 3, 2, 1]:
        # 异兽幼崽 1
        # 异兽战士 2
        # 异兽将领 3
        # 异兽元帅 4
        # 异兽母巢 5
        D.get(f"cmd=spacerelic&op=monsterdetail&id={_id}")
        if "剩余挑战次数：0" in D.html:
            D.print_info("没有挑战次数", "时空遗迹-异兽洞窟")
            D.msg_append("异兽洞窟没有挑战次数")
            break
        if "剩余血量：0" in D.html:
            # 扫荡
            D.get(f"cmd=spacerelic&op=saodang&id={_id}")
        else:
            # 挑战
            D.get(f"cmd=spacerelic&op=monsterfight&id={_id}")
        msg = D.find(r"次数.*?<br /><br />(.*?)&", "时空遗迹-异兽洞窟")
        if "请按顺序挑战异兽" in D.html:
            continue
        D.msg_append(msg)

    # 联合征伐挑战
    D.get("cmd=spacerelic&op=bossfight")
    D.msg_append(D.find(r"挑战</a><br />(.*?)&", "时空遗迹-联合征伐"))

    # 悬赏任务
    data = []
    for t in [1, 2]:
        D.get(f"cmd=spacerelic&op=task&type={t}")
        data += D.findall(r"type=(\d+)&amp;id=(\d+)")
    if not data:
        D.print_info("没有礼包可领取", "时空遗迹-悬赏任务")
        D.msg_append("没有礼包可领取")
    for t, _id in data:
        D.get(f"cmd=spacerelic&op=task&type={t}&id={_id}")
        D.msg_append(D.find(r"赛季任务</a><br /><br />(.*?)<", "时空遗迹-悬赏任务"))


def 时空遗迹():
    """
    八卦迷阵、遗迹征伐
    """
    八卦迷阵()
    遗迹征伐()


def 兵法():
    """
    周四随机助威
    周六领奖、领取斗币
    """
    if D.week == 4:
        # 助威
        D.get("cmd=brofight&subtype=13")
        if teamid := D.findall(r".*?teamid=(\d+).*?助威</a>"):
            t = random.choice(teamid)
            # 确定
            D.get(f"cmd=brofight&subtype=13&teamid={t}&type=5&op=cheer")
            D.msg_append(D.find(r"领奖</a><br />(.*?)<br />"))

    if D.week != 6:
        return

    # 兵法 -> 助威 -> 领奖
    D.get("cmd=brofight&subtype=13&op=draw")
    D.msg_append(D.find(r"领奖</a><br />(.*?)<br />"))

    for t in range(1, 6):
        D.get(f"cmd=brofight&subtype=10&type={t}")
        for n, u in D.findall(r"50000.*?(\d+).*?champion_uin=(\d+)"):
            if n == "0":
                continue
            # 领斗币
            D.get(f"cmd=brofight&subtype=10&op=draw&champion_uin={u}&type={t}")
            D.msg_append(D.find(r"排行</a><br />(.*?)<br />"))
            return


def 背包():
    """
    背包物品使用，yaml配置选择物品
    """
    _yaml: list = D.yaml["背包"]
    data = []

    # 背包
    D.get("cmd=store&store_type=0")
    page = D.find(r"第1/(\d+)")
    if page is None:
        D.print_info("背包未找到页码")
        D.msg_append("背包未找到页码")
        return

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

    id_number = []
    for _id in data:
        # 物品详情
        D.get(f"cmd=owngoods&id={_id}")
        if "很抱歉" in D.html:
            D.find(r"】</p><p>(.*?)<br />", f"背包-{_id}-不存在")
        else:
            number = D.find(r"数量：(\d+)", f"背包-{_id}-数量")
            id_number.append((str(_id), int(number)))

    for _id, number in set(id_number):
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

    for e in range(2000, 2007):
        for _ in range(50):
            # 魂珠碎片 -> 1
            D.get(f"cmd=upgradepearl&type=6&exchangetype={e}")
            _msg = D.find(r"魂珠升级</p><p>(.*?)</p>")
            if "不能合成该物品" in D.html:
                # 抱歉，您的xx魂珠碎片不足，不能合成该物品！
                break
            D.msg_append(_msg)

    for p in get_p():
        for _ in range(50):
            # 1 -> 2 -> 3 -> 4
            D.get(f"cmd=upgradepearl&type=3&pearl_id={p}")
            _msg = D.find(r"魂珠升级</p><p>(.*?)<")
            if "您拥有的魂珠数量不够" in D.html:
                break
            D.msg_append(_msg)


def 神匠坊():
    """
    周四普通合成、符石分解（默认仅I类）、符石打造
    """
    _yaml: list[int] = D.yaml["神匠坊"]
    data_1 = []
    data_2 = []

    # 背包
    for p in range(1, 20):
        D.print_info(f"背包第 {p} 页")
        # 下一页
        D.get(f"cmd=weapongod&sub=12&stone_type=0&quality=0&page={p}")
        data_1 += D.findall(r"拥有：(\d+)/(\d+).*?stone_id=(\d+)")
        if "下一页" not in D.html:
            break
    for possess, number, _id in data_1:
        if int(possess) < int(number):
            # 符石碎片不足
            continue
        count = int(int(possess) / int(number))
        for _ in range(count):
            # 普通合成
            D.get(f"cmd=weapongod&sub=13&stone_id={_id}")
            D.msg_append(D.find(r"背包<br /></p>(.*?)!"))

    # 符石分解
    for p in range(1, 10):
        D.print_info(f"符石分解第 {p} 页")
        # 下一页
        D.get(f"cmd=weapongod&sub=9&stone_type=0&page={p}")
        data_2 += D.findall(r"数量:(\d+).*?stone_id=(\d+)")
        if "下一页" not in D.html:
            break
    for num, _id in data_2:
        if int(_id) not in _yaml:
            continue
        # 分解
        D.get(f"cmd=weapongod&sub=11&stone_id={_id}&num={num}&i_p_w=num%7C")
        D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))

    # 符石打造
    # 符石
    D.get("cmd=weapongod&sub=7")
    if _number := D.find(r"符石水晶：(\d+)"):
        quotient, remainder = divmod(int(_number), 60)
        for _ in range(quotient):
            # 打造十次
            D.get("cmd=weapongod&sub=8&produce_type=1&times=10")
            D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))
        for _ in range(int(remainder / 6)):
            # 打造一次
            D.get("cmd=weapongod&sub=8&produce_type=1&times=1")
            D.msg_append(D.find(r"背包</a><br /></p>(.*?)<"))


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
            D.print_info("猜单双已经做过了")
            D.msg_append("猜单双已经做过了")
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


def 万圣节():
    """
    点亮南瓜灯
    活动截止日的前一天优先兑换礼包B，最后兑换礼包A
    """
    # 点亮南瓜灯
    D.get("cmd=hallowmas&gb_id=1")
    while True:
        if cushaw_id := D.findall(r"cushaw_id=(\d+)"):
            c_id = random.choice(cushaw_id)
            # 南瓜
            D.get(f"cmd=hallowmas&gb_id=4&cushaw_id={c_id}")
            D.msg_append(D.find())
        # 恭喜您获得10体力和南瓜灯一个！
        # 恭喜您获得20体力和南瓜灯一个！南瓜灯已刷新
        # 请领取今日的活跃度礼包来获得蜡烛吧！
        if "请领取今日的活跃度礼包来获得蜡烛吧" in D.html:
            break

    # 兑换奖励
    D.get("cmd=hallowmas&gb_id=0")
    day: str = D.find(r"至\d+月(\d+)日")
    if D.day != (int(day) - 1):
        return

    number: str = D.find(r"南瓜灯：(\d+)个")
    number_int = int(number)
    b = number_int // 40
    a = (number_int - b * 40) // 20
    for _ in range(int(b)):
        # 兑换礼包B 消耗40个南瓜灯
        D.get("cmd=hallowmas&gb_id=6")
        D.msg_append(D.find())
    for _ in range(int(a)):
        # 兑换礼包A 消耗20个南瓜灯
        D.get("cmd=hallowmas&gb_id=5")
        D.msg_append(D.find())


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


def 生肖福卡():
    """
    集卡：
        好友赠卡：领取好友赠卡
        分享：向好友分享一次福卡（选择数量最多的，如果数量最大值为1则不分享）
        领取：领取
    兑奖：
        周四合成周年福卡、分斗豆
    抽奖：
        周四抽奖：
            已合成周年福卡则抽奖
            已过合卡时间则继续抽奖
    """
    # 好友赠卡
    D.get("cmd=newAct&subtype=174&op=4")
    for name, qq, card_id in D.findall(r"送您(.*?)\*.*?oppuin=(\d+).*?id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=174&op=6&oppuin={qq}&card_id={card_id}")
        D.find(name=f"生肖福卡-{name}")
        D.msg_append(f"好友赠卡：{name}")

    # 分享福卡
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    if qq := D.yaml["生肖福卡"]:
        pattern = "[子丑寅卯辰巳午未申酉戌亥][鼠牛虎兔龙蛇马羊猴鸡狗猪]"
        data = D.findall(rf"({pattern})\s+(\d+).*?id=(\d+)")
        name, max_number, card_id = max(data, key=lambda x: int(x[1]))
        if int(max_number) >= 2:
            # 分享福卡
            D.get(
                f"cmd=newAct&subtype=174&op=5&oppuin={qq}&card_id={card_id}&confirm=1"
            )
            D.msg_append(D.find(r"~<br /><br />(.*?)<br />", f"生肖福卡-{name}福卡"))
        else:
            D.print_info("你的福卡数量不足2", "生肖福卡-取消分享")
            D.msg_append("你的福卡数量不足2")

    # 领取
    # 生肖福卡
    D.get("cmd=newAct&subtype=174")
    for task_id in D.findall(r"task_id=(\d+)"):
        # 领取
        D.get(f"cmd=newAct&subtype=174&op=7&task_id={task_id}")
        D.msg_append(D.find(r"~<br /><br />(.*?)<br />", "生肖福卡-集卡"))

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
    领取签到奖励
    活动截止日的前一天领取奖励金
    """
    # 双节签到
    D.get("cmd=newAct&subtype=144")
    day: str = D.find(r"至\d+月(\d+)日")
    if "op=1" in D.html:
        # 领取
        D.get("cmd=newAct&subtype=144&op=1")
        D.msg_append(D.find())
    if D.day == (int(day) - 1):
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
    """
    砸金蛋
    """
    # 幸运金蛋
    D.get("cmd=newAct&subtype=110&op=0")
    if index := D.find(r"index=(\d+)"):
        # 砸金蛋
        D.get(f"cmd=newAct&subtype=110&op=1&index={index}")
        D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))
    else:
        D.print_info("没有可砸蛋")
        D.msg_append("没有可砸蛋")


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
        "卯门生紫气": "兔岁报新春",
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
    第一轮赠礼三个随机礼物
    第二轮收取礼物
    """
    # 新春拜年
    D.get("cmd=newAct&subtype=147")
    if "op=1" in D.html:
        for index in random.sample(range(5), 3):
            # 选中
            D.get(f"cmd=newAct&subtype=147&op=1&index={index}")
        # 赠礼
        D.get("cmd=newAct&subtype=147&op=2")
        D.msg_append("已赠礼")
    elif "op=3" in D.html:
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


def 企鹅吉利兑():
    """
    每天领取、活动截止日的前一天兑换材料（每种至多兑换100次）
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

    day: str = D.find(r"至\d+月(\d+)日")
    if D.day != (int(day) - 1):
        return

    _yaml: list = D.yaml["企鹅吉利兑"]
    for _id in _yaml:
        for _ in range(100):
            D.get(f"cmd=geelyexchange&op=ExchangeProps&id={_id}")
            if "你的精魄不足，快去完成任务吧~" in D.html:
                break
            elif "该物品已达兑换上限~" in D.html:
                break
            D.msg_append(D.find(r"】<br /><br />(.*?)<br />"))
        if "当前精魄：0" in D.html:
            break


def 乐斗大笨钟():
    """
    领取一次
    """
    # 领取
    D.get("cmd=newAct&subtype=18")
    D.msg_append(D.find(r"<br /><br /><br />(.*?)<br />"))


def 乐斗回忆录():
    """
    周四领取回忆礼包
    """
    for _id in [1, 3, 5, 7, 9]:
        # 回忆礼包
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


class ShenZhuang:
    """
    神装进阶
    """

    def __init__(self, fail_value: int) -> None:
        # 失败祝福值
        self.fail_value = fail_value
        # 用于保存神装资料
        self.data = {}

        self.init_info = "绿色部分表明材料可以满祝福\n"
        # 所有神装页面资料
        for page_id in ["0", "1", "2", "3", "4", "5"]:
            value = self.get_info(page_id)
            self.init_info += value
            self.update_data(page_id, value)

        print("--" * 20)
        print(self.init_info)

    def update_data(self, key: str, value: str) -> None:
        """
        更新 self.data 字典数据
        """
        self.data[key] = value

    def get_info(self, page_id: str) -> str:
        _data = {
            "0": ["神兵", 3573, "cmd=arena&op=queryexchange"],
            "1": ["神铠", 3574, "cmd=arena&op=queryexchange"],
            "2": ["神羽", 3575, "cmd=exchange&subtype=10&costtype=1"],
            "3": ["神兽", 3576, "cmd=exchange&subtype=10&costtype=2"],
            "4": ["神饰", 3631, "cmd=exchange&subtype=10&costtype=2"],
            "5": ["神履", 3636, "cmd=exchange&subtype=10&costtype=3"],
        }
        _name, backpack_id, store_params = _data[page_id]

        # 神装
        D.get(f"cmd=outfit&op=0&magic_outfit_id={page_id}")
        if "10阶" in D.html:
            # 满阶跳过
            return f"\n{_name}已经满阶\n"

        result_1 = D.find(r"阶层：(.*?)<", f"{_name}-阶层")
        result_2 = D.find(r"进阶消耗：(.*?)<", f"{_name}-进阶消耗")
        result_3 = D.find(r"祝福值：(.*?)<", f"{_name}-祝福值")

        # 进阶一次消耗材料数量
        number_1 = int(result_2.split("*")[1])
        # 当前祝福值、最大祝福值
        number_2, number_3 = result_3.split("/")
        # 最大祝福值与当前祝福值之差
        number_4 = int(number_3) - int(number_2)
        # 进阶到满祝福所需材料数量，2 是额外的冗余进阶次数
        number_5 = (int(number_4 / self.fail_value) + 2) * number_1

        # 获取背包进阶材料数量
        number_6: int = get_backpack_item_count(backpack_id)
        # 获取进阶材料的商店积分
        number_7: int = get_store_points(store_params)
        # 计算进阶材料背包数量与商店积分可兑换数量之和
        number_8: int = number_6 + int(number_7 / 40)

        text = f"""
            代号：{page_id}
            神装：{_name}
            阶层：{result_1}
            进阶消耗：{result_2}
            祝福值：{result_3}
            失败祝福值：{self.fail_value}
            背包进阶材料数量：{number_6}
            商店积分：{number_7}
            满祝福所需进阶材料数量：{number_5}
            进阶材料背包数量与商店数量之和：{number_8}
        """

        # 移除每行的前导空格
        text = "\n".join([line.lstrip() for line in text.splitlines()])
        # 将字符串设为绿色
        if number_8 >= number_5:
            text = f"\033[32m{text}\033[0m"
        return text

    def 神装进阶(self, page_id: str) -> None:
        while True:
            old_info: str = self.data[page_id]
            result_1 = re.search(r"进阶消耗：(.*?)\n", old_info, re.S).group(1)
            result_2 = re.search(r"背包进阶材料数量：(.*?)\n", old_info, re.S).group(1)

            # 进阶材料名称、数量
            name, number = result_1.split("*")

            print("--" * 20)
            # 补齐进阶材料
            if int(result_2) < int(number):
                count = int(number) - int(result_2)
                self.exchange(name, count)

            # 神装
            D.get("cmd=outfit")
            if "关闭自动斗豆兑换神装进阶材料" in D.html:
                D.get(f"cmd=outfit&op=4&auto_buy=2&magic_outfit_id={page_id}")
                D.find(r"\|<br />(.*?)<br />")
            if "关闭自动斗豆兑换神技升级材料" in D.html:
                D.get(f"cmd=outfit&op=8&auto_buy=2&magic_outfit_id={page_id}")
                D.find(r"\|<br />(.*?)<br />")

            # 进阶
            D.get(f"cmd=outfit&op=1&magic_outfit_id={page_id}")
            D.find(r"神履.*?<br />(.*?)<br />")
            if "成功" in D.html:
                break
            elif "材料不足" in D.html:
                break
            elif "已经满阶" in D.html:
                break

            print("--" * 20)
            print("开始查询神装资料")
            new_info: str = self.get_info(page_id)
            self.update_data(page_id, new_info)
            print(new_info)

    def exchange(self, key: str, count: int):
        """
        兑换神装材料
        """
        data = {
            "凤凰羽毛": "cmd=exchange&subtype=2&type=1100&times=1&costtype=1",
            "奔流气息": "cmd=exchange&subtype=2&type=1205&times=1&costtype=3",
            "潜能果实": "cmd=exchange&subtype=2&type=1200&times=1&costtype=2",
            "上古玉髓": "cmd=exchange&subtype=2&type=1201&times=1&costtype=2",
            "神兵原石": "cmd=arena&op=exchange&id=3573",
            "软猥金丝": "cmd=arena&op=exchange&id=3574",
        }
        while count:
            D.get(data[key])
            D.find()
            if "不足" in D.html:
                break
            elif "恭喜" in D.html:
                count -= 1


def 神装():
    """
    神装自动积分兑换材料并进阶，不会扣除斗豆
    """
    print("日常失败祝福值是 2")
    print("活动期间是 2n 倍")
    print("输入其它非数字键退出")
    _input_1 = input("输入神装失败祝福值：")
    if not _input_1.isdigit():
        print(f"{_input_1} 不是一个数字")
        return True
    print("--" * 20)
    print("开始查询神装资料")

    s = ShenZhuang(int(_input_1))
    data = s.data
    print("--" * 20)

    print("0：神兵")
    print("1：神铠")
    print("2：神羽")
    print("3：神兽")
    print("4：神饰")
    print("5：神履")
    print("其它任意键退出")
    _input_2 = input("输入神装进阶代号：")
    if _input_2 not in ["0", "1", "2", "3", "4", "5"]:
        return True
    print(data[_input_2])

    if "已经满阶" in data[_input_2]:
        return True

    print("脚本始终关闭自动斗豆兑换，不会扣除斗豆")
    print("然后积分商店自动兑换材料并进阶")
    _input_3 = input("是否确认进阶？（y/n）：")
    if _input_3 != "y":
        return True

    # 进阶
    s.神装进阶(_input_2)

    return True


def 夺宝奇兵():
    """
    夺宝奇兵选择太空探宝场景投掷
    """
    # 合成
    D.get("cmd=element&subtype=4")
    result = D.find(r"拥有:(\d+)")
    print("--" * 20)

    print("夺宝奇兵太空探宝场景投掷")
    print("任意非数字键退出")
    _input = input("输入低于多少战功时结束投掷：")
    if not _input.isdigit():
        return True
    print("--" * 20)

    while True:
        if int(result) < int(_input):
            break

        # 投掷
        D.get("cmd=element&subtype=7")
        if "【夺宝奇兵】" in D.html:
            D.find(r"<br /><br />(.*?)<br />")
            result = D.find(r"拥有:(\d+)")
            if "您的战功不足" in D.html:
                break
        elif "【选择场景】" in D.html:
            if "你掷出了" in D.html:
                D.find(r"】<br />(.*?)<br />")
            # 选择太空探宝
            D.get("cmd=element&subtype=15&gameType=3")

    return True


def 柒承的忙碌日常(number: int):
    """
    挑战柒承的忙碌日常副本
    """
    for _ in range(number):
        # 开启副本
        D.get("cmd=jianghudream&op=beginInstance&ins_id=1")
        if "帮助" in D.html:
            # 开启副本所需追忆香炉不足
            # 您还未编辑副本队伍，无法开启副本
            D.msg_append(D.find())
            break

        for _ in range(8):
            if "进入下一天" in D.html:
                # 进入下一天
                D.get("cmd=jianghudream&op=goNextDay")
            if msg1 := D.findall(r'event_id=(\d+)">战斗\(等级1\)'):
                # 战斗
                D.get(f"cmd=jianghudream&op=chooseEvent&event_id={msg1[0]}")
                # FIGHT!
                D.get("cmd=jianghudream&op=doPveFight")
                D.find(r"<p>(.*?)<br />")
                if "战败" in D.html:
                    break
            elif msg2 := D.findall(r'event_id=(\d+)">奇遇\(等级1\)'):
                # 奇遇
                D.get(f"cmd=jianghudream&op=chooseEvent&event_id={msg2[0]}")
                # 视而不见
                D.get("cmd=jianghudream&op=chooseAdventure&adventure_id=2")
                D.find(r"获得金币：\d+<br />(.*?)<br />")
            elif msg3 := D.findall(r'event_id=(\d+)">商店\(等级1\)'):
                # 商店
                D.get(f"cmd=jianghudream&op=chooseEvent&event_id={msg3[0]}")

        # 结束回忆
        D.get("cmd=jianghudream&op=endInstance")
        D.msg_append(D.find())


class JiangHuChangMeng:
    """
    江湖长梦商店兑换
    """

    def __init__(self):
        # 江湖长梦商店积分
        self.points: int = get_store_points("cmd=longdreamexchange")
        # 商店材料初始数据
        self._init_data: dict = self._init_store_data(self._get_data())
        # 输出商店数据
        self._print_store_info()
        # 用于储存用户添加的兑换材料id及数量
        self.data = {}

    @property
    def init_data(self):
        return self._init_data

    def _init_store_data(self, data: list[tuple]) -> dict:
        """
        将售价、已售、限售str类型转为int
        """
        dict_data = {}
        for d in data:
            _id, name, 售价, 已售, 限售 = d
            dict_data[name] = {
                "id": _id,
                "售价": int(售价),
                "已售": int(已售),
                "限售": int(限售),
            }
        return dict_data

    def _get_data(self) -> list[tuple]:
        """
        获取江湖长梦商店数据
        """
        params = [
            "cmd=longdreamexchange&page_type=0&page=1",
            "cmd=longdreamexchange&page_type=0&page=2",
            "cmd=longdreamexchange&page_type=1&page=1",
            "cmd=longdreamexchange&page_type=1&page=2",
        ]
        data = []
        for p in params:
            D.get(p)
            # id、名称、售价、已售、限售
            data += D.findall(r"_id=(\d+).*?>(.*?)\*1.*?(\d+).*?(\d+)/(\d+)")
        return data

    def _print_store_info(self):
        """
        将商店中的材料名称、售价、已售、限售打印出来
        """
        headers = ["名称", "售价", "已售", "限售"]
        # 打印表头
        print("{:<12}{:<5}{:<4}{:<3}".format(*headers))
        print("--" * 20)
        for name, _dict in self.init_data.items():
            售价 = _dict["售价"]
            已售 = _dict["已售"]
            限售 = _dict["限售"]
            print(f"{name:<12}{售价:<5}{已售:<4}{限售:<3}")

    def update_points(self, name: str, number: int) -> tuple:
        """
        更新商店积分，返回包含材料名称、材料id、可售数量的元组
        """
        _dict = self.init_data[name]
        _id: str = _dict["id"]
        售价: int = _dict["售价"]
        已售: int = _dict["已售"]
        限售: int = _dict["限售"]

        if number > (限售 - 已售):
            number = 限售 - 已售

        if value := self.data.get(name):
            v: int = value["number"]
            # 回滚到未购买前的积分
            original_points = self.points + (v * 售价)
            self.points = original_points
        else:
            # 记录原始积分
            original_points = self.points

        original_points -= number * 售价
        if original_points >= 0:
            self.points = original_points
        else:
            # 计算当前积分的最大可售数量
            number = int(self.points / 售价)
            self.points -= number * 售价

        return name, _id, number

    @property
    def 兑换(self):
        """
        执行商店材料兑换
        """
        for name, _dict in self.data.items():
            _id = _dict["id"]
            number: int = _dict["number"]
            for i in range(number):
                D.get(f"cmd=longdreamexchange&op=exchange&key_id={_id}")
                D.find(r"侠士碎片</a><br />(.*?)<br />", name=f"{name}-{i + 1}")


def 江湖长梦():
    """
    商店兑换及副本挑战（柒承的忙碌日常）
    """
    print("1：江湖长梦商店兑换")
    print("2：柒承的忙碌日常")
    print("其它任意键退出")
    input_1 = input("输入选择：")
    if input_1 not in ["1", "2"]:
        return True
    print("--" * 20)

    if input_1 == "2":
        print(">>>柒承的忙碌日常")
        # 追忆香炉数量
        number = get_backpack_item_count(6477)
        print(f"追忆香炉数量：{number}")
        input_2 = input("输入挑战次数：")
        if not input_2.isdigit():
            print("只能输入数字")
            return True
        柒承的忙碌日常(int(input_2))
        return True

    print(">>>江湖长梦商店兑换")
    n = 1
    j = JiangHuChangMeng()
    if j.points < 240:
        print("--" * 20)
        print(f"积分过低：{j.points}")
        return True

    while True:
        print("--" * 20)
        print(f"剩余积分：{j.points}")
        for name, _dict in j.data.items():
            print(f"{name}：{_dict['number']}")
        input_3 = input("输入y继续添加或其它任意键退出添加：")
        if input_3 != "y":
            break
        print("--" * 20)

        input_4 = input(f"添加第 {n} 个兑换材料名称：")
        if input_4 not in j.init_data:
            print(f"{input_3} 不存在")
            continue
        if j.data.get(input_4):
            print(f"{input_4} 已添加过了，只会更新其值")

        input_5 = input(f"添加第 {n} 个兑换材料数量：")
        if not input_5.isdigit():
            print("只能输入数字")
            continue

        input_number = int(input_5)
        name, _id, number = j.update_points(input_4, input_number)
        if (number == 0) and (input_number != 0):
            print(f"{name} 已达兑换上限")
        if number != input_number:
            print(f"{name} 最多可兑换：{number}")

        j.data[name] = {
            "id": _id,
            "number": number,
        }
        n += 1

    if not j.data:
        return True

    print("--" * 20)
    input_6 = input("是否确认兑换（y/n）：")
    if input_6 != "y":
        return True
    print("--" * 20)

    j.兑换

    return True
