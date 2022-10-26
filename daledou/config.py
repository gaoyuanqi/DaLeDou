import yaml
from loguru import logger


def read_yaml(keyname, filename):
    '''
    读取 config 配置文件
    '''
    try:
        with open(f'./config/{filename}', 'r', encoding='utf-8') as fp:
            users = yaml.safe_load(fp)
        return users[keyname]
    except Exception as e:
        logger.error(e)
