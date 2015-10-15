# coding=utf8

import const
from . import base
import model
import sqlalchemy
import tornado.web
import requests
import re, json, os, sys, datetime, pickle
import itertools


class FetchDataHelper(base.FetchHelper):
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


class ProductHandler(base.BaseHelper):
    def get(self, product_id):
        product = self.db.query(model.ProductModel).filter_by(id=product_id).first()
        product and self.render('ledia/product.html', product=product)

    def post(self, product_id):
        response = {'error': '', 'data': {}}
        for product in self.db.query(model.ProductModel).filter_by(id=product_id):
            for key in self.request.arguments:
                value = self.get_argument(key)
                setattr(product, key, value)
                self.db.commit()
                response['data'][key] = value
        return self.write(response)

    def delete(self, product_id):
        for product in self.db.query(model.ProductModel).filter_by(id=product_id):
            print(product)
            self.db.delete(product)
        self.db.commit()
        os.remove(os.path.join('media/img/product/', product.offer_id, '.jpg'))
        self.write({'error': '', 'data': product_id})


class ShopHandler(FetchDataHelper):
    def initialize(self):
        super().initialize()
        self.today = datetime.date.today()
        self.config = self.db.query(model.ConfigModel).first()

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
        if not product.is_expiries(self.config.expiry_days): # 更新时间限制
            print('%s not expired!' % product.offer_id)
            return 0
        data = data or self.fetch_offer_dict(product.offer_id)
        if not data['productFeatureList'].get('货号'): # 回收站处理
            product.status = '回收站'
            if commit: self.db.commit()
            print('%s droped!' % product.offer_id)
            return -1
        old_img_url = product.img_url
        self.update_obj(product, self.fetch_product(product.offer_id, data=data, raw=True))
        self.delete_objs(product.skus)
        new_img_url = product.img_url
        product.skus = self.fetch_skus(data=data)
        product.update_sku_relative()
        product.update_date = self.today
        if new_img_url!=old_img_url: self.save_img(self.thumb(new_img_url), product.offer_id)
        if product.status=='回收站':
            product.status='上架'
            if commit: self.db.commit()
            print('%s added!' % product.offer_id)
            return 2
        if commit: self.db.commit()
        print('%s updated!' % product.offer_id)
        return 1

    def init(self):
        """ 初始化数据库. """
        if self.db.query(model.ProductModel).count(): return self.write('请删除数据库后再试!') #只作首次运行
        commit_count_temp = 0
        for offer_id in self.fetch_offer_list():
            self.add_product(offer_id)
            commit_count_temp += 1
            if commit_count_temp % 20 == 0: self.db.commit()
        self.config.update_date = self.today
        self.db.commit()
        #self.write('Init')
        self.redirect('/')

    def update(self):
        """ 抓取数据更新. """
        if not self.config.is_expiries():
            return self.write('上次更新时间是 %s, %d天内只能更新一次.' % (self.config.update_date, self.config.expiry_days))
        commit_count_temp = 0
        new_products = []
        drop_products = []
        products_dict = dict(self.db.query(model.ProductModel.offer_id, model.ProductModel).all())
        for offer_id in self.fetch_offer_list():
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(offer_id)
            product = products_dict.get(offer_id)
            if not product:
                product = self.add_product(offer_id)
                if not product: continue
                new_products.append(product)
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
        self.config.update_date = self.today
        self.db.commit()
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('Update done! %d found! %d droped!' % (len(new_products), len(drop_products)))
        self.render('ledia/update.html', new_products=new_products, drop_products=drop_products)

    def get(self, action):
        getattr(self, action)()


class HomeHandler(base.BaseHelper):
    def initialize(self):
        super().initialize()
        self.config = self.db.query(model.ConfigModel).first()

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
        else:
            data = data.order_by(model.ProductModel.id.desc())
        self.show_page('ledia/index.html', data, self.config.per_page)


class ConfigHandler(base.BaseHelper):
    def get(self):
        config = self.db.query(model.ConfigModel).first()
        self.render('ledia/config.html', config=config or {})

    def post(self):
        config_id = self.get_argument('id', None)
        config = self.db.query(model.ConfigModel).first() if config_id else model.ConfigModel()
        for key in self.request.arguments:
            if key!='id' and hasattr(config, key):
                value = self.get_argument(key, None)
                if key=='update_date' and value: value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                setattr(config, key, value or None)
        not config_id and self.db.add(config)
        self.db.commit()
        self.redirect('/config')

class BackupHandler(base.BaseHelper):
    def get(self):
        self.render('ledia/backup.html', backups=os.listdir('media/backup'))

    def post(self):
        print('create')
        backup = self.get_argument('backup')
        if backup not in ('configs', 'products'):
            return self.write({'error': True})
        target = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H%M%S%f-'+backup)
        with open('media/backup/'+target+'.bak', 'wb') as f:
            backup_model = {'configs': model.ConfigModel, 'products': model.ProductModel}.get(backup)
            columns = ('category', 'status', 'remarks') if backup=='products' else None
            backup_dict = {}
            for row in self.db.query(backup_model):
                backup_dict[row.id] = self.model2dict(row, columns, ['id'])
            pickle.dump({backup: backup_dict}, f)
            return self.write({'error': None, 'data': target})
        return self.write({'error': True})

    def put(self):
        print('import')
        target = self.get_argument('backup', None)
        if not target: return self.write({'error': True})
        with open('media/backup/'+target+'.bak', 'rb') as f:
            backup_dicts = pickle.load(f)
            backup_models= {'configs': model.ConfigModel, 'products': model.ProductModel}
            for backup in backup_dicts:
                backup_dict = backup_dicts.get(backup)
                backup_model = backup_models.get(backup)
                for row in self.db.query(backup_model):
                    for key, value in backup_dict.get(row.id, {}).items():
                        setattr(row, key, value)
            self.db.commit()
        self.write({'error': None})

    def delete(self):
        print('delete')
        target = self.get_argument('backup', None)
        target = target and 'media/backup/' + target +'.bak'
        print(target)
        if target and os.path.exists(target):
            os.remove(target)
        self.write({'error': None})


class TestHandler(base.BaseHelper):
    def get(self):
        print('********************************')
        print('test')
        self.write('test')
        self.db.query(model.ConfigModel).first().update_date = datetime.date.today()
        self.db.commit()
