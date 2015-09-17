# coding=utf8

""" 生成手机图片, 只作缩小. """

from PIL import Image, ImageEnhance
import os, sys

# 执行转换的文件后缀
EXTS = set(['.jpg', '.jpeg'])
# 调整宽度
WIDTH = 600
#WIDTH = 480
# JPEG quality
QUALITY = 87
# 保存目录
THUMB_DIR = '模特细节图_手机'
# 覆盖存在
OVERRIDE = False



def list_images(path='.'):
    for f in os.listdir(path):
        if os.path.isfile(f) and os.path.splitext(f)[1].lower() in EXTS:
            yield f

def process(f):
    target = os.path.join(THUMB_DIR, f)
    if not OVERRIDE and os.path.exists(target):
        print('Skip')
        return
    image = Image.open(f)
    if(image.size[0]<=WIDTH):
        size = image.size
    else:
        size = (WIDTH, int(image.size[1]*WIDTH/image.size[0]))
    image.thumbnail(size, 1)
    image.save(os.path.join(THUMB_DIR, f), quality=QUALITY)

def run():
    if not os.path.exists(THUMB_DIR):
        os.mkdir(THUMB_DIR)
    for f in list_images():
        print(f)
        process(f)
    print('Done!')

if __name__ == '__main__':
    run()
