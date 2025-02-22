from datetime import datetime


# 获取当前日期和时间
NOW = datetime.now()
# 1~7 对应 周一 ~ 周日
WEEK: int = NOW.weekday() + 1
DAY: int = NOW.day

# 第一轮任务
ONE = {
    "邪神秘宝": True,
    "华山论剑": DAY <= 26,
    "斗豆月卡": True,
    "兵法": WEEK in [4, 6],
    "分享": True,
    "乐斗": True,
    "报名": True,
    "巅峰之战进行中": True,
    "矿洞": True,
    "掠夺": WEEK in [2, 3],
    "踢馆": WEEK in [5, 6],
    "竞技场": True,
    "十二宫": True,
    "许愿": True,
    "抢地盘": True,
    "历练": True,
    "镖行天下": True,
    "幻境": True,
    "群雄逐鹿": WEEK == 6,
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
    "大侠回归三重好礼": WEEK == 4,
    "乐斗黄历": True,
    "飞升大作战": True,
    "深渊之潮": True,
    "侠客岛": True,
    "时空遗迹": True,
    "世界树": True,
    "任务": True,
    "我的帮派": True,
    "帮派祭坛": True,
    "江湖长梦": True,
    "每日奖励": True,
    "领取徒弟经验": True,
    "今日活跃度": True,
    "仙武修真": True,
    "器魂附魔": True,
    "猜单双": True,
    "煮元宵": True,
    "万圣节": True,
    "元宵节": WEEK == 4,
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
    "5.1礼包": WEEK == 4,
    "端午有礼": WEEK == 4,
    "圣诞有礼": WEEK == 4,
    "新春礼包": WEEK == 4,
    "登录商店": WEEK == 4,
    "盛世巡礼": WEEK == 4,
    "新春登录礼": True,
    "年兽大作战": True,
    "惊喜刮刮卡": True,
    "开心娃娃机": True,
    "好礼步步升": True,
    "企鹅吉利兑": True,
    "乐斗大笨钟": True,
    "乐斗激运牌": True,
    "乐斗能量棒": True,
    "乐斗回忆录": WEEK == 4,
    "爱的同心结": WEEK == 4,
    "周年生日祝福": WEEK == 4,
    "重阳太白诗会": True,
}

# 第二轮任务
TWO = {
    "邪神秘宝": True,
    "问鼎天下": WEEK not in [6, 7],
    "帮派商会": True,
    "任务派遣中心": True,
    "侠士客栈": True,
    "深渊之潮": True,
    "侠客岛": True,
    "背包": True,
    "镶嵌": WEEK == 4,
    "神匠坊": DAY == 20,
    "每日宝箱": DAY == 20,
    "商店": True,
    "幸运金蛋": True,
    "新春拜年": True,
    "乐斗大笨钟": True,
}

# 当天可以执行的大乐斗任务
MISSIONS_ONE = [k for k, v in ONE.items() if v]
MISSIONS_TWO = [k for k, v in TWO.items() if v]
