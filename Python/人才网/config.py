# coding=utf8

# 子类目录
subjob_path = 'sites'

# 缓存大小
cache_size = 100

# 每次提交写入数据库项数
commit_each_times = 30

# 网络超时
timeout = 5

# 下面是网络检查是否存在参数
check_url = 'http://s.job5156.com/s/p/result?csrfKey=&keywordType=2&keyword={0}&locationList='

check_reg_string = r'<a class="comName" title=\'{0}\''

check_info_from = '智通人才网'

check_encoding = 'gbk'

check_post_data = None

