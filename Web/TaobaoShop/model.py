# coding=utf8

import const
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship
import datetime, collections, re, json


engine = create_engine('sqlite:///data.sqlite', echo=False)
Base = declarative_base()



class ConfigModel(Base):
    """ 全局设定. """
    __tablename__ = 'configs'
    id = Column(Integer, primary_key=True)
    shop_name = Column(String, nullable=False)
    per_page = Column(Integer, default=20)
    expiry_days = Column(Integer, default=1)
    update_date = Column(Date, nullable=True)

    def is_expiries(self):
        return (datetime.date.today()-self.update_date).days>=self.expiry_days

    def get(self, column, default=None):
        return getattr(self, column) if hasattr(self, column) else default


class ProductModel(Base):
    """ 产品。"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    # 1688 ID
    offer_id = Column(String, unique=True, nullable=False)
    # 标题 json['subject']
    subject = Column(String, nullable=True)
    # 货号 json['productFeatureList']->['货号']
    code = Column(String, nullable=True)
    # 原始图片 json['imageList'][0]['originalImageURI']
    img_url = Column(String, nullable=True)
    # 品牌 json['productFeatureList']->['品牌']
    brand = Column(String, nullable=True)
    # 图案 json['productFeatureList']->['图案']
    pattern = Column(String, nullable=True)
    # 面料名称 json['productFeatureList']->['面料名称']
    fabric = Column(String, nullable=True)
    # 面料成分 json['productFeatureList']->['主面料成分']
    fabric_content = Column(String, nullable=True)
    # 主面料成分的含量 json['productFeatureList']->['主面料成分的含量']
    fabric_scale = Column(Float, nullable=True)
    # 价钱 json['skuMap']->['discountPrice'] or json['priceDisplay']
    price = Column(String, nullable=True) # 以json方式存储list, 因为可能存在多个单价
    # 库存数量 json['skuMap']->['canBookCount']
    book_count = Column(Integer, nullable=True)
    # 销售数量 json['skuMap']->['saleCount']
    sale_count = Column(Integer, nullable=True)
    # 备注
    remarks = Column(Text, nullable=True)
    # 更新日期(库存更新日期)
    update_date = Column(Date, default=datetime.date.today)
    # 上期库存数量
    last_book_count = Column(Integer, nullable=True)
    # 上期销售数量
    last_sale_count = Column(Integer, nullable=True)
    # 上次更新日期
    last_update_date = Column(Date)
    # 分类
    category = Column(Enum(*const.category_list), default='未分类', nullable=False)
    # 库存状态
    sku_status = Column(Enum(*const.sku_status_list), default='正常', nullable=False)
    # 销售状态
    status = Column(Enum(*const.status_list), default='上架', nullable=False)
    # SKU(码数和数量)
    skus = relationship('SkuModel', backref='product', cascade='all', single_parent=True)

    @property
    def orderd_sku(self):
        result = {}
        for sku in self.ordered_skus_by_size():
            if sku.color not in result: result[sku.color] = collections.OrderedDict()
            result[sku.color][sku.size] = {
                'book_count': sku.book_count,
                'sale_count': sku.sale_count,
                'price': sku.price,
            }
        return result

    @hybrid_property
    def book_count_diff(self):
        """ 库存差值。"""
        return self.book_count - self.last_book_count

    @hybrid_property
    def sale_count_diff(self):
        """ 销售数量差值. """
        return self.sale_count - self.last_sale_count

    @hybrid_property
    def price_diff(self):
        """ 单价差值. """
        return self.price - self.last_price


    def ordered_skus_by_size(self):
        order = {'xs': 0, 's': 1, 'm': 2, 'l': 3, 'xl': 4, 'xxl': 5, 'xxxl': 6, 'xxxxl': 7}
        reg = re.compile(r'x*[sl]|m')
        def _sku_sort(sku):
            size = sku.size.lower()
            size_search = reg.search(size)
            if size_search:
                return order.get(size_search.group(), 100)
            return size
        return sorted(self.skus, key=_sku_sort)

    # 判断是否过期需要重新更新
    def is_expiries(self, days):
        return (datetime.date.today()-self.update_date).days>=days

    def get_prices(self):
        return json.loads(self.price)

    def update_sku_relative(self):
        self.update_last()
        zero_count = 0
        book_counts = []
        sale_counts = []
        prices = set()
        for sku in self.skus:
            if sku.book_count<=0:
                zero_count+=1
            else:
                book_counts.append(sku.book_count)
            sale_counts.append(sku.sale_count)
            prices.add(sku.price)
        self.book_count = sum(book_counts)
        self.sale_count = sum(sale_counts)
        self.price = json.dumps(sorted(prices))
        length = len(book_counts)
        if length<=0:
            self.sku_status = '卖空'
        elif zero_count>0:
            self.sku_status = '缺货'
        else:
            for book_count in book_counts:
                if book_count<30:
                    self.sku_status = '紧张'
                    return
            self.sku_status = '正常'

    def update_last(self):
        self.last_update_date = self.update_date
        self.last_book_count = self.book_count
        self.last_sale_count = self.sale_count


class SkuModel(Base):
    """ Sku。json['skuMap']"""
    __tablename__ = 'skus'

    id = Column(Integer, primary_key=True)
    # 产品
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    # 颜色 json['skuMap']->['color']
    color = Column(String, nullable=True)
    # 码数 json['skuMap']->['size']
    size = Column(String, nullable=True)
    # 库存数量 json['skuMap']->['canBookCount']
    book_count = Column(Integer, nullable=True)
    # 销售数量 json['skuMap']->['saleCount']
    sale_count = Column(Integer, nullable=True)
    # 价钱 json['skuMap']->['discountPrice'] or json['priceDisplay']
    price = Column(Float, nullable=True)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
