# -*- coding: utf-8 -*-
import re
import time
import traceback
from shutil import copy
from os import environ, path, getenv
from importlib import import_module

import yaml
import requests
from loguru import logger


YAML_PATH = './config'


class CookieError(Exception):
    ...


class DaLeDouInit:
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie

    def clean_cookie(self) -> str:
        '''清洁大乐斗cookie

        :return: 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx'
        '''
        ck = ''
        for key in ['RK', 'ptcz', 'uin', 'skey']:
            try:
                result = re.search(
                    f'{key}=(.*?); ',
                    f'{self.cookie}; ',
                    re.S
                ).group(0)
            except AttributeError:
                raise CookieError(f'大乐斗cookie不正确：{self.cookie}')
            ck += f'{result}'
        return ck[:-2]

    def verify_cookie(self, cookie: str):
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
            logger.success(f'脚本创建了一个配置文件：{YAML_PATH}/{qq}.yaml')
            copy(srcpath, yamlpath)

    @staticmethod
    def create_log() -> int:
        '''创建当天日志文件'''
        date = time.strftime("%Y-%m-%d", time.localtime())
        return logger.add(
            f'./log/{getenv("QQ")}/{date}.log',
            format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>',
            enqueue=True,
            encoding='utf-8',
            retention='30 days'
        )

    def main(self):
        cookie = self.clean_cookie()
        qq = re.search(r'uin=o(\d+); ', cookie, re.S).group(1)
        environ['QQ'] = qq
        if self.verify_cookie(cookie):
            environ['COOKIE'] = cookie
            DaLeDouInit.copy_yaml(qq)
            if cookie != getenv(f'YOUXIAO_{qq}'):
                environ[f'YOUXIAO_{qq}'] = cookie
                logger.success(f'   {getenv("QQ")}：将在 13:01 和 20:01 定时运行...')
            return DaLeDouInit.create_log()

        if cookie != getenv(f'SHIXIAO_{qq}'):
            environ[f'SHIXIAO_{qq}'] = cookie
            logger.warning(f'   {getenv("QQ")}失效：{cookie}')
            push(f'cookie失效：{qq} ', [f'{cookie}'])


