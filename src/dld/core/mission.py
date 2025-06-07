from datetime import datetime

from loguru import logger
from requests import Session


class MissionPlanner:
    """任务规划类"""

    # 任务名称映射
    MISSION_NAME_MAP = {
        "5.1礼包": "五一礼包",
        "5.1预订礼包": "五一预订礼包",
    }

    @staticmethod
    def get_current_day_info() -> tuple:
        """获取当前日期信息"""
        now = datetime.now()
        return now.day, now.isoweekday()

    @staticmethod
    def get_available_missions(mission_type: str) -> list[str]:
        """获取可用任务列表"""
        day, week = MissionPlanner.get_current_day_info()

        # 任务配置
        missions = {
            "one": {
                "邪神秘宝": True,
                "华山论剑": day <= 26,
                "斗豆月卡": True,
                "分享": True,
                "乐斗": True,
                "武林": True,
                "群侠": True,
                "侠侣": week in [2, 5, 7],
                "结拜": week in [1, 2],
                "巅峰之战进行中": True,
                "矿洞": True,
                "掠夺": week in [2, 3],
                "踢馆": week in [5, 6],
                "竞技场": day <= 25,
                "十二宫": True,
                "许愿": True,
                "抢地盘": True,
                "历练": True,
                "镖行天下": True,
                "幻境": True,
                "群雄逐鹿": week == 6,
                "画卷迷踪": True,
                "门派": True,
                "门派邀请赛": True,
                "会武": True,
                "梦想之旅": True,
                "问鼎天下": True,
                "帮派商会": True,
                "帮派远征军": True,
                "帮派黄金联赛": True,
                "任务派遣中心": True,
                "武林盟主": True,
                "全民乱斗": True,
                "侠士客栈": True,
                "大侠回归三重好礼": week == 4,
                "飞升大作战": True,
                "深渊之潮": True,
                "侠客岛": True,
                "时空遗迹": True,
                "世界树": True,
                "龙凰之境": True,
                "任务": True,
                "我的帮派": True,
                "帮派祭坛": True,
                "每日奖励": True,
                "领取徒弟经验": True,
                "今日活跃度": True,
                "江湖长梦": True,
                "仙武修真": True,
                "乐斗黄历": True,
                "器魂附魔": True,
                "兵法": week in [4, 6],
                "猜单双": True,
                "煮元宵": True,
                "万圣节": True,
                "元宵节": week == 4,
                "神魔转盘": True,
                "乐斗驿站": True,
                "浩劫宝箱": True,
                "幸运转盘": True,
                "冰雪企缘": True,
                "甜蜜夫妻": True,
                "乐斗菜单": True,
                "客栈同福": True,
                "周周礼包": True,
                "登录有礼": True,
                "活跃礼包": True,
                "上香活动": True,
                "徽章战令": True,
                "生肖福卡": True,
                "长安盛会": True,
                "深渊秘宝": True,
                "中秋礼盒": True,
                "双节签到": True,
                "乐斗游记": True,
                "斗境探秘": True,
                "幸运金蛋": True,
                "春联大赛": True,
                "新春拜年": True,
                "喜从天降": True,
                "节日福利": True,
                "预热礼包": True,
                "5.1礼包": week == 4,
                "端午有礼": week == 4,
                "圣诞有礼": week == 4,
                "新春礼包": week == 4,
                "登录商店": week == 4,
                "盛世巡礼": week == 4,
                "新春登录礼": True,
                "年兽大作战": True,
                "惊喜刮刮卡": True,
                "开心娃娃机": True,
                "好礼步步升": True,
                "企鹅吉利兑": True,
                "乐斗大笨钟": True,
                "乐斗激运牌": True,
                "乐斗能量棒": True,
                "乐斗回忆录": week == 4,
                "爱的同心结": week == 4,
                "乐斗儿童节": week == 4,
                "周年生日祝福": week == 4,
                "重阳太白诗会": True,
                "5.1预订礼包": True,
            },
            "two": {
                "邪神秘宝": True,
                "问鼎天下": week not in [6, 7],
                "帮派商会": True,
                "任务派遣中心": True,
                "侠士客栈": True,
                "深渊之潮": True,
                "侠客岛": True,
                "背包": True,
                "镶嵌": week == 4,
                "神匠坊": day == 20,
                "每日宝箱": day == 20,
                "商店": True,
                "客栈同福": True,
                "幸运金蛋": True,
                "新春拜年": True,
                "乐斗大笨钟": True,
            },
        }

        return [k for k, v in missions.get(mission_type, {}).items() if v]

    @staticmethod
    def map_to_func_names(mission_names: list[str]) -> list[str]:
        """映射任务名称到函数名称"""
        return [
            MissionPlanner.MISSION_NAME_MAP.get(name, name) for name in mission_names
        ]


def fetch_dld_index(qq: str, session: Session) -> str | None:
    """获取大乐斗首页内容"""
    url = "https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    }
    for _ in range(3):
        response = session.get(url, headers=headers)
        response.encoding = "utf-8"
        if "商店" in response.text:
            return response.text.split("【退出】")[0]

    logger.warning(f"{qq}|该账号无法完成任务，可能官方系统繁忙或者维护")
    print("--" * 20)


def get_func_names(qq: str, session: Session) -> dict[str, list[str]]:
    """获取任务函数名"""
    html = fetch_dld_index(qq, session)
    if not html:
        return

    # 获取并映射任务名称
    one_missions = [
        m for m in MissionPlanner.get_available_missions("one") if m in html
    ]
    two_missions = [
        m for m in MissionPlanner.get_available_missions("two") if m in html
    ]

    return {
        "one": MissionPlanner.map_to_func_names(one_missions),
        "two": MissionPlanner.map_to_func_names(two_missions),
    }
