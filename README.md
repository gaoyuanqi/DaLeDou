## 说明

> 为了保险起见，不要保留斗豆及鹅币，以免被脚本意外消耗


## 功能

- [第一轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%B8%80%E8%BD%AE)
- [第二轮](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E7%AC%AC%E4%BA%8C%E8%BD%AE)
- [其它任务](https://www.gaoyuanqi.cn/python-daledou/?highlight=%E5%A4%A7%E4%B9%90%E6%96%97#%E5%85%B6%E5%AE%83%E4%BB%BB%E5%8A%A1)


## Python版本

```
Python 3.12
```


## 快速开始

### 1.下载脚本
```sh
git clone https://github.com/gaoyuanqi/DaLeDou.git
cd DaLeDou
```

### 2.安装依赖（三选一）

使用 `pip` 一键安装：
```sh
pip3 install -r requirements.txt
```

使用 `pip` 手动安装：
```sh
pip3 install loguru
pip3 install pyyaml
pip3 install requests
pip3 install schedule
```

使用 [uv](https://hellowac.github.io/uv-zh-cn/) 安装：
```sh
uv sync
```

### 3.添加文字版大乐斗Cookie（必须）

[获取文字版大乐斗Cookie教程](#获取文字版大乐斗cookie教程)

将Cookie直接复制填入 `config/settings.yaml`：
```yaml
DALEDOU_ACCOUNT:
  - openId=xx; accessToken=xx; newuin=111111
  - openId=xx; accessToken=xx; newuin=222222
```

### 4.添加pushplus微信通知（可选）

微信接收的消息比日志简略

修改 `config/settings.yaml`：
```yaml
PUSHPLUS_TOKEN: ""
```

### 5.启动定时

```sh
python main.py --timing
```

### 6.修改任务配置

修改 `config/你的QQ.yaml` 文件


## 脚本命令

### timing 模式

启动定时：
```sh
python main.py --timing
```

### one 模式

运行 `第一轮`，建议 `13:10` 后运行：
```sh
python main.py --one
```

运行 `第一轮` 中的某个任务
```sh
python main.py --one 邪神秘宝
```

### two 模式

运行 `第二轮`，建议 `20:01` 后运行：
```sh
python main.py --two
```

运行 `第二轮` 中的某个任务
```sh
python main.py --two 邪神秘宝
```

### other 模式

查看携带参数：
```sh
python main.py --other
```

运行神装任务：
```sh
python main.py --other 神装
```


## 安卓使用Termux来运行脚本

1.安装 [termux](https://github.com/termux/termux-app/releases)

2.更换清华镜像源：
```sh
sed -i 's@^\(deb.*stable main\)$@#\1\ndeb https://mirrors.tuna.tsinghua.edu.cn/termux/apt/termux-main stable main@' $PREFIX/etc/apt/sources.list
```

3.更新包并升级：
```sh
apt update && apt upgrade
```

4.安装Python：
```sh
pkg install python
```

5.安装Git：
```sh
pkg install git
```

6.安装Vim：
```sh
pkg install vim
```

最后 [快速开始](#快速开始)


## 获取文字版大乐斗Cookie教程

### 使用安卓Via浏览器

1.应用商店安装 `via`

2.将 `via` 设为默认浏览器

3.[一键登录大乐斗文字版](https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index&channel=0)

4.等待3秒，然后点击 `via` 左上角 `✓`，再点击 `查看Cookies`

### 使用油猴脚本自动复制

感谢 `chansanya` 提供的代码：https://github.com/gaoyuanqi/DaLeDou/issues/23

> Via也可以运行此脚本


## 关于大乐斗Cookie有效期（2025.4.11）

同一个账号不能同时在线（多设备/多应用）

每次重新登录会刷新Cookie，旧Cookie会在几分钟后失效

只要不反复登录，则Cookie长期有效
