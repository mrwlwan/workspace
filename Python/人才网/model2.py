# coding=utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///jobinfo2.sqlite', echo=False)
Base = declarative_base()


class CorpModel(Base):
    __tablename__ = 'corps'

    id  = Column(Integer, primary_key=True)
    # 企业名称.
    name = Column(String, nullable=False)
    # 企业代码.
    corp_code = Column(String, default='')
    # 地址.
    addr = Column(String, default='')
    # 联系人.
    contact_person = Column(String, default='')
    # 电话区号
    contact_tel_code = Column(String, default='')
    # 电话号码(不带区号, default='')
    contact_tel_no = Column(String, default='')
    # 邮箱.
    mail = Column(String, default='')
    # 网站.
    website = Column(String, default='')
    # 信息来源
    info_from = Column(String, nullable=False)
    # 更新时间.
    insert_date = Column(Date, nullable=False)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
