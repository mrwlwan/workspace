# coding=utf8

import const
from . import base
import model
import sqlalchemy
import tornado.web
import requests
import re, json, os, sys, datetime
import itertools


class FetchHandler(base.BaseHandler, base.FetchHelper):
    """ 抓取外部数据. """
    def fetch_product(self, offer_id, data=None, raw=False):
        """ 抓取product数据. """
        data = data or self.fetch_offer_dict(offer_id)
        print('%s fetch!' % offer_id)
        product = dict(
            offer_id = offer_id,
            subject = data['subject'],
            img_url = data['imageList'][0]['originalImageURI'],
            code = data['productFeatureList'].get('货号'),
            brand = data['productFeatureList'].get('品牌'),
            pattern = data['productFeatureList'].get('图案'),
            fabric = data['productFeatureList'].get('面料名称'),
            fabric_content = data['productFeatureList'].get('主面料成分'),
            fabric_scale = data['productFeatureList'].get('主面料成分的含量'),
        )
        return raw and product or model.ProductModel(**product)

    def fetch_skus(self, offer_id=None, data=None, raw=False):
        """ 抓取sku数据. """
        data = data or self.fetch_offer_dict(offer_id)
        skus = []
        for sku in data['skuMap'] or []:
            skus.append(dict(
                color = sku.get('color'),
                size = sku.get('size'),
                book_count = sku.get('canBookCount'),
                sale_count = sku.get('saleCount'),
                price = sku.get('discountPrice', data.get('priceDisplay')),
            ))
        return raw and skus or [model.SkuModel(**sku) for sku in skus]


class ProductHandler(base.BaseHandler):
    def get(self, product_id):
        self.write(product_id)


class ShopHandler(FetchHandler):
    def initialize(self):
        super().initialize()
        self.today = datetime.date.today()

    def add_product(self, offer_id, data=None, commit=False):
        data = data or self.fetch_offer_dict(offer_id)
        if not data['productFeatureList'].get('货号'): # 非商品不录入
            print('%s not added!' %offer_id)
            return None
        product = self.fetch_product(offer_id, data=data)
        product.update_date = self.today
        product.skus = self.fetch_skus(data=data)
        product.update_sku_relative()
        product.update_last()
        self.db.add(product)
        self.save_img(self.thumb(product.img_url), offer_id)
        if commit: self.db.commit()
        print('%s added!' %offer_id)
        return product

    def update_product(self, product, data=None, commit=False):
        if not product.is_expiries(): # 更新时间限制
            print('%s not expired!' % product.offer_id)
            return 0
        data = data or self.fetch_offer_dict(product.offer_id)
        if not data['productFeatureList'].get('货号'): # 回收站处理
            product.status = '回收站'
            if commit: self.db.commit()
            print('%s droped!' % product.offer_id)
            return -1
        self.update_obj(product, self.fetch_product(product.offer_id, data=data, raw=True))
        self.delete_objs(product.skus)
        product.skus = self.fetch_skus(data=data)
        product.update_sku_relative()
        product.update_date = self.today
        if product.status=='回收站':
            product.status='上架'
            if commit: self.db.commit()
            print('%s added!' % product.offer_id)
            return 2
        if commit: self.db.commit()
        print('%s updated!' % product.offer_id)
        return result

    def init(self):
        """ 初始化数据库. """
        if self.db.query(model.ProductModel).count(): return self.write('Delete database and try again!') #只作首次运行
        commit_count_temp = 0
        for offer_id in self.fetch_offer_list():
            self.add_product(offer_id)
            commit_count_temp += 1
            if commit_count_temp % 20 == 0: self.db.commit()
        self.db.commit()
        self.write('Init')

    def update(self):
        """ 抓取数据更新. """
        commit_count_temp = 0
        new_products = []
        drop_products = []
        products_dict = dict(self.db.query(model.ProductModel.offer_id, model.ProductModel).all())
        for offer_id in self.fetch_offer_list():
            product = products_dict.get(offer_id)
            if not product:
                product = self.add_product(offer_id)
                if product: new_products.append(product)
            else:
                products_dict.pop(offer_id)
                temp = self.update_product(product)
                if temp==0:
                    continue
                elif temp==-1:
                    drop_products.append(product)
                elif temp==2:
                    new_products.append(product)
            commit_count_temp += 1
            if commit_count_temp % 20 == 0: self.db.commit()
        for product in products_dict.values():
            temp = self.update_product(product)
            if temp==0:
                continue
            elif temp==-1:
                drop_products.append(product)
            elif temp==2:
                new_products.append(product)
            commit_count_temp += 1
            if commit_count_temp % 20 == 0: self.db.commit()
        self.db.commit()
        self.write('Update done! %d found! %d droped!' % (len(new_products), len(drop_products)))

    def get(self, action):
        getattr(self, action)()


class HomeHandler(base.BaseHandler):
    def get(self):
        filter_certains = {}
        for arg in ('category', 'sku_status', 'status'):
            value = self.get_argument(arg, '全部')
            if value!='全部': filter_certains[arg] = value
        data = self.db.query(model.ProductModel).filter_by(**filter_certains)
        keywords = self.get_argument('keywords', None)
        query_columns = self.get_argument('query_columns', None)
        query_columns_dict = dict(const.query_columns_dict)
        if keywords and query_columns and query_columns in query_columns_dict:
            columns = query_columns_dict.get(query_columns)
            keywords = keywords.lower()
            or_keywords = re.split(r' +', keywords)
            if len(or_keywords)>1:
                keywords = or_keywords
                method = sqlalchemy.or_
            else:
                keywords = [item.replace('\\+', '+') for item in re.split(r'(?<!\\)\++', keywords)]
                method = sqlalchemy.and_
            data = data.filter(method(*[getattr(model.ProductModel, columns).like('%'+keyword+'%') for keyword in keywords]))
            # 多列搜索, 个人暂不用
            #keywords = re.split(r' +', keywords.lower())
            #query_columns = self.get_argument('query_columns', '全文')
            #query_columns_dict = dict(const.query_columns_list)
            #if query_columns=='全文':
                #query_columns = query_columns_dict.values()
            #elif query_columns in query_columns_dict:
                #query_columns = [query_columns_dict.get(query_columns)]
            #else:
                #query_columns = []
            #data = self.multi_columns_query(data, model.ProductModel, query_columns, keywords)
        sort_columns = self.get_argument('sort_columns', None)
        sort_columns_dict = dict(const.sort_columns_dict)
        if sort_columns and sort_columns in sort_columns_dict:
            columns = sort_columns_dict.get(sort_columns)
            desc = self.get_argument('desc', None)
            columns_obj = getattr(model.ProductModel, columns)
            data = data.order_by(columns_obj.desc() if desc else columns_obj)
        self.show_page(data, 'ledia/index.html', 20)

