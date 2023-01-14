import requests

from settings import PUSHPLUS_TOKEN


def pushplus(title, message_list):
    '''
    '\n'.join(['aa', 'bb', 'cc'])
    >>>
    aa
    bb
    cc
    '''
    url = 'http://www.pushplus.plus/send/'
    content = '\n'.join(message_list)
    data = {
        'token': PUSHPLUS_TOKEN,
        'title': title,
        'content': content,
    }
    res = requests.post(url, data=data)
    json = res.json()
    return json.get('data')

# pushplus('22', '33')
# {'code': 999, 'msg': '无效的用户token', 'data': None}
# {'code': 999, 'msg': '请勿频繁推送相同内容', 'data': None}
# {'code': 200, 'msg': '请求成功', 'data': 'edcec621af19407383652b6547277fd0', 'count': None}
