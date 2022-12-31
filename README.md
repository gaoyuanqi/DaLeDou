## 说明

因为等级或者战力差异，脚本不一定适合所有人，作者目前等级 **133**


## 脚本运行时间

脚本定时工作时间：
- 第一轮 **13:01** 运行 **daledouone.py** 模块，耗时 **300~400** 多秒
- 第二轮 **20:01** 运行 **daledoutwo.py** 模块，耗时 **50~100** 多秒

可能会遇到某些情况，比如Cookie没来得及更新或者其他原因错过脚本运行时间，那么你可以在本地立即运行脚本

首先安装依赖：
```bash
pip3 install -r requirements.txt
```

如果你熟悉 **pipenv** ，也可以通过以下命令安装：
```bash
pipenv install
```

然后找到项目目录下的 **local.py** 模块选择执行的轮次：

```python
@repeat(every(30).minutes)
def job():
    # 第一轮
    daledou_one()
    
    # 第二轮
    # daledou_two()
```


## 大乐斗Cookie有效期

脚本每隔30分钟（定时由 **Schedule** 库实现）请求一次来保持大乐斗Cookie活跃性，从而使Cookie有效期最长可以超过48小时

当天更换Cookie，第二天依然有效，但会在第三天早上8点整左右失效

停止脚本超过一个多小时，Cookie也会失效


## 脚本执行文档

```bash
https://www.gaoyuanqi.cn/python-daledou/#more
```


## 环境

```
Python 3.10
```


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
DALEDOU_COOKIE = [
    'RX=xxx',
    'RK=xxx',
]
```

### 添加pushplus微信通知（可选）

微信公众号 **pushplus** > **pushplus** > **pushplus官网** > **一对一推送** > **一键复制**

将token添加到：
```bash
PUSHPLUS_TOKEN = 'token'
```


## 自定义任务

**./missions/config** 目录下有很多 **yaml** 后缀名的文件，根据你自己的实际情况（等级或战力）修改相关配置

比如你可以修改 **十二宫.yaml** 文件来决定扫荡某个关卡


## 部署运行（Docker-Compose）

拉取镜像：
```bash
docker pull python:3.10
```

构建镜像（在有 **Dockerfile** 文件的目录下）：
```bash
docker build -t daledou:v1 .
```

启动容器：
```bash
docker-compose up -d
```

**Linux** 系统需安装 **[docker-compose](https://www.gaoyuanqi.cn/docker-compose/#%E5%AE%89%E8%A3%85docker-compose)**

查看容器：
```bash
docker ps
```

应该看到一个名为 **daledou** 的容器

查看容器日志：
```bash
docker logs daledou
```

如果大乐斗Cookie有效，应该看到以下信息：
```
2022-11-26 15:13:38.023 | INFO     | __main__:daledou_cookies:58 - 第 1 个大乐斗Cookie有效，脚本将在指定时间运行...
2022-11-26 15:13:38.823 | INFO     | __main__:daledou_cookies:58 - 第 2 个大乐斗Cookie有效，脚本将在指定时间运行...
...
```


## 重启脚本

如果修改了一些文件（更换cookie可以不重启脚本），需要重启脚本以使配置生效：
```bash
docker restart daledou
```
