# coding=utf8

import model, config
import kisrequest
import datetime, sys, collections, multiprocessing


class Cache():
    """ 缓存. """
    def __init__(self, data=None, maxlen=None):
        self.data_set = set()
        self.data_deque = collections.deque(maxlen=maxlen)
        if data:
            for value in data:
                self.add(value)

    def exists(self, value):
        return value in self.data_set

    def add(self, value):
        if not self.exists(value):
            if self.data_deque.maxlen and len(self.data_deque) >= self.data_deque.maxlen:
                self.data_set.remove(self.data_deque.popleft())
            self.data_set.add(value)
            self.data_deque.append(value)
            return True
        return False

    def clear(self):
        self.data_set.clear()
        self.data_deque.clear()


class JobProcess(multiprocessing.Process):
    info_from = ''
    def __init__(self, queue, setting):
        """ 参数 corplist_url 和 corp_url 取胜字符串的高级格式化:format, 使用{0},{1}等通配符; """
        self.queue = queue
        self.session = kisrequest.Session()
        self.cache = Cache(maxlen=config.cache_size)
        self.setting = {
            'corplist_url': None,
            'corp_url': None,
            'corplist_reg': None,
            'corp_regs': None,
            'corplist_post_data': None,
            'corp_post_data': None,
            'pages': 50,
            'encoding': 'utf8',
        }
        self.setting.update(setting)
        self.today = datetime.datet.today()
        #if not self._check_setting(): sys.exit()

    def _check_setting(self):
        """ 检查是否缺少必要的参数. """
        miss = []
        for key in ['corplist_url', 'corp_url', 'corplist_reg', 'corp_regs']:
            if not self.setting.get(key): miss.appen(key)
        if miss:
            self.log('缺少参数: '+', '.join(miss))
            return False
        return True

    def get_setting(self, key, default=None):
        return self.setting.get(key, default)

    def urlopen(self, url, *args, **kwargs):
        """ 通用网页请求. """
        return self.session.request(url, *args, **kwargs)

    def retrieve_html(self, url, _encoding=None, _errors='strict', **kwargs):
        return self.urlopen(url, *args, **kwargs).get_text(_encoding or self.encoding, _errors)

    def retrieve_json(self, url, encoding=None, errors='strict', **kwargs):
        return self.urlopen(url, *args, **kwargs).get_json(_encoding or self.encoding, _errors)

    def log(self, msg):
        print('[{0}][{1}]{2}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), self.info_from, msg))

    def process_corp_info(self, corp_info):
        """ 写入数据库前数据处理. """
        for key, values in corp_info.items():
            corp_info[key] = values.strip()
        if 'insert_date' not in corp_info:
            corp_info['insert_date'] = self.today
        corp_info['info_from'] = self.info_from
        return corp_info

    def get_corplist_urls(self):
        """ 子类大部分须重写. """
        for page in self.get_setting('pages'):
            yield self.get_setting('corplist_url'.format(page))

    def get_corp_url(self, corp_info):
        """ 返回公司详情页链接. """
        return self.get_setting('corp_url').format(**corp_info)

    def prepare(self, *args, **kwargs):
        pass

    def fetch_corplist(self, url):
        html = self.retrieve_html(url, data=self.get_setting('corplist_post_data'))
        for match in self.get_setting('corplist_reg').finditer(html):
            yield match.groupdict()

    def fetch_corp(self, corp_info):
        url = self.get_corp_url(corp_info)
        html = self.retrieve_html(url, data=self.get_setting('corp_post_data'))
        result = {}
        try:
            for reg in self.get_setting('corp_regs'):
                match = reg.search(html)
                if match: result.update(match.groupdict())
        except:
            pass
        return result

    def run(self):
        self.prepare()
        cur_page = itertools.count(1)
        for corplist_url in self.get_corplist_urls():
            self.log('\n第%s页' % (next(cur_page)))
            for corp_info in self.fetch_corplist(corplist_url):
                self.log('*'*60)
                name = corp_info['name']
                if not self.cache.add(name):
                    self.log('{0} 已存在于 {1}'.format(name, self.info_from))
                    continue
                if self.corp_regs:
                    corp_info = self.fetch_corp(corp_info)
                self.process_corp_info(corp_info)
                self.queue.put(corp_info)
        self.log('抓取完毕!')


class Commiter(multiprocessing.Process):
    """ 向数据库添加数据项. """
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.session = kisrequest.Session()
        self.db = model.session
        self._add_times = 0

    def log(self, msg):
        print('[{0}][Commter]{2}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), msg))

    def db_exists(self, name):
        """ 判断是否已经存在于数据库中. """
        return self.db.query(model.CorpModel.name.like('%{0}%'.format(name))).one_or_none()

    def web_exists(self, name):
        url = config.check_url.format(name)
        reg = re.compile(config.check_reg_string.format(name), re.S)
        html = self.session.request(url, data=config.check_post_data).get_text(config.check_encoding)
        return reg.search(html)

    def save(self, corp_info):
        self.db.add(corp_info)
        self._add_times += 1
        if self._add_times % self.commit_each_times == 0:
            self.db.commit()

    def run(self):
        while 1:
            corp_info = self.queue.get()
            name = corp_info['name']
            corp = self.db_exists(name)
            if corp:
                self.log('{0} 已存在于 {1}'.format(name, corp.info_from))
                continue
            if corp['info_from']!=config.check_info_from and self.web_exists(name):
                self.log('{0} 已存在于 {1}'.format(name, corp_info['info_from']))
                continue
            self.save(corp_info)
            self.log('{0} 保存成功'.format(name))

