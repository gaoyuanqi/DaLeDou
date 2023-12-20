import re
import sys
import time
import random
import traceback
from shutil import copy
from importlib import reload
from os import environ, path, getenv

import yaml
import requests
from loguru import logger

import settings


MSG = []
WEEK: str = time.strftime('%w')
DATE: str = time.strftime('%d', time.localtime())

# 不支持的通知
DISABLE_PUSH = ['乐斗', '历练', '镶嵌', '神匠坊', '背包']

MISSION = {
    'one': [
        [('邪神秘宝',), True],
        [('华山论剑',), (int(DATE) <= 26)],
        [('斗豆月卡',), True],
        [('每日宝箱',), (DATE == '20')],
        [('分享',), True],
        [('乐斗',), True],
        [('报名',), True],
        [('巅峰之战进行中',), (WEEK != '2')],
        [('矿洞',), True],
        [('掠夺',), (WEEK in ['2', '3'])],
        [('踢馆',), (WEEK in ['5', '6'])],
        [('竞技场',), (int(DATE) <= 25)],
        [('十二宫',), True],
        [('许愿',), True],
        [('抢地盘',), True],
        [('历练',), True],
        [('镖行天下',), True],
        [('幻境',), True],
        [('群雄逐鹿',), (WEEK == '6')],
        [('画卷迷踪',), True],
        [('门派',), True],
        [('门派邀请赛',), (WEEK != '2')],
        [('会武',), (WEEK not in ['5', '0'])],
        [('梦想之旅',), True],
        [('问鼎天下',), True],
        [('帮派商会',), True],
        [('帮派远征军',), True],
        [('帮派黄金联赛',), True],
        [('任务派遣中心',), True],
        [('武林盟主',), True],
        [('全民乱斗',), True],
        [('侠士客栈',), True],
        [('江湖长梦',), (WEEK == '4')],
        [('任务',), True],
        [('我的帮派',), True],
        [('帮派祭坛',), True],
        [('飞升大作战',), True],
        [('深渊之潮',), True],
        [('每日奖励',), True],
        [('领取徒弟经验',), True],
        [('今日活跃度',), True],
        [('仙武修真',), True],
        [('大侠回归三重好礼',), (WEEK == '4')],
        [('乐斗黄历',), True],
        [('器魂附魔',), True],
        [('镶嵌',), (WEEK == '4')],
        [('兵法',), (WEEK in ['4', '6'])],
        [('神匠坊',), (WEEK == '4')],
        [('背包',), True],
        [('商店',), True],
        [('猜单双',), True],
        [('煮元宵',), True],
        [('元宵节',), (WEEK == '4')],
        [('万圣节',), True],
        [('神魔转盘',), True],
        [('乐斗驿站',), True],
        [('浩劫宝箱',), True],
        [('幸运转盘',), True],
        [('喜从天降',), True],
        [('冰雪企缘',), True],
        [('甜蜜夫妻',), True],
        [('幸运金蛋',), True],
        [('乐斗菜单',), True],
        [('客栈同福',), True],
        [('周周礼包',), True],
        [('登录有礼',), True],
        [('活跃礼包',), True],
        [('上香活动',), True],
        [('徽章战令',), True],
        [('生肖福卡',), True],
        [('长安盛会',), True],
        [('深渊秘宝',), True],
        [('登录商店',), (WEEK == '4')],
        [('盛世巡礼',), (WEEK == '4')],
        [('中秋礼盒',), True],
        [('双节签到',), True],
        [('圣诞有礼',), (WEEK == '4')],
        [('5.1礼包', '五一礼包'), (WEEK == '4')],
        [('新春礼包',), (WEEK == '4')],
        [('新春拜年',), True],
        [('春联大赛',), True],
        [('乐斗游记',), True],
        [('斗境探秘',), True],
        [('新春登录礼',), True],
        [('年兽大作战',), True],
        [('惊喜刮刮卡',), True],
        [('开心娃娃机',), True],
        [('好礼步步升',), True],
        [('企鹅吉利兑',), True],
        [('乐斗回忆录',), (WEEK == '4')],
        [('乐斗大笨钟',), True],
        [('爱的同心结',), (WEEK == '4')],
        [('周年生日祝福',), (WEEK == '4')],
    ],
    'two': [
        [('邪神秘宝',), True],
        [('问鼎天下',), (WEEK not in ['6', '0'])],
        [('任务派遣中心',), True],
        [('侠士客栈',), True],
        [('深渊之潮',), True],
        [('幸运金蛋',), True],
        [('新春拜年',), True],
        [('乐斗大笨钟',), True],
    ],
}


class CookieError(Exception):
    ...


class DaLeDou:
    def __init__(self, cookie: str) -> None:
        assert type(cookie) is str, '传入的cookie只能是str类型'
        self._cookie = self._clean_cookie(cookie)
        self._qq = self._match_qq()

    def _clean_cookie(self, cookie: str) -> str:
        '''清洁大乐斗cookie

        :return: 'RK=xxx; ptcz=xxx; openId=xxx; accessToken=xxx; newuin=xxx'
        '''
        ck = ''
        for key in ['RK', 'ptcz', 'openId', 'accessToken', 'newuin']:
            try:
                result = re.search(
                    f'{key}=(.*?); ',
                    f'{cookie}; ',
                    re.S
                ).group(0)
            except AttributeError:
                raise CookieError(f'大乐斗cookie不正确：{cookie}')
            ck += f'{result}'
        return ck[:-2]

    def _match_qq(self) -> str:
        '''从cookie中提取出qq'''
        return re.search(r'newuin=(\d+)', self._cookie, re.S).group(1)

    def _create_yaml(self):
        '''基于 daledou.yaml 创建一份以qq命名的 yaml 配置文件

        如果以qq命名的yaml配置文件已存在则不做任何操作
        '''
        srcpath = f'./config/daledou.yaml'
        yamlpath = f'./config/{self._qq}.yaml'
        if not path.isfile(yamlpath):
            logger.success(f'成功创建配置文件：./config/{self._qq}.yaml')
            copy(srcpath, yamlpath)

    def _push(self, title: str, message: list) -> None:
        '''pushplus微信通知'''
        if token := settings.PUSHPLUS_TOKEN:
            url = 'http://www.pushplus.plus/send/'
            content = '\n'.join(list(filter(lambda x:  x, message)))
            data = {
                'token': token,
                'title': title,
                'content': content,
            }
            res = requests.post(url, data=data)
            json: dict = res.json()
            if json.get('code') == 200:
                return logger.success(f'pushplus推送成功：{json}')
            return logger.warning(f'pushplus推送失败：{json}')
        logger.warning('pushplus没有配置token，取消微信推送')

    def session(self):
        '''若cookie有效返回Session对象，否则返回None'''
        global SESSION
        url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        with requests.session() as SESSION:
            requests.utils.add_dict_to_cookiejar(
                SESSION.cookies, {'Cookie': self._cookie})
        for _ in range(3):
            res = SESSION.get(url, headers=headers)
            res.encoding = 'utf-8'
            html = res.text
            if '商店' in html:
                logger.success(f'{self._qq}：COOKIE有效')
                if self._cookie != getenv(f'DLD_COOKIE_VALID_{self._qq}'):
                    environ[f'DLD_COOKIE_VALID_{self._qq}'] = self._cookie
                    self._create_yaml()
                return SESSION
            elif '一键登录' in html:
                logger.warning(f'{self._qq}：COOKIE无效！！!')
                break

        if self._cookie != getenv(f'DLD_COOKIE_NULL_{self._qq}'):
            environ[f'DLD_COOKIE_NULL_{self._qq}'] = self._cookie
            self._push(f'cookie失效或者系统维护：{self._qq}', [self._cookie])

    def create_log(self) -> int:
        '''创建当天日志文件

        文件夹以qq命名，日志文件以日期命名
        '''
        date = time.strftime('%Y-%m-%d', time.localtime())
        return logger.add(
            f'./log/{self._qq}/{date}.log',
            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>',
            enqueue=True,
            encoding='utf-8',
            retention='30 days'
        )

    def get(self, params: str) -> str:
        '''发送get请求获取html响应内容'''
        global HTML
        url = f'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{params}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        for _ in range(3):
            res = SESSION.get(url, headers=headers)
            res.encoding = 'utf-8'
            HTML = res.text
            time.sleep(0.2)
            if '系统繁忙' not in HTML:
                break
        return HTML

    def find(self, mode: str, name: str = '') -> str | None:
        '''匹配首个'''
        if match := re.search(mode, HTML, re.S):
            result: str = match.group(1)
        else:
            result = None
        if not name:
            name = MISSION_NAME
        logger.info(f'{self._qq} | {name}：{result}')
        return result

    def findall(self, mode: str) -> list:
        '''匹配所有'''
        return re.findall(mode, HTML, re.S)

    def read_yaml(self, key: str):
        '''读取config目录下的yaml配置文件'''
        try:
            with open(f'./config/{self._qq}.yaml', 'r', encoding='utf-8') as fp:
                users = yaml.safe_load(fp)
                data = users[key]
            return data
        except Exception:
            error = traceback.format_exc()
            logger.error(f'{self._qq}.yaml 配置不正确：\n{error}')
            self._push(f'{self._qq}.yaml 配置不正确', [error])

    def run(self, tasks: str) -> None:
        global MISSION_NAME
        start = time.time()
        for _ in range(3):
            # 大乐斗首页
            get('cmd=index')
            if '退出' in HTML:
                html = HTML.split('【退出】')[0]
                for misssion in MISSION.get(tasks, []):
                    is_mission: tuple = misssion[0]
                    is_run: bool = misssion[-1]
                    if len(is_mission) == 2:
                        mission_name, func_name = is_mission
                    else:
                        mission_name = is_mission[0]
                        func_name = is_mission[0]
                    MISSION_NAME = mission_name
                    if is_run and (mission_name in html):
                        if mission_name not in DISABLE_PUSH:
                            MSG.append(f'\n【{mission_name}】')
                        globals()[func_name]()
                break

        end = time.time()
        MSG.append(f'\n【运行时长】\n时长：{int(end - start)} s')
        self._push(f'{self._qq} {tasks}', MSG)
        MSG.clear()


def get(params: str) -> str:
    '''发送get请求获取html响应内容'''
    HTML = DALEDOU.get(params)
    return HTML


def find(mode: str, name: str = '') -> str | None:
    '''匹配首个'''
    return DALEDOU.find(mode, name)


def findall(mode: str) -> list:
    '''匹配所有'''
    return DALEDOU.findall(mode)


def read_yaml(key: str):
    '''读取yaml配置文件'''
    return DALEDOU.read_yaml(key)


def run(tasks: str = 'check') -> None:
    global DALEDOU

    if len(input := sys.argv) == 2:
        tasks = input[1]
    if tasks not in ['check', 'one', 'two']:
        assert False, f'不支持 {tasks} 参数，只支持 check | one | two'

    reload(settings)
    for ck in settings.DALEDOU_ACCOUNT:
        print('\n')
        DALEDOU = DaLeDou(ck)
        if DALEDOU.session():
            if tasks == 'check':
                continue
            trace = DALEDOU.create_log()
            DALEDOU.run(tasks)
            logger.remove(trace)
        del DALEDOU


def 邪神秘宝():
    '''邪神秘宝

    高级秘宝    免费一次 or 抽奖一次
    极品秘宝    免费一次 or 抽奖一次
    '''
    for i in [0, 1]:
        # 免费一次 or 抽奖一次
        get(f'cmd=tenlottery&op=2&type={i}')
        MSG.append(find(r'】</p>(.*?)<br />', '邪神秘宝'))


