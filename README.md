<h2>使用青龙面板在左上角切换到ql分支</h2>


## 概述

因为等级或者战力差异，脚本不一定适合所有人，脚本参考作者等级 `136`

乐斗等级战力不高的玩家使用脚本可能会有一些问题，建议手动提高等级战力后再使用

脚本定时工作时间：
- 第一轮 `13:01` 运行 `daledouone.py` 模块
- 第二轮 `20:01` 运行 `daledoutwo.py` 模块

大乐斗cookie有效期（通过账号密码登录获得时）：
- 脚本每隔30分钟（定时由 `Schedule` 库实现）请求一次来延长cookie有效期
- 当天更换cookie，第二天依然有效，但会在第三天早上8点整左右失效
- 停止脚本超过一个多小时，cookie也会失效
- 一键登录获得的cookie有效期两天

大乐斗已实现的功能：
- [文档](https://www.gaoyuanqi.cn/python-daledou/#more)


## Python版本

```
Python 3.11
```


## 使用教程

- [使用教程](./md/tutorials.md ':include')


## QQ交流群

- 783035662


## 更新日志

- [更新日志](./md/update_log.md ':include')
