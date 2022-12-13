## 概述

**Requests** 是核心技术，它将大乐斗Cookie添加到 **Session**，然后使用 **Session** 完成后续请求

**Sessions** 还会每隔30分钟（定时由 **Schedule** 库实现）请求一次来保持大乐斗Cookie活跃性，从而使Cookie有效期最长可以超过48小时

当天更换Cookie，第二天依然有效，但会在第三天早上8点02~09分左右失效（一般在这之后更换Cookie）

停止脚本超过一个多小时，Cookie也会失效


## 说明

因为等级或者战力差异，脚本不一定适合所有人，作者目前等级 **133**

脚本定时工作时间：
- 第一轮 **13:01** 运行 **daledouone.py** 模块，耗时 **200~300** 多秒
- 第二轮 **20:01** 运行 **daledoutwo.py** 模块，耗时 **50~100** 多秒

脚本运行前需在大乐斗最下面 `武林` -> `设置` -> `乐斗助手` 开启三项：
- 开启自动使用体力药水（脚本可以自动开启）
- 开启背包里的提前按钮（脚本可以自动开启）
- 开启自动使用活力药水（可选）


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

假设在开发者工具中获取的大乐斗Cookie：
```
RK=aa; ptcz=bb; uin=o123456; skey=@cc
```

另外一个大乐斗Cookie：
```
RK=AA; ptcz=BB; uin=o2222; skey=@CC
```

从上面提取出 RK、ptcz、uin、skey键值并依次填入 DALEDOU_COOKIE：
```python
# 大乐斗Cookie，不要改动键值顺序
# 支持多账号，一个字典对应一个号
DALEDOU_COOKIE = [
    {
        'RK': 'aa',
        'ptcz': 'bb',
        'uin': 'o123456',
        'skey': '@cc'
    },
    {
        'RK': 'AA',
        'ptcz': 'BB',
        'uin': 'o2222',
        'skey': '@CC',
    }
]
```


### 添加pushplus微信通知（可选）

微信公众号 **pushplus** > **pushplus** > **pushplus官网** > **一对一推送** > **一键复制**

将token添加到：
```bash
PUSHPLUS_TOKEN = 'token'
```


## 部署运行（Docker）

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

如果大乐斗Cookies有效，应该看到以下信息：
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


## 自定义任务配置（yaml）

因每人等级或战力不同，每人能做的任务也不一样，因此你可能需要自定义一些任务

**./missions/config** 目录下有很多 **yaml** 后缀名的文件，根据你自己的实际情况修改相关配置

比如你可以修改 **十二宫.yaml** 文件来决定哪个关卡


## 文档

脚本执行的任务：
```
https://www.gaoyuanqi.cn/python-daledou
```
