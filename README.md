## 说明

因为等级或者战力差异，脚本不一定适合所有人，作者目前等级 **133**

脚本定时工作时间：
- 第一轮 **13:01** 运行 **daledouone.py** 模块，耗时 **300~400** 多秒
- 第二轮 **20:01** 运行 **daledoutwo.py** 模块，耗时 **50~100** 多秒

大乐斗cookie有效期：
- 脚本每隔30分钟（定时由 **Schedule** 库实现）请求一次来保持cookie活跃性，从而使cookie有效期最长可以超过48小时
- 当天更换cookie，第二天依然有效，但会在第三天早上8点整左右失效
- 停止脚本超过一个多小时，cookie也会失效


## Python版本

```
Python 3.10
```


## 下载脚本

通过git下载：
```sh
git clone https://gitclone.com/github.com/gaoyuanqi/DaLeDou.git
cd DaLeDou
ls
```


## 更新脚本

在 **DaLeDou** 目录下执行：
```sh
git reset --hard
git pull
```

注意这会销毁你本地所有修改，你可能需要重新修改 **./settings.py** 文件和 **./missions/config** 目录下的yaml文件


## settings.py 配置

### 添加大乐斗cookie（必须，支持多账号）

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

### 添加pushplus微信通知（可选）

微信公众号 **pushplus** > **pushplus** > **pushplus官网** > **一对一推送** > **一键复制**

将token添加到：
```python
PUSHPLUS_TOKEN = 'token'
```


## 自定义任务

**./missions/config** 目录下有很多 **yaml** 后缀名的文件，根据你自己的实际情况（等级或战力）修改相关配置

比如你可以修改 **十二宫.yaml** 文件来决定扫荡某个关卡


## 使用教程

始终在 **DaLeDou** 目录下执行

### 本地使用教程

#### 一、安装依赖

```sh
pip3 install -r requirements.txt
```

如果你熟悉 **pipenv**，可以通过下面命令安装：
```sh
pipenv install
```

#### 二、立即运行指定轮次脚本

```sh
python local.py
```

然后按提示输入，`1` 表示第一轮，`2` 表示第二轮


### Docker使用教程

#### 一、安装Docker

```
https://www.gaoyuanqi.cn/docker-install/
```

#### 二、拉取镜像

```sh
docker pull python:3.10
```

#### 三、构建镜像

注意 `.` 不要省略：
```sh
docker build -t daledou:v1 .
```

#### 四、启动容器

如果是 **Linux** 系统需安装 **[docker-compose](https://www.gaoyuanqi.cn/docker-compose/#%E5%AE%89%E8%A3%85docker-compose)**

```sh
docker-compose up -d
```

#### 五、查看运行的容器

```sh
docker ps
```

应该看到有一个 **daledou** 容器：
```sh

CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS     NAMES
ab2c3ca911ea   daledou:v1   "pipenv run python3 …"   30 seconds ago   Up 28 seconds             daledou
```

#### 六、查看容器日志

```sh
docker logs daledou
```

如果大乐斗Cookie有效，应该看到以下信息：
```
2022-11-26 15:13:38.023 | INFO     | __main__:daledou_cookies:58 - 第 1 个大乐斗Cookie有效，脚本将在 13:01 和 20:01 运行...
...
```

#### 七、立即运行指定轮次脚本

进入 **daledou** 容器：
```sh
docker exec -it daledou /bin/bash
```

激活虚拟环境：
```sh
$ pipenv shell
```

运行脚本：
```sh
$ python local.py
```

然后按提示输入，`1` 表示第一轮，`2` 表示第二轮

#### 八、重启脚本

如果修改了一些文件（更换cookie可以不重启脚本），需要重启脚本以使配置生效：
```sh
docker restart daledou
```


## 脚本执行文档

```bash
https://www.gaoyuanqi.cn/python-daledou/#more
```


## QQ交流群（783035662）

![QQ交流群](QQ.jpg)
