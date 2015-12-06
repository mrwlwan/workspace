# coding=utf8

import joblib
import re


class SubJobProcess(joblib.JobProcess):
    info_from = '智通人才网'
    def __init__(self, queue):
        setting = {
            'corplist_url': 'http://s.job5156.com/s/p/result?locationList={0}&pn={1}&showType=2',
            'corp_url': 'http://dg.job5156.com/corp/{code}',
            'corplist_reg': re.compile(r'<td class="com"><a class="comName" title=\'(?P<name>[^\']+)\' href="http://[^/]+/corp/(?P<code>[^"]+)', re.S),
            'corp_regs': [
                re.compile('联系地址：</span><label>(?P<address>[^<]+)', re.S),
                re.compile('联系人：</span>(?P<contact_person>[^<]+)', re.S),
                #re.compile('电话：</span>(?P<contact_phone>[^<]+)', re.S),
            ],
            'pages': 50,
            #'encoding': 'gbk',
            'job_locations': [
                {'city': '东莞', 'code':'1401'},
                {'city': '广州', 'code':'1403'},
                {'city': '深圳', 'code':'1402'},
                {'city': '中山', 'code':'1404'},
                {'city': '江门', 'code':'1408'},
                {'city': '佛山', 'code':'1409'},
                {'city': '惠州', 'code':'1407'},
                {'city': '泉州', 'code':'17030000'},
                {'city': '厦门', 'code':'17020000'},
            ],
        }
        super().__init__(queue, setting)

    def get_corplist_urls(self):
        for job_location in self.get_setting('job_locations'):
            for page in range(1, self.get_setting('pages')+1):
                yield self.get_setting('corplist_url').format(job_location['code'], page)
