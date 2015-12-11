# coding=utf8

import http.cookiejar
import urllib.request, urllib.parse, re, json, os, gzip, ssl, sqlite3

class Session:
    def __init__(self, headers=None, handlers=None):
        """ 初始化 Session 对象.
        @cookiejar(http.cookiejar.CookieJar).
        @context(ssl.SSLContext).
        @headers(2-tuples): 格式[(key, value), ...].
        @handlers(list): 格式[handler1, ...]. 注意不要跟 default handlers 重复.
        """
        self._cookie_handler = None
        self._https_handler = None
        handlers_plus = []
        if handlers:
            for handler in handlers:
                handlers_plus.append(handler)
                if isinstance(handler, urllib.request.HTTPCookieProcessor):
                    self._cookie_handler = handler
                elif isinstance(handler, urllib.request.HTTPSHandler):
                    self._https_handler = handler
        if not self._cookie_handler:
            self._cookie_handler = urllib.request.HTTPCookieProcessor()
            handlers_plus.insert(0, self._cookie_handler)
        if not self._https_handler:
            self._https_handler = urllib.request.HTTPSHandler()
            handlers_plus.insert(0, self._https_handler)
        self.opener = urllib.request.build_opener(*handlers_plus)
        # 默认添加 Firefox useragent.
        self.opener.addheaders = headers or [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:42.0) Gecko/20100101 Firefox/42.0')]

    @property
    def cookiejar(self):
        return self._cookie_handler.cookiejar

    @cookiejar.setter
    def cookiejar(self, cookiejar):
        self._cookie_handler.cookiejar = cookiejar

    @property
    def context(self):
        return self._https_handler._context

    @context.setter
    def context(self, context):
        self._https_handler._context = context

    def set_filecookiejar(self, filename, style='lwp', **kwargs):
        """ 加载文件型cookiejar.
        @filename(str/None).
        @style(str): lwp/moz.
        """
        style = style.lower()
        if style=='lwp':
            cls = http.cookiejar.LWPCookieJar
        elif style=='moz':
            cls = http.cookiejar.MozillaCookieJar
        else: return False
        self.cookiejar = cls(filename, **kwargs)
        if filename and os.path.exists(filename): self.cookiejar.load()
        return True

    def load_cookies_sqlite(self, filename, style='moz', where=None, default_cookie=None, **kwargs):
        """ 加载 cookies.sqlte.
        @filename(str): sqlite 数据库文件.
        @where(str): sqlite 的条件语句. 过滤之用.
        @style(str): moz. 暂时支持 mozilla 的 cookies.sqlite 数据库文件.
        @kwargs: 传递给sqlite3.connect.
        """
        style = style.lower()
        if style=='moz':
            conn = sqlite3.connect(filename, **kwargs)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = 'select name, value, host as domain, path, expiry as expires, isSecure as secure from moz_cookies{0}'.format(' where '+where if where else '')
            cursor.execute(sql)
            for row in cursor.fetchall():
                default = default_cookie.copy() if default_cookie else {
                    'version': 0,
                    'port': None,
                    'port_specified': False,
                    'domain_specified': True,
                    'domain_initial_dot': True,
                    'path_specified': False,
                    'discard': False,
                    'comment': None,
                    'comment_url': None,
                    'rest': {},
                    'rfc2109': False,
                }
                default.update(row)
                default['domain_initial_dot'] = row['domain'].startswith('.')
                default['secure'] = bool(row['secure'])
                self.cookiejar.set_cookie(http.cookiejar.Cookie(**default))

    def set_default_context(self, cafile=None, capath=None, cadata=None, **kwargs):
        if not (cafile or capath or cadata):
            cafile = os.path.join(os.path.dirname(__file__), 'cacert.pem')
        self.context = ssl.create_default_context(cafile=cafile, capath=capath, cadata=cadata, **kwargs)

    def set_unverify_context(self, *args, **kwargs):
        self.context = ssl._create_unverified_context(*args, **kwargs)

    def load_context(self, cafile=None, capath=None, cadata=None, **kwargs):
        self.context.load_verify_locations(cafile=cafile, capath=capath, cadata=cadata, **kwargs)

    def remove_context(self):
        """ 删除 context. """
        self.context = None

    def add_header(self, key, value):
        self.opener.addheaders.append((key, value))

    def add_handler(self, handler):
        self.opener.add_handler(handler)

    def request(self, url, data=None, params=None, method=None, headers=None, proxies=None, timeout=None, encoding='utf8', errors='strict', doseq=False, safe='', origin_req_host=None, unverifiable=False, **kwargs):
        """ 通用 http 请求, 返回 ResponseProxy 对象.
        @params(dict/2-tuples): url queries.
        @data(str/dict/2-tuples).
        @method(str): GET/POST/PUT/OPTION/DELETE.
        @headers(2-tuples): 格式[(key, value)].
        @proxies(2-tuples): 模式[(ip1, 'http'), (ip2, 'https'), ...].
        @kwargs: 传递给 self.opener.open 方法.
        @doseq(bool): 传递给 urllib.parse.urlencode 方法.
        @safe(str): 传递给 urllib.parse.urlencode 方法.
        """
        if params:
            url = url+'?'+ urllib.parse.urlencode(params, doseq=doseq, safe=safe, encoding=encoding, errors=errors)
        r = urllib.request.Request(
            url,
            data=None if data is None else (data if isinstance(data, str) else urllib.parse.urlencode(data, doseq=doseq, safe=safe, encoding=encoding, errors=errors)).encode(encoding, errors),
            method=method,
            origin_req_host=origin_req_host,
            unverifiable=unverifiable
        )
        if headers:
            for header in headers: r.add_header(*header)
        if proxies:
            for proxy in proxies: r.set_proxy(*proxy)
        response = self.opener.open(r, timeout=timeout, **kwargs)
        return ResponseProxy(response, r)

    def get(self, url, **kwargs):
        return self.request(url, method='GET', **kwargs)

    def post(self, url, **kwargs):
        return self.request(url, method='POST', **kwargs)

    def put(self, url, **kwargs):
        return self.request(url, method='PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self.request(url, method='DELETE', **kwargs)

    def option(self, url, **kwargs):
        return self.request(url, method='OPTION', **kwargs)


class ResponseProxy:
    def __init__(self, response, request=None):
        """ 保留关键属性: _encoding, _content """
        self.response = response
        self.request = request

    @property
    def status(self):
        return self.response.status

    @property
    def content_type(self):
        return self.response.getheader('Content-Type')

    @property
    def encoding(self):
        if not hasattr(self, '_encoding'):
            search = re.search(r'charset=\s*([a-z0-9_\-]+)', self.content_type or '', re.I)
            self._encoding = search and search.group(1) or None
        return self._encoding

    @property
    def content(self):
        if not hasattr(self, '_content'):
            is_gzip = self.get_header('Content-Encoding')
            if is_gzip and is_gzip.strip().lower()=='gzip':
                self._content = gzip.GzipFile(fileobj=self.response, mode='r').read()
            else:
                self._content= self.response.read()
        return self._content

    def get_text(self, encoding=None, errors='strict'):
        return self.content.decode(encoding or self.encoding or 'utf8', errors)

    def get_json(self, default=None, strip=None, encoding=None, errors='strict'):
        text = self.get_text(encoding, errors).strip(strip)
        return json.loads(text) if text else default

    def get_header(self, key, default=None):
        return self.response.getheader(key, default)


def urlopen(*args, context=None, **kwargs):
    session = Session()
    if context: session.context = context
    return session.request(*args, **kwargs)


def retrieve_cacert(hostname, port=443, saved=None, **kwargs):
    """ 取得网站 SSL 验证 cafile 文件. """
    cert_string = ssl.get_server_certificate((hostname, port), **kwargs)
    if not saved: return cert_string
    with open(saved, 'w', newline='\n') as f:
        f.write(cert_string)


def fix_cookiefile(cookie_filename):
    """ fix ie style cookie file to netscape style. """
    lines = []
    correct = False
    reg = re.compile(r'^\s*#+\s*Netscape\s+HTTP\s+Cookie\s+File\s*$', re.I)
    with open(cookie_filename, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if line:
                if reg.match(line):
                    correct = True
                    break
                lines.append(line)
    if not correct:
        lines.insert(0, '# Netscape HTTP Cookie File')
        with open(cookie_filename, 'w', encoding='utf8') as f:
            f.write('\n'.join(lines))
