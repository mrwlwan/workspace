# coding=utf8

import functools, datetime


def coroutine(func):
    """ 用于协和的装饰器. """
    @functools.wraps
    def newfunc(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return newfunc

def until_success(func):
    """ 直至不出现异常. 常用于网络不稳定. """
    def newfunc(*args, **kwargs):
        while 1:
            try:
                return func(*args, **kwargs)
            except: pass
    return newfunc

def time_print(*args, **kwargs):
    """ 显示当前时间的 print. """
    print(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), end='')
    print(*args, **kwargs)
