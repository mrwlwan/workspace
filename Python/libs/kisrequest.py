# coding=utf8

import http.cookiejar
import urllib.request, urllib.parse, re, json, os

class Session:
    def __init__(self, cookiejar=None, headers=None, handlers=None):
        """ 初始化 Session 对象.
        @cookiejar(http.cookiejar.CookieJar/str): str 时自动转换成 http.cookiejar.LWPCookieJar 对象.
        @headers(2-tuples): 格式[(key, value), ...].
        @handlers(list): 格式[handler1, ...]. 注意不要跟 default handlers 重复.
        """
        self.opener = urllib.request.build_opener()
        # 默认添加 HTTPCookieProcessor
        if cookiejar and isinstance(cookiejar, http.cookiejar.CookieJar):
            self.cookiejar = cookiejar
        else:
            self.cookiejar = http.cookiejar.LWPCookieJar(cookiejar)
            if cookiejar and os.path.exists(cookiejar): self.cookiejar.load()
        self.opener.add_handler(urllib.request.HTTPCookieProcessor(self.cookiejar))
        if handlers:
            for handler in handlers: self.opener.add_handler(handler)
        # 默认添加 Firefox useragent.
        self.opener.addheaders = headers or [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:42.0) Gecko/20100101 Firefox/42.0')]

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
        return ResponseProxy(response, None)

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
            self._content= self.response.read()
        return self._content

    def get_text(self, encoding=None, errors='strict'):
        return self.content.decode(encoding or self.encoding or 'utf8', errors)

    def get_json(self, default=None, strip=None, encoding=None, errors='strict'):
        text = self.get_text(encoding, errors).strip(strip)
        return json.loads(text) if text else default

    def get_header(self, key, default=None):
        return self.response.getheader(key, default)


def urlopen(*args, **kwargs):
    return Session().request(*args, **kwargs)
