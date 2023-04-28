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
# 大乐斗cookie，比如 'RK=xxx; ptcz=xxx; uin=xxx; skey=xxx'
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


### 使用Docker部署运行脚本（适用于有云服务器）

**1、安装Docker**

```
https://www.gaoyuanqi.cn/docker-install/
```

**2、拉取镜像**

```sh
docker pull python:3.11
```

**3、构建镜像**

注意 `.` 不要省略：
```sh
docker build -t daledou:v1 .
```

**4、启动容器**

如果是 `Linux` 系统需安装 **[docker-compose](https://www.gaoyuanqi.cn/docker-compose/#%E5%AE%89%E8%A3%85docker-compose)**

```sh
docker-compose up -d
```

**5、查看运行的容器**

```sh
docker ps
```

应该看到有一个 `daledou` 容器：
```sh

CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS     NAMES
ab2c3ca911ea   daledou:v1   "pipenv run python3 …"   30 seconds ago   Up 28 seconds             daledou
```

**6、查看容器日志**

```sh
docker logs daledou
```

假定大乐斗cookie有效，首次运行应该看到以下信息：
```
2023-04-13 19:15:04.025 | SUCCESS  | src.daledou.daledou:copy_yaml:67 - 脚本创建了一个配置文件：./config/xxx.yaml
2023-04-13 19:15:04.029 | SUCCESS  | src.daledou.daledou:main:91 -    xxx：将在 13:01 和 20:01 定时运行...
```

**7、手动运行指定轮次脚本**

```sh
docker exec -it daledou pipenv run python local.py
```

按提示输入，`1` 表示第一轮，`2` 表示第二轮

**8、重启脚本**

如果修改了一些文件（更换cookie可以不重启脚本），就需要重启脚本以使配置生效：
```sh
docker restart daledou
```


## yaml配置（必须）

考虑到每位玩家的战力存在差别，有些任务高战力能过关，而低战力不能，因此创建yaml文件来为每个账号自定义配置

当你前面运行脚本后（`local.py`、`main.py` 之一），会自动为当前有效cookie在 `./config` 目录下创建以 `QQ` 命名的yaml文件，比如 `123456.yaml`，其内容与 `daledou.yaml` 完全一致

如果 `123456.yaml` 文件已存在则不做任何操作，这意味着当 `daledou.yaml` 有变化时，你需要手动更新 `123456.yaml`

你需要为这个 `123456.yaml` 进行配置：
- `十二宫`: 选择扫荡关卡，默认扫荡 `双鱼宫`
- `幻境`: 选择场景，默认乐斗 `鹅王的试炼`
- `深渊之潮`: `深渊秘境` 副本选择，默认选择 `曲镜空洞`
- `竞技场`: 商店兑换，默认兑换10个 `河洛图书`
- `门派邀请赛`: 商店兑换，默认兑换10个 `炼气石`
- `帮派黄金联赛`: 是否参加防守、参战，默认是
- `武林盟主`: 分站赛报名赛场选择，默认报名 `黄金赛场`
- `历练`: 选择场景，默认乐斗掉落佣兵碎片BOSS的所有场景
- `帮派商会`: 交易、兑换物品
- `背包`: 指定物品id将被使用至多70次
- `活动`: `企鹅吉利兑` 材料兑换
- `神匠坊`: 用于指定符石分解，默认分解 `I类`
