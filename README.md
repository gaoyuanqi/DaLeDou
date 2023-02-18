## 概述

`ql` 分支是为了适配青龙面板而创建的，实现功能与 `main` 主分支完全一致


## 青龙配置（v2.15.7）

**订阅管理**

|说明|输入|
|---|---|
|名称|`大乐斗`|
|链接|`https://github.com/gaoyuanqi/DaLeDou.git`|
|分支|`ql`|
|文件后缀|`py yaml`|

**环境变量**

|说明|输入|
|---|---|
|名称|`DALEDOU_ACCOUNT`|
|值|大乐斗cookie，多个cookie用 `\|` 分隔，比如 `cookie\|cookie\|cookie`|

**配置文件**

添加 `pushplus` 通知：
```sh
export PUSH_PLUS_TOKEN=""
```

**依赖管理**

安装以下依赖：
- `requests`
- `pyyaml`
- `decorator`

**定时任务**

搜索 `daledou` 关键字，除了以下三个文件，其它全删除：
- `daledouone.py`
- `daledoutwo.py`
- `daledoutiming.py`

直接运行 `daledoutiming.py`，然后查看运行日志

**脚本管理**

在 `gaoyuanqi_DaLeDou_qinglong` 目录下配置以qq命名的 `yaml`
