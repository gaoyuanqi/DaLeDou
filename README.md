## 说明

**为了保险起见，斗豆及鹅币最好手动使用掉，以免使用脚本时被意外消耗**


## 功能

- [第一轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%B8%80%E8%BD%AE) 
- [第二轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%BA%8C%E8%BD%AE)
- [其它任务](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E5%85%B6%E5%AE%83%E4%BB%BB%E5%8A%A1)


## Python版本

```
Python 3.12
```


## 快速开始

**1、下载脚本**
```sh
git clone https://github.com/gaoyuanqi/DaLeDou.git
```

**2、进入项目**
```sh
cd DaLeDou
```

**3、安装依赖**
```sh
make install
```

**4、激活虚拟环境**
```sh
pipenv shell
```

**5、`config/settings.yaml` 配置**

添加大乐斗Cookie（必须）：
```yaml
DALEDOU_ACCOUNT:
  - RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=111111
  - RK=xx; ptcz=xx; openId=xx; accessToken=xx; newuin=222222
```

添加pushplus微信通知（可选）：
```yaml
PUSHPLUS_TOKEN: ""
```

**6、创建大乐斗任务配置文件**

如果你第一次使用，运行以下命令：
```sh
python main.py check
```
这会在 `config` 目录下创建一个以 `QQ` 命名的yaml配置文件（大乐斗Cookie有效才会创建）

**7、定时任务**

启动定时命令：
```sh
python main.py
```
脚本将在 `13:10` 运行 `第一轮`，`20:01` 运行 `第二轮`

期间还会每隔2小时检查大乐斗Cookie有效期

**8、其它任务**

指 `第一轮` 和 `第二轮` 之外的任务

```sh
# 比如立即运行 神装
python main.py other -- 神装
```

**9、其它命令**

立即运行 `第一轮`，建议 `13:10` 后运行：
```sh
python main.py one
```

可以携带额外参数：
```sh
# 立即运行第一轮的邪神秘宝
python main.py one -- 邪神秘宝
```

立即运行 `第二轮`，建议 `20:01` 后运行：
```sh
python main.py two
```

可以携带额外参数：
```sh
# 立即运行第二轮的邪神秘宝
python main.py two -- 邪神秘宝
```


## 大乐斗Cookie有效期

目前测试的通过 **一键登录** 获得的Cookie有效期可以永久，但需要每隔几天手动登录大乐斗
