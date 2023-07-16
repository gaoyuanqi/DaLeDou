# -*- coding: utf-8 -*-
import re
import time
import random
import traceback
from shutil import copy
from os import environ, path, getenv

import yaml
import requests
from loguru import logger


YAML_PATH = './config'


class CookieError(Exception):
    ...


class DaLeDouInit:
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie

    @staticmethod
    def clean_cookie(cookie) -> str:
        '''清洁大乐斗cookie

        :return: 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx'
        '''
        ck = ''
        for key in ['RK', 'ptcz', 'uin', 'skey']:
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

    @staticmethod
    def verify_cookie(cookie: str):
        '''验证cookie是否有效（至多重试3次）

        :return: str | None
        '''
        url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
        headers = {
            'Cookie': cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        for _ in range(3):
            res = requests.get(url=url, headers=headers)
            res.encoding = 'utf-8'
            if '商店' in res.text:
                return True

    @staticmethod
    def copy_yaml(qq: str):
        '''从 daledou.yaml 复制一份并命名为 qq.yaml 文件'''
        srcpath = f'{YAML_PATH}/daledou.yaml'
        yamlpath = f'{YAML_PATH}/{qq}.yaml'
        if not path.isfile(yamlpath):
            logger.success(f'成功创建配置文件：{YAML_PATH}/{qq}.yaml')
            copy(srcpath, yamlpath)

    @staticmethod
    def create_log(qq: str) -> int:
        '''创建当天日志文件'''
        date = time.strftime("%Y-%m-%d", time.localtime())
        return logger.add(
            f'./log/{qq}/{date}.log',
            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>',
            enqueue=True,
            encoding='utf-8',
            retention='30 days'
        )

    def main(self):
        cookie = DaLeDouInit.clean_cookie(self.cookie)
        qq = re.search(r'uin=o(\d+); ', cookie, re.S).group(1)
        if DaLeDouInit.verify_cookie(cookie):
            environ['QQ'] = qq
            environ['DLD_COOKIE'] = cookie
            logger.success(f'   {qq}：COOKIE有效')
            if cookie != getenv(f'DLD_COOKIE_VALID_{qq}'):
                environ[f'DLD_COOKIE_VALID_{qq}'] = cookie
                DaLeDouInit.copy_yaml(qq)
            return DaLeDouInit.create_log(qq)

        logger.warning(f'   {qq}：COOKIE无效！！!')
        if cookie != getenv(f'DLD_COOKIE_NULL_{qq}'):
            environ[f'DLD_COOKIE_NULL_{qq}'] = cookie
            push(f'cookie失效：{qq} ', [f'{cookie}'])


class DaLeDou:
    @staticmethod
    def get(params: str) -> str:
        global html
        url = f'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{params}'
        headers = {
            'Cookie': getenv('DLD_COOKIE'),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        for _ in range(3):
            res = requests.get(url, headers=headers)
            res.encoding = 'utf-8'
            html = res.text
            time.sleep(0.2)
            if '系统繁忙' not in html:
                break
        return html

    @staticmethod
    def read_yaml(key: str):
        '''读取 config 目录下的 yaml 配置文件'''
        try:
            with open(f'{YAML_PATH}/{getenv("QQ")}.yaml', 'r', encoding='utf-8') as fp:
                users = yaml.safe_load(fp)
                data = users[key]
            return data
        except Exception:
            error = traceback.format_exc()
            logger.error(f'{getenv("QQ")}.yaml 配置不正确：\n{error}')
            push(f'{getenv("QQ")}.yaml 异常', [error])

    @staticmethod
    def search(mode: str) -> str:
        '''查找首个'''
        if match := re.search(mode, html, re.S):
            result = match.group(1)
            logger.info(f'{getenv("QQ")} | {getenv("DLD_MISSIONS")}：{result}')
            return result

    @staticmethod
    def findall(mode: str) -> list:
        '''查找所有'''
        return re.findall(mode, html, re.S)

    @staticmethod
    def is_dld():
        '''判断是否大乐斗首页'''
        for _ in range(3):
            DaLeDou.get('cmd=index')
            if '退出' in html:
                return html.split('【退出】')[0]


def push(title: str, message: list) -> None:
    '''pushplus 微信通知'''
    if token := getenv('PUSHPLUS_TOKEN'):
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
            return logger.success(f'  pushplus推送成功：{json}')
        return logger.warning(f'  pushplus推送失败：{json}')
    logger.warning('  pushplus配置的token无效，取消微信推送')


MSG = []
WEEK: str = time.strftime('%w')
DATE: str = time.strftime('%d', time.localtime())
D = DaLeDou()


def daledou(lunci: str):
    global MSG

    start = time.time()
    if lunci == '第一轮':
        missions = [
            [True, '邪神秘宝'],
            [(int(DATE) <= 26), '华山论剑'],
            [(DATE == '20'), '每日宝箱'],
            [True, '分享'],
            [True, '乐斗'],
            [True, '报名'],
            [True, '巅峰之战进行中'],
            [True, '矿洞'],
            [(WEEK in ['2', '3']), '掠夺'],
            [(WEEK in ['5', '6']), '踢馆'],
            [(int(DATE) <= 25), '竞技场'],
            [True, '十二宫'],
            [True, '许愿'],
            [True, '抢地盘'],
            [True, '历练'],
            [True, '镖行天下'],
            [True, '幻境'],
            [(WEEK == '6'), '群雄逐鹿'],
            [True, '画卷迷踪'],
            [True, '门派'],
            [(WEEK != '2'), '门派邀请赛'],
            [(WEEK not in ['5', '0']), '会武'],
            [True, '梦想之旅'],
            [True, '问鼎天下'],
            [True, '帮派商会'],
            [True, '帮派远征军'],
            [True, '帮派黄金联赛'],
            [True, '任务派遣中心'],
            [True, '武林盟主'],
            [True, '全民乱斗'],
            [True, '侠士客栈'],
            [True, '江湖长梦'],
            [True, '任务'],
            [True, '我的帮派'],
            [True, '帮派祭坛'],
            [True, '飞升大作战'],
            [True, '深渊之潮'],
            [True, '每日奖励'],
            [True, '今日活跃度'],
            [True, '仙武修真'],
            [(WEEK == '4'), '大侠回归三重好礼'],
            [True, '乐斗黄历'],
            [True, '器魂附魔'],
            [(WEEK == '4'), '镶嵌'],
            [(WEEK in ['4', '6']), '兵法'],
            [(WEEK == '4'), '神匠坊'],
            [True, '背包'],
            [True, '商店'],
            [True, '猜单双'],
            [True, '煮元宵'],
            [(WEEK == '4'), '元宵节'],
            [True, '万圣节'],
            [True, '神魔转盘'],
            [True, '乐斗驿站'],
            [True, '浩劫宝箱'],
            [True, '幸运转盘'],
            [True, '喜从天降'],
            [True, '冰雪企缘'],
            [True, '甜蜜夫妻'],
            [True, '幸运金蛋'],
            [True, '乐斗菜单'],
            [True, '客栈同福'],
            [True, '周周礼包'],
            [True, '登录有礼'],
            [True, '活跃礼包'],
            [True, '上香活动'],
            [True, '徽章战令'],
            [True, '生肖福卡'],
            [True, '长安盛会'],
            [True, '深渊秘宝'],
            [(WEEK == '4'), '登录商店'],
            [(WEEK == '4'), '盛世巡礼'],
            [True, '中秋礼盒'],
            [True, '双节签到'],
            [(WEEK == '4'), '圣诞有礼'],
            [(WEEK == '4'), '5.1礼包', '五一礼包'],
            [(WEEK == '4'), '新春礼包'],
            [True, '新春拜年'],
            [True, '春联大赛'],
            [True, '乐斗游记'],
            [True, '新春登录礼'],
            [True, '年兽大作战'],
            [True, '惊喜刮刮卡'],
            [True, '开心娃娃机'],
            [True, '好礼步步升'],
            [True, '企鹅吉利兑'],
            [(WEEK == '4'), '乐斗回忆录'],
            [True, '乐斗大笨钟'],
            [(WEEK == '4'), '周年生日祝福'],
        ]
    elif lunci == '第二轮':
        missions = [
            [True, '邪神秘宝'],
            [(WEEK not in ['6', '0']), '问鼎天下'],
            [True, '任务派遣中心'],
            [True, '侠士客栈'],
            [True, '深渊之潮'],
            [True, '幸运金蛋'],
            [True, '新春拜年'],
            [True, '乐斗大笨钟'],
        ]

    if html := D.is_dld():
        for bool, *data in missions:
            missions_name = data[0]
            if bool and (missions_name in html):
                if missions_name not in ['乐斗', '历练', '镶嵌', '神匠坊', '背包']:
                    MSG.append(f'\n【{missions_name}】')
                if len(data) == 1:
                    func_name = data[0]
                elif len(data) == 2:
                    func_name = data[1]
                environ['DLD_MISSIONS'] = missions_name
                globals()[func_name]()

    end = time.time()
    MSG.append(f'\n【运行时长】\n时长：{int(end - start)} s')
    push(f'{getenv("QQ")} {lunci}', MSG)

    MSG = []


def 邪神秘宝():
    '''邪神秘宝

        高级秘宝    免费一次 or 抽奖一次
        极品秘宝    免费一次 or 抽奖一次
    '''
    for i in [0, 1]:
        # 免费一次 or 抽奖一次
        D.get(f'cmd=tenlottery&op=2&type={i}')
        MSG.append(D.search(r'】</p>(.*?)<br />'))


def 华山论剑():
    '''华山论剑

        每月1~25号每天至多挑战10次，耐久不足时自动更换侠士
        每月26号领取赛季段位奖励
    '''
    if int(DATE) <= 25:
        for _ in range(10):
            # 开始挑战
            D.get('cmd=knightarena&op=challenge')
            if '耐久不足' in html:
                # 战阵调整页面
                D.get('cmd=knightarena&op=viewsetknightlist&pos=0')
                knightid = D.findall(r'knightid=(\d+)')

                # 出战侠士页面
                D.get('cmd=knightarena&op=viewteam')
                xuanze_pos = D.findall(r'pos=(\d+)">选择侠士')
                genggai = D.findall(r'耐久：(\d+)/.*?pos=(\d+)">更改侠士.*?id=(\d+)')

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
                    D.get(
                        f'cmd=knightarena&op=setknight&id={id}&pos={p}&type=1')
                continue
            MSG.append(D.search(r'荣誉兑换</a><br />(.*?)<br />'))
            if '论剑所需门票不足' in html:
                break
            elif '请先设置上阵侠士后再开始战斗' in html:
                break
    elif DATE == '26':
        D.get(r'cmd=knightarena&op=drawranking')
        MSG.append(D.search(r'【赛季段位奖励】<br />(.*?)<br />'))


def 每日宝箱():
    '''每日宝箱

        每月20号打开所有宝箱
    '''
    # 每日宝箱
    D.get('cmd=dailychest')
    while type_list := D.findall(r'type=(\d+)">打开'):
        # 打开
        D.get(f'cmd=dailychest&op=open&type={type_list[0]}')
        MSG.append(D.search(r'规则说明</a><br />(.*?)<br />'))


def 分享():
    '''分享

        每天分享直到上限，若次数不足则挑战斗神塔增加次数（每挑战11层增加一次分享）
        每周四领取分享次数奖励
    '''
    for _ in range(9):
        # 一键分享
        D.get(f'cmd=sharegame&subtype=6')
        D.findall(r'】</p>(.*?)<p>')
        if '上限' in html:
            MSG.append(D.search(r'</p><p>(.*?)<br />.*?开通达人'))
            # 自动挑战
            D.get('cmd=towerfight&type=11')
            # 结束挑战
            D.get('cmd=towerfight&type=7')
            break

        # 斗神塔
        D.get('cmd=towerfight&type=3')
        if '结束挑战' in html:
            # 结束挑战
            D.get('cmd=towerfight&type=7')
            D.search(r'】<br />(.*?)。<br />')
        for _ in range(11):
            # 开始挑战 or 挑战下一层
            D.get('cmd=towerfight&type=0')
            D.search(r'】<br />(.*?)。<br />')
            if '您败给' in html:
                # 结束挑战
                D.get('cmd=towerfight&type=7')
                D.search(r'】<br />(.*?)。<br />')
                break
            elif '请购买' in html:
                break
            if cooling := D.findall(r'战斗剩余时间：(\d+)'):
                time.sleep(int(cooling[0]))

    if WEEK == '4':
        D.get('cmd=sharegame&subtype=3')
        for s in D.findall(r'sharenums=(\d+)'):
            # 领取
            D.get(f'cmd=sharegame&subtype=4&sharenums={s}')
            MSG.append(D.search(r'】</p>(.*?)<p>'))


def 乐斗():
    '''乐斗

        开启自动使用体力药水
        贡献药水使用4次
        每天乐斗好友BOSS、帮友BOSS以及侠侣所有
    '''
    # 乐斗助手
    D.get('cmd=view&type=6')
    if '开启自动使用体力药水' in html:
        #  开启自动使用体力药水
        D.get('cmd=set&type=0')

    for _ in range(4):
        # 使用贡献药水
        D.get('cmd=use&id=3038&store_type=1&page=1')
        D.search(r'<br />(.*?)<br />斗豆')

    # 好友BOSS
    D.get('cmd=friendlist&page=1')
    for u in D.findall(r'侠：.*?B_UID=(\d+)'):
        # 乐斗
        D.get(f'cmd=fight&B_UID={u}')
        D.search(r'删</a><br />(.*?)。')
        if '体力值不足' in html:
            break

    # 帮友BOSS
    D.get('cmd=viewmem&page=1')
    for u in D.findall(r'侠：.*?B_UID=(\d+)'):
        # 乐斗
        D.get(f'cmd=fight&B_UID={u}')
        D.search(r'侠侣</a><br />(.*?)<br />')
        if '体力值不足' in html:
            break

    # 侠侣
    D.get('cmd=viewxialv&page=1')
    try:
        for u in D.findall(r'：.*?B_UID=(\d+)')[1:]:
            # 乐斗
            D.get(f'cmd=fight&B_UID={u}')
            D.search(r'侠侣<br />(.*?)。')
            if '体力值不足' in html:
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
    D.get('cmd=fastSignWulin&ifFirstSign=1')
    if '使用规则' in html:
        MSG.append(D.search(r'】</p><p>(.*?)<br />'))
    else:
        MSG.append(D.search(r'升级。<br />(.*?) '))

    # 侠侣争霸
    if WEEK in ['2', '5', '0']:
        D.get('cmd=cfight&subtype=9')
        if '使用规则' in html:
            MSG.append(D.search(r'】</p><p>(.*?)<br />'))
        else:
            MSG.append(D.search(r'报名状态.*?<br />(.*?)<br />'))

    # 笑傲群侠
    if WEEK in ['6', '0']:
        D.get('cmd=knightfight&op=signup')
        MSG.append(D.search(r'侠士侠号.*?<br />(.*?)<br />'))


def 巅峰之战进行中():
    '''巅峰之战进行中

        周一报名（随机加入）、领奖
        周二夺宝奇兵（战功需大于200000）
        周三、四、五、六、日征战
    '''
    if WEEK == '1':
        for c in ['cmd=gvg&sub=4&group=0&check=1', 'cmd=gvg&sub=1']:
            D.get(c)
            MSG.append(D.search(r'】</p>(.*?)<br />'))
    elif WEEK == '2':
        for _ in range(300):
            # 投掷
            D.get('cmd=element&subtype=7')
            D.search(r'遥控骰子</a><br /><br />(.*?)。')
            if '当前操作非法' in html:
                # 太空探宝
                D.get('cmd=element&subtype=15&gameType=3')
                D.search(r'当前地图：(.*?)')
                if text_list := D.findall(r'拥有:(\d+)战功'):
                    if int(text_list[0]) < 200000:
                        MSG.append(f'战功：{text_list[0]} 大于200000才会探宝')
                        break
    else:
        # 巅峰之战
        D.get('cmd=gvg&sub=0')
        if '战线告急' in html:
            mode = r'支援！<br />(.*?)。'
        else:
            mode = r'】</p>(.*?)。'
        for _ in range(14):
            # 征战
            D.get('cmd=gvg&sub=5')
            if '您今天' in html:
                break
            elif '请您先报名再挑战' in html:
                MSG.append(D.search(r'】</p>(.*?)<br />'))
                break
            elif '撒花祝贺' in html:
                MSG.append(D.search(r'】</p>(.*?)<br />'))
                break
            MSG.append(D.search(mode))


def 矿洞():
    '''矿洞

        每天挑战3次
        副本开启第五层简单
        领取通关奖励
    '''
    for _ in range(5):
        # 矿洞
        D.get('cmd=factionmine')
        if '领取奖励' in html:
            # 领取奖励
            D.get('cmd=factionmine&op=reward')
            MSG.append(D.search(r'】<br /><br />(.*?)<br /><a'))
        elif '开启副本' in html:
            # floor   1、2、3、4、5 对应 第一、二、三、四、五层
            # mode    1、2、3 对应 简单、普通、困难
            # 确认开启
            D.get(f'cmd=factionmine&op=start&floor=5&mode=1')
            MSG.append(D.search(r'矿石商店</a><br />(.*?)<br />'))
        elif count := D.findall(r'剩余次数：(\d+)/3<br />'):
            if count[0] != '0':
                # 挑战
                D.get('cmd=factionmine&op=fight')
                MSG.append(D.search(r'商店</a><br />(.*?)<br />'))
        else:
            break


def 掠夺():
    '''掠夺

        周二掠夺一次（选择可掠夺粮仓最低战力）、领奖
        周三领取胜负奖励
    '''
    if WEEK == '2':
        D.get('cmd=forage_war')
        if '本轮轮空' in html:
            MSG.append(D.search(r'本届战况：(.*?)<br />'))
            return

        # 掠夺
        D.get('cmd=forage_war&subtype=3')
        if gra_id := D.findall(r'gra_id=(\d+)">掠夺'):
            data = []
            for id in gra_id:
                D.get(f'cmd=forage_war&subtype=3&op=1&gra_id={id}')
                if zhanli := D.findall(r'<br />1.*? (\d+)\.'):
                    data += [(int(zhanli[0]), id)]
            if data:
                _, id = min(data)
                D.get(f'cmd=forage_war&subtype=4&gra_id={id}')
                MSG.append(D.search(r'返回</a><br />(.*?)<br />'))

        # 领奖
        D.get('cmd=forage_war&subtype=5')
        MSG.append(D.search(r'返回</a><br />(.*?)<br />'))
    elif WEEK == '3':
        D.get('cmd=forage_war&subtype=6')
        MSG.append(D.search(r'规则</a><br />(.*?)<br />'))


def 踢馆():
    '''踢馆

        周五试炼5次、高倍转盘一次、挑战至多31次
        周六领奖以及报名踢馆
    '''
    if WEEK == '5':
        for t in [2, 2, 2, 2, 2, 4]:
            # 试炼、高倍转盘
            D.get(f'cmd=facchallenge&subtype={t}')
            D.search(r'功勋商店</a><br />(.*?)<br />')
            if '你们帮没有报名参加这次比赛' in html:
                MSG.append('你们帮没有报名参加这次比赛')
                return
        for _ in range(31):
            # 挑战
            D.get('cmd=facchallenge&subtype=3')
            D.search(r'功勋商店</a><br />(.*?)<br />')
            if '您的挑战次数已用光' in html:
                MSG.append('您的挑战次数已用光')
                break
            elif '您的复活次数已耗尽' in html:
                MSG.append('您的复活次数已耗尽')
                break
    elif WEEK == '6':
        for p in ['7', '1']:
            D.get(f'cmd=facchallenge&subtype={p}')
            MSG.append(D.search(r'功勋商店</a><br />(.*?)<br />'))


def 竞技场():
    '''竞技场

        每月1~25号每天至多挑战10次、领取奖励、默认兑换10个河洛图书
    '''
    for _ in range(10):
        # 免费挑战 or 开始挑战
        D.get('cmd=arena&op=challenge')
        D.search(r'更新提示</a><br />(.*?)。')
        if '免费挑战次数已用完' in html:
            # 领取奖励
            D.get('cmd=arena&op=drawdaily')
            MSG.append(D.search(r'更新提示</a><br />(.*?)<br />'))
            break

    if yaml := D.read_yaml('竞技场'):
        # 兑换10个
        D.get(f'cmd=arena&op=exchange&id={yaml}&times=10')
        MSG.append(D.search(r'竞技场</a><br />(.*?)<br />'))


def 十二宫():
    '''十二宫

        每天默认双鱼宫请猴王扫荡
    '''
    if yaml := D.read_yaml('十二宫'):
        # 请猴王扫荡
        D.get(f'cmd=zodiacdungeon&op=autofight&scene_id={yaml}')
        if msg := D.search(r'<br />(.*?)<br /><br /></p>'):
            # 要么 扫荡
            MSG.append(msg.split('<br />')[-1])
        else:
            # 要么 挑战次数不足 or 当前场景进度不足以使用自动挑战功能！
            MSG.append(D.search(r'id="id"><p>(.*?)<br />'))


def 许愿():
    '''许愿

        每天领取许愿奖励、上香许愿、领取魂珠碎片宝箱
    '''
    for sub in [5, 1, 6]:
        D.get(f'cmd=wish&sub={sub}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 抢地盘():
    '''抢地盘

        每天无限制区攻占一次第10位

        等级  30级以下 40级以下 ... 120级以下 无限制区
        type  1       2            10        11
    '''
    D.get('cmd=recommendmanor&type=11&page=1')
    if id := D.findall(r'manorid=(\d+)">攻占</a>'):
        # 攻占
        D.get(f'cmd=manorfight&fighttype=1&manorid={id[-1]}')
        MSG.append(D.search(r'】</p><p>(.*?)。'))
    # 兑换武器
    D.get('cmd=manor&sub=0')
    MSG.append(D.search(r'【抢地盘】<br /><br />(.*?)<br /><br />'))


def 历练():
    '''历练

        每天默认掉落佣兵碎片的每个关卡BOSS会被乐斗3次
    '''
    for id in D.read_yaml('历练'):
        for _ in range(3):
            D.get(f'cmd=mappush&subtype=3&mapid=6&npcid={id}&pageid=2')
            D.search(r'阅历值：\d+<br />(.*?)<br />')
            if '您还没有打到该历练场景' in html:
                D.search(r'介绍</a><br />(.*?)<br />')
                break
            elif '还不能挑战' in html:
                break
            elif '活力不足' in html:
                return


def 镖行天下():
    '''镖行天下

        每天拦截成功3次、领取奖励、刷新押镖并启程护送
    '''
    for op in [3, 16, 7, 8, 6]:
        # 护送完成 》领取奖励 》护送押镖 》刷新押镖 》启程护送
        D.get(f'cmd=cargo&op={op}')
        MSG.append(D.search(r'商店</a><br />(.*?)<br />'))

    for _ in range(5):
        # 刷新
        D.get('cmd=cargo&op=3')
        for uin in D.findall(r'passerby_uin=(\d+)">拦截'):
            # 拦截
            D.get(f'cmd=cargo&op=14&passerby_uin={uin}')
            if '系统繁忙' in html:
                continue
            elif '这个镖车在保护期内' in html:
                continue
            elif '您今天已达拦截次数上限了' in html:
                return
            MSG.append(D.search(r'商店</a><br />(.*?)<br />'))


def 幻境():
    '''幻境

        每天默认乐斗鹅王的试炼
    '''
    if yaml := D.read_yaml('幻境'):
        D.get(f'cmd=misty&op=start&stage_id={yaml}')
        for _ in range(5):
            # 乐斗
            D.get(f'cmd=misty&op=fight')
            MSG.append(D.search(r'星数.*?<br />(.*?)<br />'))
            if '尔等之才' in html:
                break
        # 返回飘渺幻境
        D.get('cmd=misty&op=return')


def 群雄逐鹿():
    '''群雄逐鹿

        每周六报名、领奖
    '''
    for op in ['signup', 'drawreward']:
        D.get(f'cmd=thronesbattle&op={op}')
        MSG.append(D.search(r'届群雄逐鹿<br />(.*?)<br />'))


def 画卷迷踪():
    '''画卷迷踪

        每天至多挑战20次
    '''
    for _ in range(20):
        # 准备完成进入战斗
        D.get('cmd=scroll_dungeon&op=fight&buff=0')
        MSG.append(D.search(r'选择</a><br /><br />(.*?)<br />'))
        if '没有挑战次数' in html:
            break
        elif '征战书不足' in html:
            break


def 门派():
    '''门派

        万年寺：点燃 》点燃
        八叶堂：进入木桩训练 》进入同门切磋
        五花堂：至多完成任务3次
    '''
    # 点燃 》点燃
    for op in ['fumigatefreeincense', 'fumigatepaidincense']:
        D.get(f'cmd=sect&op={op}')
        MSG.append(D.search(r'修行。<br />(.*?)<br />'))

    # 进入木桩训练 》进入同门切磋
    for op in ['trainingwithnpc', 'trainingwithmember']:
        D.get(f'cmd=sect&op={op}')
        MSG.append(D.search(r'【八叶堂】<br />(.*?)<br />'))

    # 五花堂
    D.get('cmd=sect_task')
    wuhuatang = html
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
            D.get(url)
            D.search(r'【金顶】<br />(.*?)<br />')
    if '查看一名' in wuhuatang:
        # 查看一名同门成员的资料 or 查看一名其他门派成员的资料
        for page in [2, 3]:
            # 好友第2、3页
            D.get(f'cmd=friendlist&page={page}')
            for uin in D.findall(r'\d+：.*?B_UID=(\d+).*?级'):
                # 查看好友
                D.get(f'cmd=totalinfo&B_UID={uin}')
    if '进行一次心法修炼' in wuhuatang:
        '''
        少林心法      峨眉心法    华山心法      丐帮心法    武当心法      明教心法
        101 法华经    104 斩情决  107 御剑术   110 醉拳    113 太极内力  116 圣火功
        102 金刚经    105 护心决  108 龟息术   111 烟雨行  114 绕指柔剑  117 五行阵
        103 达摩心经  106 观音咒  109 养心术   112 笑尘诀  115 金丹秘诀  118 日月凌天
        '''
        for id in range(101, 119):
            D.get(f'cmd=sect_art&subtype=2&art_id={id}&times=1')
            if '修炼成功' in html:
                D.search(r'】<br />(.*?)<br />')
                break
            elif '修炼失败' in html:
                if '你的门派贡献不足无法修炼' in html:
                    break
                elif ('你的心法已达顶级无需修炼' in html) and (id == 118):
                    MSG.append('所有心法都已经顶级')
    # 五花堂
    D.get('cmd=sect_task')
    for id in D.findall(r'task_id=(\d+)">完成'):
        # 完成
        D.get(f'cmd=sect_task&subtype=2&task_id={id}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 门派邀请赛():
    '''门派邀请赛


        每周一报名、领取奖励
        每周三、四、五、六、日挑战6次以及默认兑换10个炼气石
    '''
    if WEEK == '1':
        # 组队报名
        D.get('cmd=secttournament&op=signup')
        MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
        # 领取奖励
        D.get('cmd=secttournament&op=getrankandrankingreward')
        MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
    elif WEEK not in ['1', '2']:
        for _ in range(6):
            # 开始挑战
            D.get('cmd=secttournament&op=fight')
            MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
        if yaml := D.read_yaml('门派邀请赛'):
            # 兑换10个
            D.get(f'cmd=exchange&subtype=2&type={yaml}&times=10&costtype=11')
            MSG.append(D.search(r'】<br />(.*?)<br />'))


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
            D.get('cmd=sectmelee&op=dotraining')
            # MSG.append(D.search(r'最高伤害：\d+<br />(.*?)<br />'))
            if '你已达今日挑战上限' in html:
                MSG.append('试炼场挑战已达今日挑战上限')
                break
            elif '你的试炼书不足' in html:
                # 兑换 试炼书*10
                D.get('cmd=exchange&subtype=2&type=1265&times=10&costtype=13')
                if '会武积分不足' in html:
                    # 抱歉，您的会武积分不足，不能兑换该物品！
                    MSG.append('会武积分不足兑换试炼书*10')
                    break
    elif WEEK == '4':
        # 冠军助威 丐帮
        D.get('cmd=sectmelee&op=cheer&sect=1003')
        # 冠军助威
        D.get('cmd=sectmelee&op=showcheer')
        MSG.append(D.search(r'【冠军助威】<br />(.*?)<br />'))
    elif WEEK == '6':
        # 领奖
        D.get('cmd=sectmelee&op=drawreward')
        MSG.append(D.search(r'【领奖】<br />(.*?)<br />'))
        # 兑换 真黄金卷轴*10
        D.get('cmd=exchange&subtype=2&type=1263&times=10&costtype=13')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 梦想之旅():
    '''梦想之旅

        每天普通旅行一次
        周四梦幻旅行（如果下一个区域存在 '已去过'）、领取区域、超级礼包
    '''
    # 普通旅行
    D.get('cmd=dreamtrip&sub=2')
    MSG.append(D.search(r'规则</a><br />(.*?)<br />'))

    if WEEK == '4':
        bmapid = {
            '空桑山': 2,
            '鹊山': 3,
            '鹿蜀': 4,
            '昆仑之丘': 1
        }
        # 梦想之旅
        D.get('cmd=dreamtrip')
        for k, v in bmapid.items():
            if k in html:
                # 下一个区域
                D.get(f'cmd=dreamtrip&sub=0&bmapid={v}')
                if '已去过' in html:
                    # 梦想之旅
                    D.get('cmd=dreamtrip')
                    if smapid := D.findall(r'梦幻旅行</a><br />(.*?)<br /><br />'):
                        # 查找未去过的目的地
                        id_list = []
                        list = smapid[0].split('<br />')
                        for i, v in enumerate(list):
                            if '未去过' in v:
                                id_list.append(i + 1)
                        # 消耗梦幻机票去目的地
                        for id in id_list:
                            # 去这里
                            D.get(f'cmd=dreamtrip&sub=2&smapid={id}')
                            MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
                            if '当前没有梦幻机票' in html:
                                break
        # 梦想之旅
        D.get('cmd=dreamtrip')
        for _ in range(2):
            if bmapid := D.findall(r'sub=4&amp;bmapid=(\d+)'):
                # 礼包     1 or 2 or 3 or 4
                # 超级礼包 0
                D.get(f'cmd=dreamtrip&sub=4&bmapid={bmapid[0]}')
                MSG.append(D.search(r'规则</a><br />(.*?)<br />'))


def 问鼎天下():
    '''问鼎天下

        周一领取奖励
        周一、二、三、四、五领取帮资或放弃资源点、东海攻占倒数第一个至多两次
        周六淘汰赛助威 神ㄨ阁丶
        周日排名赛助威 神ㄨ阁丶
    '''
    if WEEK == '1':
        # 领取奖励
        D.get('cmd=tbattle&op=drawreward')
        MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
    if WEEK not in ['6', '0']:
        # 问鼎天下
        D.get('cmd=tbattle')
        if '你占领的领地已经枯竭' in html:
            # 领取
            D.get('cmd=tbattle&op=drawreleasereward')
            MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
        elif '放弃' in html:
            # 放弃
            D.get('cmd=tbattle&op=abandon')
            MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
        for _ in range(2):
            # 1东海 2南荒   3西泽   4北寒
            D.get(f'cmd=tbattle&op=showregion&region=1')
            # 攻占 倒数第一个
            if id := D.findall(r'id=(\d+).*?攻占</a>'):
                D.get(f'cmd=tbattle&op=occupy&id={id[-1]}&region=1')
                MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
                if '大获全胜' in html:
                    break
    elif WEEK == '6':
        # 淘汰赛助威 神ㄨ阁丶
        D.get(f'cmd=tbattle&op=cheerregionbattle&id=10215')
        MSG.append(D.search(r'规则</a><br />(.*?)<br />'))
    elif WEEK == '0':
        # 排名赛助威 神ㄨ阁丶
        D.get(f'cmd=tbattle&op=cheerchampionbattle&id=10215')
        MSG.append(D.search(r'规则</a><br />(.*?)<br />'))


def 帮派商会():
    '''帮派商会

        每天帮派宝库领取礼包、交易会所交易物品、兑换商店兑换物品
    '''
    # 帮派宝库
    D.get('cmd=fac_corp&op=0')
    for id, t in D.findall(r'gift_id=(\d+)&amp;type=(\d+)">点击领取'):
        D.get(f'cmd=fac_corp&op=3&gift_id={id}&type={t}')
        MSG.append(D.search(r'】</p>(.*?)<br />'))

    # 交易会所
    D.get('cmd=fac_corp&op=1')
    data: dict = D.read_yaml('帮派商会')
    jiaoyi: dict = data['交易会所']
    for jiaoyi_name, params in jiaoyi.items():
        if jiaoyi_name in html:
            D.get(f'cmd=fac_corp&op=4&{params}')
            MSG.append(D.search(r'】</p>(.*?)<br />'))

    # 兑换商店
    D.get('cmd=fac_corp&op=2')
    data: dict = D.read_yaml('帮派商会')
    duihuan: dict = data['兑换商店']
    for duihuan_name, type_id in duihuan.items():
        if duihuan_name in html:
            D.get(f'cmd=fac_corp&op=5&type_id={type_id}')
            MSG.append(D.search(r'】</p>(.*?)<br />'))


def 帮派远征军():
    '''帮派远征军

        周一、二、三、四、五、六参战攻击
        周日领取奖励
    '''
    while WEEK != '0':
        # 帮派远征军
        D.get('cmd=factionarmy&op=viewIndex&island_id=-1')
        point_id = D.findall(r'point_id=(\d+)">参战')
        if not point_id:
            MSG.append('已经全部通关了，周日领取奖励')
            break
        for p in point_id:
            # 参战
            D.get(f'cmd=factionarmy&op=viewpoint&point_id={p}')
            for uin in D.findall(r'opp_uin=(\d+)">攻击'):
                # 攻击
                D.get(
                    f'cmd=factionarmy&op=fightWithUsr&point_id={p}&opp_uin={uin}')
                if '参数错误' in html:
                    continue
                elif '您的血量不足' in html:
                    MSG.append('您的血量不足，请重生后在进行战斗')
                    return
    if WEEK == '0':
        # 领取奖励
        for id in range(15):
            D.get(f'cmd=factionarmy&op=getPointAward&point_id={id}')
            MSG.append(D.search(r'领取奖励】<br />(.*?)<br />'))
        # 领取岛屿宝箱
        for id in range(5):
            D.get(f'cmd=factionarmy&op=getIslandAward&island_id={id}')
            MSG.append(D.search(r'领取奖励】<br />(.*?)<br />'))


def 帮派黄金联赛():
    '''帮派黄金联赛

        领取奖励、领取帮派赛季奖励、参与防守、参战攻击
    '''
    # 帮派黄金联赛
    D.get('cmd=factionleague&op=0')
    if '领取奖励' in html:
        # 领取轮次奖励
        D.get('cmd=factionleague&op=5')
        MSG.append(D.search(r'<p>(.*?)<br /><br />'))
    elif '领取帮派赛季奖励' in html:
        # 领取帮派赛季奖励
        D.get('cmd=factionleague&op=7')
        MSG.append(D.search(r'<p>(.*?)<br /><br />'))
    elif '参与防守' in html:
        # 参与防守
        D.get('cmd=factionleague&op=1')
        MSG.append(D.search(r'<p>(.*?)<br /><br />'))

    if '参战</a>' in html:
        uin = []
        # 参战
        D.get('cmd=factionleague&op=2')
        if pages := D.findall(r'pages=(\d+)">末页'):
            for p in range(1, int(pages[0]) + 1):
                D.get(f'cmd=factionleague&op=2&pages={p}')
                uin += D.findall(r'%&nbsp;&nbsp;(\d+).*?opp_uin=(\d+)')
            # 按战力排序
            uin.sort()
        else:
            MSG.append('没有可攻击的敌人')

        for _, uin in uin:
            # 攻击
            D.get(f'cmd=factionleague&op=4&opp_uin={uin}')
            if '不幸战败' in html:
                MSG.append(D.search(r'】<br />(.*?)<br />'))
                break
            elif '您已阵亡' in html:
                MSG.append(D.search(r'】<br /><br />(.*?)</p>'))
                break
            D.search(r'】<br />(.*?)<br />')


def 任务派遣中心():
    '''任务派遣中心

        每天领取奖励、接受任务
    '''
    # 任务派遣中心
    D.get('cmd=missionassign&subtype=0')
    for id in D.findall(r'0时0分.*?mission_id=(.*?)">查看'):
        # 领取奖励
        D.get(f'cmd=missionassign&subtype=5&mission_id={id}')
        MSG.append(D.search(r'\[任务派遣中心\](.*?)<br />'))

    # 任务派遣中心
    D.get('cmd=missionassign&subtype=0')
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
    for _ in range(3):
        mission_id = D.findall(r'小时.*?mission_id=(.*?)">接受')
        for _, id in missions_dict.items():
            if id in mission_id:
                # 快速委派
                D.get(f'cmd=missionassign&subtype=7&mission_id={id}')
                # 开始任务
                D.get(f'cmd=missionassign&subtype=8&mission_id={id}')
                if '任务数已达上限' in html:
                    break
        # 任务派遣中心
        D.get('cmd=missionassign&subtype=0')
        if '今日已领取了全部任务哦' in html:
            break
        elif html.count('查看') == 3:
            break
        elif '50斗豆' not in html:
            # 刷新任务
            D.get('cmd=missionassign&subtype=3')


def 武林盟主():
    '''武林盟主

        周三、五、日领取排行奖励和竞猜奖励
        周一、三、五分站赛默认报名黄金，总决赛不需报名
        周二、四、六竞猜
    '''
    if WEEK in ['3', '5', '0']:
        # 武林盟主
        D.get('cmd=wlmz&op=view_index')
        if data := D.findall(r'section_id=(\d+)&amp;round_id=(\d+)">'):
            for s, r in data:
                D.get(f'cmd=wlmz&op=get_award&section_id={s}&round_id={r}')
                MSG.append(D.search(r'【武林盟主】<br /><br />(.*?)</p>'))
        else:
            MSG.append('没有可领取的排行奖励和竞猜奖励')

    if WEEK in ['1', '3', '5']:
        if yaml := D.read_yaml('武林盟主'):
            D.get(f'cmd=wlmz&op=signup&ground_id={yaml}')
            if '总决赛周不允许报名' in html:
                MSG.append(D.search(r'战报</a><br />(.*?)<br />'))
                return
            MSG.append(D.search(r'赛场】<br />(.*?)<br />'))
    elif WEEK in ['2', '4', '6']:
        for index in range(8):
            # 选择
            D.get(f'cmd=wlmz&op=guess_up&index={index}')
            D.search(r'规则</a><br />(.*?)<br />')
        # 确定竞猜选择
        D.get('cmd=wlmz&op=comfirm')
        MSG.append(D.search(r'战报</a><br />(.*?)<br />'))


def 全民乱斗():
    '''全民乱斗

        乱斗竞技、乱斗任务领取
    '''
    n = True
    for t in [2, 3, 4]:
        D.get(f'cmd=luandou&op=0&acttype={t}')
        for id in D.findall(r'.*?id=(\d+)">领取</a>'):
            n = False
            # 领取
            D.get(f'cmd=luandou&op=8&id={id}')
            MSG.append(D.search(r'斗】<br /><br />(.*?)<br />'))
    if n:
        MSG.append('没有可领取的')


def 侠士客栈():
    '''侠士客栈

        每天领取奖励3次、客栈奇遇
    '''
    # 侠士客栈
    D.get('cmd=warriorinn')
    if type := D.findall(r'type=(\d+).*?领取奖励</a>'):
        for n in range(1, 4):
            # 领取奖励
            D.get(f'cmd=warriorinn&op=getlobbyreward&type={type[0]}&num={n}')
            MSG.append(D.search(r'侠士客栈<br />(.*?)<br />'))

    # 侠士客栈
    D.get('cmd=warriorinn')
    # 黑市商人 -> 你去别人家问问吧 -> 确定
    for rejectadventure in ['黑市商人', '老乞丐']:
        if rejectadventure in html:
            for pos in range(2):
                D.get(f'cmd=warriorinn&op=rejectadventure&pos={pos}')
                MSG.append(D.search(r'侠士客栈<br />(.*?)，<a'))
    # 前来捣乱的柒承 -> 与TA理论 -> 确定
    for exceptadventure in ['前来捣乱的柒承', '前来捣乱的洪七公', '前来捣乱的欧阳锋', '前来捣乱的燕青', '前来捣乱的圣诞老鹅', '前来捣乱的断亦']:
        if exceptadventure in html:
            for pos in range(2):
                D.get(f'cmd=warriorinn&op=exceptadventure&pos={pos}')
                MSG.append(D.search(r'侠士客栈<br />(.*?)，<a'))


def 江湖长梦():
    '''江湖长梦

        每天开启柒承的忙碌日常副本
        周四兑换玄铁令*7
    '''
    if WEEK == '4':
        # 【江湖长梦】兑换 玄铁令*10
        for _ in range(7):
            # 兑换 玄铁令*1
            D.get('cmd=longdreamexchange&op=exchange&key_id=5&page=1')
            # 兑换成功
            MSG.append(D.search(r'侠士碎片</a><br />(.*?)<br />'))
            if '该物品兑换次数已达上限' in html:
                MSG.append('玄铁令兑换次数已达上限')
                break
            elif '剩余积分或兑换材料不足' in html:
                MSG.append('商店剩余积分或兑换材料不足')
                break

    # 柒承的忙碌日常
    D.get('cmd=jianghudream&op=showCopyInfo&id=1')
    # 开启副本
    D.get('cmd=jianghudream&op=beginInstance&ins_id=1')
    if '开启副本所需追忆香炉不足' in html:
        MSG.append(D.search(r'【江湖长梦】<br />(.*?)<br /><a'))
        return
    # 进入下一天
    D.get('cmd=jianghudream&op=goNextDay')
    if '进入下一天异常' in html:
        # 开启副本
        D.get('cmd=jianghudream&op=beginInstance&ins_id=1')
    for _ in range(7):
        msg1 = D.findall(r'event_id=(\d+)">战斗\(等级1\)')
        msg2 = D.findall(r'event_id=(\d+)">奇遇\(等级1\)')
        msg3 = D.findall(r'event_id=(\d+)">商店\(等级1\)')
        if msg1:  # 战斗
            D.get(f'cmd=jianghudream&op=chooseEvent&event_id={msg1[0]}')
            # FIGHT!
            D.get('cmd=jianghudream&op=doPveFight')
            if '战败' in html:
                break
        elif msg2:  # 奇遇
            D.get(f'cmd=jianghudream&op=chooseEvent&event_id={msg2[0]}')
            # 视而不见
            D.get('cmd=jianghudream&op=chooseAdventure&adventure_id=2')
        elif msg3:  # 商店
            D.get(f'cmd=jianghudream&op=chooseEvent&event_id={msg3[0]}')
        # 进入下一天
        D.get('cmd=jianghudream&op=goNextDay')

    # 结束回忆
    D.get('cmd=jianghudream&op=endInstance')
    MSG.append(D.search(r'【江湖长梦】<br />(.*?)<br /><a'))


def 增强经脉():
    '''增强经脉

        每天至多传功12次
    '''
    # 经脉
    D.get('cmd=intfmerid&sub=1')
    for _ in range(12):
        for id in D.findall(r'master_id=(\d+)">传功</a>'):
            if '关闭' in html:
                # 关闭合成两次确认
                D.get('cmd=intfmerid&sub=19')
            # 一键合成
            D.get('cmd=intfmerid&sub=10&op=4')
            # 一键拾取
            D.get('cmd=intfmerid&sub=5')
            # 传功
            D.get(f'cmd=intfmerid&sub=2&master_id={id}')


def 助阵():
    '''
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
    for id, dex_list in tianshu.items():
        for dex in dex_list:
            D.get(
                f'cmd=formation&type=4&formationid={id}&attrindex={dex}&times=1')
            if n == 2:
                return
            elif '提升成功' in html:
                n += 1
                continue
            elif '经验值已经达到最大' in html:
                continue
            elif '阅历不足' in html:
                return
            elif '你还没有激活该属性' in html:
                # 要么 没有激活该属性
                # 要么 没有该属性
                break


def 查看好友资料():
    '''查看好友第二页'''
    # 武林 》设置 》乐斗助手
    D.get('cmd=view&type=6')
    if '开启查看好友信息和收徒' in html:
        #  开启查看好友信息和收徒
        D.get('cmd=set&type=1')
    # 查看好友第2页
    D.get(f'cmd=friendlist&page=2')
    for uin in D.findall(r'\d+：.*?B_UID=(\d+).*?级'):
        D.get(f'cmd=totalinfo&B_UID={uin}')


def 徽章进阶():
    '''
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
        D.get(f'cmd=achievement&op=upgradelevel&achievement_id={id}&times=1')
        if '进阶失败' in html:
            break
        elif '进阶成功' in html:
            break
        elif '物品不足' in html:
            break


def 兵法研习():
    '''
    兵法      消耗     id       功能
    金兰之泽  孙子兵法  2544     增加生命
    雷霆一击  孙子兵法  2570     增加伤害
    残暴攻势  武穆遗书  21001    增加暴击几率
    不屈意志  武穆遗书  21032    降低受到暴击几率
    '''
    for id in [21001, 2570, 21032, 2544]:
        D.get(f'cmd=brofight&subtype=12&op=practice&baseid={id}')
        if '研习成功' in html:
            break


def 挑战陌生人():
    '''斗友乐斗四次'''
    # 斗友
    D.get('cmd=friendlist&type=1')
    B_UID = D.findall(r'：.*?级.*?B_UID=(\d+).*?乐斗</a>')
    for uin in B_UID[:4]:
        # 乐斗
        D.get(f'cmd=fight&B_UID={uin}&page=1&type=9')


def 强化神装():
    # 任务
    D.get('cmd=task&sub=1')
    missions = html
    if 'id=116' in missions:
        for id in range(6):
            # 神兵  0
            # 神铠  1
            # 神羽  2
            # 神兽  3
            # 神饰  4
            # 神履  5
            D.get(f'cmd=outfit&op=1&magic_outfit_id={id}')
            D.search(r'\|<br />(.*?)<br />')
            if '进阶失败' in html:
                break
            elif '成功' in html:
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
            D.get(f'cmd=outfit&op=3&magic_skill_id={id}')
            D.search(r'</a><br />(.*?)<br />')
            if '升级失败' in html:
                break


def 武器专精():
    '''
    投掷武器专精  0
    小型武器专精  1
    中型武器专精  2
    大型武器专精  3

    武器栏      投掷武器专精  小型武器专精  中型武器专精  大型武器专精
    专精·控制   1000         1003         1006         1009
    专精·吸血   1001         1004         1007         1010
    专精·凝神   1002         1005         1008         1011
    '''
    # 任务
    D.get('cmd=task&sub=1')
    missions = html
    if 'id=114' in missions:
        # 武器专精
        for tid in range(4):
            D.get(f'cmd=weapon_specialize&op=2&type_id={tid}')
            if '失败' in html:
                break
            elif '成功' in html:
                break
    if 'id=115' in missions:
        # 武器栏
        for sid in range(1000, 1012):
            D.get(f'cmd=weapon_specialize&op=5&storage_id={sid}')
            if '失败' in html:
                break
            elif '成功' in html:
                break


def 强化铭刻():
    '''
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
        D.get(
            f'cmd=inscription&subtype=5&type_id={id}&weapon_idx={idx}&attr_id={id}')
        if '升级所需材料不足' in html:
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
    D.get('cmd=task&sub=1')
    daily_missions = html
    if '查看好友资料' in daily_missions:
        查看好友资料()
    if '徽章进阶' in daily_missions:
        徽章进阶()
    if '兵法研习' in daily_missions:
        兵法研习()
    if '挑战陌生人' in daily_missions:
        挑战陌生人()
    if '强化神装' in daily_missions:
        强化神装()
    if '武器专精' in daily_missions:
        武器专精()
    if '强化铭刻' in daily_missions:
        强化铭刻()

    # 一键完成任务
    D.get('cmd=task&sub=7')
    for k, v in D.findall(r'id=\d+">(.*?)</a>.*?>(.*?)</a>'):
        MSG.append(f'{k} {v}')


def 我的帮派():
    '''我的帮派

        每天供奉5次、帮派任务至多领取奖励3次
        周日领取奖励、报名帮派战争、激活祝福
    '''
    # 我的帮派
    D.get('cmd=factionop&subtype=3&facid=0')
    if '你的职位' not in html:
        MSG.append('您还没有加入帮派')
        return

    # 周日 领取奖励 》报名帮派战争 》激活祝福
    if WEEK == '0':
        for sub in [4, 9, 6]:
            D.get(f'cmd=facwar&sub={sub}')
            MSG.append(D.search(r'</p>(.*?)<br /><a.*?查看上届'))

    for id in D.read_yaml('我的帮派'):
        # 供奉
        D.get(f'cmd=oblation&id={id}&page=1')
        MSG.append(D.search(r'【供奉守护神】<br />(.*?)<br />'))
        if '每天最多供奉5次' in html:
            break
        elif '很抱歉' in html:
            continue

    # 帮派任务
    D.get('cmd=factiontask&sub=1')
    faction_missions = html
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
            D.get(url)
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
                D.get(f'cmd=factiontrain&type=2&id={id}&num=1&i_p_w=num%7C')
                if '你需要提升帮派等级来让你进行下一步的修炼' in html:
                    if id == 2429:
                        MSG.append('所有武功秘籍已满级')
                    break
                elif '技能经验增加' in html:
                    # 技能经验增加20！
                    n += 1
            if n == 4:
                break
    # 帮派任务
    D.get('cmd=factiontask&sub=1')
    for id in D.findall(r'id=(\d+)">领取奖励</a>'):
        # 领取奖励
        D.get(f'cmd=factiontask&sub=3&id={id}')
        MSG.append(D.search(r'日常任务</a><br />(.*?)<br />'))


def 帮派祭坛():
    '''帮派祭坛

        每天转动轮盘至多30次
        领取通关奖励
    '''
    # 帮派祭坛
    D.get('cmd=altar')
    for _ in range(30):
        if '转转券不足' in html:
            break
        elif '转动轮盘' in html:
            D.get('cmd=altar&op=spinwheel')
            MSG.append(D.search(r'兑换</a><br />(.*?)<br />'))
        elif '随机分配' in html:
            for op, id in D.findall(r'op=(.*?)&amp;id=(\d+)">选择</a>'):
                # 偷取|选择帮派
                D.get(f'cmd=altar&op={op}&id={id}')
                if '选择路线' in html:
                    # 选择路线 向前、向左、向右
                    D.get(f'cmd=altar&op=dosteal&id={id}')
                    if '该帮派已解散' in html:
                        continue
                break
        elif '领取奖励' in html:
            D.get('cmd=altar&op=drawreward')
            if '当前没有累积奖励可以领取' in html:
                MSG.append(D.search(r'<br /><br />(.*?)</p>'))
            else:
                MSG.append(D.search(r'兑换</a><br />(.*?)<br />'))


def 飞升大作战():
    '''飞升大作战

        每天优先报名单排模式，玄铁令不足或者休赛期时选择匹配模式
        周四领取赛季结束奖励
    '''
    # 境界修为
    D.get('cmd=ascendheaven&op=showrealm')
    MSG.append(D.search(r'】<br />(.*?)<br />'))

    for _ in range(2):
        # 报名单排模式
        D.get('cmd=ascendheaven&op=signup&type=1')
        MSG.append(D.search(r'】<br />(.*?)<br />S'))
        if '时势造英雄' in html:
            break
        elif '还没有入场券玄铁令' in html:
            # 兑换 玄铁令*1
            D.get('cmd=ascendheaven&op=exchange&id=2&times=1')
            MSG.append(D.search(r'】<br />(.*?)<br />'))
            if '不足' not in html:
                # 本赛季该道具库存不足
                # 积分不足，快去参加飞升大作战吧~
                continue
        elif '不在报名时间' in html:
            break
        # 当前为休赛期，报名匹配模式
        D.get('cmd=ascendheaven&op=signup&type=2')
        MSG.append(D.search(r'】<br />(.*?)<br />S'))
        break
    if WEEK == '4':
        # 飞升大作战
        D.get('cmd=ascendheaven')
        if ('赛季结算中' in html):
            # 境界修为
            D.get('cmd=ascendheaven&op=showrealm')
            for s in D.findall(r'season=(\d+)'):
                # 领取奖励
                D.get(f'cmd=ascendheaven&op=getrealmgift&season={s}')
                MSG.append(D.search(r'】<br />(.*?)<br />'))


def 深渊之潮():
    '''深渊之潮

        每天帮派巡礼领取巡游赠礼、深渊秘境默认曲镜空洞
    '''
    # 帮派巡礼 》领取巡游赠礼
    D.get('cmd=abysstide&op=getfactiongift')
    MSG.append(D.search(r'】<br />(.*?)<br />'))
    if '您暂未加入帮派' in html:
        MSG.append('帮派巡礼需要加入帮派才能领取')
    if yaml := D.read_yaml('深渊之潮'):
        for _ in range(3):
            D.get(f'cmd=abysstide&op=enterabyss&id={yaml}')
            if '暂无可用挑战次数' in html:
                break
            elif '该副本需要顺序通关解锁' in html:
                MSG.append('该副本需要顺序通关解锁！')
                break
            for _ in range(5):
                # 开始挑战
                D.get('cmd=abysstide&op=beginfight')
            # 退出副本
            D.get('cmd=abysstide&op=endabyss')
            MSG.append(D.search(r'】<br />(.*?)<br />'))


def 每日奖励():
    '''每日奖励

        每天领取4次
    '''
    for key in ['login', 'meridian', 'daren', 'wuzitianshu']:
        # 每日奖励
        D.get(f'cmd=dailygift&op=draw&key={key}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 今日活跃度():
    '''今日活跃度

        每天活跃度礼包、帮派总活跃礼包
    '''
    # 今日活跃度
    D.get('cmd=liveness')
    MSG.append(D.search(r'【(.*?)】'))
    if 'factionop' in html:
        MSG.append(D.search(r'礼包</a><br />(.*?)<a'))
    else:
        MSG.append(D.search(r'礼包</a><br />(.*?)<br />'))
    # 领取今日活跃度礼包
    for id in range(1, 5):
        D.get(f'cmd=liveness_getgiftbag&giftbagid={id}&action=1')
        MSG.append(D.search(r'】<br />(.*?)<p>1.'))
    # 领取帮派总活跃奖励
    D.get('cmd=factionop&subtype=18')
    MSG.append(D.search(r'<br />(.*?)</p><p>你的职位:'))


def 仙武修真():
    '''仙武修真

        每天领取3次任务、寻访长留山挑战至多5次
    '''
    for id in range(1, 4):
        # 领取
        D.get(f'cmd=immortals&op=getreward&taskid={id}')
        MSG.append(D.search(r'帮助</a><br />(.*?)<br />'))
    for _ in range(5):
        # 寻访 长留山
        D.get('cmd=immortals&op=visitimmortals&mountainId=1')
        if '你的今日寻访挑战次数已用光' in html:
            MSG.append(D.search(r'帮助</a><br />(.*?)<br />'))
            break
        # 挑战
        D.get('cmd=immortals&op=fightimmortals')
        MSG.append(D.search(r'帮助</a><br />(.*?)<a'))


def 大侠回归三重好礼():
    '''大侠回归三重好礼

        周四领取奖励
    '''
    # 大侠回归三重好礼
    D.get('cmd=newAct&subtype=173&op=1')
    if data := D.findall(r'subtype=(\d+).*?taskid=(\d+)'):
        for s, t in data:
            # 领取
            D.get(f'cmd=newAct&subtype={s}&op=2&taskid={t}')
            MSG.append(D.search(r'】<br /><br />(.*?)<br />'))
    else:
        MSG.append('没有可领取的奖励')


def 乐斗黄历():
    '''乐斗黄历

        每天占卜一次
    '''
    # 乐斗黄历
    D.get('cmd=calender&op=0')
    MSG.append(D.search(r'今日任务：(.*?)<br />'))
    # 领取
    D.get('cmd=calender&op=2')
    MSG.append(D.search(r'】<br /><br />(.*?)<br />'))
    if '任务未完成' in html:
        return
    # 占卜
    D.get('cmd=calender&op=4')
    MSG.append(D.search(r'】<br /><br />(.*?)<br />'))


def 器魂附魔():
    '''器魂附魔

        每天领取日活跃度达到50、80、110礼包
    '''
    # 器魂附魔
    D.get('cmd=enchant')
    for id in range(1, 4):
        # 领取
        D.get(f'cmd=enchant&op=gettaskreward&task_id={id}')
        MSG.append(D.search(r'器魂附魔<br />(.*?)<br />'))


def 镶嵌():
    '''镶嵌

        周四镶嵌魂珠升级（碎 -> 1 -> 2 -> 3）
    '''
    data = [
        zip('6666666', range(2000, 2007)),      # 魂珠碎片
        zip('3333333', range(4001, 4062, 10)),  # 魂珠1级
        zip('3333333', range(4002, 4063, 10)),  # 魂珠2级
    ]
    for iter in data:
        for k, v in iter:
            for _ in range(50):
                if k == '6':
                    # 魂珠碎片 -> 1
                    D.get(
                        f'cmd=upgradepearl&type={k}&exchangetype={v}')
                else:
                    # 1 -> 2 -> 3
                    D.get(f'cmd=upgradepearl&type={k}&pearl_id={v}')
                if '抱歉' in html:
                    D.search(r'魂珠升级</p><>(.*?)。')
                    break
                D.search(r'魂珠升级</p><p>(.*?)</p>')


def 兵法():
    '''兵法

        周四随机助威
        周六领奖、领取斗币
    '''
    if WEEK == '4':
        # 助威
        D.get('cmd=brofight&subtype=13')
        if teamid := D.findall(r'.*?teamid=(\d+).*?助威</a>'):
            t = random.choice(teamid)
            # 确定
            D.get(f'cmd=brofight&subtype=13&teamid={t}&type=5&op=cheer')
            MSG.append(D.search(r'领奖</a><br />(.*?)<br />'))
    elif WEEK == '6':
        # 兵法 -> 助威 -> 领奖
        D.get('cmd=brofight&subtype=13&op=draw')
        MSG.append(D.search(r'领奖</a><br />(.*?)<br />'))

        for t in range(1, 6):
            D.get(f'cmd=brofight&subtype=10&type={t}')
            for number, uin in D.findall(r'50000&nbsp;&nbsp;(\d+).*?champion_uin=(\d+)'):
                if number == '0':
                    continue
                # 领取斗币
                D.get(
                    f'cmd=brofight&subtype=10&op=draw&champion_uin={uin}&type={t}')
                MSG.append(D.search(r'排行</a><br />(.*?)<br />'))
                return


def 神匠坊():
    '''神匠坊

        周四普通合成、符石打造、符石分解（仅I类）
    '''
    data = []
    for p in range(1, 20):
        # 下一页
        D.get(f'cmd=weapongod&sub=12&stone_type=0&quality=0&page={p}')
        data += D.findall(r'拥有：(\d+)/(\d+).*?stone_id=(\d+)')
        if '下一页' not in html:
            break
    for remaining, amount, id in data:
        if int(remaining) >= int(amount):
            count = int(int(remaining) / int(amount))
            for _ in range(count):
                # 普通合成
                D.get(f'cmd=weapongod&sub=13&stone_id={id}')
                D.search(r'背包<br /></p>(.*?)!')

    # 符石分解
    if yaml := D.read_yaml('神匠坊'):
        data = []
        for p in range(1, 10):
            # 下一页
            D.get(f'cmd=weapongod&sub=9&stone_type=0&page={p}')
            data += D.findall(r'数量:(\d+).*?stone_id=(\d+)')
            if '下一页' not in html:
                break
        for num, id in data:
            if int(id) in yaml:
                # 分解
                D.get(
                    f'cmd=weapongod&sub=11&stone_id={id}&num={num}&i_p_w=num%7C')
                D.search(r'背包</a><br /></p>(.*?)<')

    # 符石打造
    # 符石
    D.get('cmd=weapongod&sub=7')
    if data := D.findall(r'符石水晶：(\d+)'):
        amount = int(data[0])
        ten = int(amount / 60)
        one = int((amount - (ten * 60)) / 6)
        for _ in range(ten):
            # 打造十次
            D.get('cmd=weapongod&sub=8&produce_type=1&times=10')
            D.search(r'背包</a><br /></p>(.*?)<')
        for _ in range(one):
            # 打造一次
            D.get('cmd=weapongod&sub=8&produce_type=1&times=1')
            D.search(r'背包</a><br /></p>(.*?)<')


def 背包():
    '''背包

        每天消耗掉锦囊、属性（xx洗刷刷除外）物品
        周四消耗掉所有带宝箱的物品、yaml文件指定的物品至多消耗掉70次
    '''
    # 锦囊
    D.get('cmd=store&store_type=5&page=1')
    for number, id in D.findall(r'数量：(\d+).*?id=(\d+).*?使用'):
        if id in ['3023', '3024', '3025', '3103']:
            # xx洗刷刷
            continue
            # 提前
        else:
            for _ in range(int(number)):
                # 使用
                D.get(f'cmd=use&id={id}&store_type=2&page=1')
                D.search(r'<br />(.*?)<br />斗豆')

    # 属性
    D.get('cmd=store&store_type=2&page=1')
    for number, id in D.findall(r'数量：(\d+).*?id=(\d+).*?使用'):
        for _ in range(int(number)):
            # 使用
            D.get(f'cmd=use&id={id}&store_type=2&page=1')
            D.search(r'<br />(.*?)<br />斗豆')

    if WEEK == '4':
        data = []
        # 背包
        D.get('cmd=store')
        if page := D.findall(r'第1/(\d+)'):
            for p in range(1, int(page[0]) + 1):
                # 下页
                D.get(f'cmd=store&store_type=0&page={p}')
                data += D.findall(r'宝箱</a>数量：(\d+).*?id=(\d+).*?使用')

            # 使用
            for k, v in data:
                for _ in range(int(k)):
                    D.get(f'cmd=use&id={v}&store_type=0')
                    D.search(r'<br />(.*?)<br />斗豆')

            for id in D.read_yaml('背包'):
                for _ in range(70):
                    D.get(f'cmd=use&id={id}')
                    D.search(r'<br />(.*?)<br />斗豆')
                    if '您使用了' not in html:
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
        D.get(f'cmd=exchange&subtype=10&costtype={type}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))

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
        D.get(url)
        MSG.append(D.search(r'】<br />(.*?)<br />'))
    # 竞技场
    D.get('cmd=arena&op=queryexchange')
    MSG.append(D.search(r'竞技场</a><br />(.*?)<br /><br />'))
    # 帮派商会
    D.get('cmd=fac_corp&op=2')
    MSG.append(D.search(r'剩余刷新时间.*?秒&nbsp;(.*?)<br />'))


def 猜单双():
    '''猜单双

        随机单数、双数
    '''
    # 猜单双
    D.get('cmd=oddeven')
    for _ in range(5):
        if value := D.findall(r'value=(\d+)">.*?数'):
            value = random.choice(value)
            # 单数1 双数2
            D.get(f'cmd=oddeven&value={value}')
            MSG.append(D.search(r'】<br />(.*?)<br />'))
        else:
            break


def 煮元宵():
    '''煮元宵

        成熟度>=96时赶紧出锅
    '''
    # 煮元宵
    D.get('cmd=yuanxiao2014')
    # number: list = D.findall(r'今日剩余烹饪次数：(\d+)')
    for _ in range(4):
        # 开始烹饪
        D.get('cmd=yuanxiao2014&op=1')
        if '领取烹饪次数' in html:
            MSG.append('没有烹饪次数了')
            break
        for _ in range(20):
            maturity = D.findall(r'当前元宵成熟度：(\d+)')
            if int(maturity[0]) >= 96:
                # 赶紧出锅
                D.get('cmd=yuanxiao2014&op=3')
                MSG.append(D.search(r'活动规则</a><br /><br />(.*?)。'))
                break
            # 继续加柴
            D.get('cmd=yuanxiao2014&op=2')


def 元宵节():
    '''元宵节

        周四领取、领取月桂兔
    '''
    # 领取
    D.get('cmd=newAct&subtype=101&op=1')
    MSG.append(D.search(r'】</p>(.*?)<br />'))
    # 领取月桂兔
    D.get('cmd=newAct&subtype=101&op=2&index=0')
    MSG.append(D.search(r'】</p>(.*?)<br />'))


def 万圣节():
    '''万圣节

        点亮南瓜灯
        活动截止日的前一天优先兑换礼包B，最后兑换礼包A
    '''
    # 点亮南瓜灯
    D.get('cmd=hallowmas&gb_id=1')
    while True:
        if cushaw_id := D.findall(r'cushaw_id=(\d+)'):
            id = random.choice(cushaw_id)
            # 南瓜
            D.get(f'cmd=hallowmas&gb_id=4&cushaw_id={id}')
            MSG.append(D.search(r'】<br />(.*?)<br />'))
        # 恭喜您获得10体力和南瓜灯一个！
        # 恭喜您获得20体力和南瓜灯一个！南瓜灯已刷新
        # 请领取今日的活跃度礼包来获得蜡烛吧！
        if '请领取' in html:
            break

    # 兑换奖励
    D.get('cmd=hallowmas&gb_id=0')
    try:
        date: str = D.findall(r'~\d+月(\d+)日')[0]
        if int(DATE) == int(date) - 1:
            num: str = D.findall(r'南瓜灯：(\d+)个')[0]
            B = int(num) / 40
            A = (int(num) - int(B) * 40) / 20
            for _ in range(int(B)):
                # 礼包B 消耗40个南瓜灯
                D.get('cmd=hallowmas&gb_id=6')
                MSG.append(D.search(r'】<br />(.*?)<br />'))
            for _ in range(int(A)):
                # 礼包A 消耗20个南瓜灯
                D.get('cmd=hallowmas&gb_id=5')
                MSG.append(D.search(r'】<br />(.*?)<br />'))
    except Exception:
        ...


def 神魔转盘():
    '''神魔转盘

        幸运抽奖一次
    '''
    D.get('cmd=newAct&subtype=88&op=1')
    MSG.append(D.search(r'】<br />(.*?)<br />'))


def 乐斗驿站():
    '''乐斗驿站

        免费领取淬火结晶*1
    '''
    D.get('cmd=newAct&subtype=167&op=2')
    MSG.append(D.search(r'】<br />(.*?)<br />'))


def 浩劫宝箱():
    '''浩劫宝箱

        领取
    '''
    D.get('cmd=newAct&subtype=152')
    MSG.append(D.search(r'浩劫宝箱<br />(.*?)<br />'))


def 幸运转盘():
    '''幸运转盘

        转动轮盘
    '''
    D.get('cmd=newAct&subtype=57&op=roll')
    MSG.append(D.search(r'0<br /><br />(.*?)<br />'))


def 喜从天降():
    '''喜从天降

        点燃烟花
    '''
    D.get('cmd=newAct&subtype=137&op=1')
    MSG.append(D.search(r'】<br />(.*?)<br />'))


def 冰雪企缘():
    '''冰雪企缘

        至多领取两次
    '''
    # 冰雪企缘
    D.get('cmd=newAct&subtype=158&op=0')
    for t in D.findall(r'gift_type=(\d+)'):
        # 领取
        D.get(f'cmd=newAct&subtype=158&op=2&gift_type={t}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 甜蜜夫妻():
    '''甜蜜夫妻

        夫妻好礼或单身好礼领取3次
    '''
    for i in range(1, 4):
        # 领取
        D.get(f'cmd=newAct&subtype=129&op=1&flag={i}')


def 幸运金蛋():
    '''幸运金蛋

        砸金蛋
    '''
    # 幸运金蛋
    D.get('cmd=newAct&subtype=110&op=0')
    for i in D.findall(r'index=(\d+)'):
        # 砸金蛋
        D.get(f'cmd=newAct&subtype=110&op=1&index={i}')
        MSG.append(D.search(r'】<br /><br />(.*?)<br />'))


def 乐斗菜单():
    '''乐斗菜单

        点单
    '''
    # 乐斗菜单
    D.get('cmd=menuact')
    if gift := D.findall(r'套餐.*?gift=(\d+).*?点单</a>'):
        # 点单
        D.get(f'cmd=menuact&sub=1&gift={gift[0]}')
        MSG.append(D.search(r'哦！<br /></p>(.*?)<br />'))
    else:
        MSG.append('点单已领取完')


def 客栈同福():
    '''客栈同福

        献酒三次
    '''
    for _ in range(3):
        # 献酒
        D.get('cmd=newAct&subtype=155')
        MSG.append(D.search(r'】<br /><p>(.*?)<br />'))
        if '黄酒不足' in html:
            break


def 周周礼包():
    '''周周礼包

        领取一次
    '''
    # 周周礼包
    D.get('cmd=weekgiftbag&sub=0')
    if id := D.findall(r';id=(\d+)">领取'):
        # 领取
        D.get(f'cmd=weekgiftbag&sub=1&id={id[0]}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 登录有礼():
    '''登录有礼

        领取一次
    '''
    # 登录有礼
    D.get('cmd=newAct&subtype=56')
    # 领取
    if index := D.findall(r'gift_index=(\d+)">领取'):
        D.get(
            f'cmd=newAct&subtype=56&op=draw&gift_type=1&gift_index={index[-1]}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 活跃礼包():
    '''活跃礼包

        领取两次
    '''
    for p in ['1', '2']:
        D.get(f'cmd=newAct&subtype=94&op={p}')
        MSG.append(D.search(r'】.*?<br />(.*?)<br />'))


def 上香活动():
    '''上香活动

        领取檀木香、龙涎香各两次
    '''
    for _ in range(2):
        # 檀木香
        D.get('cmd=newAct&subtype=142&op=1&id=1')
        MSG.append(D.search(r'】<br />(.*?)<br />'))
        # 龙涎香
        D.get('cmd=newAct&subtype=142&op=1&id=2')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 徽章战令():
    '''徽章战令

        领取每日礼包
    '''
    # 每日礼包
    D.get('cmd=badge&op=1')
    MSG.append(D.search(r'】<br />(.*?)<br />'))


def 生肖福卡():
    '''生肖福卡

        领取
    '''
    # 领取
    D.get('cmd=newAct&subtype=174&op=7&task_id=1')
    MSG.append(D.search(r'~<br /><br />(.*?)<br />活跃度80'))


def 长安盛会():
    '''长安盛会

        盛会豪礼点击领取
        签到宝箱点击领取
        点击参与至多3次
    '''
    for _ in range(3):
        # 长安盛会
        D.get('cmd=newAct&subtype=118&op=0')
        for id in D.findall(r'op=1&amp;id=(\d+)'):
            if id == 3:
                # 选择奖励内容 3036黄金卷轴 or 5089黄金卷轴
                D.get('cmd=newAct&subtype=118&op=2&select_id=3036')
            D.get(f'cmd=newAct&subtype=118&op=1&id={id}')
            if '【周年嘉年华】' in html:
                MSG.append(D.search(r'】<br /><br />(.*?)</p>'))
                return
            else:
                MSG.append(D.search(r'】<br />(.*?)<br />'))


def 深渊秘宝():
    '''深渊秘宝

        仅三魂秘宝和七魄秘宝都能免费抽奖时才执行
    '''
    # 深渊秘宝
    D.get('cmd=newAct&subtype=175')
    number: int = html.count('免费抽奖')
    if number == 2:
        for type in range(1, 3):
            D.get(
                f'cmd=newAct&subtype=175&op=1&type={type}&times=1')
            MSG.append(D.search(r'深渊秘宝<br />(.*?)<br />'))
    else:
        MSG.append(f'免费抽奖次数为 {number}，不足两次时该任务不执行')


def 登录商店():
    '''登录商店

        周四全部兑换黄金卷轴*1
    '''
    for _ in range(5):
        # 兑换5次 黄金卷轴*5
        D.get(
            'cmd=newAct&op=exchange&subtype=52&type=1223&times=5')
        MSG.append(D.search(r'<br /><br />(.*?)<br /><br />'))
    for _ in range(3):
        # 兑换3次 黄金卷轴*1
        D.get(
            'cmd=newAct&op=exchange&subtype=52&type=1223&times=1')
        MSG.append(D.search(r'<br /><br />(.*?)<br /><br />'))


def 盛世巡礼():
    '''盛世巡礼

        周四收下礼物
        对话		cmd=newAct&subtype=150&op=3&itemId=0
        点击继续	cmd=newAct&subtype=150&op=4&itemId=0
        收下礼物	cmd=newAct&subtype=150&op=5&itemId=0
    '''
    for itemId in [0, 4, 6, 9, 11, 14, 17]:
        # 收下礼物
        D.get(f'cmd=newAct&subtype=150&op=5&itemId={itemId}')
        MSG.append(D.search(r'礼物<br />(.*?)<br />'))


def 中秋礼盒():
    '''中秋礼盒

        领取
    '''
    for _ in range(3):
        # 中秋礼盒
        D.get('cmd=midautumngiftbag&sub=0')
        ids = D.findall(r'amp;id=(\d+)')
        if not ids:
            MSG.append('没有可领取的了')
            break
        for id in ids:
            # 领取
            D.get(f'cmd=midautumngiftbag&sub=1&id={id}')
            MSG.append(D.search(r'】<br />(.*?)<br />'))
            if '已领取完该系列任务所有奖励' in html:
                continue


def 双节签到():
    '''双节签到

        领取签到奖励
        活动截止日的前一天领取奖励金
    '''
    # 双节签到
    D.get('cmd=newAct&subtype=144')
    date: str = D.findall(r'至\d+月(\d+)日')[0]
    if 'op=1' in html:
        # 领取
        D.get('cmd=newAct&subtype=144&op=1')
        MSG.append(D.search(r'】<br />(.*?)<br />'))
    if int(DATE) == int(date) - 1:
        # 奖励金
        D.get('cmd=newAct&subtype=144&op=3')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 圣诞有礼():
    '''圣诞有礼

        周四领取点亮奖励和连线奖励
    '''
    # 圣诞有礼
    D.get('cmd=newAct&subtype=145')
    for id in D.findall(r'task_id=(\d+)'):
        # 任务描述：领取奖励
        D.get(f'cmd=newAct&subtype=145&op=1&task_id={id}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))
    # 连线奖励
    for index in D.findall(r'index=(\d+)'):
        D.get(f'cmd=newAct&subtype=145&op=2&index={index}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 五一礼包():
    '''五一礼包

        周四领取三次劳动节礼包
    '''
    for id in range(3):
        D.get(f'cmd=newAct&subtype=113&op=1&id={id}')
        if '【劳动节礼包】' in html:
            mode = r'】<br /><br />(.*?)</p>'
        else:
            mode = r'】<br /><br />(.*?)<br />'
        MSG.append(D.search(mode))


def 新春礼包():
    '''新春礼包

        周四领取礼包
    '''
    # 新春礼包
    D.get('cmd=xinChunGift&subtype=1')
    date_list = D.findall(r'~\d+月(\d+)日')
    giftid = D.findall(r'giftid=(\d+)')
    for date, id in zip(date_list, giftid):
        if int(DATE) == int(date) - 1:
            D.get(f'cmd=xinChunGift&subtype=2&giftid={id}')
            MSG.append(D.search(r'】<br />(.*?)<br />'))


def 新春拜年():
    '''新春拜年

        第一轮赠礼三个礼物
        第二轮收取礼物
    '''
    # 新春拜年
    D.get('cmd=newAct&subtype=147')
    if 'op=1' in html:
        for index in random.sample(range(5), 3):
            # 选中
            D.get(f'cmd=newAct&subtype=147&op=1&index={index}')
        # 赠礼
        D.get('cmd=newAct&subtype=147&op=2')
        MSG.append('已赠礼')
    elif 'op=3' in html:
        # 收取礼物
        D.get('cmd=newAct&subtype=147&op=3')
        MSG.append(D.search(r'祝您：.*?<br /><br />(.*?)<br />'))


def 春联大赛():
    '''春联大赛

        选择、领取斗币各三次
    '''
    # 开始答题
    D.get('cmd=newAct&subtype=146&op=1')
    if '您的活跃度不足' in html:
        MSG.append('您的活跃度不足50')
        return
    elif '今日答题已结束' in html:
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
        for s in D.findall(r'上联：(.*?) 下联：'):
            x = chunlian.get(s)
            if x is None:
                # 上联在字库中不存在，将随机选择
                xialian = [random.choice(range(3))]
            else:
                xialian = D.findall(f'{x}<a.*?index=(\d+)')
            if xialian:
                # 选择
                # index 0 1 2
                D.get(f'cmd=newAct&subtype=146&op=3&index={xialian[0]}')
                MSG.append(D.search(r'剩余\d+题<br />(.*?)<br />'))
                # 确定选择
                D.get('cmd=newAct&subtype=146&op=2')
                MSG.append(D.search(r'】<br />(.*?)<br />'))

    for id in range(1, 4):
        # 领取
        D.get(f'cmd=newAct&subtype=146&op=4&id={id}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 乐斗游记():
    '''乐斗游记

        每天领取积分
        每周四一键领取、兑换十次、兑换一次
    '''
    # 乐斗游记
    D.get('cmd=newAct&subtype=176')

    # 今日游记任务
    for id in D.findall(r'task_id=(\d+)'):
        # 领取
        D.get(f'cmd=newAct&subtype=176&op=1&task_id={id}')
        MSG.append(D.search(r'积分。<br /><br />(.*?)<br />'))

    if WEEK == '4':
        # 一键领取
        D.get('cmd=newAct&subtype=176&op=5')
        MSG.append(D.search(r'积分。<br /><br />(.*?)<br />'))
        MSG.append(D.search(r'十次</a><br />(.*?)<br />乐斗'))
        # 兑换
        num_list: list = D.findall(r'溢出积分：(\d+)')
        if (num := int(num_list[0])) != 0:
            num10 = int(num / 10)
            num1 = num - (num10 * 10)
            for _ in range(num10):
                # 兑换十次
                D.get('cmd=newAct&subtype=176&op=2&num=10')
                MSG.append(D.search(r'积分。<br /><br />(.*?)<br />'))
            for _ in range(num1):
                # 兑换一次
                D.get('cmd=newAct&subtype=176&op=2&num=1')
                MSG.append(D.search(r'积分。<br /><br />(.*?)<br />'))


def 新春登录礼():
    '''新春登录礼

        每天至多领取七次
    '''
    # 新春登录礼
    D.get('cmd=newAct&subtype=99&op=0')
    for day in D.findall(r'day=(\d+)'):
        # 领取
        D.get(f'cmd=newAct&subtype=99&op=1&day={day}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))


def 年兽大作战():
    '''年兽大作战

        随机武技库免费一次
        自选武技库从大、中、小、投、技各随机选择一个补位
        挑战3次
    '''
    # 年兽大作战
    D.get('cmd=newAct&subtype=170&op=0')
    if '等级不够' in html:
        MSG.append('等级不够，还未开启年兽大作战哦！')
        return
    for _ in D.findall(r'剩余免费随机次数：(\d+)'):
        # 随机武技库 免费一次
        D.get('cmd=newAct&subtype=170&op=6')
        MSG.append(D.search(r'帮助</a><br />(.*?)<br />'))

    # 自选武技库
    # 从大、中、小、投、技各随机选择一个
    if '暂未选择' in html:
        for t in range(5):
            D.get(f'cmd=newAct&subtype=170&op=4&type={t}')
            if '取消选择' in html:
                continue
            if ids := D.findall(r'id=(\d+)">选择'):
                # 选择
                D.get(f'cmd=newAct&subtype=170&op=7&id={random.choice(ids)}')
                if '自选武技列表已满' in html:
                    break

    for _ in range(3):
        # 挑战
        D.get('cmd=newAct&subtype=170&op=8')
        MSG.append(D.search(r'帮助</a><br />(.*?)。'))


def 惊喜刮刮卡():
    '''惊喜刮刮卡

        每天至多领取三次
    '''
    for i in range(3):
        D.get(f'cmd=newAct&subtype=148&op=2&id={i}')
        MSG.append(D.search(r'奖池预览</a><br /><br />(.*?)<br />'))


def 开心娃娃机():
    '''开心娃娃机

        每天抓取一次
    '''
    D.get('cmd=newAct&subtype=124&op=1')
    MSG.append(D.search(r'】<br />(.*?)<br />'))


def 好礼步步升():
    '''好礼步步升

        每天领取一次
    '''
    D.get('cmd=newAct&subtype=43&op=get')
    MSG.append(D.search(r'】<br />(.*?)<br />'))


def 企鹅吉利兑():
    '''企鹅吉利兑

        领取、活动截止日的前一天兑换材料（每种至多兑换100次）
    '''
    # 企鹅吉利兑
    D.get('cmd=geelyexchange')
    # 修炼任务 》每日任务
    for id in D.findall(r'id=(\d+)">领取</a>'):
        # 领取
        D.get(f'cmd=geelyexchange&op=GetTaskReward&id={id}')
        MSG.append(D.search(r'】<br /><br />(.*?)<br /><br />'))

    try:
        # 限时兑换
        date: str = D.findall(r'至\d+月(\d+)日')[0]
        if int(DATE) == int(date) - 1:
            for p in D.read_yaml('企鹅吉利兑'):
                for _ in range(100):
                    D.get(f'cmd=geelyexchange&op=ExchangeProps&id={p}')
                    if '你的精魄不足，快去完成任务吧~' in html:
                        break
                    elif '该物品已达兑换上限~' in html:
                        break
                    MSG.append(D.search(r'】<br /><br />(.*?)<br />'))
                if '当前精魄：0' in html:
                    break
    except Exception:
        ...
    # 当前精魄
    MSG.append(D.search(r'喔~<br />(.*?)<br /><br />'))


def 乐斗回忆录():
    '''乐斗回忆录

        周四领取回忆礼包
    '''
    for id in [1, 3, 5, 7, 9]:
        # 回忆礼包
        D.get(f'cmd=newAct&subtype=171&op=3&id={id}')
        MSG.append(D.search(r'6点<br />(.*?)<br />'))


def 乐斗大笨钟():
    '''乐斗大笨钟

        领取一次
    '''
    # 领取
    D.get('cmd=newAct&subtype=18')
    MSG.append(D.search(r'<br /><br /><br />(.*?)<br />'))


def 周年生日祝福():
    '''周年生日祝福

        周四领取
    '''
    for day in range(1, 8):
        D.get(f'cmd=newAct&subtype=165&op=3&day={day}')
        MSG.append(D.search(r'】<br />(.*?)<br />'))
