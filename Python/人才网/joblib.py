# coding=utf8

import model, config
import kisfunc, kisrequest
import datetime, itertools, sys, collections, multiprocessing, re, urllib.parse

def _log(sender, msg):
    #print('[{0}][{1}]{2}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), sender, msg)
    kisfunc.time_print('[{0}]{1}'.format(sender, msg))


class Cache():
    """ 缓存. """
    def __init__(self, maxlen=None, key=None):
        self.key = key
        self.data_set = set()
        self.data_deque = collections.deque(maxlen=maxlen)

    @property
    def length(self):
        return len(self.data_set)

    def _set_value(self, value):
        return value[self.key] if self.key else value

    def exists(self, value):
        return self._set_value(value) in self.data_set

    def add(self, value):
        set_value = self._set_value(value)
        if not self.exists(value):
            if self.data_deque.maxlen and len(self.data_deque) >= self.data_deque.maxlen:
                self.data_set.remove(self._set_value(self.data_deque.popleft()))
            self.data_set.add(set_value)
            self.data_deque.append(value)
            return True
        return False

    def clear(self):
        self.data_set.clear()
        self.data_deque.clear()

    def get_values(self):
        return list(self.data_deque)


class JobProcess(multiprocessing.Process):
    info_from = ''
    def __init__(self, queue, setting):
        """ 参数 corplist_url 和 corp_url 取胜字符串的高级格式化:format, 使用{0},{1}等通配符; """
        super().__init__()
        self.queue = queue
        self.session = kisrequest.Session()
        self.cache = Cache(key='name', maxlen=config.cache_size)
        self.setting = {
            'corplist_url': None,
            'corp_url': None,
            'corplist_reg': None,
            'corp_regs': None,
            'corplist_post_data': None,
            'corp_post_data': None,
            'pages': 50,
            'encoding': None, # 通用自动识别
        }
        self.setting.update(setting)
        self.today = datetime.date.today()
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
        return self.urlopen(url, **kwargs).get_text(_encoding or self.get_setting('encoding'), _errors)

    def retrieve_json(self, url, encoding=None, errors='strict', **kwargs):
        return self.urlopen(url, **kwargs).get_json(_encoding or self.get_setting('encoding'), _errors)

    def log(self, msg):
        _log(self.info_from, msg)

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
        for page in range(1, self.get_setting('pages')+1):
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
            self.log('第%s页' % (next(cur_page)))
            self.log('*'*40)
            for corp_info in self.fetch_corplist(corplist_url):
                if not self.cache.add(corp_info):
                    self.log('{0} 已存在于 {1}'.format(corp_info['name'], self.info_from))
                    continue
                if self.get_setting('corp_regs'):
                    corp_info.update(self.fetch_corp(corp_info))
                self.process_corp_info(corp_info)
                self.queue.put(corp_info)
        self.queue.put(None)
        self.log('抓取完毕!')


class Commiter(multiprocessing.Process):
    """ 向数据库添加数据项. """
    def __init__(self, queue, count):
        super().__init__()
        self.queue = queue
        self.count = count
        self.db_lock = multiprocessing.Lock()
        self.sub_input_queue = multiprocessing.Queue()
        self.sub_output_queue = multiprocessing.Queue()
        self.web_check_processes = []
        self.write_process = None

    def run_init(self):
        self.session = kisrequest.Session()
        self.db = model.session

    def start_sub_processes(self):
        for i in range(1, config.check_web_exists_process+1):
            process = WebCheckProcess(self.sub_input_queue, self.sub_output_queue, name='WebCheck-{0}'.format(i))
            self.web_check_processes.append(process)
            process.start()
        self.log('开始 WebCheckProcess')
        self.write_process = WriteProcess(self.sub_output_queue, self.db_lock)
        self.write_process.start()
        self.log('开始 WriteProcess')

    def stop_sub_processes(self):
        self.log('正在结束 WebCheckProcess...')
        for process in self.web_check_processes:
            self.sub_input_queue.put(None)
        for process in self.web_check_processes:
            process.join()
        self.log('正在结束 WriteProcess...')
        self.sub_output_queue.put(None)
        self.write_process.join()

    def log(self, msg):
        _log('Commiter', msg)

    def db_exists(self, corp_info):
        """ 判断是否已经存在于数据库中. """
        self.db_lock.acquire()
        result = self.db.query(model.CorpModel).filter(model.CorpModel.name.like('%{0}%'.format(corp_info['name']))).first()
        self.db_lock.release()
        return result

    def run(self):
        self.run_init()
        self.start_sub_processes()
        while self.count:
            corp_info = self.queue.get()
            if not corp_info:
                self.count -= 1
                continue
            if self.db_exists(corp_info):
                self.log('{0} 已存在于数据库'.format(corp_info['name']))
                continue
            if corp_info['info_from']!=config.check_info_from:
                self.sub_input_queue.put(corp_info)
                continue
            self.sub_output_queue.put(corp_info)
        self.stop_sub_processes()
        self.log('结束 Commiter!')


class WriteProcess(multiprocessing.Process):
    """ 写入数据库进程. """
    def __init__(self, queue, db_lock):
        super().__init__()
        self.queue = queue
        self.db_lock = db_lock
        self.cache = dict()

    def run_init(self):
        self.db = model.session

    def log(self, msg):
        _log('Writer', msg)

    def _save(self):
        if not self.cache: return
        self.db_lock.acquire()
        self.db.add_all([model.CorpModel(**value) for value in self.cache.values()])
        self.db.commit()
        self.cache.clear()
        self.db_lock.release()
        self.log('****提交数据库成功!****')

    def save(self, corp_info):
        name = corp_info['name']
        if name in self.cache:
            self.log('{0} 已存在于写入缓存'.format(name))
            return
        self.cache[name] = corp_info
        self.log('{0} 保存成功'.format(name))
        if len(self.cache)>=config.commit_each_times: self._save()

    def run(self):
        self.run_init()
        while 1:
            corp_info = self.queue.get()
            if not corp_info:
                self._save()
                self.log('结束 WriteProcess!')
                break
            self.save(corp_info)


class WebCheckProcess(multiprocessing.Process):
    """ 网站上检查存在性. """
    def __init__(self, input_queue, output_queue, name=None):
        super().__init__(name=name)
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run_init(self):
        self.session = kisrequest.Session()

    def log(self, msg):
        _log(self.name, msg)

    def exists(self, corp_info):
        name = corp_info['name']
        url = config.check_url.format(urllib.parse.quote(name))
        reg = re.compile(config.check_reg_string.format(re.escape(name)), re.S)
        while 1:
            try:
                html = self.session.request(url, data=config.check_post_data).get_text(config.check_encoding)
                if html: break
            except:
                self.log('Http error. Target: {0}'.format(name))
        return reg.search(html)

    def run(self):
        self.run_init()
        while 1:
            corp_info = self.input_queue.get()
            if not corp_info:
                self.log('结束一个 WebCheckProcess!')
                break
            if self.exists(corp_info):
                self.log('{0} 已存在于 {1}'.format(corp_info['name'], config.check_info_from))
                corp_info['info_from'] = config.check_info_from
            self.output_queue.put(corp_info)