class DaLeDou:
    def __init__(self) -> None:
        self.msg: list = []
        self.date: str = time.strftime('%d', time.localtime())
        self.week: str = time.strftime('%w')
        self.path = 'src.daledou.'

    @staticmethod
    def get(params: str) -> str:
        global html
        url = f'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?{params}'
        headers = {
            'Cookie': getenv('COOKIE'),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        html = res.text
        time.sleep(0.2)
        return html

    @staticmethod
    def read_yaml(key: str) -> dict:
        '''读取 config 目录下的 yaml 配置文件'''
        try:
            with open(f'{YAML_PATH}/{getenv("QQ")}.yaml', 'r', encoding='utf-8') as fp:
                users: dict = yaml.safe_load(fp)
                data: dict = users[key]
            return data
        except Exception:
            error = traceback.format_exc()
            logger.error(f'{getenv("QQ")}.yaml 配置不正确：\n{error}')
            push(f'{getenv("QQ")}.yaml 异常', [error])

    @staticmethod
    def load_object(path: str) -> list:
        '''动态导入模块并运行实例方法run

        传入参数 src.daledou.xieshenmibao.XieShen 被拆分为：
            module：src.daledou.xieshenmibao
            name：XieShen
        '''
        dot = path.rindex('.')
        module, name = path[:dot], path[dot + 1:]
        mod = import_module(module)
        return getattr(mod, name)().run()

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

    def run(self):
        ...

    def main(self, lunci: str):
        start = time.time()
        self.run()
        end = time.time()
        self.msg.append(f'\n【运行时长】\n时长：{int(end - start)} s')

        push(f'{getenv("QQ")} {lunci}', self.msg)


class DaLeDouOne(DaLeDou):
    '''大乐斗第一轮'''

    def __init__(self) -> None:
        super().__init__()
        self.modulepath = [
            ['邪神秘宝', True, 'xieshenmibao.XieShen'],
            ['华山论剑', (int(self.date) <= 26), 'huashanlunjian.HuaShan'],
            ['每日宝箱', (self.date == '20'), 'meiribaoxiang.MeiRi'],
            ['分享', True, 'fenxiang.FenXiang'],
            ['乐斗', True, 'ledou.LeDou'],
            ['报名', True, 'baoming.BaoMing'],
            ['巅峰之战进行中', True, 'dianfengzhizhan.DianFeng'],
            ['矿洞', True, 'kuangdong.KuangDong'],
            ['掠夺', (self.week in ['2', '3']), 'lueduo.LueDuo'],
            ['踢馆', (self.week in ['5', '6']), 'tiguan.TiGuan'],
            ['竞技场', (int(self.date) <= 25), 'jingjichang.JingJiChang'],
            ['十二宫', True, 'shiergong.ShiErGong'],
            ['许愿', True, 'xuyuan.XuYuan'],
            ['抢地盘', True, 'qiangdipan.QiangDiPan'],
            ['历练', True, 'lilian.LiLian'],
            ['镖行天下', True, 'biaoxingtianxia.BiaoXing'],
            ['幻境', True, 'huanjing.HuanJing'],
            ['群雄逐鹿', (self.week == '6'), 'qunxiongzhulu.QunXiong'],
            ['画卷迷踪', True, 'huajuanmizong.HuaJuan'],
            ['门派', True, 'menpai.MenPai'],
            ['门派邀请赛', (self.week != '2'), 'menpaiyaoqingsai.MenPai'],
            ['会武', (self.week not in ['5', '0']), 'huiwu.HuiWu'],
            ['梦想之旅', True, 'mengxiangzhilv.MengXiang'],
            ['问鼎天下', True, 'wendingtianxia.WenDingOne'],
            ['帮派商会', True, 'bangpaishanghui.BangPai'],
            ['帮派远征军', True, 'baipaiyuanzhengjun.BangPai'],
            ['帮派黄金联赛', True, 'baipaihuangjinliansai.BangPai'],
            ['任务派遣中心', True, 'renwupaiqianzhongxin.RenWu'],
            ['武林盟主', True, 'wulinmengzhu.WuLin'],
            ['全民乱斗', True, 'quanminluandou.QuanMin'],
            ['侠士客栈', True, 'xiashikezhan.XiaShi'],
            ['江湖长梦', True, 'jianghuchangmeng.JiangHu'],
            ['任务', True, 'renwu.RenWu'],
            ['我的帮派', True, 'mygang.MyGang'],
            ['帮派祭坛', True, 'baipaijitan.BangPai'],
            ['飞升大作战', True, 'feisheng.FeiSheng'],
            ['深渊之潮', True, 'shenyuanzhichao.ShenYuan'],
            ['每日奖励', True, 'meirijiangli.MeiRi'],
            ['今日活跃度', True, 'jinrihuoyuedu.JinRi'],
            ['仙武修真', True, 'xianwuxiuzhen.XianWu'],
            ['大侠回归三重好礼', (self.week == '4'), 'daxiahuigui.DaXia'],
            ['乐斗黄历', True, 'ledouhuangli.LeDou'],
            ['奥义', True, 'aoyi.AoYi'],
            ['专精', True, 'zhuanjing.ZhuanJing'],
            ['镶嵌', (self.week == '4'), 'xiangqian.XiangQian'],
            ['兵法', (self.week in ['4', '6']), 'bingfa.BingFa'],
            ['神匠坊', (self.week == '4'), 'shenjiangfang.ShenJiang'],
            ['活动', True, 'events.EventsOne'],
            ['背包', True, 'beibao.BeiBao'],
            ['商店', True, 'shangdian.ShangDian'],
        ]

    def run(self):
        if mission := DaLeDou.is_dld():
            for name, bool, path in self.modulepath:
                if (name in mission) and bool:
                    if name not in ['乐斗', '活动', '镶嵌', '神匠坊', '背包']:
                        self.msg.append(f'\n【{name}】')
                    environ['DLD_MISSIONS'] = name
                    self.msg += DaLeDou.load_object(f'{self.path}{path}')
        # print(self.msg)
        return self.msg


class DaLeDouTwo(DaLeDou):
    '''大乐斗第二轮'''

    def __init__(self) -> None:
        super().__init__()
        self.modulepath = [
            ['邪神秘宝', True, 'xieshenmibao.XieShen'],
            ['问鼎天下', (self.week not in ['6', '0']),
             'wendingtianxia.WenDingTwo'],
            ['任务派遣中心', True, 'renwupaiqianzhongxin.RenWu'],
            ['侠士客栈', True, 'xiashikezhan.XiaShi'],
            ['深渊之潮', True, 'shenyuanzhichao.ShenYuan'],
            ['活动', True, 'events.EventsTwo'],
        ]

    def run(self):
        if mission := DaLeDou.is_dld():
            for name, bool, path in self.modulepath:
                if (name in mission) and bool:
                    if name != '活动':
                        self.msg.append(f'\n【{name}】')
                    environ['DLD_MISSIONS'] = name
                    self.msg += DaLeDou.load_object(f'{self.path}{path}')
        # print(self.msg)
        return self.msg


def push(title: str, message: list) -> None:
    ''' pushplus 微信通知'''
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
            logger.success(f'  pushplus推送成功：{json}')
            return

        logger.warning(f'  pushplus推送失败：{json}')
        return

    logger.warning('  pushplus配置的token无效，取消微信推送')
