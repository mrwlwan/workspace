# coding=utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///jobinfo.sqlite', echo=False)
Base = declarative_base()

class CorpModel(Base):
    __tablename__ = 'corps'

    id  = Column(Integer, primary_key=True)
    # 企业名称.
    name = Column(String, nullable=False)
    # 企业代码.
    code = Column(String, nullable=True)
    # 地址.
    address = Column(String, nullable=True)
    # 联系人.
    contact_person = Column(String, nullable=True)
    # 电话号码
    contact_phone = Column(String, nullable=True)
    # 邮箱.
    mail = Column(String, nullable=True)
    # 网站.
    website = Column(String, nullable=True)
    # 信息来源
    info_from = Column(String, nullable=False)
    # 更新时间.
    insert_date = Column(Date, nullable=False)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
