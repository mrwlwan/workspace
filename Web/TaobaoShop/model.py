# coding=utf8

from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime


engine = create_engine('sqlite:///data.sqlite', echo=True)
Base = declarative_base()

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
    # 备注
    remarks = Column(Text, nullable=True)
    # 更新日期
    update_date = Column(Date, default=datetime.date.today)
    # 状态
    status = Column(Enum('正常', '缺货', '下架'))
    # SKU(码数和数量)
    skus = relationship('SkuModel', backref='product', cascade='all', single_parent=True)

    # 判断是否过期需要重新更新
    def is_expiries(self):
        return datetime.date.today()-self.update_date>=1

    def brief_sku:
        pass


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
    # 更新日期
    update_date = Column(Date, default=datetime.date.today)
    # 上期库存数量
    last_book_count = Column(Integer, nullable=True)
    # 上期销售数量
    last_sale_count = Column(Integer, nullable=True)
    # 上期价钱
    last_price = Column(Float, nullable=True)
    # 上次更新日期
    last_update_date = Column(Date)

    # 判断是否过期需要重新更新
    def is_expiries(self):
        return datetime.date.today()-self.update_date>=1

    @property
    def book_count_diff(self):
        """ 库存差值。"""
        return self.book_count - self.last_book_count

    @property
    def sale_count_diff(self):
        """ 销售数量差值. """
        return self.sale_count - self.last_sale_count

    @property
    def price_diff(self):
        """ 单价差值. """
        return self.price - self.last_price


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
