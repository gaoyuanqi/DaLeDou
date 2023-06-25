## 下载脚本

通过git下载：
```sh
git clone https://github.com/gaoyuanqi/DaLeDou.git
```


## settings.py 配置

**1、添加大乐斗cookie（必须，支持多账号）**

抓包以下链接：
```
https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index&channel=0
```

将复制的大乐斗Cookie直接填入：
```python
# 大乐斗cookie，至少包含 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx'
# 支持多账号，每行对应一个账号
DALEDOU_ACCOUNT = [
    # 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx',
    # 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx',
]
```

**2、添加pushplus微信通知（可选）**

微信公众号 `pushplus` > `pushplus` > `pushplus官网` > `一对一推送` > `一键复制`

将token添加到：
```python
PUSHPLUS_TOKEN = ''
```


## 运行脚本

>   确保在 `DaLeDou` 目录下


### 本地运行

**1、安装依赖**

```sh
pip3 install -r requirements.txt
```

如果你熟悉 `pipenv`，可以通过下面命令安装：
```sh
pipenv install
```

**2、手动运行指定轮次脚本**

```sh
python local.py
```

按提示输入，`1` 表示第一轮，`2` 表示第二轮


### Docker部署运行

**1、拉取镜像**

```sh
docker pull python:3.11
```

**2、构建镜像**

注意 `.` 不要省略：
```sh
docker build -t daledou:v1 .
```

**3、启动容器**

```sh
docker-compose up -d
```

**4、查看容器日志**

```sh
docker logs daledou
```

假定大乐斗cookie有效，第一次运行应该看到以下信息：
```
2023-06-24 19:52:51.264 | SUCCESS  | daledou:main:82 -    xxxx：COOKIE有效
2023-06-24 19:52:51.264 | SUCCESS  | daledou:copy_yaml:60 - 脚本创建了一个配置文件：./config/2278612931.yaml
```


## yaml配置（必须）

考虑到每位玩家的战力存在差别，有些任务高战力能过关，而低战力不能，因此创建yaml文件来为每个账号自定义配置

当你前面运行脚本后（`local.py`、`main.py` 文件之一），如果cookie有效，会自动在 `./config` 目录下创建以 `QQ` 命名的yaml文件，比如 `123456.yaml`，其内容与 `daledou.yaml` 完全一致

如果 `123456.yaml` 文件已存在则不做任何操作，这意味着当 `daledou.yaml` 有变化时，你需要手动更新 `123456.yaml`
