## 说明

因为等级或者战力差异，脚本不一定适合所有人，作者目前等级 `134`

脚本定时工作时间：
- 第一轮 `13:01` 运行 `daledouone.py` 模块，耗时 `300~400` 多秒
- 第二轮 `20:01` 运行 `daledoutwo.py` 模块，耗时 50~100 多秒

大乐斗cookie有效期：
- 脚本每隔30分钟（定时由 `Schedule` 库实现）请求一次来保持cookie活跃性，从而使cookie有效期最长可以超过48小时
- 当天更换cookie，第二天依然有效，但会在第三天早上8点整左右失效
- 停止脚本超过一个多小时，cookie也会失效


## Python版本

```
Python 3.10
```


## 下载脚本

通过git下载：
```sh
$ git clone https://github.com/gaoyuanqi/DaLeDou.git
$ cd DaLeDou
$ ls
```


## 更新脚本

在 **DaLeDou** 目录下执行：
```sh
git reset --hard
git pull
```

注意这会销毁你本地所有修改，你可能需要重新修改 `./settings.py` 文件和 `./config` 目录下的yaml文件（除了 `_daledou.yaml`）


## settings.py 配置

**添加大乐斗cookie（必须，支持多账号）**

首先浏览器登录大乐斗：
```
https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index&channel=0
```

将复制的大乐斗Cookie直接填入：
```python
# 大乐斗Cookie
# 支持多账号，每行对应一个账号
# 不要有中文字符
DALEDOU_COOKIE = [
    'Cookie1',
    'Cookie2',
]
```

**添加pushplus微信通知（可选）**

微信公众号 `pushplus` > `pushplus` > `pushplus官网` > `一对一推送` > `一键复制`

将token添加到：
```python
PUSHPLUS_TOKEN = 'token'
```


## 自定义账号配置

脚本运行会自动为当前有效cookie创建以 `QQ` 命名的yaml文件，该文件在`./config` 目录下，其内容与 `_daledou.yaml` 完全一致

如果文件存在则不做任何操作

一个 `QQ.yaml` 文件对应唯一一个账号，你可以为每个账号独立配置

`_daledou.yaml` 支持配置如下：
- `十二宫`: 选择挑战哪个关卡
- `幻境`: 选择挑战哪个关卡
- `深渊之潮`: 选择挑战 **深渊秘境**
- `历练`: 选择挑战哪些关卡
- `竞技场`: 商店兑换
- `门派邀请赛`: 商店兑换
- `帮派商会`: 交易和兑换
- `活动`: 企鹅吉利兑和春联大赛
- `背包`: 使用和提前


## 使用教程

- [使用教程](./md/tutorials.md ':include')


## 脚本执行文档

```bash
https://www.gaoyuanqi.cn/python-daledou/#more
```


## QQ交流群

- 783035662


## 更新日志

- [更新日志](./md/update_log.md ':include')
