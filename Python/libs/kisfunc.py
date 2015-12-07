# coding=utf8

import functools


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
