# coding=utf8

import datetime


# 子类目录
subjob_path = 'sites'

# 数据库日期格式, 用于将日期字符串转换为 Datetime.date 对象.
date_format = '%Y-%m-%d'

# 缓存大小
cache_size = 100

# 每次提交写入数据库项数
commit_each_times = 30

# 网络超时
timeout = 30

# 下面是网络检查是否存在参数
check_url = 'http://s.job5156.com/s/p/result?csrfKey=&keywordType=2&keyword={0}&locationList='

check_reg_string = r'<a class="comName" title=\'{0}\''

check_info_from = '智通人才网'

check_encoding = 'utf8'

check_post_data = None

check_web_exists_process = 5

report_date = datetime.date.today()

report_encoding = 'gbk'

report_filename = '最新公司信息_' + report_date.strftime('%Y-%m-%d.csv')

def _subjob_property(attr):
    def func(subjob, corp):
        p = getattr(subjob, attr)
        return p(corp) if callable(p) else p
    return func

report_fields = [('名称', 'name'), ('地址', 'address'), ('联系人', 'contact_person'), ('电话', 'contact_phone'), ('邮箱', 'mail'), ('网站', 'website'), ('来源', 'info_from'), ('链接', _subjob_property('get_corp_url'))]

