# coding=utf8

import tornado.web
import requests
import re, json, os

class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.model = self.application.model
        self.db = self.application.model.session

    def on_finish(self):
        self.db.close()

    def save_img(self, url, filename):
        target = os.path.join(os.getcwd(), 'media/product/img', filename+'.jpg')
        content = requests.get(url).content
        with open(target, 'wb') as f:
            f.write(content)
        return '/media/img/product/' + filename + '.jpg'

    def update_product(self, product, **kwargs):
        product = self.model.ProductModel(
            offer_id = offer_id,
            subject = data['subject'],
            code = data['productFeatureList'].get('货号', ''),
            brand = data['productFeatureList'].get('品牌', ''),
            pattern = data['productFeatureList'].get('图案', '纯色'),
            fabric = data['productFeatureList'].get('面料名称', ''),
            fabric_content = data['productFeatureList'].get('主面料成份', ''),
            fabric_scale = data['productFeatureList'].get('主面料成分的含量', '100.0')
        )


class FetchHelper:
    LIST_INDEX_URL = 'http://benf6.1688.com/page/offerlist.htm'
    LIST_URL = 'http://benf6.1688.com/page/offerlist.htm?showType=catalog&tradenumFilter=false&sampleFilter=false&mixFilter=false&privateFilter=false&mobileOfferFilter=%24mobileOfferFilter&groupFilter=false&sortType=timedown&pageNum={page}'
    PRODUCT_URL = 'http://m.1688.com/offer/{offer_id}.html'
    MAX_PAGE_RE = re.compile(r'<li>共<em class="page-count">(\d+)', re.S)
    PRODUCT_RE = re.compile(r'<a href="http://detail.1688.com/offer/([^\.]+)[^>]+>\s+<img src="([^"]+)" alt="[^"]+"\s+/>', re.S)
    DETAIL_RE = re.compile(r'<script>window\.wingxViewData=window\.wingxViewData\|\|\{\};window\.wingxViewData\[0\]=(.+?)(?=</script></div></div>)', re.S)

    def get_offer_list(self):
        list_page = requests.get(self.LIST_INDEX_URL).text
        pages = int(self.MAX_PAGE_RE.search(list_page).group(1))
        for page in range(1, pages+1):
            print('第%d页' % page)
            list_page = requests.get(self.LIST_URL.format(page=page)).text
            for product_search in self.PRODUCT_RE.finditer(list_page):
                yield (product_search.group(1), 'http:'+product_search.group(2))

    def get_offer_dict(self, offer_id):
        product_page = requests.get(self.PRODUCT_URL.format(offer_id=offer_id)).text
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



