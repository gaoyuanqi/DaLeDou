# 保持pip版本为最新版、安装pipenv、创建虚拟环境及安装第三方库
python3 -m pip install --upgrade pip -i https://pypi.mirrors.ustc.edu.cn/simple/ \
&& pip3 install pipenv -i https://pypi.mirrors.ustc.edu.cn/simple/ \
&& pipenv install
