# coding=utf8

import model
import app.ledia as ledia
import tornado.ioloop
import tornado.web
import os, sys

# 将当前目录加入 sys.path
sys.path.insert(0, os.path.abspath('.'))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', ledia.HomeHandler),
            #(r'/init', ledia.InitHandler),
        ]
        settings = {
            'debug': True,
            'autoreload': True,
            'template_path': 'template',
            'static_path': 'media',
            'static_url_prefix': '/media/',
        }
        super().__init__(handlers, **settings)
        self.model = model

if __name__ == '__main__':
    Application().listen(8080)
    tornado.ioloop.IOLoop.current().start()
