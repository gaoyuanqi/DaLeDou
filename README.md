<h2>使用青龙面板在左上角切换到ql分支（已停止维护）</h2>


## 说明

脚本最适合的玩家：等级不低于50、战力越高越好、达人等级越高越好

乐斗等级战力不高的玩家使用脚本可能会有一些问题，建议手动提高等级战力后再使用


## Python版本

```
Python 3.11
```


## 快速开始

1、下载脚本
```sh
git clone https://github.com/gaoyuanqi/DaLeDou.git
```

2、在 `settings.py` 文件中添加大乐斗Cookie、pushplus微信通知

3、安装依赖
```sh
pip3 install -r requirements.txt
```

4、如果你第一次使用，需运行以下命令
```sh
python local.py 0
```

输出如下
```sh
2023-06-24 19:52:51.264 | SUCCESS  | daledou:main:82 -    123456：COOKIE有效
2023-06-24 19:52:51.264 | SUCCESS  | daledou:copy_yaml:60 - 成功创建配置文件：./config/123456.yaml
```

5、修改创建的 `./config/123456.yaml` 配置文件（大乐斗Cookie有效才会创建）

6、**13:05** 之后运行第一轮
```sh
python local.py 1
```

7、**20:01** 之后运行第二轮
```sh
python local.py 2
```

第一轮和第二轮时间间隔尽量长一些；时间不够优先运行第一轮，第一轮包括了绝大部分任务

要查看脚本会做哪些任务见：[文档](https://www.gaoyuanqi.cn/python-daledou/#more)


## Docker部署

1、构建镜像
```sh
docker-compose build
```

2、启动服务
```sh
docker-compose up -d
```

容器每天定时运行：
- 默认 `13:05` 运行第一轮
- 默认 `20:01` 运行第二轮


## 大乐斗cookie有效期

cookie有效期有多长取决于登录方式，不管哪种方式，通常都是在早上8点左右失效

**通过一键登录**

这种方式获得的cookie有效期最长，通常两天左右

**通过账号密码登录**

这种方式获得的cookie有效期很短，通常1小时左右

这种方式对需定时运行不太友好，所以脚本会每隔30分钟请求一次来延长cookie有效期，这样有效期也能达到两天
