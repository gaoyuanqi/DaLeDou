'''
假设两个账号的大乐斗Cookie：
    RK=aa; ptcz=bb; uin=o123456; skey=@cc
    RK=AA; ptcz=BB; uin=o2222; skey=@CC
将 RK、ptcz、uin、skey键值依次填入 DALEDOU_COOKIE

支持多账号，一个字典对应一个号
最好等所有Cookie失效后再更换
'''
DALEDOU_COOKIE = [
    {
        'RK': 'aa',
        'ptcz': 'bb',
        'uin': 'o123456',
        'skey': '@cc'
    },
    {
        'RK': 'AA',
        'ptcz': 'BB',
        'uin': 'o2222',
        'skey': '@CC',
    }
]

# pushplus一对一推送token
PUSHPLUS_TOKEN = 'token'
