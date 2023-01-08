import requests


def login(cookie: str) -> bool:
    '''
    验证大乐斗cookie是否有效
    '''
    try:
        url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        for _ in range(3):
            res = requests.get(url, headers=headers)
            res.encoding = 'utf-8'
            if '商店' in res.text:
                return True
    except Exception:
        pass
