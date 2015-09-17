# coding=utf8

from lib.corp import Corp
import re

class QZRCCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '泉州人才网',
            'corplist_url': 'http://qzrc.com/area.aspx?a={1}&pn=100&p={0}',
            'corp_url': 'http://qzrc.com/CompanyDetail.aspx?id={corp_code}',
            'corplist_reg': re.compile(r'<div class="companyname"><a href=["\']/CompanyDetail\.aspx\?id=(?P<corp_code>\d+)[^>]+>(?P<name>[^<]+)', re.S),
            'corp_regs': [
                re.compile(r"·联 系 人：(?P<contact_person>[^<]+)", re.S),
                re.compile(r"·通讯地址：(?P<addr>[^<\n]+)", re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)
        self.jobareas = [
            ('350582', 50), # 普江
        ]


        self.pages = 100

    def get_next_page_url(self):
        for jobarea_code, pages in self.jobareas:
            for page in range(1, pages+1):
                yield self.corplist_url.format(page, jobarea_code)
