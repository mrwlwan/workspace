# coding=utf8

""" 原图加水印, 再缩小处理. """

from PIL import Image, ImageEnhance
import os, sys

# 执行转换的文件后缀
EXTS = set(['.jpg', '.jpeg'])
# 调整宽度
WIDTH = 750
WIDTH_M = 600
# JPEG quality
QUALITY = 87
QUALITY_M = 87
# 保存目录
THUMB_DIR = '模特细节图'
THUMB_DIR_M = '手机模特细节图'
# 覆盖存在
OVERRIDE = False
# 水印图片
MARKIMAGE = 'g:/百度云/淘宝/店铺装修/ledia_logo_水印.png'
# 透明度
OPACITY = 0.5
# 水印Padding
PADDING = 10



def list_images(path='.'):
    for f in os.listdir(path):
        if os.path.isfile(f) and os.path.splitext(f)[1].lower() in EXTS:
            yield f

def get_markimage(opacity=None):
    opacity = opacity or OPACITY
    image = Image.open(MARKIMAGE)
    if image.mode != 'RGBA':
        image.convert('RGBA')
    alpha = ImageEnhance.Brightness(image.split()[3]).enhance(opacity)
    image.putalpha(alpha)
    return image


def water_mark(image, markimage):
    if image.mode != 'RGBA':
        image.convert('RGBA')
    layer = Image.new('RGBA', image.size, (0,0,0,0))
    half_width = int(image.size[0]/3)
    if markimage.size[0] > half_width:
        markimage = markimage.resize((half_width, int(markimage.size[1]*half_width/markimage.size[0])), 1)
    position = (PADDING, image.size[1]-markimage.size[1]-PADDING)

    layer.paste(markimage,position)
    return Image.composite(layer, image, layer)

def process(f, markimage, thumb_dir, max_width, quality):
        target = os.path.join(thumb_dir, f)
        if not OVERRIDE and os.path.exists(target):
            print('Skip')
            return
        image = Image.open(f)
        if(image.size[0]<=max_width):
            size = image.size
        else:
            size = (max_width, int(image.size[1]*max_width/image.size[0]))
        image.thumbnail(size, 1)
        image = water_mark(image, markimage)
        image.save(target, quality=quality)

def run(args):
    if not args:
        return
    #for thumb_dir in (THUMB_DIR, THUMB_DIR_M):
        #if not os.path.exists(thumb_dir):
            #os.mkdir(thumb_dir)
    for arg in args:
        if not os.path.exists(arg[0]):
            os.mkdir(arg[0])
    markimage = get_markimage()
    for f in list_images():
        print(f)
        for thumb_dir, max_width, quality in [(THUMB_DIR, WIDTH, QUALITY), (THUMB_DIR_M, WIDTH_M, QUALITY_M)]:
            process(f, markimage, thumb_dir, max_width, quality)
    print('Done!')

if __name__ == '__main__':
    ARGS = {
        '-p': (THUMB_DIR, WIDTH, QUALITY),
        '-m': (THUMB_DIR_M, WIDTH_M, QUALITY_M),
    }
    if len(sys.argv)>1:
        run(ARGS.get(sys.argv[1], []))
    else:
        run(ARGS.values())
