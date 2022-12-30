import requests


def session(cookies: dict) -> object | None:
    url = 'https://dld.qzapp.z.qq.com/qpet/cgi-bin/phonepk?cmd=index'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    for _ in range(5):
        with requests.session() as session:
            requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
        res = session.get(url, headers=headers)
        res.encoding = 'utf-8'
        if '商店' in res.text:
            return session
