# coding=utf8

from sqlalchemy import or_
import tornado.web
import requests
import re, json, os

class BaseHandler(tornado.web.RequestHandler):
    #_cache_query_all = {}

    def initialize(self):
        self.model = self.application.model
        self.db = self.application.model.session

    def on_finish(self):
        self.db.close()

    def update_obj(self, obj, data, commit=False):
        for key in data:
            hasattr(obj, key) and setattr(obj, key, data.get(key))
        commit and self.db.commit()

    def delete_objs(self, objs, commit=False):
        for obj in objs:
            self.db.delete(obj)
        commit and self.db.commit()

    #def cache_query_all(self, model, certain={}):
        #if model in self._cache_query_all:
            #cache_certain = self._cache_query_all[model]['certain']
            #if len(certain)==len(cache_certain):
                #dissimilar = 0
                #for key in certain:
                    #if key not in cache_certain or certain[key]!=cache_certain[key]: dissimilar+=1
                #if not dissimilar: return self._cache_query_all[model]['data']
        #data = self.db.query(model).filter_by(**certain).all()
        #self._cache_query_all[model] = {'certain': certain, 'data': data}
        #print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>create')
        #return data

    #def clear_cache_query(self, models=[]):
        #if models:
            #for model in models:
                #if model in self._cache_query: del self._cache_query[model]
        #else:
            #self._cache_query.clear()

    def multi_columns_query(self, query, model, columns, keywords):
        if columns and keywords:
            keywords = ['%'+keyword+'%' for keyword in keywords]
            keyword_certains = []
            for keyword in keywords:
                keyword_certains.append(or_(*[getattr(model, column).like(keyword) for column in columns]))
            return query.filter(*keyword_certains)
        return query

    def show_page(self, template, query, per_page, *args, **kwargs):
        page = int(self.get_argument('page', 1))
        if page<1:
            return
        start_index = (page-1)*per_page
        count = query.count()
        if count and page>count:
            return
        self.render(template, *args, data=query.offset(start_index).limit(per_page), page=page, max_page=count//per_page+1, start_index=start_index+1, count=count, **kwargs)


class FetchHelper:
    LIST_INDEX_URL = 'http://benf6.1688.com/page/offerlist.htm'
    LIST_URL = 'http://benf6.1688.com/page/offerlist.htm?showType=catalog&tradenumFilter=false&sampleFilter=false&mixFilter=false&privateFilter=false&mobileOfferFilter=%24mobileOfferFilter&groupFilter=false&sortType=timedown&pageNum={page}'
    PRODUCT_URL = 'http://m.1688.com/offer/{offer_id}.html'
    MAX_PAGE_RE = re.compile(r'<li>共<em class="page-count">(\d+)', re.S)
    PRODUCT_RE = re.compile(r'<a href="http://detail.1688.com/offer/([^\.]+)[^>]+>\s+<img src="[^"]+" alt="[^"]+"\s+/>', re.S)
    DETAIL_RE = re.compile(r'<script>window\.wingxViewData=window\.wingxViewData\|\|\{\};window\.wingxViewData\[0\]=(.+?)(?=</script></div></div>)', re.S)

    def fetch_offer_list(self):
        while 1:
            try:
                list_page = requests.get(self.LIST_INDEX_URL).text
                if list_page: break
            except:
                print('Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        pages = int(self.MAX_PAGE_RE.search(list_page).group(1))
        for page in range(1, pages+1):
            print('第%d页' % page)
            list_page = requests.get(self.LIST_URL.format(page=page)).text
            for product_search in self.PRODUCT_RE.finditer(list_page):
                yield product_search.group(1)

    def fetch_offer_dict(self, offer_id):
        while 1:
            try:
                product_page = requests.get(self.PRODUCT_URL.format(offer_id=offer_id)).text
                if product_page: break
            except:
                print('Error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        detail_search = self.DETAIL_RE.search(product_page)
        data = json.loads(detail_search.group(1))
        if data.get('priceDisplay') != None:
            data['priceDisplay'] = float(data.get('priceDisplay'))
        data['productFeatureList'] = dict(((i['name'], i['value']) for i in data['productFeatureList']))
        if data['productFeatureList'].get('主面料成分的含量') != None:
            data['productFeatureList']['主面料成分的含量'] = float(data['productFeatureList']['主面料成分的含量'])
        temp = []
        for name in data['skuMap'] or []:
            item = data['skuMap'][name]
            item.update(zip(['color', 'size'], name.split('&gt;')))
            for key, data_type in (('canBookCount', int), ('discountPrice', float), ('saleCount', int)):
                if key in item and item[key] != None:
                    item[key] = data_type(item[key])
            temp.append(item)
        data['skuMap'] = temp
        return data

    def thumb(self, url, size=100):
        """ 返回缩略图地址."""
        url_split = url.rsplit('.', 1)
        url_split.insert(1, '%dx%d' % (size, size))
        return '.'.join(url_split)

    def save_img(self, url, filename):
        target = os.path.join(os.getcwd(), 'media/img/product', filename+'.jpg')
        content = requests.get(url).content
        with open(target, 'wb') as f:
            f.write(content)
        return '/media/img/product/' + filename + '.jpg'
