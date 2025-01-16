"""
本模块为大乐斗其它任务

不会定时运行，只能手动模式运行

手动运行某个函数：
python main.py other -- 神装
"""

from daledou.utils import yield_dld_objects


_FUNC_NAME = [
    "神装",
    "夺宝奇兵",
    "江湖长梦",
    "星盘",
    "新元婴神器",
    "深渊之潮",
    "神魔录",
    "奥义",
]


def check_func_name_existence(func_name: str):
    """
    判断函数名称是否存在
    """
    if func_name not in _FUNC_NAME:
        print("other 模式支持以下参数：")
        for i, item in enumerate(_FUNC_NAME):
            print(f"{i + 1}.{item}")
        print("--" * 20)
        raise KeyError(func_name)


def run_other(unknown_args: list):
    global D
    for D in yield_dld_objects():
        print("--" * 20)
        for func_name in unknown_args:
            check_func_name_existence(func_name)
            D.func_name = func_name
            D.msg_append(f"\n【{func_name}】")
            globals()[func_name]()

        D.run_time()
        print("--" * 20)


# ============================================================


def compute(fail_value, deplete_value, now_value, total_value) -> int:
    """
    返回技能强化至满祝福或者满进度时消耗的材料数量

    进度满了会升级成功；祝福满了不一定升级成功

    Args:
        fail_value: int类型，失败祝福值或者进度
        deplete_value: int类型，强化一次消耗材料数量
        now_value: int类型，当前祝福值或者当前进度
        total_value: int类型，总祝福值或者总进度
    """
    # 计算强化次数，向上取整
    number = -((now_value - total_value) // fail_value)
    # 计算总消耗材料数量
    total_deplete = number * deplete_value
    return total_deplete


def get_backpack_item_count(item_id: str | int) -> int:
    """
    返回背包物品id数量
    """
    # 背包物品详情
    D.get(f"cmd=owngoods&id={item_id}")
    if "很抱歉" in D.html:
        number = 0
    else:
        number = D.findall(r"数量：(\d+)")[0]
    return int(number)


def get_store_points(params: str) -> int:
    """
    返回商店积分
    """
    # 商店
    D.get(params)
    result = D.findall(r"<br />(.*?)<")[0]
    _, store_points = result.split("：")
    return int(store_points)


class Exchange:
    """
    积分商店兑换
    """

    def __init__(self, url: dict, consume_num: int, possess_num: int):
        # 材料兑换10个链接
        self.exchange_ten_url = url["ten"]
        # 材料兑换一个链接
        self.exchange_one_url = url["one"]
        # 材料消耗数量
        self.consume_num = consume_num
        # 材料拥有数量
        self.possess_num = possess_num

    def exchange(self):
        """
        如果材料消耗数量大于材料拥有数量则兑换两者差值数量的材料
        """
        print("--" * 20)
        if self.possess_num >= self.consume_num:
            return

        exchange_num = self.consume_num - self.possess_num
        ten_count, one_count = divmod(exchange_num, 10)
        if not self.exchange_count(self.exchange_ten_url, ten_count):
            return
        if not self.exchange_count(self.exchange_one_url, one_count):
            return

        # 兑换成功则两者数量一致
        self.possess_num = self.consume_num
        print("--" * 20)

    def exchange_count(self, url: str, count: int) -> bool:
        """
        兑换足够数量返回True，否则返回False
        """
        while count > 0:
            D.get(url)
            D.find()
            if "成功" in D.html:
                count -= 1
            elif "不足" in D.html:
                return False
        return True

    def update_possess_num(self):
        """
        更新材料拥有数量
        """
        if self.possess_num >= self.consume_num:
            self.possess_num -= self.consume_num


class Input:
    """
    处理用户输入
    """

    def __init__(self):
        self.print_header()

    def print_header(self):
        """
        打印头部信息
        """
        print("任意位置输入 q 退出当前账号任务")
        print("--" * 20)
        print("技能强化不会使用斗豆自动兑换")

    def print_mission(self, mission: dict | list):
        """
        打印任务信息
        """
        if isinstance(mission, dict):
            for key, value in mission.items():
                print(f"{key}：{value}")
        elif isinstance(mission, list):
            for name in mission:
                print(f"任务名称：{name}")
        else:
            raise TypeError("mission类型必须是字典或者列表")

    def select_mission(self, mission: dict | list, prompt: str) -> str | None:
        """
        返回用户选择的任务
        """
        while True:
            print("--" * 20)
            self.print_mission(mission)
            _input = input(prompt)
            if _input == "q":
                return None
            if _input in mission:
                return _input
            print("--" * 20)
            print(f">>>不存在：{_input}")

    def select_upgrade(self, skill_class, skill_params=None):
        """
        将用户选择的技能升级
        """
        while True:
            if skill_params is None:
                s = skill_class()
            else:
                s = skill_class(skill_params)

            for _, _dict in s.data.items():
                print("--" * 20)
                for k, v in _dict.items():
                    print(f"{k}：{v}")

            if not s.data:
                print("--" * 20)
                print(">>>没有可执行的操作，请重新运行更换任务")
                return

            while True:
                print("--" * 20)
                _input = input("选择强化名称：")
                if _input == "q":
                    return
                print("--" * 20)
                if _input not in s.data:
                    print(f">>>不存在：{_input}")
                    continue
                if s.data[_input]["是否升级"]:
                    s.upgrade(_input)
                    break
                else:
                    print(f">>>{_input}材料或者积分不足，不能升级")

    def get_number(self, prompt: str) -> int | None:
        """
        返回用户输入的数字
        """
        while True:
            print("--" * 20)
            _input = input(prompt)
            if _input == "q":
                return None
            if _input.isdigit():
                return int(_input)
            print("--" * 20)
            print(">>>请输入一个非负整数")


# ============================================================


class ShenZhuang:
    """
    神装一键进阶
    """

    def __init__(self, fail_value: int):
        # 失败祝福值
        self.fail_value = fail_value

        self.data = self.get_data()

    def get_data(self) -> dict:
        """
        获取神装数据，不包含满阶和必成数据
        """
        data_dict = {
            "神兵": {
                "id": "0",
                "backpack_id": 3573,
                "store_url": "cmd=arena&op=queryexchange",
            },
            "神铠": {
                "id": "1",
                "backpack_id": 3574,
                "store_url": "cmd=arena&op=queryexchange",
            },
            "神羽": {
                "id": "2",
                "backpack_id": 3575,
                "store_url": "cmd=exchange&subtype=10&costtype=1",
            },
            "神兽": {
                "id": "3",
                "backpack_id": 3576,
                "store_url": "cmd=exchange&subtype=10&costtype=2",
            },
            "神饰": {
                "id": "4",
                "backpack_id": 3631,
                "store_url": "cmd=exchange&subtype=10&costtype=2",
            },
            "神履": {
                "id": "5",
                "backpack_id": 3636,
                "store_url": "cmd=exchange&subtype=10&costtype=3",
            },
        }
        data = {}

        for name, _dict in data_dict.items():
            _id = _dict["id"]
            backpack_id = _dict["backpack_id"]
            store_url = _dict["store_url"]
            result = self.get_match_data(name, _id, backpack_id, store_url)
            if result:
                data[name] = result
        return data

    def get_match_data(self, name, _id, backpack_id, store_url) -> dict | None:
        """
        获取神装匹配数据
        """
        # 神装
        D.get(f"cmd=outfit&op=0&magic_outfit_id={_id}")
        if ("10阶" in D.html) or ("必成" in D.html):
            return None

        # 阶层
        level = D.findall(r"阶层：(.*?)<")[0]
        # 材料消耗名称
        consume_name = D.findall(r"进阶消耗：(.*?)\*")[0]
        # 材料消耗数量
        consume_num = int(D.findall(r"\*(\d+)")[0])
        # 当前祝福值
        now_value = int(D.findall(r"祝福值：(\d+)")[0])
        # 满祝福值
        total_value = int(D.findall(r"祝福值：\d+/(\d+)")[0])

        # 满祝福消耗数量
        full_value_consume_num = compute(
            self.fail_value, consume_num, now_value, total_value
        )
        # 材料拥有数量
        possess_num = get_backpack_item_count(backpack_id)
        # 商店积分
        store_points = get_store_points(store_url)
        # 商店积分可兑换数量
        store_num = store_points // 40

        return {
            "名称": name,
            "id": _id,
            "阶层": level,
            "消耗": f"{consume_name}*{consume_num}",
            "祝福值": f"{now_value}/{total_value}",
            "材料消耗名称": consume_name,
            "材料消耗数量": consume_num,
            "材料拥有数量": possess_num,
            "积分": f"{store_points}（{store_num}）",
            "满祝福消耗数量": f"{full_value_consume_num}（必成再+{consume_num}）",
            "失败祝福值": self.fail_value,
            "是否升级": (possess_num + store_num)
            >= (full_value_consume_num + consume_num),
        }

    def upgrade(self, name: str):
        """
        神装进阶
        """
        url = {
            "凤凰羽毛": {
                "ten": "cmd=exchange&subtype=2&type=1100&times=10&costtype=1",
                "one": "cmd=exchange&subtype=2&type=1100&times=1&costtype=1",
            },
            "奔流气息": {
                "ten": "cmd=exchange&subtype=2&type=1205&times=10&costtype=3",
                "one": "cmd=exchange&subtype=2&type=1205&times=1&costtype=3",
            },
            "潜能果实": {
                "ten": "cmd=exchange&subtype=2&type=1200&times=10&costtype=2",
                "one": "cmd=exchange&subtype=2&type=1200&times=1&costtype=2",
            },
            "上古玉髓": {
                "ten": "cmd=exchange&subtype=2&type=1201&times=10&costtype=2",
                "one": "cmd=exchange&subtype=2&type=1201&times=1&costtype=2",
            },
            "神兵原石": {
                "ten": "cmd=arena&op=exchange&id=3573&times=10",
                "one": "cmd=arena&op=exchange&id=3573&times=1",
            },
            "软猥金丝": {
                "ten": "cmd=arena&op=exchange&id=3574&times=10",
                "one": "cmd=arena&op=exchange&id=3574&times=1",
            },
        }

        data = self.data[name]
        _id: str = data["id"]
        consume_name: str = data["材料消耗名称"]
        consume_num: int = data["材料消耗数量"]
        possess_num: int = data["材料拥有数量"]

        e = Exchange(url[consume_name], consume_num, possess_num)

        # 关闭自动斗豆兑换神装进阶材料
        D.get(f"cmd=outfit&op=4&auto_buy=2&magic_outfit_id={_id}")
        D.find(r"\|<br />(.*?)<br />")

        while True:
            # 积分商店兑换材料
            e.exchange()

            # 进阶
            D.get(f"cmd=outfit&op=1&magic_outfit_id={_id}")
            D.find(r"神履.*?<br />(.*?)<br />", name)
            D.find(r"祝福值：(.*?)<", name)
            if "进阶失败" not in D.html:
                break

            # 更新材料拥有数量
            e.update_possess_num()


class ShenJi:
    """
    神技一键升级
    """

    def __init__(self, store_name: str):
        store = {
            "矿洞": get_store_points("cmd=exchange&subtype=10&costtype=3"),
            "掠夺": get_store_points("cmd=exchange&subtype=10&costtype=2"),
            "踢馆": get_store_points("cmd=exchange&subtype=10&costtype=1"),
            "竞技场": get_store_points("cmd=arena&op=queryexchange"),
        }
        # 积分商店名称
        self.store_name = store_name
        self.points = store[store_name]

        self.data = self.get_data()

    def get_data_id(self) -> list:
        """
        获取神装附带技能id，不包含满级id
        """
        data = []
        for _id in range(6):
            # 神装
            D.get(f"cmd=outfit&op=0&magic_outfit_id={_id}")
            data += D.findall(r'skill_id=(\d+)">升级十次.*?等级：(\d+)')

        return [_id for _id, level in data if level != "10"]

    def get_data(self) -> dict:
        """
        获取神技详情数据
        """
        data = {}
        # 神秘精华拥有数量
        possess_num = get_backpack_item_count(3567)
        # 积分商店可兑换数量
        store_num = self.points // 40

        for _id in self.get_data_id():
            D.get(f"cmd=outfit&op=2&magic_skill_id={_id}")
            # 神技名称
            name = D.findall(r"<br />=(.*?)=<a")[0]
            # 当前等级
            level = D.findall(r"当前等级：(\d+)")[0]
            # 材料消耗名称
            consume_name = "神秘精华"
            # 升级消耗数量
            consume_num = int(D.findall(r"\*(\d+)<")[0])
            # 升级成功率
            success = D.findall(r"升级成功率：(.*?)<")[0]
            # 当前效果
            effect = D.findall(r"当前效果：(.*?)<")[0]

            if success == "必成":
                is_upgrade = True if store_num >= consume_num else False

            data[name] = {
                "名称": name,
                "id": _id,
                "当前等级": level,
                "升级消耗": f"{consume_name}*{consume_num}",
                "升级成功率": success,
                "当前效果": effect,
                "材料消耗名称": consume_name,
                "材料消耗数量": consume_num,
                "材料拥有数量": possess_num,
                f"{self.store_name}积分": f"{self.points}（{store_num}）",
                "是否升级": is_upgrade,
            }
        return data

    def upgrade(self, name: str):
        """
        神技升级
        """
        url = {
            "矿洞": {
                "ten": "cmd=exchange&subtype=2&type=1206&times=10&costtype=3",
                "one": "cmd=exchange&subtype=2&type=1206&times=1&costtype=3",
            },
            "掠夺": {
                "ten": "cmd=exchange&subtype=2&type=1202&times=10&costtype=2",
                "one": "cmd=exchange&subtype=2&type=1202&times=1&costtype=2",
            },
            "踢馆": {
                "ten": "cmd=exchange&subtype=2&type=1101&times=10&costtype=1",
                "one": "cmd=exchange&subtype=2&type=1101&times=1&costtype=1",
            },
            "竞技场": {
                "ten": "cmd=arena&op=exchange&id=3567&times=10",
                "one": "cmd=arena&op=exchange&id=3567&times=1",
            },
        }

        data = self.data[name]
        _id: str = data["id"]
        consume_num: int = data["材料消耗数量"]
        possess_num: int = data["材料拥有数量"]

        e = Exchange(url[self.store_name], consume_num, possess_num)

        # 关闭自动斗豆兑换神技升级材料
        D.get(f"cmd=outfit&op=8&auto_buy=2&magic_outfit_id={_id}")
        D.find(r"\|<br />(.*?)<br />")

        while True:
            # 积分商店兑换材料
            e.exchange()

            # 升级
            D.get(f"cmd=outfit&op=3&magic_skill_id={_id}")
            D.find(r"套装强化</a><br />(.*?)<br />", name)
            if "升级失败" not in D.html:
                break

            # 更新材料拥有数量
            e.update_possess_num()


def 神装():
    """
    神装自动兑换强化：神装进阶和神技升级
    """
    mission_list = ["神装", "神技"]
    mission_dict = {
        "矿洞": get_store_points("cmd=exchange&subtype=10&costtype=3"),
        "掠夺": get_store_points("cmd=exchange&subtype=10&costtype=2"),
        "踢馆": get_store_points("cmd=exchange&subtype=10&costtype=1"),
        "竞技场": get_store_points("cmd=arena&op=queryexchange"),
    }

    i = Input()

    mission_name = i.select_mission(mission_list, "选择任务名称：")
    if mission_name is None:
        return

    if mission_name == "神装":
        fail_value = i.get_number("输入失败祝福值：")
        if fail_value is None:
            return
        i.select_upgrade(ShenZhuang, fail_value)
    elif mission_name == "神技":
        store_name = i.select_mission(mission_dict, "选择商店名称：")
        if store_name is None:
            return
        i.select_upgrade(ShenJi, store_name)


class DuoBaoQiBing:
    """
    五行夺宝奇兵自动投掷
    """

    def __init__(self):
        self.exploits = self.get_exploits()
        print("--" * 20)
        print(f"战功：{self.exploits}")

    def get_exploits(self) -> int:
        """
        获取五行战功
        """
        # 五行-合成
        D.get("cmd=element&subtype=4")
        exploits = D.findall(r"拥有:(\d+)")[0]
        return int(exploits)

    def pelted(self, input_exploits: int):
        """
        太空探宝16倍场景投掷
        """
        print("--" * 20)
        while True:
            if input_exploits > self.exploits:
                break

            # 投掷
            D.get("cmd=element&subtype=7")
            if "【夺宝奇兵】" in D.html:
                D.find(r"<br /><br />(.*?)<br />")
                D.find(r"进度：(.*?)<", "进度")
                result = D.find(r"拥有:(\d+)", "战功")
                self.exploits = int(result)
                if "您的战功不足" in D.html:
                    break
            elif "【选择场景】" in D.html:
                if "你掷出了" in D.html:
                    D.find(r"】<br />(.*?)<br />")
                # 选择太空探宝
                D.get("cmd=element&subtype=15&gameType=3")
                print("--" * 20)


def 夺宝奇兵():
    """
    五行夺宝奇兵：太空探宝场景投掷（16倍）
    """
    i = Input()
    while True:
        o = DuoBaoQiBing()
        # 获取输入战功
        input_exploits = i.get_number("输入低于多少战功时结束投掷：")
        if input_exploits is None:
            break
        o.pelted(input_exploits)


class QiCheng:
    """
    挑战柒承的忙碌日常
    """

    def __init__(self):
        print("--" * 20)
        print(f"追忆香炉数量：{get_backpack_item_count(6477)}")
        print(f"江湖长梦积分：{get_store_points("cmd=longdreamexchange")}")

    def challenge(self, challenge_count: int):
        """
        优先级：战斗 > 奇遇（视而不见）> 商店（不购买）
        """
        p = "cmd=jianghudream&op=chooseEvent&event_id="
        for _ in range(challenge_count):
            print("--" * 20)
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
                    result_1 = D.findall(r'event_id=(\d+)">战斗')
                    result_2 = D.findall(r'event_id=(\d+)">奇遇')
                    result_3 = D.findall(r'event_id=(\d+)">商店')
                if result_1:
                    # 战斗
                    D.get(f"{p}{result_1[0]}")
                    # FIGHT!
                    D.get("cmd=jianghudream&op=doPveFight")
                    D.find(r"<p>(.*?)<br />")
                    if "战败" in D.html:
                        break
                elif result_2:
                    # 奇遇
                    D.get(f"{p}{result_2[0]}")
                    # 视而不见
                    D.get("cmd=jianghudream&op=chooseAdventure&adventure_id=2")
                    D.find(r"获得金币：\d+<br />(.*?)<br />")
                elif result_3:
                    # 商店
                    D.get(f"{p}{result_3[0]}")

            # 结束回忆
            D.get("cmd=jianghudream&op=endInstance")
            D.msg_append(D.find())


def 江湖长梦():
    """
    挑战柒承的忙碌日常
    """
    i = Input()
    while True:
        o = QiCheng()
        challenge_count = i.get_number("输入挑战次数：")
        if challenge_count is None:
            break
        o.challenge(challenge_count)


class XingPan:
    """
    星石一键合成
    """

    def __init__(self, level: int):
        # 合成等级
        self.level = level
        # 各级合成次数
        self.count = {}
        # 各级转换关系
        self.level_ties = {
            1: 5,  # 5个1级星石合成一个2级星石
            2: 4,  # 4个2级星石合成一个3级星石
            3: 4,  # 4个3级星石合成一个4级星石
            4: 3,  # 3个4级星石合成一个5级星石
            5: 3,  # 3个5级星石合成一个6级星石
            6: 2,  # 2个6级星石合成一个7级星石
        }
        self.star_gem = {
            "日曜石": 1,
            "玛瑙石": 2,
            "迅捷石": 3,
            "月光石": 4,
            "翡翠石": 5,
            "紫黑玉": 6,
            "狂暴石": 7,
            "神愈石": 8,
        }

        # 幻境商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=9")

        self.data_id = self.get_star_id()
        self.data = self.get_data()

    def get_star_id(self) -> dict:
        """
        返回2~7级星石合成id
        """
        data = {}
        for name, gem in self.star_gem.items():
            D.get(f"cmd=astrolabe&op=showgemupgrade&gem_type={gem}")
            result = D.findall(r"gem=(\d+)")[1:]

            # 2~7级星石合成id
            star_id = {i + 2: item for i, item in enumerate(result)}
            data[name] = {
                "id": star_id,
            }
        return data

    def get_data(self) -> dict:
        """
        获取1~6级星石数量及2~7级星石合成id
        """
        data = {}
        for name, gem in self.star_gem.items():
            D.get(f"cmd=astrolabe&op=showgemupgrade&gem_type={gem}")
            result = D.findall(r"（(\d+)）")[1:]

            # 1~6级星石数量
            star_number = {i + 1: int(item) for i, item in enumerate(result)}
            # 幻境商店可兑换数量
            store_num = self.get_store_max_number(name)
            self.count[name] = {}
            # 一级星石兑换数量
            exchange_number = self.compute(name, self.level, star_number)

            data[name] = {
                "名称": name,
                "1级数量": star_number[1],
                "2级数量": star_number[2],
                "3级数量": star_number[3],
                "4级数量": star_number[4],
                "5级数量": star_number[5],
                "6级数量": star_number[6],
                "积分": f"{self.points}（{store_num}）",
                "一级星石兑换数量": exchange_number,
                "合成等级": self.level,
                "是否升级": store_num >= exchange_number,
            }
        return data

    def get_store_max_number(self, name: str) -> int:
        """
        返回幻境商店星石最大兑换数量
        """
        data = {
            "翡翠石": 32,
            "玛瑙石": 40,
            "迅捷石": 40,
            "紫黑玉": 40,
            "日曜石": 48,
            "月光石": 32,
        }
        if price := data.get(name):
            return self.points // price
        return 0

    def compute(self, name: str, level: int, star_number: dict, count=1) -> int:
        """
        返回一级某星石兑换数量
        """
        self.count[name][level] = count
        # 下一级
        level -= 1
        # 次级拥有数量
        possess_num = star_number[level]
        # 次级消耗数量
        consume_num = self.level_ties[level] * count

        if possess_num >= consume_num:
            return 0
        else:
            number = consume_num - possess_num
            if level == 1:
                # 一级星石兑换数量
                return number
            else:
                return self.compute(name, level, star_number, number)

    def upgrade(self, name: str):
        """
        星石合成
        """
        url = {
            "翡翠石": {
                "ten": "cmd=exchange&subtype=2&type=1233&times=10&costtype=9",
                "one": "cmd=exchange&subtype=2&type=1233&times=1&costtype=9",
            },
            "玛瑙石": {
                "ten": "cmd=exchange&subtype=2&type=1234&times=10&costtype=9",
                "one": "cmd=exchange&subtype=2&type=1234&times=1&costtype=9",
            },
            "迅捷石": {
                "ten": "cmd=exchange&subtype=2&type=1235&times=10&costtype=9",
                "one": "cmd=exchange&subtype=2&type=1235&times=1&costtype=9",
            },
            "紫黑玉": {
                "ten": "cmd=exchange&subtype=2&type=1236&times=10&costtype=9",
                "one": "cmd=exchange&subtype=2&type=1236&times=1&costtype=9",
            },
            "日曜石": {
                "ten": "cmd=exchange&subtype=2&type=1237&times=10&costtype=9",
                "one": "cmd=exchange&subtype=2&type=1237&times=1&costtype=9",
            },
            "月光石": {
                "ten": "cmd=exchange&subtype=2&type=1238&times=10&costtype=9",
                "one": "cmd=exchange&subtype=2&type=1238&times=1&costtype=9",
            },
        }

        if name in url:
            exchange_num = self.data[name]["一级星石兑换数量"]
            Exchange(url[name], exchange_num, 0).exchange()

        id_dict = self.data_id[name]["id"]
        data = dict(sorted(self.count[name].items()))
        for level, count in data.items():
            _id = id_dict[level]
            for _ in range(count):
                # 合成
                D.get(f"cmd=astrolabe&op=upgradegem&gem={_id}")
                D.find(r"规则</a><br />(.*?)<", f"{level}级{name}")


def 星盘():
    """
    星石一键合成
    """
    i = Input()

    upgrade_level = i.get_number("输入合成星石等级（2~7）：")
    if upgrade_level is None:
        return
    elif upgrade_level not in [2, 3, 4, 5, 6, 7]:
        print("--" * 20)
        print(">>>合成等级只能是2~7级")
        return
    i.select_upgrade(XingPan, upgrade_level)


class XinYuanYingShenQi:
    """
    新元婴神器一键升级
    """

    def __init__(self, name: str):
        self._name = name

        # 真黄金卷轴拥有数量
        self.possess_num = get_backpack_item_count(5089)

        self.data = self.get_data(self._name)

    def get_data(self, name: str) -> dict:
        """
        获取神器数据
        """
        params_data = {
            "投掷武器": "op=1&type=0",
            "小型武器": "op=1&type=1",
            "中型武器": "op=1&type=2",
            "大型武器": "op=1&type=3",
            "被动技能": "op=2&type=4",
            "伤害技能": "op=2&type=5",
            "特殊技能": "op=2&type=6",
        }
        data = {}
        params = params_data[name]
        D.get(f"cmd=newAct&subtype=104&{params}")
        D.html = D.html.split("|")[-1]

        # 获取神器名称
        result_1 = D.findall(r"([\u4e00-\u9fff]+)&nbsp;\d+星")
        # 获取神器星级
        result_2 = D.findall(r"(\d+)星")
        # 获取神器id
        result_3 = D.findall(r"item_id=(\d+).*?一键")
        # 获取消耗数量
        result_4 = D.findall(r":(\d+)")
        # 获取当前祝福值
        result_5 = D.findall(r"(\d+)/")
        # 获取满祝福值
        result_6 = D.findall(r"/(\d+)")

        # 过滤5星
        result_7 = [(k, v) for k, v in zip(result_1, result_2) if v != "5"]
        for index, t in enumerate(result_7):
            name, level = t
            number_1 = int(result_4[index])
            number_2 = int(result_5[index])
            number_3 = int(result_6[index])

            if level in ["0", "1", "2"]:
                number = number_1
            else:
                number = compute(2, number_1, number_2, number_3)

            data[name] = {
                "名称": name,
                "id": result_3[index],
                "星级": level,
                "升级消耗": f"真黄金卷轴*{number_1}（{self.possess_num}）",
                "祝福值": f"{number_2}/{number_3}",
                "材料消耗名称": "真黄金卷轴",
                "材料消耗数量": number_1,
                "材料拥有数量": self.possess_num,
                "满进度消耗数量": number,
                "是否升级": self._number >= number,
            }
        return data

    def upgrade(self, name: str):
        """
        升级神器
        """
        params_data = {
            "投掷武器": "0",
            "小型武器": "1",
            "中型武器": "2",
            "大型武器": "3",
            "被动技能": "4",
            "伤害技能": "5",
            "特殊技能": "6",
        }
        _id: str = self.data[name]["id"]
        t = params_data[self._name]
        p = f"cmd=newAct&subtype=104&op=3&one_click=0&item_id={_id}&type={t}"
        while True:
            # 升级一次
            D.get(p)
            D.find(name=name)
            D.find(rf"{name}.*?:\d+ [\u4e00-\u9fff]+ (.*?)<br />", name)
            if "恭喜您" in D.html:
                break


def 新元婴神器():
    """
    自动升级神器
    """
    mission_list = [
        "投掷武器",
        "小型武器",
        "中型武器",
        "大型武器",
        "被动技能",
        "伤害技能",
        "特殊技能",
    ]
    i = Input()

    mission_name = i.select_mission(mission_list, "选择任务名称：")
    if mission_name is None:
        return
    i.select_upgrade(XinYuanYingShenQi, mission_name)


class SanHun:
    """
    灵枢精魄三魂一键进阶
    """

    def __init__(self):
        # 深渊积分
        self.points = get_store_points("cmd=abysstide&op=viewabyssshop")

        self.data = self.get_data()

    def get_data(self) -> dict:
        """
        获取三魂数据
        """
        data_dict = {"天魂": "1", "地魂": "2", "命魂": "3"}
        data = {}

        # 商店积分可兑换数量
        store_num = self.points // 90

        for name, _id in data_dict.items():
            D.get(f"cmd=abysstide&op=showsoul&soul_id={_id}")
            if "五阶五星" in D.html:
                continue
            # 阶段
            level = D.findall(r"阶段：(.*?)<")[0]
            # 材料消耗名称
            consume_name = D.findall(r"消耗：(.*?)\*")[0]
            # 材料消耗数量
            consume_num = int(D.findall(r"消耗：.*?\*(\d+)")[0])
            # 材料拥有数量
            possess_num = int(D.findall(r"\((\d+)\)")[0])
            # 当前进度
            now_value = int(D.findall(r"进度：(\d+)/")[0])
            # 总进度
            total_value = int(D.findall(r"进度：\d+/(\d+)")[0])

            # 满进度消耗数量
            full_value_consume_num = compute(2, consume_num, now_value, total_value)

            data[name] = {
                "名称": name,
                "id": _id,
                "阶段": level,
                "消耗": f"{consume_name}*{consume_num}（{possess_num}）",
                "进度": f"{now_value}/{total_value}",
                "材料消耗名称": consume_name,
                "材料消耗数量": consume_num,
                "材料拥有数量": possess_num,
                "积分": f"{self.points}（{store_num}）",
                "满进度消耗数量": full_value_consume_num,
                "是否升级": (possess_num + store_num) >= full_value_consume_num,
            }
        return data

    def upgrade(self, name: str):
        """
        三魂进阶
        """
        url = {
            "御魂丹-天": {
                "ten": "cmd=abysstide&op=abyssexchange&id=1&times=10",
                "one": "cmd=abysstide&op=abyssexchange&id=1&times=1",
            },
            "御魂丹-地": {
                "ten": "cmd=abysstide&op=abyssexchange&id=2&times=10",
                "one": "cmd=abysstide&op=abyssexchange&id=2&times=1",
            },
            "御魂丹-命": {
                "ten": "cmd=abysstide&op=abyssexchange&id=3&times=10",
                "one": "cmd=abysstide&op=abyssexchange&id=3&times=1",
            },
        }

        data = self.data[name]
        _id: str = data["id"]
        consume_name: str = data["材料消耗名称"]
        consume_num: int = data["材料消耗数量"]
        possess_num: int = data["材料拥有数量"]

        e = Exchange(url[consume_name], consume_num, possess_num)

        # 关闭自动斗豆兑换
        D.get(f"cmd=abysstide&op=setauto&value=0&soul_id={_id}")
        D.print_info("关闭自动斗豆兑换")

        while True:
            # 积分商店兑换材料
            e.exchange()

            # 进阶
            D.get(f"cmd=abysstide&op=upgradesoul&soul_id={_id}&times=1")
            if "恭喜您升级成功" in D.html:
                D.find(name=name)
                break
            elif "道具不足" in D.html:
                D.find(name=name)
                break

            D.find(r"进度：(.*?)&", name)

            # 更新材料拥有数量
            e.update_possess_num()


def 深渊之潮():
    """
    灵枢精魄三魂一键进阶
    """
    i = Input()
    i.select_upgrade(SanHun)


class LingShouPian:
    """
    神魔录灵兽篇一键提升
    """

    def __init__(self, fail_value: int):
        self.fail_value = fail_value

        # 问鼎天下商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=14")

        self.data = self.get_data()

    def get_data(self) -> dict:
        """
        获取灵兽篇数据
        """
        data_dict = {
            "夔牛经": "1",
            "饕餮经": "2",
            "烛龙经": "3",
            "黄鸟经": "4",
        }
        data = {}

        for name, _id in data_dict.items():
            D.get(f"cmd=ancient_gods&op=1&id={_id}")
            if "五阶五级" in D.html:
                continue

            # 等级
            level = D.findall(r"等级：(.*?)&")[0]
            # 材料消耗名称
            consume_name = D.findall(r"消耗：(.*?)\*")[0]
            # 材料消耗数量
            consume_num = int(D.findall(r"\*(\d+)")[0])
            # 材料拥有数量
            possess_num = int(D.findall(r"（(\d+)）")[0])
            # 当前祝福值
            now_value = int(D.findall(r"祝福值：(\d+)")[0])
            # 总祝福值
            total_value = int(D.findall(r"祝福值：\d+/(\d+)")[0])

            # 满祝福消耗数量
            full_value_number = compute(
                self.fail_value, consume_num, now_value, total_value
            )
            # 商店积分可兑换数量
            store_num = self.points // 40

            data[name] = {
                "名称": name,
                "id": _id,
                "等级": level,
                "消耗": f"{consume_name}*{consume_num}（{possess_num}）",
                "祝福值": f"{now_value}/{total_value}",
                "材料消耗名称": consume_name,
                "材料消耗数量": consume_num,
                "材料拥有数量": possess_num,
                "积分": f"{self.points}（{store_num}）",
                "满祝福消耗数量": f"{full_value_number}（必成再+{consume_num}）",
                "失败祝福值": self.fail_value,
                "是否升级": (possess_num + store_num)
                >= (full_value_number + consume_num),
            }
        return data

    def upgrade(self, name: str):
        """
        灵兽篇提升
        """
        url = {
            "神魔残卷": {
                "ten": "cmd=exchange&subtype=2&type=1267&times=10&costtype=14",
                "one": "cmd=exchange&subtype=2&type=1267&times=1&costtype=14",
            }
        }

        data = self.data[name]
        _id: str = data["id"]
        consume_name: str = data["材料消耗名称"]
        consume_num: int = data["材料消耗数量"]
        possess_num: int = data["材料拥有数量"]

        e = Exchange(url[consume_name], consume_num, possess_num)

        # 关闭自动斗豆兑换
        D.get(f"cmd=ancient_gods&op=5&autoBuy=0&id={_id}")
        D.print_info("关闭自动斗豆兑换")

        while True:
            # 积分商店兑换材料
            e.exchange()

            # 提升一次
            D.get(f"cmd=ancient_gods&op=6&id={_id}&times=1")
            D.find(name=name)
            D.find(r"祝福值：(.*?)<", name=name)
            if "升级失败" not in D.html:
                break

            # 更新材料拥有数量
            e.update_possess_num()


class GuZhenPian:
    """
    古阵篇一键突破
    """

    def __init__(self):
        # 问鼎天下商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=14")

        self.data = self.get_data()

    def get_data(self) -> dict:
        """
        获取古阵篇数据
        """
        data_dict = {
            "夔牛鼓": "1",
            "饕餮鼎": "2",
            "烛龙印": "3",
            "黄鸟伞": "4",
        }
        data = {}

        # 商店积分可兑换突破石数量
        t_store_num = self.points // 40
        # 突破石拥有数量
        t_possess_num = get_backpack_item_count(5153)

        for name, _id in data_dict.items():
            # 宝物详情
            D.get(f"cmd=ancient_gods&op=4&id={_id}")

            # 当前等级
            now_level = D.findall(r"等级：(\d+)")[0]
            # 最高等级
            highest_level = D.findall(r"至(\d+)")[0]
            if now_level == highest_level:
                continue

            # 突破石消耗数量
            t_consume_num = int(D.findall(r"突破石\*(\d+)")[0])
            # 碎片消耗名称
            s_consume_name = D.findall(r"\+ (.*?)\*")[0]
            # 碎片消耗数量
            s_consume_num = int(D.findall(r"碎片\*(\d+)")[0])
            # 碎片拥有数量
            s_possess_num = self._get_backpack_number(s_consume_name)

            data[name] = {
                "name": name,
                "id": _id,
                "等级": now_level,
                "消耗": f"突破石*{t_consume_num}+{s_consume_name}*{s_consume_num}",
                "碎片消耗名称": s_consume_name,
                "碎片消耗数量": s_consume_num,
                "碎片拥有数量": s_possess_num,
                "突破石消耗数量": t_consume_num,
                "突破石拥有数量": t_possess_num,
                "积分": f"{self.points}（{t_store_num}）",
                "是否升级": ((t_possess_num + t_store_num) >= t_consume_num)
                and (s_possess_num >= s_consume_num),
            }
        return data

    def _get_backpack_number(self, name: str) -> int:
        """
        获取碎片背包数量
        """
        data = {
            "夔牛碎片": 5154,
            "饕餮碎片": 5155,
            "烛龙碎片": 5156,
            "黄鸟碎片": 5157,
        }
        return get_backpack_item_count(data[name])

    def upgrade(self, name: str):
        """
        古阵篇突破
        """
        url = {
            "突破石": {
                "ten": "cmd=exchange&subtype=2&type=1266&times=10&costtype=14",
                "one": "cmd=exchange&subtype=2&type=1266&times=1&costtype=14",
            }
        }

        data = self.data[name]
        _id: str = data["id"]
        t_consume_num: int = data["突破石消耗数量"]
        t_possess_num: int = data["突破石消耗数量"]

        e = Exchange(url["突破石"], t_consume_num, t_possess_num)

        # 积分商店兑换材料
        e.exchange()

        # 突破等级
        D.get(f"cmd=ancient_gods&op=7&id={_id}")
        D.find(name=name)


def 神魔录():
    """
    神魔录：灵兽篇一键提升、古阵篇一键突破
    """
    mission_list = ["灵兽篇", "古阵篇"]

    i = Input()

    mission_name = i.select_mission(mission_list, "选择任务名称：")
    if mission_name is None:
        return

    if mission_name == "灵兽篇":
        fail_value = i.get_number("输入失败祝福值：")
        if fail_value is None:
            return
        i.select_upgrade(LingShouPian, fail_value)
    elif mission_name == "古阵篇":
        i.select_upgrade(GuZhenPian)


class AoYi:
    """
    奥义一键升级
    """

    def __init__(self, fail_value: int):
        self.fail_value = fail_value

        # 帮派祭坛商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=12")

        self.data = self.get_data()

    def get_data(self) -> dict:
        """
        获取奥义数据
        """
        data = {}
        name = "奥义"

        # 奥义
        D.get("cmd=skillEnhance&op=0")
        if "五阶&nbsp;5星" in D.html:
            return {}

        # 阶段
        level = D.findall(r"阶段：(.*?)<")[0]
        # 材料消耗名称
        consume_name = "奥秘元素"
        # 材料消耗数量
        consume_num = int(D.findall(r"\*(\d+)")[0])
        # 材料拥有数量
        possess_num = int(D.findall(r"（(\d+)）")[0])
        # 当前祝福值
        now_value = int(D.findall(r"(\d+)/")[0])
        # 总祝福值
        total_value = int(D.findall(r"\d+/(\d+)")[0])

        # 满祝福消耗数量
        full_value_consume_num = compute(
            self.fail_value, consume_num, now_value, total_value
        )
        # 商店积分可兑换数量
        store_num = self.points // 40

        data[name] = {
            "名称": name,
            "阶段": level,
            "消耗": f"{consume_name}*{consume_num}（{possess_num}）",
            "祝福值": f"{now_value}/{total_value}",
            "材料消耗名称": consume_name,
            "材料消耗数量": consume_num,
            "材料拥有数量": possess_num,
            "积分": f"{self.points}（{store_num}）",
            "满祝福消耗数量": f"{full_value_consume_num}（必成再+{consume_num}）",
            "失败祝福值": self.fail_value,
            "是否升级": (possess_num + store_num)
            >= (full_value_consume_num + consume_num),
        }
        return data

    def upgrade(self, name):
        """
        奥义升级
        """
        url = {
            "奥秘元素": {
                "ten": "cmd=exchange&subtype=2&type=1261&times=10&costtype=12",
                "one": "cmd=exchange&subtype=2&type=1261&times=1&costtype=12",
            }
        }

        data = self.data[name]
        consume_name: str = data["材料消耗名称"]
        consume_num: int = data["材料消耗数量"]
        possess_num: int = data["材料拥有数量"]

        e = Exchange(url[consume_name], consume_num, possess_num)

        # 关闭自动斗豆兑换
        D.get("cmd=skillEnhance&op=9&autoBuy=0")
        D.print_info("关闭自动斗豆兑换")

        while True:
            # 积分商店兑换材料
            e.exchange()

            # 升级
            D.get("cmd=skillEnhance&op=2")
            D.find(name=name)
            D.find(r"祝福值：(.*?) ", name)
            if "升星失败" not in D.html:
                break

            # 更新材料拥有数量
            e.update_possess_num()


class JiNengLan:
    """
    奥义技能栏一键升级
    """

    def __init__(self, fail_value: int):
        self.fail_value = fail_value

        # 帮派祭坛商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=12")

        self.data = self.get_data()

    def get_data(self) -> dict:
        """
        获取奥义技能栏数据
        """
        data = {}

        # 技能栏
        D.get("cmd=skillEnhance&op=0&view=storage")
        for _id in D.findall(r'storage_id=(\d+)">查看详情'):
            # 查看详情
            D.get(f"cmd=skillEnhance&op=4&storage_id={_id}")

            # 奥义名称
            name = D.findall(r"<br />=(.*?)=")[0]
            # 当前等级
            level = int(D.findall(r"当前等级：(\d+)")[0])
            # 材料消耗名称
            consume_name = D.findall(r"升级消耗：(.*?)\*")[0]
            # 材料消耗数量
            consume_num = int(D.findall(r"\*(\d+)")[0])
            # 材料拥有数量
            possess_num = int(D.findall(r"（(\d+)）")[0])
            # 当前祝福值
            now_value = int(D.findall(r"祝福值：(\d+)")[0])
            # 总祝福值
            total_value = int(D.findall(r"祝福值：\d+/(\d+)")[0])

            if level <= 7:
                # 7级（含）前失败祝福值
                fail_value = self.fail_value
            else:
                # 7级后失败祝福值
                fail_value = 2

            # 满祝福消耗数量
            full_value_consume_num = compute(
                fail_value, consume_num, now_value, total_value
            )
            # 商店积分可兑换数量
            store_num = self.points // 40

            data[name] = {
                "名称": name,
                "id": _id,
                "当前等级": level,
                "升级消耗": f"{consume_name}*{consume_num}（{possess_num}）",
                "祝福值": f"{now_value}/{total_value}",
                "材料消耗名称": consume_name,
                "材料消耗数量": consume_num,
                "材料拥有数量": possess_num,
                "积分": f"{self.points}（{store_num}）",
                "满祝福消耗数量": f"{full_value_consume_num}（必成再+{consume_num}）",
                "失败祝福值": fail_value,
                "是否升级": (possess_num + store_num)
                >= (full_value_consume_num + consume_num),
            }
        return data

    def upgrade(self, name: str):
        """
        奥义技能栏升级
        """
        url = {
            "四灵魂石": {
                "ten": "cmd=exchange&subtype=2&type=1262&times=10&costtype=12",
                "one": "cmd=exchange&subtype=2&type=1262&times=1&costtype=12",
            }
        }

        data = self.data[name]
        _id: str = data["id"]
        consume_name: str = data["材料消耗名称"]
        consume_num: int = data["材料消耗数量"]
        possess_num: int = data["材料拥有数量"]

        e = Exchange(url[consume_name], consume_num, possess_num)

        # 关闭自动斗豆兑换
        D.get(f"cmd=skillEnhance&op=10&storage_id={_id}&auto_buy=0")
        D.print_info("关闭自动斗豆兑换")

        while True:
            # 积分商店兑换材料
            e.exchange()

            # 升级
            D.get(f"cmd=skillEnhance&op=5&storage_id={_id}")
            D.find(name=name)
            D.find(r"祝福值：(.*?) ", name)
            if "升星失败" not in D.html:
                break

            # 更新材料拥有数量
            e.update_possess_num()


def 奥义():
    """
    奥义、技能栏一键升级
    """
    mission_list = ["奥义", "技能栏"]
    i = Input()

    mission_name = i.select_mission(mission_list, "选择任务名称：")
    if mission_name is None:
        return

    if mission_name == "奥义":
        fail_value = i.get_number("输入失败祝福值：")
        if fail_value is None:
            return
        i.select_upgrade(AoYi, fail_value)
    elif mission_name == "技能栏":
        fail_value = i.get_number("输入7级（含）前失败祝福值：")
        if fail_value is None:
            return
        i.select_upgrade(JiNengLan, fail_value)
