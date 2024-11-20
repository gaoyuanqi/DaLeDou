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


class ShenZhuang:
    """
    神装自动兑换进阶
    """

    def __init__(self, fail_value: int):
        # 失败祝福值
        self.fail_value = fail_value
        self.data = {}

        for name in ["神兵", "神铠", "神羽", "神兽", "神饰", "神履"]:
            self._get_data(name)

        self._print_info()

    def _get_data(self, name: str):
        """
        获取神装数据
        """
        data_dict = {
            "神兵": {
                "outfit_id": 0,
                "backpack_id": 3573,
                "store_params": "cmd=arena&op=queryexchange",
            },
            "神铠": {
                "outfit_id": 1,
                "backpack_id": 3574,
                "store_params": "cmd=arena&op=queryexchange",
            },
            "神羽": {
                "outfit_id": 2,
                "backpack_id": 3575,
                "store_params": "cmd=exchange&subtype=10&costtype=1",
            },
            "神兽": {
                "outfit_id": 3,
                "backpack_id": 3576,
                "store_params": "cmd=exchange&subtype=10&costtype=2",
            },
            "神饰": {
                "outfit_id": 4,
                "backpack_id": 3631,
                "store_params": "cmd=exchange&subtype=10&costtype=2",
            },
            "神履": {
                "outfit_id": 5,
                "backpack_id": 3636,
                "store_params": "cmd=exchange&subtype=10&costtype=3",
            },
        }

        outfit_id = data_dict[name]["outfit_id"]
        backpack_id = data_dict[name]["backpack_id"]
        store_params = data_dict[name]["store_params"]

        # 神装
        D.get(f"cmd=outfit&op=0&magic_outfit_id={outfit_id}")
        if "10阶" in D.html:
            self.data[name] = {}
        else:
            result_1 = D.findall(r"阶层：(.*?)<")[0]
            result_2 = D.findall(r"进阶消耗：(.*?)<")[0]
            result_3 = D.findall(r"祝福值：(.*?)<")[0]
            self.data[name] = {
                "outfit_id": outfit_id,
                "神装": name,
                "阶层": result_1,
                "进阶消耗": result_2,
                "祝福值": result_3,
            }

            # 进阶一次消耗材料数量
            number_1 = int(result_2.split("*")[1])
            # 当前祝福值、最大祝福值
            number_2, number_3 = result_3.split("/")
            # 最大祝福值与当前祝福值之差
            number_4 = int(number_3) - int(number_2)
            # 进阶到满祝福所需材料数量，2 是额外的冗余进阶次数
            number_5 = ((number_4 // self.fail_value) + 2) * number_1
            self.data[name]["满祝福进阶消耗"] = number_5

            # 获取背包进阶材料数量
            number_6: int = get_backpack_item_count(backpack_id)
            # 获取进阶材料的商店积分
            number_7: int = get_store_points(store_params)
            # 计算进阶材料背包数量与商店积分可兑换数量之和
            number_8: int = number_6 + (number_7 // 40)
            self.data[name]["积分与背包数量之和"] = number_8
            self.data[name]["商店积分"] = number_7
            self.data[name]["背包数量"] = number_6

    def _print_info(self):
        """
        打印神装数据
        """
        for name, _dict in self.data.items():
            if not _dict:
                continue
            for k, v in _dict.items():
                print(f"{k}：{v}")
            print("--" * 20)
        print(f"失败祝福值：{self.fail_value}")

        print("--" * 20)
        for name, value in self.data.items():
            if not value:
                continue
            number = self.compute_difference(name)
            if number < 0:
                print(f"{name}：还差 {number} 个")
            else:
                print(f"{name}：余出 {number} 个")

    def run(self, name: str) -> bool:
        """
        神装进阶
        如果失败祝福值一致则返回True，否则返回False
        """
        outfit_id = self.data[name]["outfit_id"]
        while True:
            print("--" * 20)
            祝福值 = self.data[name]["祝福值"]
            进阶消耗: str = self.data[name]["进阶消耗"]
            number_1: int = self.data[name]["背包数量"]
            # 当前祝福值
            old_value = int(祝福值.split("/")[0])
            # 进阶材料名称、数量
            _name, number_2 = 进阶消耗.split("*")
            # 补齐进阶材料
            if int(number_2) > number_1:
                number_3 = int(number_2) - number_1
                self.兑换(_name, number_3)

            if self.进阶(outfit_id):
                break

            print("--" * 20)
            # 获取神装数据
            self._get_data(name)
            for k, v in self.data[name].items():
                print(f"{k}：{v}")

            # 进阶后的祝福值
            祝福值 = self.data[name]["祝福值"]
            new_value = int(祝福值.split("/")[0])
            value = new_value - old_value
            if value != self.fail_value:
                print("--" * 20)
                print(f"你输入的祝福值：{self.fail_value}")
                print(f"实际祝福值：{value}")
                return False

        return True

    def 进阶(self, outfit_id: int) -> bool:
        """
        神装进阶，始终不会使用斗豆兑换
        如果进阶成功则返回True，否则返回False
        """
        # 神装
        D.get("cmd=outfit")
        if "关闭自动斗豆兑换神装进阶材料" in D.html:
            D.get(f"cmd=outfit&op=4&auto_buy=2&magic_outfit_id={outfit_id}")
            D.find(r"\|<br />(.*?)<br />")
        if "关闭自动斗豆兑换神技升级材料" in D.html:
            D.get(f"cmd=outfit&op=8&auto_buy=2&magic_outfit_id={outfit_id}")
            D.find(r"\|<br />(.*?)<br />")

        # 进阶
        D.get(f"cmd=outfit&op=1&magic_outfit_id={outfit_id}")
        D.find(r"神履.*?<br />(.*?)<br />")
        if "成功" in D.html:
            return True
        return False

    def 兑换(self, name: str, number: int):
        """
        兑换神装材料
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
        ten, one = divmod(number, 10)
        for _ in range(ten):
            D.get(data[name]["ten"])
            D.find()
            if "不足" in D.html:
                break
        for _ in range(one):
            D.get(data[name]["one"])
            D.find()
            if "不足" in D.html:
                break

    def compute_difference(self, name: str) -> int:
        """
        计算满祝福进阶消耗与积分和背包数量之差
        """
        number_1 = self.data[name]["满祝福进阶消耗"]
        number_2 = self.data[name]["积分与背包数量之和"]
        return number_2 - number_1


def 神装():
    """
    神装自动积分兑换材料并进阶，始终不会使用斗豆兑换
    """
    print("任意位置输入exit退出当前账号任务")
    print("--" * 20)
    print("日常失败祝福值是 2")
    print("活动期间是 2n 倍")
    print("始终不会使用斗豆自动兑换")
    while True:
        print("--" * 20)
        input_1 = input("输入神装失败祝福值：")
        if input_1 == "exit":
            return
        if not input_1.isdigit():
            print("只能输入数字")
            continue

        while True:
            print("--" * 20)
            s = ShenZhuang(int(input_1))

            while True:
                print("--" * 20)
                input_2 = input("输入进阶神装名称：")
                if input_2 == "exit":
                    return
                if input_2 not in s.data:
                    print(f"{input_2} 不存在")
                    continue

                number = s.compute_difference(input_2)
                if number < 0:
                    print(f"{input_2}满祝福材料还差 {number}")
                    continue

                print("--" * 20)
                input_3 = input("输入y确定进阶：")
                if input_3 == "exit":
                    return
                if input_3 != "y":
                    continue
                break

            if not s.run(input_2):
                break


def 夺宝奇兵():
    """
    夺宝奇兵选择太空探宝场景投掷
    """
    print("任意位置输入exit退出当前账号任务")
    print("--" * 20)
    print("夺宝奇兵太空探宝16倍场景投掷")
    while True:
        print("--" * 20)
        # 五行合成页面
        D.get("cmd=element&subtype=4")
        result = D.findall(r"拥有:(\d+)")[0]
        print(f"战功：{result}")
        print("--" * 20)

        _input = input("输入低于多少战功时结束投掷：")
        if _input == "exit":
            return
        if not _input.isdigit():
            print("只能输入数字")
            continue
        number_1 = int(result)
        number_2 = int(_input)
        if number_2 > number_1:
            print(f"拥有战功{number_1}已经低于输入战功{number_2}")
            continue
        break

    while True:
        if number_2 > int(result):
            break

        # 投掷
        D.get("cmd=element&subtype=7")
        if "【夺宝奇兵】" in D.html:
            D.find(r"<br /><br />(.*?)<br />")
            result = D.find(r"拥有:(\d+)", name="战功")
            if "您的战功不足" in D.html:
                break
        elif "【选择场景】" in D.html:
            if "你掷出了" in D.html:
                D.find(r"】<br />(.*?)<br />")
            # 选择太空探宝
            D.get("cmd=element&subtype=15&gameType=3")


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
        # 商店材料数据
        self._data: dict = self._get_store_data()
        # 输出商店数据
        self._print_store_info()

    @property
    def data(self):
        return self._data

    def _get_store_data(self) -> dict:
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
            data_dict[name] = {
                "id": _id,
                "售价": int(售价),
                "已售": int(已售),
                "限售": int(限售),
            }
        return data_dict

    def _print_store_info(self):
        """
        将商店中的材料名称、售价、已售、限售打印出来
        """
        headers = ["名称", "售价", "已售", "限售"]
        # 打印表头
        print("{:<12}{:<5}{:<4}{:<3}".format(*headers))
        print("--" * 20)
        for name, _dict in self.data.items():
            售价 = _dict["售价"]
            已售 = _dict["已售"]
            限售 = _dict["限售"]
            print(f"{name:<12}{售价:<5}{已售:<4}{限售:<3}")

    def get_store_id_and_number(self, name: str) -> tuple:
        """
        返回江湖长梦商店兑换id、可兑换数量
        """
        data_dict = self.data[name]
        _id: str = data_dict["id"]
        售价: int = data_dict["售价"]
        已售: int = data_dict["已售"]
        限售: int = data_dict["限售"]

        # 剩余兑换额度
        number_1: int = 限售 - 已售
        # 积分最多可兑换数量
        number_2: int = self.points // 售价
        if number_1 <= number_2:
            number = number_1
        else:
            number = number_2

        return _id, number

    def 兑换(self, name: str, number: int):
        """
        江湖长梦商店材料兑换
        """
        _id: str = self.data[name]["id"]
        for i in range(number):
            D.get(f"cmd=longdreamexchange&op=exchange&key_id={_id}")
            D.find(r"侠士碎片</a><br />(.*?)<", name=f"{name}-{i + 1}")


def 江湖长梦():
    """
    商店兑换及副本挑战（柒承的忙碌日常）
    """
    print("任意位置输入exit退出当前账号任务")
    while True:
        print("--" * 20)
        print("柒承的忙碌日常")
        print("江湖长梦商店兑换")
        input_1 = input("输入任务：")
        if input_1 == "exit":
            return
        if input_1 not in ["柒承的忙碌日常", "江湖长梦商店兑换"]:
            print(f"{input_1} 不存在")
            continue
        break

    if input_1 == "柒承的忙碌日常":
        while True:
            print("--" * 20)
            number_1 = get_backpack_item_count(6477)
            print(f"追忆香炉数量：{number_1}")
            print("--" * 20)
            input_2 = input("输入挑战次数：")
            if input_2 == "exit":
                return
            if not input_2.isdigit():
                print("只能输入数字")
                continue

            number_2 = int(input_2)
            if number_1 < number_2:
                print(f"最多可挑战{number_1}次，请重新输入")
                continue
            柒承的忙碌日常(number_2)

    if input_1 != "江湖长梦商店兑换":
        return

    while True:
        print("--" * 20)
        j = JiangHuChangMeng()
        print("--" * 20)
        print(f"商店积分：{j.points}")
        while True:
            print("--" * 20)
            input_3 = input("输入兑换材料名称：")
            if input_3 == "exit":
                return
            if input_3 not in j.data:
                print(f"{input_3} 不存在，请重新输入")
                continue
            break
        while True:
            print("--" * 20)
            input_4 = input("输入兑换材料数量：")
            if input_4 == "exit":
                return
            if not input_4.isdigit():
                print("只能输入数字")
                continue

            number_3 = int(input_4)
            _id, number_4 = j.get_store_id_and_number(input_3)
            print(f"{input_3}最多可兑换{number_4}个")
            if number_4 == 0:
                print("请更换兑换材料名称")
                break
            if number_3 > number_4:
                print("超过可兑换数量，请重新输入")
                continue
            break

        print(f"{input_3}：{number_3}")
        input_5 = input("输入y确定兑换：")
        print("--" * 20)
        if input_5 == "exit":
            return
        if input_5 == "y":
            j.兑换(input_3, number_4)


class XingPanInfo:
    """
    获取星盘信息
    """

    def __init__(self):
        # 幻境商店积分
        p = "cmd=exchange&subtype=10&costtype=9"
        self.points: int = get_store_points(p)
        self.data = {}
        self._get_xingpan_data()
        self._print_info()

    def _get_store_max_number(self, name: str) -> int | None:
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

    def _get_xingpan_data(self):
        """
        获取1~6级星石数量及2~7级星石合成id
        """
        data = {
            "日曜石": 1,
            "玛瑙石": 2,
            "迅捷石": 3,
            "月光石": 4,
            "翡翠石": 5,
            "紫黑玉": 6,
            "狂暴石": 7,
            "神愈石": 8,
        }
        for name, gem in data.items():
            D.get(f"cmd=astrolabe&op=showgemupgrade&gem_type={gem}")
            result_1 = D.findall(r"（(\d+)）")[1:]
            result_2 = D.findall(r"gem=(\d+)")[1:]
            # 1~6级星石数量
            data_1 = {i + 1: int(item) for i, item in enumerate(result_1)}
            # 2~7级星石合成id
            data_2 = {i + 2: item for i, item in enumerate(result_2)}
            self.data[name] = {
                "possess": data_1,
                "合成id": data_2,
                "store_max_number": self._get_store_max_number(name),
            }

    def _print_info(self):
        """
        显示星石信息
        """
        print("1~6级星石数量")
        for name, v in self.data.items():
            print(f"{name}：{v['possess']}")


class XingPan:
    """
    星石兑换合成
    """

    def __init__(self, name: str, data: dict):
        self._name = name
        self.data = data
        if data.get(name) is None:
            self.possess = None
        else:
            self.possess = self.data[self._name]["possess"]
            self.store_max_number = self.data[self._name]["store_max_number"]
            self.合成次数 = {}
            # 各级星石转换关系
            self._level_ties = {
                1: 5,  # 5个1级星石合成一个2级星石
                2: 4,  # 4个2级星石合成一个3级星石
                3: 4,  # 4个3级星石合成一个4级星石
                4: 3,  # 3个4级星石合成一个5级星石
                5: 3,  # 3个5级星石合成一个6级星石
                6: 2,  # 2个6级星石合成一个7级星石
            }

    def compute(self, level: int, number: int) -> tuple[int, int]:
        """
        返回需兑换的1级星石数量及星石等级

        Args:
            level: 合成星石等级
            number: 合成星石数量
        """

        level -= 1
        if self.possess[level] >= self._level_ties[level] * number:
            self.合成次数[level + 1] = number
            return 0, level
        else:
            _number = self._level_ties[level] * number - self.possess[level]
            self.合成次数[level + 1] = number
            if level == 1:
                return _number, level
            else:
                return self.compute(level, _number)

    def 兑换(self, number: int):
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
        t = data[self._name]
        quotient, remainder = divmod(number, 10)
        for _ in range(quotient):
            # 兑换10个
            D.get(f"cmd=exchange&subtype=2&type={t}&times=10&costtype=9")
            D.find(name="幻境商店")
        for _ in range(remainder):
            # 兑换1个
            D.get(f"cmd=exchange&subtype=2&type={t}&times=1&costtype=9")
            D.find(name="幻境商店")

    def 合成(self):
        """
        星石合成
        """
        data = dict(sorted(self.合成次数.items()))
        for level, number in data.items():
            gem = self.data[self._name]["合成id"][level]
            for _ in range(number):
                D.get(f"cmd=astrolabe&op=upgradegem&gem={gem}")
                D.find(r"规则</a><br />(.*?)<", name=f"{level}级{self._name}")


def 星盘():
    """
    星石自动兑换合成
    """
    print("任意位置输入exit退出当前账号任务")
    while True:
        print("--" * 20)
        x_info = XingPanInfo()
        print("--" * 20)
        print(f"商店积分：{x_info.points}")

        while True:
            print("--" * 20)
            input_1 = input("输入合成星石名称：")
            if input_1 == "exit":
                return
            x = XingPan(input_1, x_info.data)
            if x.possess:
                break
            print(f"{input_1} 不存在，请重新输入")

        while True:
            print("--" * 20)
            input_2 = input("输入合成星石等级（2~7）：")
            if input_2 == "exit":
                return
            if input_2 in ["2", "3", "4", "5", "6", "7"]:
                break
            print("星石等级只能是2~7级")

        while True:
            print("--" * 20)
            input_3 = input(f"输入合成{input_2}级星石数量：")
            if input_3 == "exit":
                return
            if not input_3.isdigit():
                print("只能输入数字")
                continue
            if input_3 == "0":
                print("输入数字不能为0")
                continue
            break

        print("--" * 20)
        number, level = x.compute(int(input_2), int(input_3))
        if number != 0:
            store_max_number = x.store_max_number
            print(f"合成{input_3}个{input_2}级{input_1}还需兑换{number}个1级{input_1}")
            if store_max_number is None:
                print(f"幻境商店不可兑换{input_1}，请重新输入")
                continue

            print(f"幻境商店最多可兑换{store_max_number}个{input_1}")
            if store_max_number < number:
                print(f"还差{number - store_max_number}个，请重新输入")
                continue

            input_4 = input("输入y确定兑换：")
            if input_4 == "exit":
                return
            if input_4 != "y":
                continue
            x.兑换(number)
        else:
            print(f"{input_2}级{input_1}可直接从{level}级开始合成")

        x.合成()


class XinYuanYingShenQi:
    """
    新元婴神器
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
        params = params_data[name]
        D.get(f"cmd=newAct&subtype=104&{params}")
        D.html = D.html.split("|")[-1]
        # 获取神器名称
        result_1 = D.findall(r"([\u4e00-\u9fff]+)&nbsp;\d+星")
        # 获取神器星级
        result_2 = D.findall(r"(\d+)星")
        # 获取神器id
        result_3 = D.findall(r"item_id=(\d+).*?一键")
        # 获取消耗
        result_4 = D.findall(r":(\d+)")
        # 获取祝福值进度
        result_5 = D.findall(r"(\d+)/")
        # 获取祝福值满值
        result_6 = D.findall(r"/(\d+)")

        # 过滤5星
        result_7 = [(k, v) for k, v in zip(result_1, result_2) if v != "5"]
        data = {}
        for index, t in enumerate(result_7):
            name, level = t
            number_1 = int(result_4[index])
            number_2 = int(result_5[index])
            number_3 = int(result_6[index])
            number_4 = self._compute(number_1, number_2, number_3)
            data[name] = {
                "神器星级": level,
                "id": result_3[index],
                "神器消耗": number_1,
                "神器祝福值进度": number_2,
                "神器满祝福值": number_3,
                "真黄金卷轴数量": self._number,
                "满祝福消耗数量": number_4,
                "是否升级": self._number >= number_4,
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
        for name, _dict in data.items():
            print("--" * 20)
            print(f"神器名称：{name}")
            for k, v in _dict.items():
                print(f"{k}：{v}")

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
            D.find(rf"{name}.*?:\d+ [\u4e00-\u9fff]+ (.*?)<br />", name=name)
            if "恭喜您" in D.html:
                break


def 新元婴神器():
    """
    自动升级神器
    """
    print("任意位置输入exit退出当前账号任务")
    print("--" * 20)
    print("三星（含）以下必成，最好去手动升级")
    print("三星以上失败祝福值 2")
    print("--" * 20)
    category = [
        "投掷武器",
        "小型武器",
        "中型武器",
        "大型武器",
        "被动技能",
        "伤害技能",
        "特殊技能",
    ]
    print("神器类别：")
    for n in category:
        print(n)
    while True:
        while True:
            print("--" * 20)
            input_1 = input("输入神器类别：")
            if input_1 == "exit":
                return
            if input_1 in category:
                break
            print(f"不存在神器类别：{input_1}")

        x = XinYuanYingShenQi(input_1)
        while True:
            print("--" * 20)
            input_2 = input("输入升级神器名称：")
            if input_2 == "exit":
                return
            if input_2 not in x.data:
                print(f"不存在神器名称：{input_2}")
                continue
            if x.data[input_2]["是否升级"]:
                x.upgrade(input_2)
                break
            else:
                print(f"{input_2}：满祝福材料不足")
