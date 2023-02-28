## 使用教程

>   始终在 `DaLeDou` 目录下执行


### 本地使用教程

**一、安装依赖**

```sh
pip3 install -r requirements.txt
```

如果你熟悉 `pipenv`，可以通过下面命令安装：
```sh
pipenv install
```

**二、立即运行指定轮次脚本**

```sh
python local.py
```

按提示输入，`1` 表示第一轮，`2` 表示第二轮


### Docker使用教程

**一、安装Docker**

```
https://www.gaoyuanqi.cn/docker-install/
```

**二、拉取镜像**

```sh
docker pull python:3.10
```

**三、构建镜像**

注意 `.` 不要省略：
```sh
docker build -t daledou:v1 .
```

**四、启动容器**

如果是 `Linux` 系统需安装 **[docker-compose](https://www.gaoyuanqi.cn/docker-compose/#%E5%AE%89%E8%A3%85docker-compose)**

```sh
docker-compose up -d
```

**五、查看运行的容器**

```sh
docker ps
```

应该看到有一个 `daledou` 容器：
```sh

CONTAINER ID   IMAGE        COMMAND                  CREATED          STATUS          PORTS     NAMES
ab2c3ca911ea   daledou:v1   "pipenv run python3 …"   30 seconds ago   Up 28 seconds             daledou
```

**六、查看容器日志**

```sh
docker logs daledou
```

如果大乐斗cookie有效，应该看到以下信息：
```
2023-02-12 19:55:02.586 | INFO     | src.daledou._set:daledou_timing:21 - xxxx 将在 13:01 和 20:01 运行...
```

**七、立即运行指定轮次脚本**

```sh
docker exec -it daledou pipenv run python local.py
```

按提示输入，`1` 表示第一轮，`2` 表示第二轮

**八、重启脚本**

如果修改了一些文件（更换cookie可以不重启脚本），就需要重启脚本以使配置生效：
```sh
docker restart daledou
```
