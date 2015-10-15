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
            (r'/test', ledia.TestHandler),
            (r'/', ledia.HomeHandler),
            (r'/config', ledia.ConfigHandler),
            (r'/backup/?', ledia.BackupHandler),
            (r'/shop/(init|update)', ledia.ShopHandler),
            (r'/product/(\d+)', ledia.ProductHandler),
            (r'/media/(.+)', tornado.web.StaticFileHandler, {'path': 'media/'}),
            (r'/static/(.+)', tornado.web.StaticFileHandler, {'path': 'g:/lib/'}),
            (r'/staticw/(.+)', tornado.web.StaticFileHandler, {'path': 'g:/workspace/Web/'}),
        ]
        settings = {
            'debug': True,
            'autoreload': True,
            'template_path': 'template',
        }
        super().__init__(handlers, **settings)
        self.model = model

if __name__ == '__main__':
    Application().listen(8080)
    tornado.ioloop.IOLoop.current().start()
