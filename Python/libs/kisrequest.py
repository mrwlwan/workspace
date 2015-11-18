# coding=utf8

from http.cookiejar import CookieJar, LWPCookieJar
import urllib.request, urllib.parse, re, json

class Session:
    def __init__(self, cookiejar=None, headers=[], handlers=[]):
        # 默认添加 HTTPCookieProcessor
        if not handlers or [True for handler in handlers if not isinstance(handler, urllib.request.HTTPCookieProcessor)]:
            if cookiejar and isinstance(cookiejar, CookieJar):
                self.cookiejar = cookiejar
            else:
                self.cookiejar = LWPCookieJar(cookiejar)
                if cookiejar and os.path.exists(cookiejar): self.cookiejar.load()
            handlers.append(urllib.request.HTTPCookieProcessor(self.cookiejar))
        self.opener = urllib.request.build_opener(*handlers)
        # 默认添加 HTTPCookieProcessor
        self.opener.addheaders = headers or [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101 Firefox/41.0')]

    def add_header(self, header):
        self.opener.addheaders.append(header)

    def add_handler(self, handler):
        self.opener.add_handler(handler)

    def request(self, url, params={}, data=None, method=None, headers=[], proxies=[], timeout=None, encoding='utf8', errors='strict', origin_req_host=None, unverifiable=False, **kwargs):
        if params:
            url = url+'?'+ urllib.parse.urlencode(params).encoding(encoding, errors)
        r = urllib.request.Request(
            url,
            data=data and (isinstance(data, str) and data or urllib.parse.urlencode(data)).encode(encoding, errors),
            method=method,
            origin_req_host=origin_req_host,
            unverifiable=unverifiable
        )
        for header in headers:
            r.add_header(*header)
        for proxy in proxies:
            r.set_proxy(*proxy)
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
    """ 保留关键属性: _encoding, _content """
    def __init__(self, response, request):
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
            search = re.search(r'charset=\s*([a-z0-9_\-]+)', self.content_type, re.I)
            self._encoding = search and search.group(1) or None
        return self._encoding

    @property
    def content(self):
        if not hasattr(self, '_content'):
            self._content= self.response.read()
        return self._content

    def get_text(self, encoding=None, errors='strict'):
        return self.content.decode(encoding or self.encoding or 'utf8', errors)

    def get_json(self, default=None, encoding=None, errors='strict'):
        text = self.get_text(encoding, errors).strip()
        return json.loads(text) if text else None

    def get_header(self, key, default=None):
        return self.response.getheader(key, default)
