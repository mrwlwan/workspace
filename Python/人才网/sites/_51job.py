# coding=utf8

import joblib
import re


class SubJobProcess(joblib.JobProcess):
    info_from = '51job'
    def __init__(self, queue):
        setting = {
            'corplist_url': 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea={1}&district=000000&funtype=0000&industrytype=00&issuedate=9&providesalary=99&keywordtype=1&curr_page={0}&lang=c&stype=2&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&fromType=14&dibiaoid=0&confirmdate=9',
            'corp_url': 'http://jobs.51job.com/{0.code}.html',
            'corplist_reg': re.compile(r'<span class="t2"><a target="_blank" title="(?P<name>[^"]+)" href="http://jobs.51job.com/(?P<code>[^\."]+)', re.S),
            'corp_regs': [
                re.compile(r'<dt>公司网站：</dt>\.+?href="(?P<website>[^"]+)', re.S),
                re.compile(r'<dt>公司地址：</dt>\s*<[^>]+>(?P<address>[^<]+)', re.S),
            ],
            'encoding': 'gbk',
            'jobareas_pages': [
                ('110400', 50), # 泉州
                ('030800', 50), # 东莞
                ('030300', 20), # 惠州
                #('040000', 20), # 深圳
                #('030200', 20), # 广州
                #('030600', 20), # 佛山
                #('080400', 50), # 温州
                #('080400', 50), # 温州
                #('190200', 50), # 长沙
            ]
        }
        super().__init__(queue, setting)

    def get_corplist_urls(self):
        for jobarea_code, pages in self.get_setting('jobareas_pages'):
            for page in range(1, pages+1):
                yield self.get_setting('corplist_url').format(page, jobarea_code)
