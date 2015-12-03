import kisrequest
import codecs, re, sys, os, datetime, time, io, collections, ssl

class JDMAuto:
    def __init__(self, username, password=None):
        self.username = username
        self._password = password
        self.session = kisrequest.Session()
        cookie_filename = os.path.join('cookies', self.username+'.m.txt')
        kisrequest.fix_cookiefile(cookie_filename)
        self.session.load_filecookiejar(cookie_filename, style='moz')
        #self.session.set_default_context()
        #self.session.load_context(cafile='jd.pem')

    @property
    def password(self):
        if not self._password:
            self.log()
            self._password = getpass.getpass('请输入密码:').strip()
        return self._password

    def log(self, msg=''):
        print('[{0}][{1}]{2}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), self.username, msg))

    def _dict_str2(self, data, data_type, keys=None):
        for key in keys or data.keys():
            data[key] = float(data[key])
        return data

    def load_context(self, cafile='jd.pem'):
        """ for multiprocess.Process, pickle use. """
        self.session.set_default_context()
        self.session.load_context(cafile=cafile)

    def save_cookies(self):
        self.session.cookiejar.save()

    def unicode_escape_decode(self, text):
        return codecs.unicode_escape_decode(text)[0]

    def get_server_datetime(self):
        #time_str = self.session.get('http://passport.jd.com/loginservice.aspx?method=Login').get_header('Date')
        time_str = self.session.get('http://m.jd.com').get_header('Date')
        server_datetime = datetime.datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S GMT') + datetime.timedelta(hours=8)
        return server_datetime

    def time_stamp(self, key='yys'):
        return {key: int(time.time()*1000)}

    def input_verify(self, url, params=None, data=None, headers=None, saved='verify.jpg'):
        #img_url = 'https://plogin.m.jd.com/cgi-bin/m/authcode?mod=login'
        request_params = {'yys': int(time.time()*1000)}
        if params: request_params.update(params)
        with open(saved, 'wb') as f:
            f.write(self.session.request(url, params=request_params, data=data, headers=headers).content)
        subprocess.Popen('rundll32.exe shimgvw.dll,ImageView_Fullscreen '+os.path.abspath(saved))
        self.log()
        return input('请输入验证码:').strip()

    def login(self):
        """ login with cookies. """
        url = 'https://passport.m.jd.com/user/login.action?returnurl=http://m.jd.com?indexloc=1'
        self.session.get(url)
        #reg = re.compile(r'sid=([^"\']+)')
        #html = self.session.get(url).get_text()
        #return reg.search(html).group(1)

    def check_logined(self):
        url = 'http://home.m.jd.com'
        text = self.session.get(url).get_text()
        return text.find('我的京东')>=0

    def get_seckill_taps(self):
        """ 返回 OrderedDict: [(tap, gid),...]. """
        url = 'http://m.jd.com/seckill/seckillList.action'
        reg = re.compile(r'"MHandSecKill_Tag" report-eventparam="(\d+)点场_(\d+)')
        html = self.session.get(url).get_text()
        return collections.OrderedDict(reg.findall(html))

    def get_seckill_products_iter(self, gid):
        """ 返回某整点场下秒杀的商品列表. """
        url = 'http://m.jd.com/seckill/seckillList.action?gid={0}'.format(gid)
        reg = re.compile(r'<a class="J_ping" report-eventid="MHandSecKill_Commodity" report-eventparam="\d+点场_\d+_(?P<product_id>[^"]+)" href="(?P<url>[^"]+)">\s*<img src="(?P<img_url>[^"]+)">\s*<p class="g-title">(?P<title>[^<]+)</p>\s*<p class="g-price">￥(?P<price>[\d\.]+)</p>\s*<p class="g-price-odd"><del>￥(?P<price_odd>[\d\.]+)</del></p>\s*<span class="count">(?P<discount>[\d\.]+)折</span>', re.S)
        html = self.session.get(url).get_text()
        for re_match in reg.finditer(html):
            product = re_match.groupdict()
            self._dict_str2(product, data_type=float, keys=['price', 'price_odd', 'discount'])
            yield product

    def get_addresses(self):
        url = 'http://p.m.jd.com/norder/address.action'
        html = self.session.get(url).get_text()
        reg = re.compile(r'javascript:selectAddress\((?P<address_id>\d+)\)">\s*<div [^>]+>\s*<span>(?P<name>[^<]+)</span>\s*<strong>(?P<phone>[^<]+)</strong>\s*</div>\s*<div class="mc">\s*<p>\s*(?:<i class="sitem-tip">[^>]+>\s*)*(?P<detail>[^\n\r]+)', re.S)
        addresses = []
        for re_match in reg.finditer(html):
            addresses.append(re_match.groupdict())
        return addresses

    def get_order_sid(self, product_id, num=1):
        url = 'http://p.m.jd.com/norder/order.action?wareId={0}&wareNum={1}&enterOrder=true'.format(product_id, num)
        reg = re.compile(r'sid=([^"\']+)')
        html = self.session.get(url).get_text()
        return reg.search(html).group(1)

    def get_pay_shipments(self):
        url = 'http://p.m.jd.com/norder/payShipment.action'
        html = self.session.get(url).get_text()

    def save_pay_shipment(self, sid, data):
        url = 'http://p.m.jd.com/norder/savePaymentShipment.action?sid={0}'.format(sid)
        self.session.post(url, data=data)

    def is_picksite_full(self, picksite_id, sid, _text=None):
        """ 返回自提点的数据. 判断是否已满. 打开订单页面后再调用. """
        if int(picksite_id)<=1000: return False # 自提站永远不满
        if not _text:
            url = 'http://p.m.jd.com/norder/payShipment.action?sid={0}'.format(sid)
            _text = self.session.get(url).get_text()
        return _text.find('<option id="{0}"'.format(picksite_id))<0

    def pick_used_picksite(self, picksites, sid, default=None):
        """ 从备选的自提点picksites中挑选一个可用的自提点. 打开订单页面后再调用. """
        url = 'http://p.m.jd.com/norder/payShipment.action?sid={0}'.format(sid)
        text = self.session.get(url).get_text()
        for picksite in picksites:
            result = self.is_picksite_full(picksite, sid, _text=text)
            if not result: return picksite
        return default

    #def pre_order(self, url):
        #reg = re.compile(r'sid=(?P<sid>[^"]+)')
        #html = self.session.get(url).get_text()
        #return reg.search(html).groupdict()

    def refresh_ordered_price(self, sid):
        url = 'http://p.m.jd.com/norder/commodityInfo.action?sid={0}'.format(sid)
        html = self.session.get(url).get_text()
        reg = re.compile(r'cost-price">\s*￥([\d\.]+)', re.S)
        return float(reg.search(html).group(1))

    def get_product_name(self, product_id):
        url = 'http://item.m.jd.com/product/{0}.html'.format(product_id)
        html = self.session.get(url).get_text()
        reg = re.compile(r'<meta name="keywords" CONTENT="([^"]+)', re.I)
        return reg.search(html).group(1)

    def order(self, sid, product_id, num=1):
        #url = 'http://p.m.jd.com/norder/order.action?wareId=1928296&wareNum=1&enterOrder=true'
        url = 'http://p.m.jd.com/norder/order.action?wareId={0}&wareNum={1}&enterOrder=true'.format(product_id, num)
        self.session.get(url) # 再次进入填写订单页面.
        url = 'http://p.m.jd.com/norder/submit.action?sid={0}'.format(sid)
        data = {
            'stockStatusValue': '无货',
            'paymentType': 4,
            'securityPayPassword': '',
            'mixPayMent': 'false',
            'flowType': '',
        }
        html = self.session.post(url, data=data, headers=[('Referer', url)]).get_text()
        with open(os.path.join('logs', str(int(time.time()*1000000))+'.html'), 'w', newline='\n') as f:
            f.write(html)
        if html.find('正在进入收银台')>=0:
            return 1
        elif html.find('只能抢购一件')>=0:
            return 0
        return -1
