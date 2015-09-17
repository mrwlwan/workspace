# coding=utf8

from . import base
import model
import tornado.web
import requests
import re, json, os, sys, datetime
import itertools

class HomeHandler(base.BaseHandler):
    def get(self):
        page = int(self.get_argument('page', 1))
        if page<1:
            return
        start_index = (page-1)*20
        data=self.db.query(model.ProductModel)
        count = data.count()
        if page>count:
            return
        self.render('ledia/index.html', data=data.offset(start_index).limit(20), page=page, max_page=count//20+1, start_index=start_index+1, count=count)


class InitHandler(base.BaseHandler, base.FetchHelper):
    def get(self):
        self.write('Init')
        commit_count_temp = 0
        for offer_id, img_url in self.get_offer_list():
            print('********************************************************')
            print(offer_id)
            print(img_url)
            data = self.get_offer_dict(offer_id)
            if not data['productFeatureList'].get('货号'):
                continue
            data['offer_id'] = offer_id
            print(data)
            product = self.model.ProductModel(
                offer_id = offer_id,
                subject = data['subject'],
                code = data['productFeatureList'].get('货号'),
                brand = data['productFeatureList'].get('品牌'),
                pattern = data['productFeatureList'].get('图案'),
                fabric = data['productFeatureList'].get('面料名称'),
                fabric_content = data['productFeatureList'].get('主面料成分'),
                fabric_scale = data['productFeatureList'].get('主面料成分的含量')
            )
            skus = []
            today = datetime.date.today()
            for sku in data['skuMap'] or []:
                skus.append(self.model.SkuModel(
                    color = sku.get('color'),
                    size = sku.get('size'),
                    book_count = sku.get('canBookCount'),
                    sale_count = sku.get('saleCount'),
                    price = sku.get('discountPrice', data.get('priceDisplay')),
                    last_book_count = sku.get('canBookCount'),
                    last_sale_count = sku.get('saleCount'),
                    last_price = sku.get('discountPrice', data.get('priceDisplay')),
                    last_update_date = today
                ))
            product.skus = skus
            self.db.add(product)
            self.save_img(img_url, offer_id)
            commit_count_temp += 1
            if commit_count_temp % 20 == 0:
                self.db.commit()
        self.db.commit()




