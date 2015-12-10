# coding=utf8

import joblib
import re


class SubJobProcess(joblib.JobProcess):
    info_from = '卓博人才网'
    def __init__(self, queue):
        setting = {
            'corplist_url': 'http://www.jobcn.com/search/result_servlet.ujson',
            'corp_url': 'http://www.jobcn.com/position/company.xhtml?comId={0.code}',
            'corplist_post_data': {
                'p.keyword': '',
                'p.keyword2': '',
                'p.keywordType': '2',
                'p.pageNo': '1',
                'p.pageSize': '20',
                'p.sortBy': 'postdate',
                'p.statistics': 'false',
            },
            'corplist_reg': None,
            'corp_regs': [
                re.compile(r'<dl><dt>联系人：</dt><dd>(?P<contact_person>[^<]+)', re.S),
                re.compile(r'<dl><dt>联?系?电话：</dt><dd>(?P<contact_phone>[^<]+)', re.S),
                re.compile(r'<dl><dt>主页：</dt><dd><a rel="external nofollow" href="(?P<website>[^"]+)', re.S),
                re.compile(r'<dl><dt>地址：</dt><dd>(?P<address>[^<]+)', re.S),
            ],
            'pages': 30,
            'encoding': 'gbk',
        }
        super().__init__(queue, setting)

    def get_corplist_urls(self):
        for job_location in self.get_setting('job_locations'):
            for page in range(1, self.get_setting('pages')+1):
                yield self.get_setting('corplist_url').format(job_location['code'], page)

    def get_corplist_urls(self):
        for page in range(1, self.get_setting('pages')+1):
            self.get_setting('corplist_post_data')['p.pageNo'] = page
            yield self.get_setting('corplist_url')

    def fetch_corplist(self, page_url):
        json = self.retrieve_json(page_url, data=self.get_setting('corplist_post_data'))
        corp_list = json['rows']
        return ({
            'name': corp_info['comName'],
            'code': str(corp_info['comId']),
            #'insert_date': corp_info['postDate'],
        } for corp_info in corp_list)
