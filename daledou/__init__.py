import datetime


MSG = []

# 获取当前日期和时间
NOW = datetime.datetime.now()
WEEK: int = NOW.weekday() + 1
DAY: int = NOW.day

_CHINESE = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
WEEK_CHINESE = _CHINESE[WEEK - 1]

# 不支持的通知
DISABLE_PUSH = ['乐斗', '历练', '镶嵌', '神匠坊', '背包']

_ONE = {
    '邪神秘宝': True,
    '华山论剑': DAY <= 26,
    '斗豆月卡': True,
    '每日宝箱': DAY == 20,
    '分享': True,
    '乐斗': True,
    '报名': True,
    '巅峰之战进行中': WEEK != 2,
    '矿洞': True,
    '掠夺': WEEK in [2, 3],
    '踢馆': WEEK in [5, 6],
    '竞技场': DAY <= 25,
    '十二宫': True,
    '许愿': True,
    '抢地盘': True,
    '历练': True,
    '镖行天下': True,
    '幻境': True,
    '群雄逐鹿': WEEK == 6,
    '画卷迷踪': True,
    '门派': True,
    '门派邀请赛': WEEK != 2,
    '会武': WEEK not in [5, 7],
    '梦想之旅': True,
    '问鼎天下': True,
    '帮派商会': True,
    '帮派远征军': True,
    '帮派黄金联赛': True,
    '任务派遣中心': True,
    '武林盟主': True,
    '全民乱斗': True,
    '侠士客栈': True,
    '江湖长梦': WEEK == 4,
    '任务': True,
    '我的帮派': True,
    '帮派祭坛': True,
    '飞升大作战': True,
    '深渊之潮': True,
    '每日奖励': True,
    '领取徒弟经验': True,
    '今日活跃度': True,
    '仙武修真': True,
    '大侠回归三重好礼': WEEK == 4,
    '乐斗黄历': True,
    '器魂附魔': True,
    '侠客岛': True,
    '镶嵌': WEEK == 4,
    '兵法': WEEK in [4, 6],
    '神匠坊': WEEK == 4,
    '背包': True,
    '商店': True,
    '猜单双': True,
    '煮元宵': True,
    '元宵节': WEEK == 4,
    '万圣节': True,
    '神魔转盘': True,
    '乐斗驿站': True,
    '浩劫宝箱': True,
    '幸运转盘': True,
    '冰雪企缘': True,
    '甜蜜夫妻': True,
    '幸运金蛋': True,
    '乐斗菜单': True,
    '客栈同福': True,
    '周周礼包': True,
    '登录有礼': True,
    '活跃礼包': True,
    '上香活动': True,
    '徽章战令': True,
    '生肖福卡': True,
    '长安盛会': True,
    '深渊秘宝': True,
    '登录商店': WEEK == 4,
    '盛世巡礼': WEEK == 4,
    '中秋礼盒': True,
    '双节签到': True,
    '圣诞有礼': WEEK == 4,
    '5.1礼包': WEEK == 4,
    '新春礼包': WEEK == 4,
    '新春拜年': True,
    '春联大赛': True,
    '乐斗游记': True,
    '斗境探秘': True,
    '新春登录礼': True,
    '年兽大作战': True,
    '惊喜刮刮卡': True,
    '开心娃娃机': True,
    '好礼步步升': True,
    '企鹅吉利兑': True,
    '乐斗回忆录': WEEK == 4,
    '乐斗大笨钟': True,
    '爱的同心结': WEEK == 4,
    '周年生日祝福': WEEK == 4,
}

_TWO = {
    '邪神秘宝': True,
    '问鼎天下': WEEK not in [6, 7],
    '任务派遣中心': True,
    '侠士客栈': True,
    '深渊之潮': True,
    '侠客岛': True,
    '幸运金蛋': True,
    '新春拜年': True,
    '喜从天降': True,
    '乐斗大笨钟': True,
}


# 过滤掉为假的任务
MISSIONS_ONE = {k: v for k, v in _ONE.items() if v}
MISSIONS_TWO = {k: v for k, v in _TWO.items() if v}