def 华山论剑():
    '''华山论剑

    每月1~25号每天至多挑战10次，耐久不足时自动更换侠士
    每月26号领取赛季段位奖励
    '''
    if int(DATE) <= 25:
        for _ in range(10):
            # 开始挑战
            get('cmd=knightarena&op=challenge')
            if '耐久不足' in HTML:
                # 战阵调整页面
                get('cmd=knightarena&op=viewsetknightlist&pos=0')
                knightid = findall(r'knightid=(\d+)')

                # 出战侠士页面
                get('cmd=knightarena&op=viewteam')
                xuanze_pos = findall(r'pos=(\d+)">选择侠士')
                genggai = findall(r'耐久：(\d+)/.*?pos=(\d+)">更改侠士.*?id=(\d+)')

                genggai_pos = []
                for n, p, id in genggai:
                    # 移除不可出战的侠士id
                    knightid.remove(id)
                    if n == '0':
                        # 筛选耐久为 0 的侠士出战次序
                        genggai_pos.append(p)

                # 选择/更改侠士
                for p in (xuanze_pos + genggai_pos):
                    if not knightid:
                        break
                    id: str = knightid.pop()
                    # 出战
                    get(f'cmd=knightarena&op=setknight&id={id}&pos={p}&type=1')
                continue
            MSG.append(find(r'荣誉兑换</a><br />(.*?)<br />'))
            if '论剑所需门票不足' in HTML:
                break
            elif '请先设置上阵侠士后再开始战斗' in HTML:
                break
    elif DATE == '26':
        get(r'cmd=knightarena&op=drawranking')
        MSG.append(find(r'【赛季段位奖励】<br />(.*?)<br />'))


def 斗豆月卡():
    '''斗豆月卡

    每天领取150斗豆
    '''
    # 领取150斗豆
    get('cmd=monthcard&sub=1')
    MSG.append(find(r'<p>(.*?)<br />'))


def 每日宝箱():
    '''每日宝箱

    每月20号打开所有宝箱
    '''
    # 每日宝箱
    get('cmd=dailychest')
    while type_list := findall(r'type=(\d+)">打开'):
        # 打开
        get(f'cmd=dailychest&op=open&type={type_list[0]}')
        MSG.append(find(r'规则说明</a><br />(.*?)<br />'))
        if '今日开宝箱次数已达上限' in HTML:
            break


def 分享():
    '''分享

    每天分享直到上限，若次数不足则挑战斗神塔增加次数（每挑战11层增加一次分享）
    每周四领取分享次数奖励
    '''
    for _ in range(9):
        # 一键分享
        get(f'cmd=sharegame&subtype=6')
        find(r'】</p>(.*?)<p>', '一键分享')
        if '上限' in HTML:
            MSG.append(find(r'</p><p>(.*?)<br />.*?开通达人', '分享次数'))
            # 自动挑战
            get('cmd=towerfight&type=11')
            find(r'】<br />(.*?)<', '斗神塔')
            # 结束挑战
            get('cmd=towerfight&type=7')
            find(r'】<br />(.*?)<br />', '斗神塔')
            break

        # 斗神塔
        get('cmd=towerfight&type=3')
        if '结束挑战' in HTML:
            # 结束挑战
            get('cmd=towerfight&type=7')
            find(r'】<br />(.*?)<br />', '斗神塔')
        for _ in range(11):
            # 开始挑战 or 挑战下一层
            get('cmd=towerfight&type=0')
            find(r'】<br />(.*?)<', '斗神塔')
            if '您需要消耗斗神符才能继续挑战斗神塔' in HTML:
                # 一键分享
                get(f'cmd=sharegame&subtype=6')
                find(r'】</p>(.*?)<p>', '斗神塔')
                return
            elif '您败给' in HTML:
                # 结束挑战
                get('cmd=towerfight&type=7')
                find(r'】<br />(.*?)<br />', '斗神塔')
                break

            if cooling := findall(r'战斗剩余时间：(\d+)'):
                time.sleep(int(cooling[0]))

    if WEEK == '4':
        get('cmd=sharegame&subtype=3')
        for s in findall(r'sharenums=(\d+)'):
            # 领取
            get(f'cmd=sharegame&subtype=4&sharenums={s}')
            MSG.append(find(r'】</p>(.*?)<p>'), '斗神塔')


def 乐斗():
    '''乐斗

    开启自动使用体力药水
    贡献药水使用4次
    每天乐斗好友BOSS、帮友BOSS以及侠侣所有
    '''
    # 乐斗助手
    get('cmd=view&type=6')
    if '开启自动使用体力药水' in HTML:
        #  开启自动使用体力药水
        get('cmd=set&type=0')

    for _ in range(4):
        # 使用贡献药水
        get('cmd=use&id=3038&store_type=1&page=1')
        if '使用规则' in HTML:
            find(r'】</p><p>(.*?)<br />')
            break
        else:
            find(r'<br />(.*?)<br />斗豆')

    # 好友BOSS
    get('cmd=friendlist&page=1')
    for u in findall(r'侠：.*?B_UID=(\d+)'):
        # 乐斗
        get(f'cmd=fight&B_UID={u}')
        find(r'删</a><br />(.*?)，')
        if '体力值不足' in HTML:
            break

    # 帮友BOSS
    get('cmd=viewmem&page=1')
    for u in findall(r'侠：.*?B_UID=(\d+)'):
        # 乐斗
        get(f'cmd=fight&B_UID={u}')
        find(r'侠侣</a><br />(.*?)，')
        if '体力值不足' in HTML:
            break

    # 侠侣
    get('cmd=viewxialv&page=1')
    try:
        for u in findall(r'：.*?B_UID=(\d+)')[1:]:
            # 乐斗
            get(f'cmd=fight&B_UID={u}')
            if '使用规则' in HTML:
                find(r'】</p><p>(.*?)<br />')
            elif '查看乐斗过程' in HTML:
                find(r'删</a><br />(.*?)！')
            if '体力值不足' in HTML:
                break
    except Exception:
        ...


def 报名():
    '''报名

    每天报名武林大会
    周二、五、日报名侠侣争霸
    周六、日报名笑傲群侠
    '''
    # 武林大会
    get('cmd=fastSignWulin&ifFirstSign=1')
    if '使用规则' in HTML:
        MSG.append(find(r'】</p><p>(.*?)<br />'))
    else:
        MSG.append(find(r'升级。<br />(.*?) '))

    # 侠侣争霸
    if WEEK in ['2', '5', '0']:
        get('cmd=cfight&subtype=9')
        if '使用规则' in HTML:
            MSG.append(find(r'】</p><p>(.*?)<br />'))
        else:
            MSG.append(find(r'报名状态.*?<br />(.*?)<br />'))

    # 笑傲群侠
    if WEEK in ['6', '0']:
        get('cmd=knightfight&op=signup')
        MSG.append(find(r'侠士侠号.*?<br />(.*?)<br />'))


def 巅峰之战进行中():
    '''巅峰之战进行中

    周一报名（随机加入）、领奖
    周三、四、五、六、日征战
    '''
    if WEEK == '1':
        for c in ['cmd=gvg&sub=4&group=0&check=1', 'cmd=gvg&sub=1']:
            get(c)
            MSG.append(find(r'】</p>(.*?)<br />'))
    elif WEEK not in ['1', '2']:
        # 巅峰之战
        get('cmd=gvg&sub=0')
        for _ in range(14):
            # 征战
            get('cmd=gvg&sub=5')
            if '你在巅峰之战中' in HTML:
                if '战线告急' in HTML:
                    MSG.append(find(r'支援！<br />(.*?)。'))
                else:
                    MSG.append(find(r'】</p>(.*?)。'))
            else:
                # 冷却时间
                # 撒花祝贺
                # 请您先报名再挑战
                # 您今天已经用完复活次数了
                if '战线告急' in HTML:
                    MSG.append(find(r'支援！<br />(.*?)<br />'))
                else:
                    MSG.append(find(r'】</p>(.*?)<br />'))
                break


def 矿洞():
    '''矿洞

    每天挑战3次
    副本开启第五层简单
    领取通关奖励
    '''
    # 矿洞
    get('cmd=factionmine')
    for _ in range(5):
        if '领取奖励' in HTML:
            # 领取奖励
            get('cmd=factionmine&op=reward')
            MSG.append(find(r'】<br /><br />(.*?)<br />'))
        elif '开启副本' in HTML:
            # floor   1、2、3、4、5 对应 第一、二、三、四、五层
            # mode    1、2、3 对应 简单、普通、困难
            # 确认开启
            get('cmd=factionmine&op=start&floor=5&mode=1')
            MSG.append(find(r'矿石商店</a><br />(.*?)<br />'))
        elif '副本挑战中' in HTML:
            # 挑战
            get('cmd=factionmine&op=fight')
            MSG.append(find(r'商店</a><br />(.*?)<br />'))
            if '挑战次数不足' in HTML:
                break


def 掠夺():
    '''掠夺

    周二掠夺一次（选择可掠夺粮仓最低战力）、领奖
    周三领取胜负奖励
    '''
    if WEEK == '2':
        get('cmd=forage_war')
        if '本轮轮空' in HTML:
            MSG.append(find(r'本届战况：(.*?)<br />'))
            return

        # 掠夺
        get('cmd=forage_war&subtype=3')
        if gra_id := findall(r'gra_id=(\d+)">掠夺'):
            data = []
            for id in gra_id:
                get(f'cmd=forage_war&subtype=3&op=1&gra_id={id}')
                if zhanli := findall(r'<br />1.*? (\d+)\.'):
                    data += [(int(zhanli[0]), id)]
            if data:
                _, id = min(data)
                get(f'cmd=forage_war&subtype=4&gra_id={id}')
                MSG.append(find(r'返回</a><br />(.*?)<br />'))

        # 领奖
        get('cmd=forage_war&subtype=5')
        MSG.append(find(r'返回</a><br />(.*?)<br />'))
    elif WEEK == '3':
        get('cmd=forage_war&subtype=6')
        MSG.append(find(r'规则</a><br />(.*?)<br />'))


def 踢馆():
    '''踢馆

    周五试炼5次、高倍转盘一次、挑战至多31次
    周六领奖以及报名踢馆
    '''
    if WEEK == '5':
        for t in [2, 2, 2, 2, 2, 4]:
            # 试炼、高倍转盘
            get(f'cmd=facchallenge&subtype={t}')
            find(r'功勋商店</a><br />(.*?)<br />')
            if '你们帮没有报名参加这次比赛' in HTML:
                MSG.append('你们帮没有报名参加这次比赛')
                return
        for _ in range(31):
            # 挑战
            get('cmd=facchallenge&subtype=3')
            find(r'功勋商店</a><br />(.*?)<br />')
            if '您的挑战次数已用光' in HTML:
                MSG.append('您的挑战次数已用光')
                break
            elif '您的复活次数已耗尽' in HTML:
                MSG.append('您的复活次数已耗尽')
                break
    elif WEEK == '6':
        for p in ['7', '1']:
            get(f'cmd=facchallenge&subtype={p}')
            MSG.append(find(r'功勋商店</a><br />(.*?)<br />'))


def 竞技场():
    '''竞技场

    每月1~25号每天至多挑战10次、领取奖励、默认兑换10个河洛图书
    '''
    for _ in range(10):
        # 免费挑战 or 开始挑战
        get('cmd=arena&op=challenge')
        if '免费挑战次数已用完' in HTML:
            find(r'更新提示</a><br />(.*?)！')
            # 领取奖励
            get('cmd=arena&op=drawdaily')
            MSG.append(find(r'更新提示</a><br />(.*?)<br />'))
            break
        find(r'更新提示</a><br />(.*?)。')

    if yaml := read_yaml('竞技场'):
        # 兑换10个
        get(f'cmd=arena&op=exchange&id={yaml}&times=10')
        MSG.append(find(r'竞技场</a><br />(.*?)<br />'))


def 十二宫():
    '''十二宫

    每天默认白羊宫请猴王扫荡
    '''
    if yaml := read_yaml('十二宫'):
        # 请猴王扫荡
        get(f'cmd=zodiacdungeon&op=autofight&scene_id={yaml}')
        if '恭喜你' in HTML:
            MSG.append(find(r'恭喜你，(.*?)！'))
            return
        elif '是否复活再战' in HTML:
            MSG.append(find(r'<br.*>(.*?)，'))
            return
        # 你已经不幸阵亡，请复活再战！
        # 挑战次数不足
        # 当前场景进度不足以使用自动挑战功能
        MSG.append(find(r'<p>(.*?)<br />'))


