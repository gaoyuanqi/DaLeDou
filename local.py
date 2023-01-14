from src.daledou._set import _daledouone, _daledoutwo


def main():
    '''
    1 表示第一轮
    2 表示第二轮
    '''
    lunci = input('输入1或2选择执行轮次：')
    if lunci == '1':
        _daledouone()
    elif lunci == '2':
        _daledoutwo()


if __name__ == '__main__':
    main()
