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


def store_exchange(ten_p: str, one_p: str, number: int):
    """
    积分商店兑换材料
    """
    ten_number, one_number = divmod(number, 10)
    while ten_number:
        D.get(ten_p)
        D.find()
        if "成功" in D.html:
            ten_number -= 1
        if "不足" in D.html:
            return
    while one_number:
        D.get(one_p)
        D.find()
        if "成功" in D.html:
            one_number -= 1
        if "不足" in D.html:
            return
    print("--" * 20)


def print_info(data: dict):
    """
    打印信息
    """
    for name, _dict in data.items():
        print("--" * 20)
        print(f"名称：{name}")
        for k, v in _dict.items():
            print(f"{k}：{v}")


class ShenZhuang:
    """
    神装自动兑换进阶
    """

    def __init__(self, fail_value: int):
        self.fail_value = fail_value
        self.data = self._get_data()
        self._print_info(self.data)

    def _get_data(self) -> dict:
        """
        获取神装数据，不包含满阶和必成数据
        """
        data_dict = {
            "神兵": {
                "id": 0,
                "backpack_id": 3573,
                "store_params": "cmd=arena&op=queryexchange",
            },
            "神铠": {
                "id": 1,
                "backpack_id": 3574,
                "store_params": "cmd=arena&op=queryexchange",
            },
            "神羽": {
                "id": 2,
                "backpack_id": 3575,
                "store_params": "cmd=exchange&subtype=10&costtype=1",
            },
            "神兽": {
                "id": 3,
                "backpack_id": 3576,
                "store_params": "cmd=exchange&subtype=10&costtype=2",
            },
            "神饰": {
                "id": 4,
                "backpack_id": 3631,
                "store_params": "cmd=exchange&subtype=10&costtype=2",
            },
            "神履": {
                "id": 5,
                "backpack_id": 3636,
                "store_params": "cmd=exchange&subtype=10&costtype=3",
            },
        }
        data = {}
        for name, _dict in data_dict.items():
            _id = _dict["id"]
            b_id = _dict["backpack_id"]
            store_params = _dict["store_params"]

            # 神装
            D.get(f"cmd=outfit&op=0&magic_outfit_id={_id}")
            if "10阶" in D.html:
                continue
            if "必成" in D.html:
                continue

            # 获取阶层
            result_1 = D.findall(r"阶层：(.*?)<")[0]
            # 获取进阶消耗名称、数量
            result_2, result_3 = D.findall(r"进阶消耗：(.*?)\*(\d+)")[0]
            # 获取当前祝福值、满祝福值
            result_4, result_5 = D.findall(r"祝福值：(\d+)/(\d+)")[0]

            number_1 = int(result_3)
            number_2 = int(result_4)
            number_3 = int(result_5)
            number_4 = self._compute(number_1, number_2, number_3)
            # 获取背包进阶材料数量
            number_5 = get_backpack_item_count(b_id)
            # 获取进阶材料的商店积分
            number_6 = get_store_points(store_params)
            data[name] = {
                "id": _id,
                "阶层": result_1,
                "进阶消耗名称": result_2,
                "进阶消耗数量": number_1,
                "祝福值": f"{number_2}/{number_3}",
                "满祝福消耗数量": number_4,
                "材料数量": number_5,
                "商店积分": number_6,
                "是否升级": (number_5 + (number_6 // 40)) >= number_4,
            }
        return data

    def _compute(self, n_1: int, n_2: int, n_3: int) -> int:
        """
        计算神装升级至满祝福消耗所需材料数量（额外增加两次升级消耗）

        Args:
            n_1: 升级一次消耗数量
            n_2: 当前祝福值
            n_3: 满祝福值
        """
        return (((n_3 - n_2) // self.fail_value) + 2) * n_1

    def _print_info(self, data: dict):
        """
        打印神装信息
        """
        print_info(data)
        print("--" * 20)
        print(f"失败祝福值：{self.fail_value}")

    def upgrade(self, name: str):
        """
        神装进阶
        """
        _id: int = self.data[name]["id"]
        result: str = self.data[name]["进阶消耗名称"]
        number_1: int = self.data[name]["进阶消耗数量"]
        number_2: int = self.data[name]["材料数量"]

        # 关闭自动斗豆兑换神装进阶材料
        D.get(f"cmd=outfit&op=4&auto_buy=2&magic_outfit_id={_id}")
        D.find(r"\|<br />(.*?)<br />")

        while True:
            print("--" * 20)
            if number_1 > number_2:
                self._store_exchange(result, (number_1 - number_2))
                number_2 = number_1

            # 进阶
            D.get(f"cmd=outfit&op=1&magic_outfit_id={_id}")
            D.find(r"神履.*?<br />(.*?)<br />", name)
            D.find(r"祝福值：(.*?)<", name)
            if "进阶失败" in D.html:
                # 更新背包材料数量
                if (number_2 - number_1) >= 0:
                    number_2 -= number_1
            else:
                break

    def _store_exchange(self, name: str, number: int):
        """
        神装积分商店兑换
        """
        data = {
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
        ten_p = data[name]["ten"]
        one_p = data[name]["one"]
        store_exchange(ten_p, one_p, number)


class ShenJi:
    """
    神技自动兑换升级
    """

    def __init__(self):
        # 神秘精华数量
        self.backpack_number = get_backpack_item_count(3567)
        self.data = self._get_data(self._get_data_id())
        self._print_info(self.data)

    def _get_data_id(self) -> list:
        """
        获取神装附带技能id，不包含满级id
        """
        data = []
        for _id in range(6):
            # 神装
            D.get(f"cmd=outfit&op=0&magic_outfit_id={_id}")
            data += D.findall(r'skill_id=(\d+)">升级十次.*?等级：(\d+)')

        data_id = []
        for _id, level in data:
            if level != "10":
                data_id.append(_id)
        return data_id

    def _get_data(self, data_id: str) -> dict:
        """
        获取神技详情数据
        """
        data = {}
        for _id in data_id:
            D.get(f"cmd=outfit&op=2&magic_skill_id={_id}")
            # 神技名称
            result_1 = D.findall(r"<br />=(.*?)=<a")[0]
            # 当前等级
            result_2 = D.findall(r"当前等级：(\d+)")[0]
            # 升级消耗
            result_3 = D.findall(r"\*(\d+)<")[0]
            # 升级成功率
            result_4 = D.findall(r"升级成功率：(.*?)<")[0]
            # 当前效果
            result_5 = D.findall(r"当前效果：(.*?)<")[0]
            data[result_1] = {
                "id": _id,
                "当前等级": int(result_2),
                "升级消耗": int(result_3),
                "升级成功率": result_4,
                "当前效果": result_5,
            }
        return data

    def _print_info(self, data: dict):
        """
        打印神技信息
        """
        print_info(data)
        print("--" * 20)
        print(f"神秘精华数量：{self.backpack_number}")

    def upgrade(self, name: str, store: str):
        """
        神技升级
        """
        _id = self.data[name]["id"]
        # 升级消耗
        number = self.data[name]["升级消耗"]

        # 关闭自动斗豆兑换神技升级材料
        D.get(f"cmd=outfit&op=8&auto_buy=2&magic_outfit_id={_id}")
        D.find(r"\|<br />(.*?)<br />")

        while True:
            print("--" * 20)
            if number > self.backpack_number:
                self._store_exchange(store, (number - self.backpack_number))
                self.backpack_number = get_backpack_item_count(3567)

            # 升级
            D.get(f"cmd=outfit&op=3&magic_skill_id={_id}")
            D.find(r"套装强化</a><br />(.*?)<br />", name)
            if "升级失败" in D.html:
                # 更新背包材料数量
                if (self.backpack_number - number) >= 0:
                    self.backpack_number -= number
            else:
                break

    def _store_exchange(self, name: str, number: int):
        """
        积分商店兑换神秘精华
        """
        data = {
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
        ten_p = data[name]["ten"]
        one_p = data[name]["one"]
        store_exchange(ten_p, one_p, number)


def 神装进阶():
    while True:
        print("--" * 20)
        print("基本失败祝福值是 2，活动期间是 2n 倍")
        input_1 = input("输入神装失败祝福值：")
        if input_1 == "q":
            return True
        if input_1.isdigit():
            break
        print(">>>只能输入数字")

    while True:
        s = ShenZhuang(int(input_1))
        if not s.data:
            print("--" * 20)
            print(">>>神装全部已满级")
            break
        while True:
            print("--" * 20)
            input_2 = input("选择进阶神装名称：")
            if input_2 == "q":
                return True
            if input_2 not in s.data:
                print(f">>>不存在：{input_2}")
                continue
            if s.data[input_2]["是否升级"]:
                s.upgrade(input_2)
                break
            else:
                print(f">>>{input_2}材料不足以满祝福，不能升级")


def 神技升级():
    store_category = {
        "矿洞": get_store_points("cmd=exchange&subtype=10&costtype=3"),
        "掠夺": get_store_points("cmd=exchange&subtype=10&costtype=2"),
        "踢馆": get_store_points("cmd=exchange&subtype=10&costtype=1"),
        "竞技场": get_store_points("cmd=arena&op=queryexchange"),
    }
    while True:
        s = ShenJi()
        if not s.data:
            print("--" * 20)
            print(">>>神技全部已满级")
            break
        while True:
            print("--" * 20)
            input_1 = input("选择升级神技名称：")
            if input_1 == "q":
                return True
            if input_1 in s.data:
                break
            print(f">>>不存在：{input_1}")
        while True:
            print("--" * 20)
            for k, v in store_category.items():
                print(f"{k}：{v}")
            input_2 = input("选择积分兑换商店：")
            if input_2 == "q":
                return True
            if input_2 in store_category:
                s.upgrade(input_1, input_2)
                break
            print(f">>>不存在：{input_2}")


def 神装():
    """
    神装自动积分兑换材料并进阶，始终不会使用斗豆兑换
    """
    print("任意位置输入 q 退出当前账号任务")
    print("--" * 20)
    print("始终不会使用斗豆自动兑换")
    category = ["神装进阶", "神技升级"]
    while True:
        while True:
            print("--" * 20)
            for i, n in enumerate(category):
                print(f"{i + 1}.{n}")
            _input = input("选择神装类别名称：")
            if _input == "q":
                return
            if _input in category:
                break
            print(f">>>不存在：{_input}")

        if _input == "神装进阶":
            if 神装进阶():
                return
        elif _input == "神技升级":
            if 神技升级():
                return


class DuoBaoQiBing:
    """
    五行夺宝奇兵自动投掷
    """

    def __init__(self):
        self.exploits = self._get_exploits()

    def _get_exploits(self) -> int:
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
        while True:
            if input_exploits > self.exploits:
                break

            # 投掷
            D.get("cmd=element&subtype=7")
            if "【夺宝奇兵】" in D.html:
                D.find(r"<br /><br />(.*?)<br />")
                result = D.find(r"拥有:(\d+)", "战功")
                D.find(r"进度：(.*?)<", "进度")
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
    五行夺宝奇兵选择太空探宝场景投掷
    """
    print("任意位置输入 q 退出当前账号任务")
    while True:
        print("--" * 20)
        print("夺宝奇兵太空探宝16倍场景投掷")
        d = DuoBaoQiBing()
        while True:
            print("--" * 20)
            print(f"战功：{d.exploits}")
            _input = input("输入低于多少战功时结束投掷：")
            if _input == "q":
                return
            if _input.isdigit():
                d.pelted(int(_input))
                break
            print(">>>只能输入数字")


class JiangHuChangMeng:
    """
    江湖长梦商店兑换
    """

    def __init__(self):
        # 江湖长梦商店积分
        self.points: int = get_store_points("cmd=longdreamexchange")
        # 商店材料数据
        self.data = self._get_data()
        # 打印商店数据
        self._print_info(self.data)

    def _get_data(self) -> dict:
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
        data_dict = {}

        for p in params:
            D.get(p)
            # id、名称、售价、已售、限售
            data += D.findall(r"_id=(\d+).*?>(.*?)\*1.*?(\d+).*?(\d+)/(\d+)")

        for d in data:
            _id, name, 售价, 已售, 限售 = d
            if 已售 == 限售:
                continue
            data_dict[name] = {
                "id": _id,
                "售价": 售价,
                "购买次数": f"{已售}/{限售}",
            }
        return data_dict

    def _print_info(self, data: dict):
        """
        打印江湖长梦商店材料数据
        """
        print_info(data)
        print("--" * 20)
        print(f"商店积分：{self.points}")

    def exchange(self, name: str, number: int):
        """
        江湖长梦商店材料兑换
        """
        _id: str = self.data[name]["id"]
        for i in range(number):
            _name = f"{name}-{i + 1}"
            D.get(f"cmd=longdreamexchange&op=exchange&key_id={_id}")
            if "成功" not in D.html:
                D.find(r"】<br />(.*?)<", _name)
                break
            D.find(r"侠士碎片</a><br />(.*?)<", _name)


class QiCheng:
    """
    挑战副本柒承的忙碌日常
    """

    def __init__(self):
        # 追忆香炉数量
        self.backpack_number = get_backpack_item_count(6477)
        # 江湖长梦商店积分
        self.points: int = get_store_points("cmd=longdreamexchange")

    def challenge(self, number: int):
        """
        优先级：战斗 > 奇遇（视而不见）> 商店（不购买）
        """
        p = "cmd=jianghudream&op=chooseEvent&event_id="
        for _ in range(number):
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


def 江湖长梦_商店兑换():
    while True:
        j = JiangHuChangMeng()
        while True:
            print("--" * 20)
            input_1 = input("输入兑换材料名称：")
            if input_1 == "q":
                return True
            if input_1 in j.data:
                break
            print(f">>>不存在：{input_1}")
        while True:
            print("--" * 20)
            input_2 = input("输入兑换数量：")
            if input_2 == "q":
                return True
            if input_2.isdigit():
                j.exchange(input_1, int(input_2))
                break
            print(">>>只能输入数字")


def 柒承的忙碌日常():
    while True:
        q = QiCheng()
        while True:
            print("--" * 20)
            print(f"追忆香炉数量：{q.backpack_number}")
            print(f"商店积分：{q.points}")
            _input = input("输入开启次数：")
            if _input == "q":
                return True
            if _input.isdigit():
                q.challenge(int(_input))
                break
            print(">>>只能输入数字")


def 江湖长梦():
    """
    商店兑换及副本挑战（柒承的忙碌日常）
    """
    print("任意位置输入 q 退出当前账号任务")
    category = ["江湖长梦商店兑换", "柒承的忙碌日常"]
    while True:
        print("--" * 20)
        for i, n in enumerate(category):
            print(f"{i + 1}.{n}")
        _input = input("选择任务：")
        if _input == "q":
            return
        if _input in category:
            break
        print(f">>>不存在：{_input}")

    if _input == "江湖长梦商店兑换":
        if 江湖长梦_商店兑换():
            return
    elif _input == "柒承的忙碌日常":
        if 柒承的忙碌日常():
            return


class XingPan:
    """
    星石兑换合成
    """

    def __init__(self):
        # 幻境商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=9")
        self.data = self._get_data()
        self._print_info(self.data)
        self.合成次数 = {}
        self._level_ties = {
            1: 5,  # 5个1级星石合成一个2级星石
            2: 4,  # 4个2级星石合成一个3级星石
            3: 4,  # 4个3级星石合成一个4级星石
            4: 3,  # 3个4级星石合成一个5级星石
            5: 3,  # 3个5级星石合成一个6级星石
            6: 2,  # 2个6级星石合成一个7级星石
        }

    def _get_store_max_number(self, name: str) -> int:
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

    def _get_data(self) -> dict:
        """
        获取1~6级星石数量及2~7级星石合成id
        """
        data_dict = {
            "日曜石": 1,
            "玛瑙石": 2,
            "迅捷石": 3,
            "月光石": 4,
            "翡翠石": 5,
            "紫黑玉": 6,
            "狂暴石": 7,
            "神愈石": 8,
        }
        data = {}
        for name, gem in data_dict.items():
            D.get(f"cmd=astrolabe&op=showgemupgrade&gem_type={gem}")
            result_1 = D.findall(r"gem=(\d+)")[1:]
            result_2 = D.findall(r"（(\d+)）")[1:]
            # 2~7级星石合成id
            data_id = {i + 2: item for i, item in enumerate(result_1)}
            # 1~6级星石数量
            data_number = {i + 1: int(item) for i, item in enumerate(result_2)}
            data[name] = {
                "id": data_id,
                "number": data_number,
                "幻境可兑换数量": self._get_store_max_number(name),
            }
        return data

    def _print_info(self, data: dict):
        """
        打印星石数据
        """
        for name, _dict in data.items():
            print("--" * 20)
            print(f"名称：{name}")
            for k, v in _dict.items():
                if k == "id":
                    continue
                elif k == "number":
                    for level, number in v.items():
                        print(f"{level}级：{number}")
                else:
                    print(f"{k}：{v}")
        print("--" * 20)
        print(f"商店积分：{self.points}")

    def _get_level_number(self, name: str, level: int) -> int:
        """
        获取星石某级数量
        """
        return self.data[name]["number"][level]

    def compute(self, name: str, level: int, number: int) -> tuple[int, int]:
        """
        返回星石等级及兑换数量

        Args:
            name: 星石名称
            level: 合成星石等级
            number: 合成星石数量
        """
        level -= 1
        # 拥有数量
        possess_number = self._get_level_number(name, level)
        # 消耗数量
        deplete_number = self._level_ties[level] * number
        if possess_number >= deplete_number:
            self.合成次数[level + 1] = number
            return level, 0
        else:
            exchange_number = deplete_number - possess_number
            self.合成次数[level + 1] = number
            if level == 1:
                return level, exchange_number
            else:
                return self.compute(name, level, exchange_number)

    def exchange(self, name: str, number: int):
        """
        幻境商店兑换材料
        """
        data = {
            "翡翠石": 1233,
            "玛瑙石": 1234,
            "迅捷石": 1235,
            "紫黑玉": 1236,
            "日曜石": 1237,
            "月光石": 1238,
        }
        if name not in data:
            return

        t = data[name]
        quotient, remainder = divmod(number, 10)
        for _ in range(quotient):
            # 兑换10个
            D.get(f"cmd=exchange&subtype=2&type={t}&times=10&costtype=9")
            D.find(name="幻境商店")
        for _ in range(remainder):
            # 兑换1个
            D.get(f"cmd=exchange&subtype=2&type={t}&times=1&costtype=9")
            D.find(name="幻境商店")
        print("--" * 20)

    def 合成(self, name: str):
        """
        星石合成
        """
        id_dict = self.data[name]["id"]
        data = dict(sorted(self.合成次数.items()))
        for level, number in data.items():
            _id = id_dict[level]
            for _ in range(number):
                D.get(f"cmd=astrolabe&op=upgradegem&gem={_id}")
                D.find(r"规则</a><br />(.*?)<", f"{level}级{name}")


def 星盘():
    """
    星石自动兑换合成
    """
    print("任意位置输入 q 退出当前账号任务")
    print("--" * 20)
    while True:
        x = XingPan()
        while True:
            print("--" * 20)
            input_1 = input("输入合成星石名称：")
            if input_1 == "q":
                return
            if input_1 in x.data:
                break
            print(f">>>不存在：{input_1}")
        while True:
            print("--" * 20)
            input_2 = input("输入合成星石等级（2~7）：")
            if input_2 == "q":
                return
            if not input_2.isdigit():
                print(">>>只能输入数字")
                continue
            if input_2 in ["2", "3", "4", "5", "6", "7"]:
                break
            else:
                print(">>>合成星石等级只能是2~7级")
        while True:
            print("--" * 20)
            input_3 = input(f"输入合成{input_2}级星石数量：")
            if input_3 == "q":
                return
            if not input_3.isdigit():
                print(">>>只能输入数字")
                continue
            if input_3 == "0":
                break

            store_number = x.data[input_1]["幻境可兑换数量"]
            level, number = x.compute(input_1, int(input_2), int(input_3))
            if store_number >= number:
                x.exchange(input_1, int(number))
                x.合成(input_1)
                break
            print(">>>幻境商店兑换积分不足或不可兑换")
            print(">>>输入 0 重新开始")


class XinYuanYingShenQi:
    """
    新元婴神器自动升级
    """

    def __init__(self, name: str):
        self._name = name
        self._number = self._get_number()
        self.data = self._get_data(self._name)
        self._print_info(self.data)

    def _get_data(self, name: str) -> dict:
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
                number = self._compute(number_1, number_2, number_3)

            data[name] = {
                "id": result_3[index],
                "星级": level,
                "升级消耗": f"真黄金卷轴*{number_1}（{self._number}）",
                "祝福值": f"{number_2}/{number_3}",
                "满祝福消耗数量": number,
                "是否升级": self._number >= number,
            }
        return data

    def _get_number(self) -> int:
        """
        获取真黄金卷轴数量
        """
        # 新元婴神器
        D.get("cmd=newAct&subtype=104&op=1&type=3")
        result = D.findall(r"真黄金卷轴：(\d+)")[0]
        return int(result)

    def _compute(self, n_1: int, n_2: int, n_3: int) -> int:
        """
        计算神器升级至满祝福消耗所需材料数量（额外增加一次升级消耗）

        Args:
            n_1: 升级一次消耗数量
            n_2: 当前祝福值
            n_3: 满祝福值
        """
        # 失败祝福值
        fail_value = 2
        return (((n_3 - n_2) // fail_value) + 1) * n_1

    def _print_info(self, data: dict):
        """
        打印神器信息
        """
        print_info(data)

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
        _id = self.data[name]["id"]
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
    print("任意位置输入 q 退出当前账号任务")
    category = [
        "投掷武器",
        "小型武器",
        "中型武器",
        "大型武器",
        "被动技能",
        "伤害技能",
        "特殊技能",
    ]
    while True:
        print("--" * 20)
        for i, n in enumerate(category):
            print(f"{i + 1}.{n}")
        input_1 = input("选择神器类别名称：")
        if input_1 == "q":
            return
        if input_1 in category:
            break
        print(f">>>不存在：{input_1}")
    while True:
        x = XinYuanYingShenQi(input_1)
        if not x.data:
            print("--" * 20)
            print(f">>>{input_1}全部已满级")
            break
        while True:
            print("--" * 20)
            input_2 = input("输入升级神器名称：")
            if input_2 == "q":
                return
            if input_2 not in x.data:
                print(f">>>不存在：{input_2}")
                continue
            if x.data[input_2]["是否升级"]:
                x.upgrade(input_2)
                break
            else:
                print(f">>>{input_2} 满祝福材料不足")


class SanHun:
    """
    灵枢精魄三魂自动兑换进阶
    """

    def __init__(self):
        self.points = get_store_points("cmd=abysstide&op=viewabyssshop")
        self.data = self._get_data()
        self._print_info(self.data)

    def _get_data(self) -> dict:
        """
        获取三魂数据
        """
        data_dict = {"天魂": 1, "地魂": 2, "命魂": 3}
        data = {}
        for name, _id in data_dict.items():
            D.get(f"cmd=abysstide&op=showsoul&soul_id={_id}")
            if "五阶五星" in D.html:
                continue
            # 阶段
            result_1 = D.findall(r"阶段：(.*?)<")[0]
            # 消耗名称
            result_2 = D.findall(r"消耗：(.*?)\*")[0]
            # 消耗数量
            result_3 = D.findall(r"消耗：.*?\*(\d+)")[0]
            # 材料数量
            result_4 = D.findall(r"\((\d+)\)")[0]
            # 当前进度
            result_5 = D.findall(r"进度：(\d+)/")[0]
            # 总进度
            result_6 = D.findall(r"进度：\d+/(\d+)")[0]

            number_1 = int(result_3)
            number_2 = int(result_4)
            number_3 = int(result_5)
            number_4 = int(result_6)
            number_5 = self._compute(number_1, number_3, number_4)
            data[name] = {
                "id": _id,
                "阶段": result_1,
                "消耗名称": result_2,
                "消耗数量": number_1,
                "当前进度": number_3,
                "总进度": number_4,
                "满进度消耗数量": number_5,
                "材料数量": number_2,
                "是否升级": (number_2 + (self.points // 90)) >= number_5,
            }
        return data

    def _compute(self, n_1: int, n_2: int, n_3: int) -> int:
        """
        计算三魂进阶至满进度消耗所需材料数量

        Args:
            n_1: 进阶一次消耗数量
            n_2: 当前进度
            n_3: 总进度
        """
        return ((n_3 - n_2) // 2) * n_1

    def _print_info(self, data: dict):
        """
        打印三魂数据
        """
        print_info(data)
        print("--" * 20)
        print(f"商店积分：{self.points}")

    def upgrade(self, name: str):
        """
        三魂进阶
        """
        _id: int = self.data[name]["id"]
        result: str = self.data[name]["消耗名称"]
        number_1: int = self.data[name]["消耗数量"]
        number_2: int = self.data[name]["材料数量"]
        number_3: int = self.data[name]["当前进度"]
        number_4: int = self.data[name]["总进度"]

        # 关闭斗豆自动兑换
        D.get(f"cmd=abysstide&op=setauto&value=0&soul_id={_id}")

        while True:
            print("--" * 20)
            if (number_4 - number_3) >= 20:
                t = 10
                number_5 = number_1 * 10
            else:
                t = 1
                number_5 = number_1

            if number_5 > number_2:
                self._store_exchange(result, (number_5 - number_2))
                number_2 = number_5

            # 进阶十次
            D.get(f"cmd=abysstide&op=upgradesoul&soul_id={_id}&times={t}")
            if "恭喜您升级成功" in D.html:
                D.find(name=name)
                break
            elif "道具不足" in D.html:
                D.find(name=name)
                break

            result_1 = D.find(r"进度：(.*?)&", f"{name}-进度")
            # 当前进度、总进度
            result_2, result_3 = result_1.split("/")
            number_3 = int(result_2)
            number_4 = int(result_3)
            # 更新背包材料数量
            if (number_2 - number_5) >= 0:
                number_2 -= number_5

    def _store_exchange(self, name: str, number: int):
        """
        深渊黑商兑换材料
        """
        data = {
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
        ten_p = data[name]["ten"]
        one_p = data[name]["one"]
        store_exchange(ten_p, one_p, number)


def 深渊之潮():
    """
    灵枢精魄三魂自动兑换进阶
    """
    print("任意位置输入 q 退出当前账号任务")
    print("--" * 20)
    print("优先进阶十次，尾数进阶一次")
    print("始终不会使用斗豆自动兑换")
    while True:
        s = SanHun()
        if not s.data:
            print("--" * 20)
            print(">>>三魂全部已满级")
            break
        while True:
            print("--" * 20)
            _input = input("选择进阶三魂名称：")
            if _input == "q":
                return True
            if _input not in s.data:
                print(f">>>不存在：{_input}")
                continue
            if s.data[_input]["是否升级"]:
                s.upgrade(_input)
                break
            else:
                print(">>>材料不足以满进度，不能进阶")


class LingShouPian:
    """
    神魔录灵兽篇自动兑换提升
    """

    def __init__(self, fail_value: int):
        # 问鼎天下商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=14")
        self.fail_value = fail_value
        self.data = self._get_data()
        self._print_info(self.data)

    def _get_data(self) -> dict:
        """
        获取灵兽篇数据
        """
        data_dict = {"夔牛经": 1, "饕餮经": 2, "烛龙经": 3, "黄鸟经": 4}
        data = {}
        for name, _id in data_dict.items():
            D.get(f"cmd=ancient_gods&op=1&id={_id}")
            if "五阶五级" in D.html:
                continue
            # 等级
            result_1 = D.findall(r"等级：(.*?)&")[0]
            # 消耗数量
            result_2 = D.findall(r"\*(\d+)")[0]
            # 神魔残卷数量
            result_3 = D.findall(r"（(\d+)）")[0]
            # 当前祝福值
            result_4 = D.findall(r"祝福值：(\d+)")[0]
            # 总祝福值
            result_5 = D.findall(r"祝福值：\d+/(\d+)")[0]

            number = self._compute(int(result_2), int(result_4), int(result_5))
            data[name] = {
                "id": _id,
                "等级": result_1,
                "消耗数量": int(result_2),
                "祝福值": f"{result_4}/{result_5}",
                "满祝福消耗数量": number,
                "材料数量": int(result_3),
                "是否升级": (int(result_3) + (self.points // 40)) >= number,
            }
        return data

    def _compute(self, n_1: int, n_2: int, n_3: int) -> int:
        """
        计算灵兽提升至满祝福值消耗所需材料数量（额外提升两次）

        Args:
            n_1: 提升一次消耗数量
            n_2: 当前祝福值
            n_3: 总祝福值
        """
        return (((n_3 - n_2) // self.fail_value) + 2) * n_1

    def _print_info(self, data: dict):
        """
        打印灵兽篇数据
        """
        print_info(data)
        print("--" * 20)
        print(f"问鼎天下商店积分：{self.points}")
        print(f"失败祝福值：{self.fail_value}")

    def upgrade(self, name: str):
        """
        灵兽篇提升
        """
        _id: int = self.data[name]["id"]
        number_1: int = self.data[name]["消耗数量"]
        number_2: int = self.data[name]["材料数量"]

        # 关闭斗豆自动兑换
        D.get(f"cmd=ancient_gods&op=5&autoBuy=0&id={_id}")

        while True:
            print("--" * 20)
            if number_1 > number_2:
                self._store_exchange("神魔残卷", (number_1 - number_2))
                number_2 = number_1

            # 提升一次
            D.get(f"cmd=ancient_gods&op=6&id={_id}&times=1")
            D.find(name=name)
            D.find(r"祝福值：(.*?)<", name=name)
            if "升级成功" in D.html:
                break
            elif "所需材料不足" in D.html:
                break

            # 升级失败更新背包材料数量
            if (number_2 - number_1) >= 0:
                number_2 -= number_1

    def _store_exchange(self, name: str, number: int):
        """
        问鼎天下兑换材料
        """
        data = {
            "神魔残卷": {
                "ten": "cmd=exchange&subtype=2&type=1267&times=10&costtype=14",
                "one": "cmd=exchange&subtype=2&type=1267&times=1&costtype=14",
            }
        }
        ten_p = data[name]["ten"]
        one_p = data[name]["one"]
        store_exchange(ten_p, one_p, number)


class GuZhenPian:
    """
    古阵篇自动兑换突破
    """

    def __init__(self):
        # 问鼎天下商店积分
        self.points = get_store_points("cmd=exchange&subtype=10&costtype=14")
        # 突破石数量
        self.number = get_backpack_item_count(5153)
        self.data = self._get_data()
        self._print_info(self.data)

    def _get_data(self) -> dict:
        """
        获取古阵篇数据
        """
        data_dict = {"夔牛鼓": 1, "饕餮鼎": 2, "烛龙印": 3, "黄鸟伞": 4}
        data = {}
        for name, _id in data_dict.items():
            D.get(f"cmd=ancient_gods&op=4&id={_id}")
            # 当前等级
            now_level = D.findall(r"等级：(\d+)")[0]
            # 最高等级
            highest_level = D.findall(r"至(\d+)")[0]
            if now_level == highest_level:
                continue
            # 突破石消耗数量
            result_1 = D.findall(r"突破石\*(\d+)")[0]
            # 碎片消耗名称
            result_2 = D.findall(r"\+ (.*?)\*")[0]
            # 碎片消耗数量
            result_3 = D.findall(r"碎片\*(\d+)")[0]

            _number = self._get_backpack_number(result_2)
            result_4 = f"突破石*{result_1}（{self.number}）"
            result_5 = f"{result_2}*{result_3}（{_number}）"
            data[name] = {
                "id": _id,
                "等级": now_level,
                "消耗": f"{result_4}+ {result_5}",
                "突破石消耗数量": int(result_1),
                "是否升级": self._compute(int(result_1), int(result_3), _number),
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

    def _compute(self, n_1: int, n_2: int, n_3: int) -> bool:
        """
        计算材料数量是否充足

        Args:
            n_1: 突破石消耗数量
            n_2: 碎片消耗数量
            n_3: 碎片背包数量
        """
        number_1 = (self.number + (self.points // 40)) - n_1
        number_2 = n_3 - n_2
        if number_1 >= 0 and number_2 >= 0:
            return True
        return False

    def _print_info(self, data: dict):
        """
        打印灵兽篇数据
        """
        print_info(data)
        print("--" * 20)
        print(f"问鼎天下商店积分：{self.points}")

    def upgrade(self, name: str):
        """
        古阵篇突破
        """
        _id: int = self.data[name]["id"]
        number: int = self.data[name]["突破石消耗数量"]

        while True:
            print("--" * 20)
            if number > self.number:
                self._store_exchange("突破石", (number - self.number))

            # 突破等级
            D.get(f"cmd=ancient_gods&op=7&id={_id}")
            D.find(name=name)
            if "升级成功" in D.html:
                break
            elif "升级所需碎片不足" in D.html:
                break

    def _store_exchange(self, name: str, number: int):
        """
        问鼎天下兑换材料
        """
        data = {
            "突破石": {
                "ten": "cmd=exchange&subtype=2&type=1266&times=10&costtype=14",
                "one": "cmd=exchange&subtype=2&type=1266&times=1&costtype=14",
            }
        }
        ten_p = data[name]["ten"]
        one_p = data[name]["one"]
        store_exchange(ten_p, one_p, number)


def 灵兽篇():
    """
    自动兑换材料提升
    """
    while True:
        print("--" * 20)
        input_1 = input("输入失败祝福值：")
        if input_1 == "q":
            return True
        if input_1.isdigit():
            break
        print(">>>只能输入数字")

    while True:
        ling = LingShouPian(int(input_1))
        if not ling.data:
            print("--" * 20)
            print(">>>灵兽篇全部已满级")
            break
        while True:
            print("--" * 20)
            input_2 = input("选择提升灵兽名称：")
            if input_2 == "q":
                return True
            if input_2 not in ling.data:
                print(f">>>不存在：{input_2}")
                continue
            if ling.data[input_2]["是否升级"]:
                ling.upgrade(input_2)
                break
            else:
                print(f">>>{input_2}材料不足以满祝福，不能升级")


def 古阵篇():
    """
    古阵篇自动兑换突破
    """
    while True:
        g = GuZhenPian()
        if not g.data:
            print("--" * 20)
            print(">>>古阵篇全部已满级")
            break
        while True:
            print("--" * 20)
            print("只会兑换突破石，碎片由于兑换上限无法兑换")
            _input = input("选择突破古阵名称：")
            if _input == "q":
                return True
            if _input not in g.data:
                print(f">>>不存在：{_input}")
                continue
            if g.data[_input]["是否升级"]:
                g.upgrade(_input)
                break
            else:
                print(f">>>{_input}材料不足，不能升级")


def 神魔录():
    """
    神魔录自动兑换提升、突破等级
    """
    print("任意位置输入 q 退出当前账号任务")
    category = [
        "灵兽篇",
        "古阵篇",
    ]
    while True:
        while True:
            print("--" * 20)
            for i, n in enumerate(category):
                print(f"{i + 1}.{n}")
            _input = input("选择神魔录类别名称：")
            if _input == "q":
                return
            if _input in category:
                break
            print(f">>>不存在：{_input}")

        if _input == "灵兽篇":
            if 灵兽篇():
                return
        elif _input == "古阵篇":
            if 古阵篇():
                return