def 许愿():
    '''许愿

    每天领取许愿奖励、上香许愿、领取魂珠碎片宝箱
    '''
    for sub in [5, 1, 6]:
        get(f'cmd=wish&sub={sub}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 抢地盘():
    '''抢地盘

    每天无限制区攻占一次第10位

    等级  30级以下 40级以下 ... 120级以下 无限制区
    type  1       2            10        11
    '''
    get('cmd=recommendmanor&type=11&page=1')
    if id := findall(r'manorid=(\d+)">攻占</a>'):
        # 攻占
        get(f'cmd=manorfight&fighttype=1&manorid={id[-1]}')
        MSG.append(find(r'】</p><p>(.*?)。'))
    # 兑换武器
    get('cmd=manor&sub=0')
    MSG.append(find(r'【抢地盘】<br /><br />(.*?)<br /><br />'))


def 历练():
    '''历练

    每天默认掉落佣兵碎片的每个关卡BOSS会被乐斗3次
    '''
    for id in read_yaml('历练'):
        for _ in range(3):
            get(f'cmd=mappush&subtype=3&mapid=6&npcid={id}&pageid=2')
            find(r'阅历值：\d+<br />(.*?)<br />')
            if '您还没有打到该历练场景' in HTML:
                find(r'介绍</a><br />(.*?)<br />')
                break
            elif '还不能挑战' in HTML:
                break
            elif '活力不足' in HTML:
                return


def 镖行天下():
    '''镖行天下

    每天拦截成功3次、领取奖励、刷新押镖并启程护送
    '''
    for op in [15, 16, 7, 8, 6]:
        # 护送完成 》领取奖励 》护送押镖 》刷新押镖 》启程护送
        get(f'cmd=cargo&op={op}')
        if '镖行天下' in HTML:
            MSG.append(find(r'商店</a><br />(.*?)<br />'))
        elif op == 8:
            find(r'】<br />(.*?)<br />')

    for _ in range(5):
        # 刷新
        get('cmd=cargo&op=3')
        for uin in findall(r'passerby_uin=(\d+)">拦截'):
            # 拦截
            get(f'cmd=cargo&op=14&passerby_uin={uin}')
            if '系统繁忙' in HTML:
                continue
            elif '这个镖车在保护期内' in HTML:
                continue
            elif '您今天已达拦截次数上限了' in HTML:
                return
            MSG.append(find(r'商店</a><br />(.*?)<br />'))


def 幻境():
    '''幻境

    每天默认乐斗鹅王的试炼
    '''
    if yaml := read_yaml('幻境'):
        get(f'cmd=misty&op=start&stage_id={yaml}')
        for _ in range(5):
            # 乐斗
            get(f'cmd=misty&op=fight')
            MSG.append(find(r'星数.*?<br />(.*?)<br />'))
            if '尔等之才' in HTML:
                break
        # 返回飘渺幻境
        get('cmd=misty&op=return')


def 群雄逐鹿():
    '''群雄逐鹿

    每周六报名、领奖
    '''
    for op in ['signup', 'drawreward']:
        get(f'cmd=thronesbattle&op={op}')
        MSG.append(find(r'届群雄逐鹿<br />(.*?)<br />'))


def 画卷迷踪():
    '''画卷迷踪

    每天至多挑战20次
    '''
    for _ in range(20):
        # 准备完成进入战斗
        get('cmd=scroll_dungeon&op=fight&buff=0')
        MSG.append(find(r'选择</a><br /><br />(.*?)<br />'))
        if '没有挑战次数' in HTML:
            break
        elif '征战书不足' in HTML:
            break


def 门派():
    '''门派

    万年寺：点燃 》点燃
    八叶堂：进入木桩训练 》进入同门切磋
    五花堂：至多完成任务3次
    '''
    # 点燃 》点燃
    for op in ['fumigatefreeincense', 'fumigatepaidincense']:
        get(f'cmd=sect&op={op}')
        MSG.append(find(r'修行。<br />(.*?)<br />'))

    # 进入木桩训练 》进入同门切磋
    for op in ['trainingwithnpc', 'trainingwithmember']:
        get(f'cmd=sect&op={op}')
        MSG.append(find(r'【八叶堂】<br />(.*?)<br />'))

    # 五花堂
    wuhuatang = get('cmd=sect_task')
    missions = {
        '进入华藏寺看一看': 'cmd=sect_art',
        '进入伏虎寺看一看': 'cmd=sect_trump',
        '进入金顶看一看': 'cmd=sect&op=showcouncil',
        '进入八叶堂看一看': 'cmd=sect&op=showtraining',
        '进入万年寺看一看': 'cmd=sect&op=showfumigate',
        '与掌门进行一次武艺切磋': 'cmd=sect&op=trainingwithcouncil&rank=1&pos=1',
        '与首座进行一次武艺切磋': 'cmd=sect&op=trainingwithcouncil&rank=2&pos=1',
        '与堂主进行一次武艺切磋': 'cmd=sect&op=trainingwithcouncil&rank=3&pos=1',
    }
    for name, url in missions.items():
        if name in wuhuatang:
            get(url)
    if '查看一名' in wuhuatang:
        # 查看一名同门成员的资料 or 查看一名其他门派成员的资料
        for page in [2, 3]:
            # 好友第2、3页
            get(f'cmd=friendlist&page={page}')
            for uin in findall(r'\d+：.*?B_UID=(\d+).*?级'):
                # 查看好友
                get(f'cmd=totalinfo&B_UID={uin}')
    if '进行一次心法修炼' in wuhuatang:
        '''
        少林心法      峨眉心法    华山心法      丐帮心法    武当心法      明教心法
        101 法华经    104 斩情决  107 御剑术   110 醉拳    113 太极内力  116 圣火功
        102 金刚经    105 护心决  108 龟息术   111 烟雨行  114 绕指柔剑  117 五行阵
        103 达摩心经  106 观音咒  109 养心术   112 笑尘诀  115 金丹秘诀  118 日月凌天
        '''
        for id in range(101, 119):
            get(f'cmd=sect_art&subtype=2&art_id={id}&times=1')
            if '修炼成功' in HTML:
                find(r'】<br />(.*?)<br />')
                break
            elif '修炼失败' in HTML:
                if '你的门派贡献不足无法修炼' in HTML:
                    break
                elif ('你的心法已达顶级无需修炼' in HTML) and (id == 118):
                    MSG.append('所有心法都已经顶级')
    # 五花堂
    get('cmd=sect_task')
    for id in findall(r'task_id=(\d+)">完成'):
        # 完成
        get(f'cmd=sect_task&subtype=2&task_id={id}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 门派邀请赛():
    '''门派邀请赛


    每周一报名、领取奖励
    每周三、四、五、六、日挑战6次以及默认兑换10个炼气石
    '''
    if WEEK == '1':
        # 组队报名
        get('cmd=secttournament&op=signup')
        if '已加入到某只队伍中' in HTML:
            MSG.append(find(r'规则</a><br />(.*?)<br />'))
        elif '邀请好友' in HTML:
            MSG.append(find(r'】<br />(.*?)<br />'))
        # 领取奖励
        get('cmd=secttournament&op=getrankandrankingreward')
        MSG.append(find(r'规则</a><br />(.*?)<br />'))
    elif WEEK not in ['1', '2']:
        for _ in range(6):
            # 开始挑战
            get('cmd=secttournament&op=fight')
            MSG.append(find(r'规则</a><br />(.*?)<br />'))
        if yaml := read_yaml('门派邀请赛'):
            # 兑换10个
            get(f'cmd=exchange&subtype=2&type={yaml}&times=10&costtype=11')
            MSG.append(find(r'】<br />(.*?)<br />'))


def 会武():
    '''会武

    周一初级、中级至多挑战5次，高级至多挑战10次
    周二、三高级至多挑战10次（自动兑换试炼书*10）
    周四助威丐帮
    周六领取奖励、兑换真黄金卷轴*10
    '''
    if WEEK in ['1', '2', '3']:
        for _ in range(21):
            # 挑战
            get('cmd=sectmelee&op=dotraining')
            # MSG.append(find(r'最高伤害：\d+<br />(.*?)<br />'))
            if '你已达今日挑战上限' in HTML:
                MSG.append('试炼场挑战已达今日挑战上限')
                break
            elif '你的试炼书不足' in HTML:
                # 兑换 试炼书*10
                get('cmd=exchange&subtype=2&type=1265&times=10&costtype=13')
                if '会武积分不足' in HTML:
                    # 抱歉，您的会武积分不足，不能兑换该物品！
                    MSG.append('会武积分不足兑换试炼书*10')
                    break
    elif WEEK == '4':
        # 冠军助威 丐帮
        get('cmd=sectmelee&op=cheer&sect=1003')
        # 冠军助威
        get('cmd=sectmelee&op=showcheer')
        MSG.append(find(r'【冠军助威】<br />(.*?)<br />'))
    elif WEEK == '6':
        # 领奖
        get('cmd=sectmelee&op=drawreward')
        MSG.append(find(r'【领奖】<br />(.*?)<br />'))
        # 兑换 真黄金卷轴*10
        get('cmd=exchange&subtype=2&type=1263&times=10&costtype=13')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 梦想之旅():
    '''梦想之旅

    每天普通旅行一次
    周四梦幻旅行（如果下一个区域存在 '已去过'）、领取区域、超级礼包
    '''
    # 普通旅行
    get('cmd=dreamtrip&sub=2')
    MSG.append(find(r'规则</a><br />(.*?)<br />'))

    if WEEK == '4':
        bmapid = {
            '空桑山': 2,
            '鹊山': 3,
            '鹿蜀': 4,
            '昆仑之丘': 1
        }
        # 梦想之旅
        get('cmd=dreamtrip')
        for k, v in bmapid.items():
            if k in HTML:
                # 下一个区域
                get(f'cmd=dreamtrip&sub=0&bmapid={v}')
                if '已去过' in HTML:
                    # 梦想之旅
                    get('cmd=dreamtrip')
                    if smapid := findall(r'梦幻旅行</a><br />(.*?)<br /><br />'):
                        # 查找未去过的目的地
                        id_list = []
                        list = smapid[0].split('<br />')
                        for i, v in enumerate(list):
                            if '未去过' in v:
                                id_list.append(i + 1)
                        # 消耗梦幻机票去目的地
                        for id in id_list:
                            # 去这里
                            get(f'cmd=dreamtrip&sub=2&smapid={id}')
                            MSG.append(find(r'规则</a><br />(.*?)<br />'))
                            if '当前没有梦幻机票' in HTML:
                                break
        # 梦想之旅
        get('cmd=dreamtrip')
        for _ in range(2):
            if bmapid := findall(r'sub=4&amp;bmapid=(\d+)'):
                # 礼包     1 or 2 or 3 or 4
                # 超级礼包 0
                get(f'cmd=dreamtrip&sub=4&bmapid={bmapid[0]}')
                MSG.append(find(r'规则</a><br />(.*?)<br />'))


def 问鼎天下():
    '''问鼎天下

    周一领取奖励
    周一、二、三、四、五领取帮资或放弃资源点、东海攻占倒数第一个至多两次
    周六淘汰赛助威 神ㄨ阁丶
    周日排名赛助威 神ㄨ阁丶
    '''
    if WEEK == '1':
        # 领取奖励
        get('cmd=tbattle&op=drawreward')
        MSG.append(find(r'规则</a><br />(.*?)<br />'))
    if WEEK not in ['6', '0']:
        # 问鼎天下
        get('cmd=tbattle')
        if '你占领的领地已经枯竭' in HTML:
            # 领取
            get('cmd=tbattle&op=drawreleasereward')
            MSG.append(find(r'规则</a><br />(.*?)<br />'))
        elif '放弃' in HTML:
            # 放弃
            get('cmd=tbattle&op=abandon')
            MSG.append(find(r'规则</a><br />(.*?)<br />'))
        for _ in range(2):
            # 1东海 2南荒   3西泽   4北寒
            get(f'cmd=tbattle&op=showregion&region=1')
            # 攻占 倒数第一个
            if id := findall(r'id=(\d+).*?攻占</a>'):
                get(f'cmd=tbattle&op=occupy&id={id[-1]}&region=1')
                MSG.append(find(r'规则</a><br />(.*?)<br />'))
                if '大获全胜' in HTML:
                    break
    elif WEEK == '6':
        # 淘汰赛助威
        id = read_yaml('问鼎天下')['淘汰赛']
        get(f'cmd=tbattle&op=cheerregionbattle&id={id}')
        MSG.append(find(r'规则</a><br />(.*?)<br />'))
    elif WEEK == '0':
        # 排名赛助威
        id = read_yaml('问鼎天下')['排名赛']
        get(f'cmd=tbattle&op=cheerchampionbattle&id={id}')
        MSG.append(find(r'规则</a><br />(.*?)<br />'))


def 帮派商会():
    '''帮派商会

    每天帮派宝库领取礼包、交易会所交易物品、兑换商店兑换物品
    '''
    for _ in range(10):
        # 帮派宝库
        get('cmd=fac_corp&op=0')
        if mode := findall(r'gift_id=(\d+)&amp;type=(\d+)">点击领取'):
            for id, t in mode:
                get(f'cmd=fac_corp&op=3&gift_id={id}&type={t}')
                MSG.append(find(r'】</p>(.*?)<br />'))
        else:
            break

    # 交易会所
    get('cmd=fac_corp&op=1')
    data: dict = read_yaml('帮派商会')
    jiaoyi: dict = data['交易会所']
    for jiaoyi_name, params in jiaoyi.items():
        if jiaoyi_name in HTML:
            get(f'cmd=fac_corp&op=4&{params}')
            MSG.append(find(r'】</p>(.*?)<br />'))

    # 兑换商店
    get('cmd=fac_corp&op=2')
    data: dict = read_yaml('帮派商会')
    duihuan: dict = data['兑换商店']
    for duihuan_name, type_id in duihuan.items():
        if duihuan_name in HTML:
            get(f'cmd=fac_corp&op=5&type_id={type_id}')
            MSG.append(find(r'】</p>(.*?)<br />'))


def 帮派远征军():
    '''帮派远征军

    周一、二、三、四、五、六参战攻击
    周日领取奖励
    '''
    while WEEK != '0':
        # 帮派远征军
        get('cmd=factionarmy&op=viewIndex&island_id=-1')
        point_id = findall(r'point_id=(\d+)">参战')
        if not point_id:
            MSG.append('已经全部通关了，周日领取奖励')
            break
        for p in point_id:
            # 参战
            get(f'cmd=factionarmy&op=viewpoint&point_id={p}')
            for u in findall(r'opp_uin=(\d+)">攻击'):
                # 攻击
                get(
                    f'cmd=factionarmy&op=fightWithUsr&point_id={p}&opp_uin={u}')
                if '参数错误' in HTML:
                    continue
                elif '您的血量不足' in HTML:
                    MSG.append('您的血量不足，请重生后在进行战斗')
                    return
    if WEEK == '0':
        # 领取奖励
        for id in range(15):
            get(f'cmd=factionarmy&op=getPointAward&point_id={id}')
            if '【帮派远征军】' in HTML:
                find(r'】<br /><br />(.*?)</p>')
                if '点尚未攻占下来' in HTML:
                    break
            elif '恭喜您' in HTML:
                MSG.append(find(r'】<br />(.*?)<br />'))
        # 领取岛屿宝箱
        for id in range(5):
            get(f'cmd=factionarmy&op=getIslandAward&island_id={id}')
            if '【帮派远征军】' in HTML:
                find(r'】<br /><br />(.*?)</p>')
                if '岛尚未攻占下来' in HTML:
                    break
            elif '恭喜您' in HTML:
                MSG.append(find(r'】<br />(.*?)<br />'))


def 帮派黄金联赛():
    '''帮派黄金联赛

    领取奖励、领取帮派赛季奖励、参与防守、参战攻击
    '''
    # 帮派黄金联赛
    get('cmd=factionleague&op=0')
    if '领取奖励' in HTML:
        # 领取轮次奖励
        get('cmd=factionleague&op=5')
        MSG.append(find(r'<p>(.*?)<br /><br />'))
    elif '领取帮派赛季奖励' in HTML:
        # 领取帮派赛季奖励
        get('cmd=factionleague&op=7')
        MSG.append(find(r'<p>(.*?)<br /><br />'))
    elif '参与防守' in HTML:
        # 参与防守
        get('cmd=factionleague&op=1')
        MSG.append(find(r'<p>(.*?)<br /><br />'))

    if '参战</a>' in HTML:
        uin = []
        # 参战
        get('cmd=factionleague&op=2')
        if pages := findall(r'pages=(\d+)">末页'):
            for p in range(1, int(pages[0]) + 1):
                get(f'cmd=factionleague&op=2&pages={p}')
                uin += findall(r'%&nbsp;&nbsp;(\d+).*?opp_uin=(\d+)')
            # 按战力排序
            uin.sort()
        else:
            MSG.append('没有可攻击的敌人')

        for _, uin in uin:
            # 攻击
            get(f'cmd=factionleague&op=4&opp_uin={uin}')
            if '不幸战败' in HTML:
                MSG.append(find(r'】<br />(.*?)<br />'))
                break
            elif '您已阵亡' in HTML:
                MSG.append(find(r'】<br /><br />(.*?)</p>'))
                break
            find(r'】<br />(.*?)<br />')


def 任务派遣中心():
    '''任务派遣中心

    每天领取奖励、接受任务
    '''
    # 任务派遣中心
    get('cmd=missionassign&subtype=0')
    for id in findall(r'mission_id=(.*?)">查看'):
        # 领取奖励
        get(f'cmd=missionassign&subtype=5&mission_id={id}')
        MSG.append(find(r'\[任务派遣中心\](.*?)<br />'))

    # 接受任务
    missions_dict = {
        '少女天团': '2',
        '闺蜜情深': '17',
        '男女搭配': '9',
        '鼓舞士气': '5',
        '仙人降临': '6',
        '雇佣军团': '11',
        '调整状态': '12',
        '防御工事': '10',
        '护送长老': '1',
        '坚持不懈': '4',
        '降妖除魔': '3',
        '深山隐士': '7',
        '抓捕小偷': '8',
        '小队巡逻': '13',
        '武艺切磋': '14',
        '哥俩好啊': '15',
        '协助村长': '16',
        '打扫房间': '18',
        '货物运送': '19',
        '消除虫害': '20',
        '帮助邻居': '21',
        '上山挑水': '22',
        '房屋维修': '23',
        '清理蟑螂': '24',
        '收割作物': '25',
        '炊烟袅袅': '26',
        '湖边垂钓': '27',
        '勤劳园丁': '29'
    }
    # 任务派遣中心
    get('cmd=missionassign&subtype=0')
    for _ in range(3):
        mission_id = findall(r'mission_id=(\d+)">接受')
        for _, id in missions_dict.items():
            if id in mission_id:
                # 快速委派
                get(f'cmd=missionassign&subtype=7&mission_id={id}')
                # 开始任务
                get(f'cmd=missionassign&subtype=8&mission_id={id}')
                if '任务数已达上限' in HTML:
                    break
        # 任务派遣中心
        get('cmd=missionassign&subtype=0')
        if '今日已领取了全部任务哦' in HTML:
            break
        elif HTML.count('查看') == 3:
            break
        elif '50斗豆' not in HTML:
            # 刷新任务
            get('cmd=missionassign&subtype=3')

    # 任务派遣中心
    get('cmd=missionassign&subtype=0')
    for msg in findall(r'<br />(.*?)&nbsp;<a.*?查看'):
        MSG.append(msg)


def 武林盟主():
    '''武林盟主

    周三、五、日领取排行奖励和竞猜奖励
    周一、三、五分站赛默认报名黄金，总决赛不需报名
    周二、四、六竞猜
    '''
    if WEEK in ['3', '5', '0']:
        # 武林盟主
        get('cmd=wlmz&op=view_index')
        if data := findall(r'section_id=(\d+)&amp;round_id=(\d+)">'):
            for s, r in data:
                get(f'cmd=wlmz&op=get_award&section_id={s}&round_id={r}')
                MSG.append(find(r'【武林盟主】<br /><br />(.*?)</p>'))
        else:
            MSG.append('没有可领取的排行奖励和竞猜奖励')

    if WEEK in ['1', '3', '5']:
        if yaml := read_yaml('武林盟主'):
            get(f'cmd=wlmz&op=signup&ground_id={yaml}')
            if '总决赛周不允许报名' in HTML:
                MSG.append(find(r'战报</a><br />(.*?)<br />'))
                return
            MSG.append(find(r'赛场】<br />(.*?)<br />'))
    elif WEEK in ['2', '4', '6']:
        for index in range(8):
            # 选择
            get(f'cmd=wlmz&op=guess_up&index={index}')
            find(r'规则</a><br />(.*?)<br />')
        # 确定竞猜选择
        get('cmd=wlmz&op=comfirm')
        MSG.append(find(r'战报</a><br />(.*?)<br />'))


def 全民乱斗():
    '''全民乱斗

    乱斗竞技、乱斗任务领取
    '''
    n = True
    for t in [2, 3, 4]:
        get(f'cmd=luandou&op=0&acttype={t}')
        for id in findall(r'.*?id=(\d+)">领取</a>'):
            n = False
            # 领取
            get(f'cmd=luandou&op=8&id={id}')
            MSG.append(find(r'斗】<br /><br />(.*?)<br />'))
    if n:
        MSG.append('没有可领取的')


def 侠士客栈():
    '''侠士客栈

    每天领取奖励3次、客栈奇遇
    '''
    # 侠士客栈
    get('cmd=warriorinn')
    if type := findall(r'type=(\d+).*?领取奖励</a>'):
        for n in range(1, 4):
            # 领取奖励
            get(f'cmd=warriorinn&op=getlobbyreward&type={type[0]}&num={n}')
            MSG.append(find(r'侠士客栈<br />(.*?)<br />'))

    # 奇遇
    for p in findall(r'pos=(\d+)'):
        get(f'cmd=warriorinn&op=showAdventure&pos={p}')
        if '前来捣乱的' in HTML:
            # 前来捣乱的xx -> 与TA理论 -> 确认
            get(f'cmd=warriorinn&op=exceptadventure&pos={p}')
            if '战斗' in HTML:
                MSG.append(find(r'侠士客栈<br />(.*?) ，'))
                continue
            MSG.append(find(r'侠士客栈<br />(.*?)<br />'))
        else:
            # 黑市商人、老乞丐 -> 你去别人家问问吧、拯救世界的任务还是交给别人把 -> 确认
            get(f'cmd=warriorinn&op=rejectadventure&pos={p}')


def 江湖长梦():
    '''江湖长梦

    周四兑换玄铁令*7、开启柒承的忙碌日常副本
    '''
    for _ in range(7):
        # 兑换 玄铁令*1
        get('cmd=longdreamexchange&op=exchange&key_id=5&page=1')
        if '兑换成功' in HTML:
            MSG.append(find(r'侠士碎片</a><br />(.*?)<br />'))
        elif '【江湖长梦-兑换商店】' in HTML:
            MSG.append(find(r'】<br />(.*?)<br />'))
            break

    for id, num in read_yaml('江湖长梦'):
        if id != 1:
            MSG.append('目前仅支持柒承的忙碌日常')
            break
        for _ in range(num):
            get(f'cmd=jianghudream&op=showCopyInfo&id={id}')
            # 开启副本
            get(f'cmd=jianghudream&op=beginInstance&ins_id={id}')
            if '开启副本所需追忆香炉不足' in HTML:
                return
            elif '无法开启副本' in HTML:
                return

            # 进入下一天
            get('cmd=jianghudream&op=goNextDay')
            if '进入下一天异常' in HTML:
                # 开启副本
                get(f'cmd=jianghudream&op=beginInstance&ins_id={id}')
            for _ in range(7):
                if msg1 := findall(r'event_id=(\d+)">战斗\(等级1\)'):
                    # 战斗
                    get(f'cmd=jianghudream&op=chooseEvent&event_id={msg1[0]}')
                    # FIGHT!
                    get('cmd=jianghudream&op=doPveFight')
                    find(r'<p>(.*?)<br />')
                    if '战败' in HTML:
                        break
                elif msg2 := findall(r'event_id=(\d+)">奇遇\(等级1\)'):
                    # 奇遇
                    get(f'cmd=jianghudream&op=chooseEvent&event_id={msg2[0]}')
                    # 视而不见
                    get('cmd=jianghudream&op=chooseAdventure&adventure_id=2')
                    find(r'获得金币：\d+<br />(.*?)<br />')
                elif msg3 := findall(r'event_id=(\d+)">商店\(等级1\)'):
                    # 商店
                    get(f'cmd=jianghudream&op=chooseEvent&event_id={msg3[0]}')
                # 进入下一天
                get('cmd=jianghudream&op=goNextDay')

            # 结束回忆
            get('cmd=jianghudream&op=endInstance')
            MSG.append(find(r'【江湖长梦】<br />(.*?)<br /><a'))


def 增强经脉():
    '''任务-增强经脉

    每天至多传功12次
    '''
    # 关闭传功符不足用斗豆代替
    get('cmd=intfmerid&sub=21&doudou=0')
    if '关闭' in HTML:
        # 关闭合成两次确认
        get('cmd=intfmerid&sub=19')
    for _ in range(12):
        for id in findall(r'master_id=(\d+)">传功</a>'):
            url = [
                'cmd=intfmerid&sub=10&op=4',   # 一键合成
                'cmd=intfmerid&sub=5',  # 一键拾取
                f'cmd=intfmerid&sub=2&master_id={id}'  # 传功
            ]
            for u in url:
                get(u)
                find(r'</p>(.*?)<p>', '任务-增强经脉')
                if '传功符不足！' in HTML:
                    return


def 助阵():
    '''任务-助阵

    助阵组合  id   dex
    毒光剑影  1    0（生命）
    正邪两立  2    0、1（投掷减免、投掷伤害）
    纵剑天下  3    0、1、2（小型减免、速度、小型伤害）
    致命一击  9    0、1、2（暴击伤害、暴击减免、生命）
    老谋深算  4    0、1、2、3（大型减免、大型伤害、速度、生命）
    智勇双全  5    0、1、2、3（中型减免、中型伤害、减暴、暴击）
    以柔克刚  6    0、1、2、3（技能减免、技能伤害、闪避、命中）
    雕心鹰爪  7    0、1、2、3（投掷和小型武器穿透、技能穿透、大型穿透、中型穿透）
    根骨奇特  8    0、1、2、3、4（空手减免、空手伤害、力量、敏捷、生命）
    '''
    tianshu = {
        1: [0],
        2: [0, 1],
        3: [0, 1, 2],
        9: [0, 1, 2],
        4: [0, 1, 2, 3],
        5: [0, 1, 2, 3],
        6: [0, 1, 2, 3],
        7: [0, 1, 2, 3],
        8: [0, 1, 2, 3, 4]
    }
    n = 0
    for i, d in [(i, d) for i, dex in tianshu.items() for d in dex]:
        if n == 3:
            break
        get(f'cmd=formation&type=4&formationid={i}&attrindex={d}&times=1')
        if '提升成功' in HTML:
            find(r'战斗力：.*?<br />(.*?)<br />', '任务-助阵')
            n += 1
        elif '不满足条件' in HTML:
            find(r'战斗力：.*?<br /><br />(.*?)。', '任务-助阵')
        elif '阅历不足' in HTML:
            find(r'战斗力：.*?<br /><br />(.*?)，', '任务-助阵')
            break


def 查看好友资料():
    '''任务-查看好友资料

    查看好友第二页
    '''
    # 武林 》设置 》乐斗助手
    get('cmd=view&type=6')
    if '开启查看好友信息和收徒' in HTML:
        #  开启查看好友信息和收徒
        get('cmd=set&type=1')
    # 查看好友第2页
    get(f'cmd=friendlist&page=2')
    for uin in findall(r'\d+：.*?B_UID=(\d+).*?级'):
        get(f'cmd=totalinfo&B_UID={uin}')


def 徽章进阶():
    '''任务-徽章进阶

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
    '''
    for id in range(1, 34):
        get(f'cmd=achievement&op=upgradelevel&achievement_id={id}&times=1')
        find(r';<br />(.*?)<br />', '任务-徽章进阶')
        if '进阶失败' in HTML:
            break
        elif '进阶成功' in HTML:
            break
        elif '物品不足' in HTML:
            break


def 兵法研习():
    '''任务-兵法研习

    兵法      消耗     id       功能
    金兰之泽  孙子兵法  2544     增加生命
    雷霆一击  孙子兵法  2570     增加伤害
    残暴攻势  武穆遗书  21001    增加暴击几率
    不屈意志  武穆遗书  21032    降低受到暴击几率
    '''
    for id in [21001, 2570, 21032, 2544]:
        get(f'cmd=brofight&subtype=12&op=practice&baseid={id}')
        find(r'武穆遗书：\d+个<br />(.*?)<br />', '任务-兵法研习')
        if '研习成功' in HTML:
            break


def 挑战陌生人():
    '''任务-挑战陌生人

    斗友乐斗四次
    '''
    # 斗友
    get('cmd=friendlist&type=1')
    B_UID = findall(r'：.*?级.*?B_UID=(\d+).*?乐斗</a>')
    for uin in B_UID[:4]:
        # 乐斗
        get(f'cmd=fight&B_UID={uin}&page=1&type=9')
        find(r'删</a><br />(.*?)！', '任务-挑战陌生人')


def 强化神装():
    '''任务-强化神装

    神装或技能升级一次（升级成功或失败才算一次）
    '''
    # 任务
    missions = get('cmd=task&sub=1')
    if 'id=116' in missions:
        for id in range(6):
            # 神兵  0
            # 神铠  1
            # 神羽  2
            # 神兽  3
            # 神饰  4
            # 神履  5
            get(f'cmd=outfit&op=1&magic_outfit_id={id}')
            find(r'\|<br />(.*?)<br />', '任务-强化神装')
            if '进阶失败' in HTML:
                break
            elif '成功' in HTML:
                break
    if 'id=117' in missions:
        magic_skill_id = [
            2644,  # 武神附体
            2665,  # 断筋
            2675,  # 召唤神兵
            2653,  # 圣盾术
            2687,  # 荆刺护甲
            2697,  # 无懈可击
            2782,  # 惩击
            2794,  # 圣洁之躯
            2804,  # 愈合祷言
            2831,  # 龟甲术
            2854,  # 重伤之爪
            2842,  # 蛮力猛击
            2888,  # 钻石锋刃
            2877,  # 至高皇权
            2865,  # 吸血咒
            2905,  # 动如脱兔
            2915,  # 足下生根
            2926,  # 迷踪步
        ]
        for id in magic_skill_id:
            get(f'cmd=outfit&op=3&magic_skill_id={id}')
            find(r'</a><br />(.*?)<br />', '任务-强化神装')
            if '升级失败' in HTML:
                break


def 武器专精():
    '''任务-武器专精

    专精或武器栏升级一次（升级成功或失败才算一次）
    '''
    # 任务
    missions = get('cmd=task&sub=1')
    if 'id=114' in missions:
        # 武器专精
        for tid in range(4):
            get(f'cmd=weapon_specialize&op=2&type_id={tid}')
            find(r'<br />(.*?)<br />', '任务-武器专精')
            if '升星失败' in HTML:
                break
            elif '升星成功' in HTML:
                break
    if 'id=115' in missions:
        # 武器栏
        for sid in range(1000, 1012):
            # 武器栏      投掷武器专精  小型武器专精  中型武器专精  大型武器专精
            # 专精·控制   1000         1003         1006         1009
            # 专精·吸血   1001         1004         1007         1010
            # 专精·凝神   1002         1005         1008         1011
            get(f'cmd=weapon_specialize&op=5&storage_id={sid}')
            if '激活' in HTML:
                find(r'<br /><br />(.*?)<br />', '任务-武器专精')
                continue
            find(r'<br />(.*?)<br />', '任务-武器专精')
            if '升星失败' in HTML:
                break
            elif '升星成功' in HTML:
                break


def 强化铭刻():
    '''任务-强化铭刻

    强化一次（强化成功或失败才算一次）

    技能      id  材料
    坚韧不拔  0   坚固的砥石
    嗜血如命  1   染血的羊皮
    坚定不移  2   稳固的磐石
    生存本能  3   沧桑的兽骨
    横扫千军  4   尖锐的铁器
    三魂之力  5   三彩水晶石
    四魂天功  6   四色补天石
    炙血战魂  7   破碎的铠甲
    百战之躯  8   粗壮的牛角
    攻无不克  9   锋利的狼牙
    魅影舞步  10
    '''
    idx = random.randint(0, 3)
    id = random.randint(0, 4)
    for id in range(11):
        get(
            f'cmd=inscription&subtype=5&type_id={id}&weapon_idx={idx}&attr_id={id}')
        find(r'<br />(.*?)<br />', '任务-强化铭刻')
        if '升级所需材料不足' in HTML:
            continue
        else:
            break


def 任务():
    '''任务

    增强经脉、助阵每天必做
    '''
    增强经脉()
    助阵()

    # 日常任务
    missions = get('cmd=task&sub=1')
    if '查看好友资料' in missions:
        查看好友资料()
    if '徽章进阶' in missions:
        徽章进阶()
    if '兵法研习' in missions:
        兵法研习()
    if '挑战陌生人' in missions:
        挑战陌生人()
    if '强化神装' in missions:
        强化神装()
    if '武器专精' in missions:
        武器专精()
    if '强化铭刻' in missions:
        强化铭刻()

    # 一键完成任务
    get('cmd=task&sub=7')
    for k, v in findall(r'id=\d+">(.*?)</a>.*?>(.*?)</a>'):
        MSG.append(f'{k} {v}')


def 我的帮派():
    '''我的帮派

    每天供奉5次、帮派任务至多领取奖励3次
    周日领取奖励、报名帮派战争、激活祝福
    '''
    # 我的帮派
    get('cmd=factionop&subtype=3&facid=0')
    if '你的职位' not in HTML:
        MSG.append('您还没有加入帮派')
        return

    # 周日 领取奖励 》报名帮派战争 》激活祝福
    if WEEK == '0':
        for sub in [4, 9, 6]:
            get(f'cmd=facwar&sub={sub}')
            MSG.append(find(r'</p>(.*?)<br /><a.*?查看上届'))

    for id in read_yaml('我的帮派'):
        # 供奉
        get(f'cmd=oblation&id={id}&page=1')
        if '每天最多供奉5次' in HTML:
            find(r'】</p><p>(.*?)<br />')
            break
        elif '很抱歉' in HTML:
            find(r'】</p><p>(.*?)<br />')
            continue
        MSG.append(find(r'】<br />(.*?)<br />'))

    # 帮派任务
    faction_missions = get('cmd=factiontask&sub=1')
    missions = {
        '帮战冠军': 'cmd=facwar&sub=4',
        '查看帮战': 'cmd=facwar&sub=4',
        '查看帮贡': 'cmd=factionhr&subtype=14',
        '查看祭坛': 'cmd=altar',
        '查看踢馆': 'cmd=facchallenge&subtype=0',
        '查看要闻': 'cmd=factionop&subtype=8&pageno=1&type=2',
        # '加速贡献': 'cmd=use&id=3038&store_type=1&page=1',
        '粮草掠夺': 'cmd=forage_war',
    }
    for name, url in missions.items():
        if name in faction_missions:
            get(url)
    if '帮派修炼' in faction_missions:
        n = 0
        for id in [2727, 2758, 2505, 2536, 2437, 2442, 2377, 2399, 2429]:
            '''
            2727  紫霞秘籍
            2758  逍遥心法
            2505  铁砂掌
            2536  真元护体
            2437  九阳神功
            2442  金钟罩
            2377  北冥神功
            2399  乾坤大挪移
            2429  养生之道
            '''
            for _ in range(4):
                get(f'cmd=factiontrain&type=2&id={id}&num=1&i_p_w=num%7C')
                if '你需要提升帮派等级来让你进行下一步的修炼' in HTML:
                    if id == 2429:
                        MSG.append('所有武功秘籍已满级')
                    break
                elif '技能经验增加' in HTML:
                    # 技能经验增加20！
                    n += 1
            if n == 4:
                break
    # 帮派任务
    get('cmd=factiontask&sub=1')
    for id in findall(r'id=(\d+)">领取奖励</a>'):
        # 领取奖励
        get(f'cmd=factiontask&sub=3&id={id}')
        MSG.append(find(r'日常任务</a><br />(.*?)<br />'))


def 帮派祭坛():
    '''帮派祭坛

    每天转动轮盘至多30次、领取通关奖励
    '''
    # 帮派祭坛
    get('cmd=altar')
    for _ in range(30):
        if '转动轮盘' in HTML:
            get('cmd=altar&op=spinwheel')
            if '随机分配' not in HTML:
                MSG.append(find(r'兑换</a><br />(.*?)<br />'))
                if '转转券不足' in HTML:
                    break
        elif '随机分配' in HTML:
            for op, id in findall(r'op=(.*?)&amp;id=(\d+)'):
                # 首次【随机分配】选择，后续【复仇列表】选择
                get(f'cmd=altar&op={op}&id={id}')
                if '选择路线' in HTML:
                    # 选择路线
                    get(f'cmd=altar&op=dosteal&id={id}')
                    if '随机分配' in HTML:
                        # 系统繁忙！
                        # 该帮派已解散
                        find(r'】<br /><br />(.*?)<br />')
                        continue
                if '【帮派祭坛】' in HTML:
                    MSG.append(find(r'兑换</a><br />(.*?)<br />'))
                    break
        elif '领取奖励' in HTML:
            get('cmd=altar&op=drawreward')
            if '当前没有累积奖励可以领取' in HTML:
                MSG.append(find(r'<br /><br />(.*?)</p>'))
            else:
                MSG.append(find(r'兑换</a><br />(.*?)<br />'))


def 飞升大作战():
    '''飞升大作战

    每天优先报名单排模式，玄铁令不足或者休赛期时选择匹配模式
    周四领取赛季结束奖励
    '''
    # 境界修为
    get('cmd=ascendheaven&op=showrealm')
    MSG.append(find(r'】<br />(.*?)<br />'))

    for _ in range(2):
        # 报名单排模式
        get('cmd=ascendheaven&op=signup&type=1')
        MSG.append(find(r'】<br />(.*?)<br />S'))
        if '时势造英雄' in HTML:
            break
        elif '还没有入场券玄铁令' in HTML:
            # 兑换 玄铁令*1
            get('cmd=ascendheaven&op=exchange&id=2&times=1')
            MSG.append(find(r'】<br />(.*?)<br />'))
            if '不足' not in HTML:
                # 本赛季该道具库存不足
                # 积分不足，快去参加飞升大作战吧~
                continue
        elif '不在报名时间' in HTML:
            break
        # 当前为休赛期，报名匹配模式
        get('cmd=ascendheaven&op=signup&type=2')
        MSG.append(find(r'】<br />(.*?)<br />S'))
        break
    if WEEK == '4':
        # 飞升大作战
        get('cmd=ascendheaven')
        if ('赛季结算中' in HTML):
            # 境界修为
            get('cmd=ascendheaven&op=showrealm')
            for s in findall(r'season=(\d+)'):
                # 领取奖励
                get(f'cmd=ascendheaven&op=getrealmgift&season={s}')
                MSG.append(find(r'】<br />(.*?)<br />'))


def 深渊之潮():
    '''深渊之潮

    每天帮派巡礼领取巡游赠礼、深渊秘境默认曲镜空洞
    '''
    # 帮派巡礼 》领取巡游赠礼
    get('cmd=abysstide&op=getfactiongift')
    MSG.append(find(r'】<br />(.*?)<br />'))
    if '您暂未加入帮派' in HTML:
        MSG.append('帮派巡礼需要加入帮派才能领取')
    if yaml := read_yaml('深渊之潮'):
        for _ in range(3):
            get(f'cmd=abysstide&op=enterabyss&id={yaml}')
            if '暂无可用挑战次数' in HTML:
                break
            elif '该副本需要顺序通关解锁' in HTML:
                MSG.append('该副本需要顺序通关解锁！')
                break
            for _ in range(5):
                # 开始挑战
                get('cmd=abysstide&op=beginfight')
            # 退出副本
            get('cmd=abysstide&op=endabyss')
            MSG.append(find(r'】<br />(.*?)<br />'))


def 每日奖励():
    '''每日奖励

    每天领取4次
    '''
    for key in ['login', 'meridian', 'daren', 'wuzitianshu']:
        # 每日奖励
        get(f'cmd=dailygift&op=draw&key={key}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 领取徒弟经验():
    '''领取徒弟经验

    每天一次
    '''
    # 领取徒弟经验
    get('cmd=exp')
    MSG.append(find(r'每日奖励</a><br />(.*?)<br />'))


def 今日活跃度():
    '''今日活跃度

    领取每天活跃度礼包、帮派总活跃礼包
    '''
    # 今日活跃度
    get('cmd=liveness')
    MSG.append(find(r'【(.*?)】'))
    if '帮派总活跃' in HTML:
        MSG.append(find(r'礼包</a><br />(.*?)<'))
    # 领取今日活跃度礼包
    for id in range(1, 5):
        get(f'cmd=liveness_getgiftbag&giftbagid={id}&action=1')
        MSG.append(find(r'】<br />(.*?)<p>'))
    # 领取帮派总活跃奖励
    get('cmd=factionop&subtype=18')
    if '创建帮派' in HTML:
        MSG.append(find(r'帮派</a><br />(.*?)<br />'))
    else:
        MSG.append(find(r'<br />(.*?)</p>'))


def 仙武修真():
    '''仙武修真

    每天领取3次任务、寻访长留山挑战至多5次
    '''
    for id in range(1, 4):
        # 领取
        get(f'cmd=immortals&op=getreward&taskid={id}')
        MSG.append(find(r'帮助</a><br />(.*?)<br />'))
    for _ in range(5):
        # 寻访 长留山
        get('cmd=immortals&op=visitimmortals&mountainId=1')
        if '你的今日寻访挑战次数已用光' in HTML:
            MSG.append(find(r'帮助</a><br />(.*?)<br />'))
            break
        # 挑战
        get('cmd=immortals&op=fightimmortals')
        MSG.append(find(r'帮助</a><br />(.*?)<a'))


def 大侠回归三重好礼():
    '''大侠回归三重好礼

    周四领取奖励
    '''
    # 大侠回归三重好礼
    get('cmd=newAct&subtype=173&op=1')
    if data := findall(r'subtype=(\d+).*?taskid=(\d+)'):
        for s, t in data:
            # 领取
            get(f'cmd=newAct&subtype={s}&op=2&taskid={t}')
            MSG.append(find(r'】<br /><br />(.*?)<br />'))
    else:
        MSG.append('没有可领取的奖励')


def 乐斗黄历():
    '''乐斗黄历

    每天占卜一次
    '''
    # 乐斗黄历
    get('cmd=calender&op=0')
    MSG.append(find(r'今日任务：(.*?)<br />'))
    # 领取
    get('cmd=calender&op=2')
    MSG.append(find(r'】<br /><br />(.*?)<br />'))
    if '任务未完成' in HTML:
        return
    # 占卜
    get('cmd=calender&op=4')
    MSG.append(find(r'】<br /><br />(.*?)<br />'))


def 器魂附魔():
    '''器魂附魔

    每天领取日活跃度达到50、80、110礼包
    '''
    # 器魂附魔
    get('cmd=enchant')
    for id in range(1, 4):
        # 领取
        get(f'cmd=enchant&op=gettaskreward&task_id={id}')
        MSG.append(find(r'器魂附魔<br />(.*?)<br />'))


def 镶嵌():
    '''镶嵌

    周四镶嵌魂珠升级（碎 -> 1 -> 2 -> 3）
    '''
    data = [
        zip('6666666', range(2000, 2007)),      # 魂珠碎片
        zip('3333333', range(4001, 4062, 10)),  # 魂珠1级
        zip('3333333', range(4002, 4063, 10)),  # 魂珠2级
    ]
    for t, id in [(t, id) for iter in data for t, id in iter]:
        for _ in range(50):
            if t == '6':
                # 魂珠碎片 -> 1
                get(f'cmd=upgradepearl&type={t}&exchangetype={id}')
                find(r'魂珠升级</p><p>(.*?)</p>')
                if '不能合成该物品' in HTML:
                    # 抱歉，您的xx魂珠碎片不足，不能合成该物品！
                    break
            else:
                # 1 -> 2 -> 3
                get(f'cmd=upgradepearl&type={t}&pearl_id={id}')
                if '您拥有的魂珠数量不够' in HTML:
                    find(r'魂珠升级</p><p>(.*?)。')
                    break
                find(r'魂珠升级</p><p>(.*?)</p>')


def 兵法():
    '''兵法

    周四随机助威
    周六领奖、领取斗币
    '''
    if WEEK == '4':
        # 助威
        get('cmd=brofight&subtype=13')
        if teamid := findall(r'.*?teamid=(\d+).*?助威</a>'):
            t = random.choice(teamid)
            # 确定
            get(f'cmd=brofight&subtype=13&teamid={t}&type=5&op=cheer')
            MSG.append(find(r'领奖</a><br />(.*?)<br />'))
    elif WEEK == '6':
        # 兵法 -> 助威 -> 领奖
        get('cmd=brofight&subtype=13&op=draw')
        MSG.append(find(r'领奖</a><br />(.*?)<br />'))

        for t in range(1, 6):
            get(f'cmd=brofight&subtype=10&type={t}')
            for number, uin in findall(r'50000&nbsp;&nbsp;(\d+).*?champion_uin=(\d+)'):
                if number == '0':
                    continue
                # 领取斗币
                get(
                    f'cmd=brofight&subtype=10&op=draw&champion_uin={uin}&type={t}')
                MSG.append(find(r'排行</a><br />(.*?)<br />'))
                return


def 神匠坊():
    '''神匠坊

    周四普通合成、符石打造、符石分解（仅I类）
    '''
    data = []
    for p in range(1, 20):
        # 下一页
        get(f'cmd=weapongod&sub=12&stone_type=0&quality=0&page={p}')
        data += findall(r'拥有：(\d+)/(\d+).*?stone_id=(\d+)')
        if '下一页' not in HTML:
            break
    for remaining, amount, id in data:
        if int(remaining) >= int(amount):
            count = int(int(remaining) / int(amount))
            for _ in range(count):
                # 普通合成
                get(f'cmd=weapongod&sub=13&stone_id={id}')
                find(r'背包<br /></p>(.*?)!')

    # 符石分解
    if yaml := read_yaml('神匠坊'):
        data = []
        for p in range(1, 10):
            # 下一页
            get(f'cmd=weapongod&sub=9&stone_type=0&page={p}')
            data += findall(r'数量:(\d+).*?stone_id=(\d+)')
            if '下一页' not in HTML:
                break
        for num, id in data:
            if int(id) in yaml:
                # 分解
                get(
                    f'cmd=weapongod&sub=11&stone_id={id}&num={num}&i_p_w=num%7C')
                find(r'背包</a><br /></p>(.*?)<')

    # 符石打造
    # 符石
    get('cmd=weapongod&sub=7')
    if data := findall(r'符石水晶：(\d+)'):
        amount = int(data[0])
        ten = int(amount / 60)
        one = int((amount - (ten * 60)) / 6)
        for _ in range(ten):
            # 打造十次
            get('cmd=weapongod&sub=8&produce_type=1&times=10')
            find(r'背包</a><br /></p>(.*?)<')
        for _ in range(one):
            # 打造一次
            get('cmd=weapongod&sub=8&produce_type=1&times=1')
            find(r'背包</a><br /></p>(.*?)<')


def 背包():
    '''背包

    yaml文件指定的物品、所有带宝箱的物品、锦囊、属性（xx洗刷刷除外）被使用至多10次
    '''
    data: list = read_yaml('背包')
    # 背包
    get('cmd=store&store_type=0')
    if page := findall(r'第1/(\d+)'):
        for p in range(1, int(page[0]) + 1):
            # 下页
            get(f'cmd=store&store_type=0&page={p}')
            data += findall(r'宝箱</a>数量：.*?id=(\d+).*?使用')

    # 锦囊、属性
    for t in [5, 2]:
        get(f'cmd=store&store_type={t}&page=1')
        data += findall(r'数量：.*?id=(\d+).*?使用')

    for id in data:
        if id in ['3023', '3024', '3025', '3103']:
            # xx洗刷刷
            continue
        for _ in range(10):
            # 使用
            get(f'cmd=use&id={id}')
            if '您使用了' in HTML:
                find(r'<br />(.*?)<br />斗豆')
            elif '你打开' in HTML:
                find(r'<br />(.*?)<br />斗豆')
            else:
                if '使用规则' in HTML:
                    find(r'】</p><p>(.*?)<br />')
                break


def 商店():
    '''商店

    每天查询积分，比如矿石商店、粮票商店、功勋商店等中的积分
    '''
    for type in [1, 2, 3, 4, 9, 10, 11, 12, 13, 14]:
        '''
        1 踢馆
        2 掠夺
        3 矿洞
        4 镖行天下
        9 幻境
        10 群雄逐鹿
        11 门派邀请赛
        12 帮派祭坛
        13 会武
        14 问鼎天下
        '''
        get(f'cmd=exchange&subtype=10&costtype={type}')
        MSG.append(find(r'】<br />(.*?)<br />'))

    # 江湖长梦
    # 武林盟主
    # 飞升大作战
    # 深渊之潮
    urls = [
        'cmd=longdreamexchange',
        'cmd=wlmz&op=view_exchange',
        'cmd=ascendheaven&op=viewshop',
        'cmd=abysstide&op=viewabyssshop'
    ]
    for url in urls:
        get(url)
        MSG.append(find(r'】<br />(.*?)<br />'))
    # 竞技场
    get('cmd=arena&op=queryexchange')
    MSG.append(find(r'竞技场</a><br />(.*?)<br /><br />'))
    # 帮派商会
    get('cmd=fac_corp&op=2')
    MSG.append(find(r'剩余刷新时间.*?秒&nbsp;(.*?)<br />'))


def 猜单双():
    '''猜单双

    随机单数、双数
    '''
    # 猜单双
    get('cmd=oddeven')
    for _ in range(5):
        if value := findall(r'value=(\d+)">.*?数'):
            value = random.choice(value)
            # 单数1 双数2
            get(f'cmd=oddeven&value={value}')
            MSG.append(find(r'】<br />(.*?)<br />'))
        else:
            break


def 煮元宵():
    '''煮元宵

    成熟度>=96时赶紧出锅
    '''
    # 煮元宵
    get('cmd=yuanxiao2014')
    # number: list = findall(r'今日剩余烹饪次数：(\d+)')
    for _ in range(4):
        # 开始烹饪
        get('cmd=yuanxiao2014&op=1')
        if '领取烹饪次数' in HTML:
            MSG.append('没有烹饪次数了')
            break
        for _ in range(20):
            maturity = findall(r'当前元宵成熟度：(\d+)')
            if int(maturity[0]) >= 96:
                # 赶紧出锅
                get('cmd=yuanxiao2014&op=3')
                MSG.append(find(r'活动规则</a><br /><br />(.*?)。'))
                break
            # 继续加柴
            get('cmd=yuanxiao2014&op=2')


def 元宵节():
    '''元宵节

    周四领取、领取月桂兔
    '''
    # 领取
    get('cmd=newAct&subtype=101&op=1')
    MSG.append(find(r'】</p>(.*?)<br />'))
    # 领取月桂兔
    get('cmd=newAct&subtype=101&op=2&index=0')
    MSG.append(find(r'】</p>(.*?)<br />'))


def 万圣节():
    '''万圣节

    点亮南瓜灯
    活动截止日的前一天优先兑换礼包B，最后兑换礼包A
    '''
    # 点亮南瓜灯
    get('cmd=hallowmas&gb_id=1')
    while True:
        if cushaw_id := findall(r'cushaw_id=(\d+)'):
            id = random.choice(cushaw_id)
            # 南瓜
            get(f'cmd=hallowmas&gb_id=4&cushaw_id={id}')
            MSG.append(find(r'】<br />(.*?)<br />'))
        # 恭喜您获得10体力和南瓜灯一个！
        # 恭喜您获得20体力和南瓜灯一个！南瓜灯已刷新
        # 请领取今日的活跃度礼包来获得蜡烛吧！
        if '请领取' in HTML:
            break

    # 兑换奖励
    get('cmd=hallowmas&gb_id=0')
    try:
        date: str = findall(r'~\d+月(\d+)日')[0]
        if int(DATE) == int(date) - 1:
            num: str = findall(r'南瓜灯：(\d+)个')[0]
            B = int(num) / 40
            A = (int(num) - int(B) * 40) / 20
            for _ in range(int(B)):
                # 礼包B 消耗40个南瓜灯
                get('cmd=hallowmas&gb_id=6')
                MSG.append(find(r'】<br />(.*?)<br />'))
            for _ in range(int(A)):
                # 礼包A 消耗20个南瓜灯
                get('cmd=hallowmas&gb_id=5')
                MSG.append(find(r'】<br />(.*?)<br />'))
    except Exception:
        ...


def 神魔转盘():
    '''神魔转盘

    幸运抽奖一次
    '''
    get('cmd=newAct&subtype=88&op=1')
    MSG.append(find(r'】<br />(.*?)<br />'))


def 乐斗驿站():
    '''乐斗驿站

    免费领取淬火结晶*1
    '''
    get('cmd=newAct&subtype=167&op=2')
    MSG.append(find(r'】<br />(.*?)<br />'))


def 浩劫宝箱():
    '''浩劫宝箱

    领取一次
    '''
    get('cmd=newAct&subtype=152')
    MSG.append(find(r'浩劫宝箱<br />(.*?)<br />'))


def 幸运转盘():
    '''幸运转盘

    转动轮盘一次
    '''
    get('cmd=newAct&subtype=57&op=roll')
    MSG.append(find(r'0<br /><br />(.*?)<br />'))


def 喜从天降():
    '''喜从天降

    点燃烟花
    '''
    get('cmd=newAct&subtype=137&op=1')
    MSG.append(find(r'】<br />(.*?)<br />'))


def 冰雪企缘():
    '''冰雪企缘

    至多领取两次
    '''
    # 冰雪企缘
    get('cmd=newAct&subtype=158&op=0')
    for t in findall(r'gift_type=(\d+)'):
        # 领取
        get(f'cmd=newAct&subtype=158&op=2&gift_type={t}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 甜蜜夫妻():
    '''甜蜜夫妻

    夫妻甜蜜好礼      至多领取3次
    单身鹅鼓励好礼    至多领取3次
    '''
    # 甜蜜夫妻
    get('cmd=newAct&subtype=129')
    for i in findall(r'flag=(\d+)'):
        # 领取
        get(f'cmd=newAct&subtype=129&op=1&flag={i}')
        MSG.append(find(r'】</p>(.*?)<br />'))


def 幸运金蛋():
    '''幸运金蛋

    砸金蛋
    '''
    # 幸运金蛋
    get('cmd=newAct&subtype=110&op=0')
    for i in findall(r'index=(\d+)'):
        # 砸金蛋
        get(f'cmd=newAct&subtype=110&op=1&index={i}')
        MSG.append(find(r'】<br /><br />(.*?)<br />'))


def 乐斗菜单():
    '''乐斗菜单

    点单
    '''
    # 乐斗菜单
    get('cmd=menuact')
    if gift := findall(r'套餐.*?gift=(\d+).*?点单</a>'):
        # 点单
        get(f'cmd=menuact&sub=1&gift={gift[0]}')
        MSG.append(find(r'哦！<br /></p>(.*?)<br />'))
    else:
        MSG.append('点单已领取完')


def 客栈同福():
    '''客栈同福

    献酒三次
    '''
    for _ in range(3):
        # 献酒
        get('cmd=newAct&subtype=155')
        MSG.append(find(r'】<br /><p>(.*?)<br />'))
        if '黄酒不足' in HTML:
            break


def 周周礼包():
    '''周周礼包

    领取一次
    '''
    # 周周礼包
    get('cmd=weekgiftbag&sub=0')
    if id := findall(r';id=(\d+)">领取'):
        # 领取
        get(f'cmd=weekgiftbag&sub=1&id={id[0]}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 登录有礼():
    '''登录有礼

    领取一次
    '''
    # 登录有礼
    get('cmd=newAct&subtype=56')
    # 领取
    if index := findall(r'gift_index=(\d+)">领取'):
        get(
            f'cmd=newAct&subtype=56&op=draw&gift_type=1&gift_index={index[-1]}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 活跃礼包():
    '''活跃礼包

    领取两次
    '''
    for p in ['1', '2']:
        get(f'cmd=newAct&subtype=94&op={p}')
        MSG.append(find(r'】.*?<br />(.*?)<br />'))


def 上香活动():
    '''上香活动

    领取檀木香、龙涎香各两次
    '''
    for _ in range(2):
        # 檀木香
        get('cmd=newAct&subtype=142&op=1&id=1')
        MSG.append(find(r'】<br />(.*?)<br />'))
        # 龙涎香
        get('cmd=newAct&subtype=142&op=1&id=2')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 徽章战令():
    '''徽章战令

    领取每日礼包
    '''
    # 每日礼包
    get('cmd=badge&op=1')
    MSG.append(find(r'】<br />(.*?)<br />'))


def 生肖福卡():
    '''生肖福卡

    领取
    '''
    # 领取
    get('cmd=newAct&subtype=174&op=7&task_id=1')
    MSG.append(find(r'~<br /><br />(.*?)<br />活跃度80'))


def 长安盛会():
    '''长安盛会

    盛会豪礼点击领取
    签到宝箱点击领取
    点击参与至多3次
    '''
    for _ in range(3):
        # 长安盛会
        get('cmd=newAct&subtype=118&op=0')
        for id in findall(r'op=1&amp;id=(\d+)'):
            if id == 3:
                # 选择奖励内容 3036黄金卷轴 or 5089黄金卷轴
                get('cmd=newAct&subtype=118&op=2&select_id=3036')
            get(f'cmd=newAct&subtype=118&op=1&id={id}')
            if '【周年嘉年华】' in HTML:
                MSG.append(find(r'】<br /><br />(.*?)</p>'))
                return
            else:
                MSG.append(find(r'】<br />(.*?)<br />'))


def 深渊秘宝():
    '''深渊秘宝

    三魂秘宝、七魄秘宝各免费抽奖一次
    '''
    # 深渊秘宝
    get('cmd=newAct&subtype=175')
    for t in findall(r'type=(\d+)&amp;times=1">免费抽奖'):
        get(f'cmd=newAct&subtype=175&op=1&type={t}&times=1')
        MSG.append(find(r'深渊秘宝<br />(.*?)<br />'))


def 登录商店():
    '''登录商店

    周四全部兑换黄金卷轴*1
    '''
    for _ in range(5):
        # 兑换5次 黄金卷轴*5
        get('cmd=newAct&op=exchange&subtype=52&type=1223&times=5')
        MSG.append(find(r'<br /><br />(.*?)<br /><br />'))
    for _ in range(3):
        # 兑换3次 黄金卷轴*1
        get('cmd=newAct&op=exchange&subtype=52&type=1223&times=1')
        MSG.append(find(r'<br /><br />(.*?)<br /><br />'))


def 盛世巡礼():
    '''盛世巡礼

    周四收下礼物

    对话		cmd=newAct&subtype=150&op=3&itemId=0
    点击继续	cmd=newAct&subtype=150&op=4&itemId=0
    收下礼物	cmd=newAct&subtype=150&op=5&itemId=0
    '''
    for itemId in [0, 4, 6, 9, 11, 14, 17]:
        # 收下礼物
        get(f'cmd=newAct&subtype=150&op=5&itemId={itemId}')
        MSG.append(find(r'礼物<br />(.*?)<br />'))


def 中秋礼盒():
    '''中秋礼盒

    领取
    '''
    # 中秋礼盒
    get('cmd=midautumngiftbag&sub=0')
    ids = findall(r'amp;id=(\d+)')
    if not ids:
        MSG.append('没有可领取的')
        return
    for id in ids:
        # 领取
        get(f'cmd=midautumngiftbag&sub=1&id={id}')
        MSG.append(find(r'】<br />(.*?)<br />'))
        if '已领取完该系列任务所有奖励' in HTML:
            continue


def 双节签到():
    '''双节签到

    领取签到奖励
    活动截止日的前一天领取奖励金
    '''
    # 双节签到
    get('cmd=newAct&subtype=144')
    date: str = findall(r'至\d+月(\d+)日')[0]
    if 'op=1' in HTML:
        # 领取
        get('cmd=newAct&subtype=144&op=1')
        MSG.append(find(r'】<br />(.*?)<br />'))
    if int(DATE) == int(date) - 1:
        # 奖励金
        get('cmd=newAct&subtype=144&op=3')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 圣诞有礼():
    '''圣诞有礼

    周四领取点亮奖励和连线奖励
    '''
    # 圣诞有礼
    get('cmd=newAct&subtype=145')
    for id in findall(r'task_id=(\d+)'):
        # 任务描述：领取奖励
        get(f'cmd=newAct&subtype=145&op=1&task_id={id}')
        MSG.append(find(r'】<br />(.*?)<br />'))
    # 连线奖励
    for index in findall(r'index=(\d+)'):
        get(f'cmd=newAct&subtype=145&op=2&index={index}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 五一礼包():
    '''五一礼包

    周四领取三次劳动节礼包
    '''
    for id in range(3):
        get(f'cmd=newAct&subtype=113&op=1&id={id}')
        if '【劳动节礼包】' in HTML:
            mode = r'】<br /><br />(.*?)</p>'
        else:
            mode = r'】<br /><br />(.*?)<br />'
        MSG.append(find(mode))


def 新春礼包():
    '''新春礼包

    周四领取礼包
    '''
    # 新春礼包
    get('cmd=xinChunGift&subtype=1')
    date_list = findall(r'~\d+月(\d+)日')
    giftid = findall(r'giftid=(\d+)')
    for date, id in zip(date_list, giftid):
        if int(DATE) == int(date) - 1:
            get(f'cmd=xinChunGift&subtype=2&giftid={id}')
            MSG.append(find(r'】<br />(.*?)<br />'))


def 新春拜年():
    '''新春拜年

    第一轮赠礼三个礼物
    第二轮收取礼物
    '''
    # 新春拜年
    get('cmd=newAct&subtype=147')
    if 'op=1' in HTML:
        for index in random.sample(range(5), 3):
            # 选中
            get(f'cmd=newAct&subtype=147&op=1&index={index}')
        # 赠礼
        get('cmd=newAct&subtype=147&op=2')
        MSG.append('已赠礼')
    elif 'op=3' in HTML:
        # 收取礼物
        get('cmd=newAct&subtype=147&op=3')
        MSG.append(find(r'祝您：.*?<br /><br />(.*?)<br />'))


def 春联大赛():
    '''春联大赛

    选择、领取斗币各三次
    '''
    # 开始答题
    get('cmd=newAct&subtype=146&op=1')
    if '您的活跃度不足' in HTML:
        MSG.append('您的活跃度不足50')
        return
    elif '今日答题已结束' in HTML:
        MSG.append('今日答题已结束')
        return

    chunlian = {
        '虎年腾大步': '兔岁展宏图',
        '虎辟长安道': '兔开大吉春',
        '虎跃前程去': '兔携好运来',
        '虎去雄风在': '兔来喜气浓',
        '虎带祥云去': '兔铺锦绣来',
        '虎蹄留胜迹': '兔角搏青云',
        '虎留英雄气': '兔会世纪风',
        '金虎辞旧岁': '银兔贺新春',
        '虎威惊盛世': '兔翰绘新春',
        '虎驰金世界': '兔唤玉乾坤',
        '虎声传捷报': '兔影抖春晖',
        '虎嘶飞雪里': '兔舞画图中',
        '兔归皓月亮': '花绽春光妍',
        '兔俊千山秀': '春暖万水清',
        '兔毫抒壮志': '燕梭织春光',
        '玉兔迎春至': '黄莺报喜来',
        '玉兔迎春到': '红梅祝福来',
        '玉兔蟾宫笑': '红梅五岭香',
        '卯时春入户': '兔岁喜盈门',
        '卯门生紫气': '兔岁报新春',
        '卯来四季美': '兔献百家福',
        '红梅迎春笑': '玉兔出月欢',
        '红梅赠虎岁': '彩烛耀兔年',
        '红梅迎雪放': '玉兔踏春来',
        '丁年歌盛世': '卯兔耀中华',
        '寅年春锦绣': '卯序业辉煌',
        '燕舞春光丽': '兔奔曙光新',
        '笙歌辞旧岁': '兔酒庆新春',
        '瑞雪兆丰年': '迎得玉兔归',
        '雪消狮子瘦': '月满兔儿肥',
    }
    for _ in range(3):
        for s in findall(r'上联：(.*?) 下联：'):
            x = chunlian.get(s)
            if x is None:
                # 上联在字库中不存在，将随机选择
                xialian = [random.choice(range(3))]
            else:
                xialian = findall(f'{x}<a.*?index=(\d+)')
            if xialian:
                # 选择
                # index 0 1 2
                get(f'cmd=newAct&subtype=146&op=3&index={xialian[0]}')
                MSG.append(find(r'剩余\d+题<br />(.*?)<br />'))
                # 确定选择
                get('cmd=newAct&subtype=146&op=2')
                MSG.append(find(r'】<br />(.*?)<br />'))

    for id in range(1, 4):
        # 领取
        get(f'cmd=newAct&subtype=146&op=4&id={id}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 乐斗游记():
    '''乐斗游记

    每天领取积分
    每周四一键领取、兑换十次、兑换一次
    '''
    # 乐斗游记
    get('cmd=newAct&subtype=176')

    # 今日游记任务
    for id in findall(r'task_id=(\d+)'):
        # 领取
        get(f'cmd=newAct&subtype=176&op=1&task_id={id}')
        MSG.append(find(r'积分。<br /><br />(.*?)<br />'))

    if WEEK == '4':
        # 一键领取
        get('cmd=newAct&subtype=176&op=5')
        MSG.append(find(r'积分。<br /><br />(.*?)<br />'))
        MSG.append(find(r'十次</a><br />(.*?)<br />乐斗'))
        # 兑换
        num_list: list = findall(r'溢出积分：(\d+)')
        if (num := int(num_list[0])) != 0:
            num10 = int(num / 10)
            num1 = num - (num10 * 10)
            for _ in range(num10):
                # 兑换十次
                get('cmd=newAct&subtype=176&op=2&num=10')
                MSG.append(find(r'积分。<br /><br />(.*?)<br />'))
            for _ in range(num1):
                # 兑换一次
                get('cmd=newAct&subtype=176&op=2&num=1')
                MSG.append(find(r'积分。<br /><br />(.*?)<br />'))


def 斗境探秘():
    '''斗境探秘

    领取每日探秘奖励、累计探秘奖励
    '''
    # 斗境探秘
    get('cmd=newAct&subtype=177')
    # 领取每日探秘奖励
    for id in findall(r'id=(\d+)&amp;type=2'):
        # 领取
        get(f'cmd=newAct&subtype=177&op=2&id={id}&type=2')
        MSG.append(find(r'】<br /><br />(.*?)<br />'))
    # 领取累计探秘奖励
    for id in findall(r'id=(\d+)&amp;type=1'):
        # 领取
        get(f'cmd=newAct&subtype=177&op=2&id={id}&type=1')
        MSG.append(find(r'】<br /><br />(.*?)<br />'))


def 新春登录礼():
    '''新春登录礼

    每天至多领取七次
    '''
    # 新春登录礼
    get('cmd=newAct&subtype=99&op=0')
    for day in findall(r'day=(\d+)'):
        # 领取
        get(f'cmd=newAct&subtype=99&op=1&day={day}')
        MSG.append(find(r'】<br />(.*?)<br />'))


def 年兽大作战():
    '''年兽大作战

    随机武技库免费一次
    自选武技库从大、中、小、投、技各随机选择一个补位
    挑战3次
    '''
    # 年兽大作战
    get('cmd=newAct&subtype=170&op=0')
    if '等级不够' in HTML:
        MSG.append('等级不够，还未开启年兽大作战哦！')
        return
    for _ in findall(r'剩余免费随机次数：(\d+)'):
        # 随机武技库 免费一次
        get('cmd=newAct&subtype=170&op=6')
        MSG.append(find(r'帮助</a><br />(.*?)<br />'))

    # 自选武技库
    # 从大、中、小、投、技各随机选择一个
    if '暂未选择' in HTML:
        for t in range(5):
            get(f'cmd=newAct&subtype=170&op=4&type={t}')
            if '取消选择' in HTML:
                continue
            if ids := findall(r'id=(\d+)">选择'):
                # 选择
                get(f'cmd=newAct&subtype=170&op=7&id={random.choice(ids)}')
                if '自选武技列表已满' in HTML:
                    break

    for _ in range(3):
        # 挑战
        get('cmd=newAct&subtype=170&op=8')
        MSG.append(find(r'帮助</a><br />(.*?)。'))


def 惊喜刮刮卡():
    '''惊喜刮刮卡

    每天至多领取三次、点击刮卡二十次
    '''
    for i in range(3):
        get(f'cmd=newAct&subtype=148&op=2&id={i}')
        MSG.append(find(r'奖池预览</a><br /><br />(.*?)<br />'))
    for _ in range(20):
        get('cmd=newAct&subtype=148&op=1')
        MSG.append(find(r'奖池预览</a><br /><br />(.*?)<br />'))
        if '您没有刮刮卡了' in HTML:
            break


def 开心娃娃机():
    '''开心娃娃机

    每天抓取一次
    '''
    get('cmd=newAct&subtype=124&op=1')
    MSG.append(find(r'】<br />(.*?)<br />'))


def 好礼步步升():
    '''好礼步步升

    每天领取一次
    '''
    get('cmd=newAct&subtype=43&op=get')
    MSG.append(find(r'】<br />(.*?)<br />'))


def 企鹅吉利兑():
    '''企鹅吉利兑

    领取、活动截止日的前一天兑换材料（每种至多兑换100次）
    '''
    # 企鹅吉利兑
    get('cmd=geelyexchange')
    # 修炼任务 》每日任务
    for id in findall(r'id=(\d+)">领取</a>'):
        # 领取
        get(f'cmd=geelyexchange&op=GetTaskReward&id={id}')
        MSG.append(find(r'】<br /><br />(.*?)<br /><br />'))

    try:
        # 限时兑换
        date: str = findall(r'至\d+月(\d+)日')[0]
        if int(DATE) == int(date) - 1:
            for p in read_yaml('企鹅吉利兑'):
                for _ in range(100):
                    get(f'cmd=geelyexchange&op=ExchangeProps&id={p}')
                    if '你的精魄不足，快去完成任务吧~' in HTML:
                        break
                    elif '该物品已达兑换上限~' in HTML:
                        break
                    MSG.append(find(r'】<br /><br />(.*?)<br />'))
                if '当前精魄：0' in HTML:
                    break
    except Exception:
        ...
    # 当前精魄
    MSG.append(find(r'喔~<br />(.*?)<br /><br />'))


def 乐斗回忆录():
    '''乐斗回忆录

    周四领取回忆礼包
    '''
    for id in [1, 3, 5, 7, 9]:
        # 回忆礼包
        get(f'cmd=newAct&subtype=171&op=3&id={id}')
        MSG.append(find(r'6点<br />(.*?)<br />'))


def 乐斗大笨钟():
    '''乐斗大笨钟

    领取一次
    '''
    # 领取
    get('cmd=newAct&subtype=18')
    MSG.append(find(r'<br /><br /><br />(.*?)<br />'))


def 爱的同心结():
    '''爱的同心结

    依次兑换礼包5、4、3、2、1
    '''
    duihuan = {
        4016: 20,
        4015: 16,
        4014: 10,
        4013: 4,
        4012: 2,
    }
    for id, count in duihuan.items():
        for _ in range(count):
            # 兑换
            get(f'cmd=loveknot&sub=2&id={id}')
            MSG.append(find(r'】<br />(.*?)<br />'))
            if '恭喜您兑换成功' not in HTML:
                break


def 周年生日祝福():
    '''周年生日祝福

    周四领取
    '''
    for day in range(1, 8):
        get(f'cmd=newAct&subtype=165&op=3&day={day}')
        MSG.append(find(r'】<br />(.*?)<br />'))
