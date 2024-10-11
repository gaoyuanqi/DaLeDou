## 说明

**为了保险起见，斗豆及鹅币最好手动使用掉，以免使用脚本时被意外消耗**

本项目适合等级战力高、有乐斗达人的普通玩家，活跃度通常80以上


## Python版本

```
Python 3.11
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

**7、定时运行大乐斗任务**

启动定时命令：
```sh
python main.py timing
```
脚本将在 `13:10` 运行 [第一轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%B8%80%E8%BD%AE)，`20:01` 运行 [第二轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%BA%8C%E8%BD%AE)

`timing` 参数可以省略，上面命令等同于：
```sh
python main.py
```

还会每隔2小时检查大乐斗Cookie有效期

**8、其它命令**

立即运行 [第一轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%B8%80%E8%BD%AE)，建议 `13:10` 后运行：
```sh
python main.py one
```

立即运行 [第二轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%BA%8C%E8%BD%AE)，建议 `20:01` 后运行：
```sh
python main.py two
```

运行 `run.py` 中的一个或多个函数：
```sh
python main.py dev -- [func_name]
```

例如：
```sh
# 运行 邪神秘宝
python main.py dev -- 邪神秘宝

# 依次运行 邪神秘宝、矿洞
python main.py dev -- 邪神秘宝 矿洞
```

**9、其它大乐斗任务**

这些任务只能通过 `dev` 命令模式执行，它们不在 **第一轮** 和 **第二轮** 中

以下列出的清单表明已支持：
- `神装`：自动兑换材料并进阶
- `夺宝奇兵`：太空探宝场景投掷

运行神装：
```sh
python main.py dev -- 神装
```


## 大乐斗Cookie有效期

目前测试的通过 **一键登录** 获得的Cookie有效期可以永久，但需要每隔几天手动登录大乐斗
