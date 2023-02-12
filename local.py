from src.daledou._run import daledou_one, daledou_two


def main():
    '''
    1 表示第一轮
    2 表示第二轮
    '''
    lunci = input('输入1或2选择执行轮次：')
    if lunci == '1':
        daledou_one()
    elif lunci == '2':
        daledou_two()


if __name__ == '__main__':
    main()
