# coding=utf8

from lib.corp import Corp
import re

class Job5156Corp(Corp):
    def __init__(self):
        config = {
            'info_from': 'job5156',
            'corplist_url': 'http://s.job5156.com/s/p/result?locationList={0}&pn={1}&showType=2',
            'corp_url': 'http://dg.job5156.com/corp/{corp_code}',
            'corplist_post_data': None,
            'corp_post_data': None,
            'corplist_reg': re.compile(r'<td class="com"><a class="comName" title=\'(?P<name>[^\']+)\' href="http://[^/]+/corp/(?P<corp_code>[^"]+)', re.S),
            'corp_regs': [
                re.compile('联系地址：</span><label>(?P<addr>[^<]+)', re.S),
                re.compile('联系人：</span>(?P<contact_person>[^<]+)', re.S),
                #re.compile('电话：</span>(?P<contact_tel_no>[^<]+)', re.S),
                #re.compile('"addr":"(?P<addr>[^"]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            #'charset': 'gbk',
            'timeout': 10,
        }
        super().__init__(**config)

        self.job_locations = (
            {'city': '东莞', 'code':'1401'},
            {'city': '广州', 'code':'1403'},
            {'city': '深圳', 'code':'1402'},
            {'city': '中山', 'code':'1404'},
            {'city': '江门', 'code':'1408'},
            {'city': '佛山', 'code':'1409'},
            {'city': '惠州', 'code':'1407'},
            {'city': '泉州', 'code':'17030000'},
            {'city': '厦门', 'code':'17020000'},
        )
        self.pages = 50

    def get_next_page_url(self):
        return (self.corplist_url.format(job_location['code'], page) for job_location in self.job_locations for page in range(1, self.pages + 1))
