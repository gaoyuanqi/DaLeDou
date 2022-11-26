import yaml
from loguru import logger


def read_yaml(keyname, filename):
    '''
    读取 config 配置文件
    '''
    try:
        with open(f'./missions/daledou/config/{filename}', 'r', encoding='utf-8') as fp:
            users = yaml.safe_load(fp)
        return users[keyname]
    except Exception as e:
        logger.error(f'【config】：读取错误 {e}')


def write_yaml(filename, dict):
    '''
    写入 config 配置文件
    '''
    try:
        with open(f'./missions/daledou/config/{filename}', 'w', encoding='utf-8') as fp:
            yaml.dump(dict, fp)
    except Exception as e:
        logger.error(f'【config】：写入错误 {e}')
