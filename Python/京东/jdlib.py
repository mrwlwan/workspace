# coding=utf8

import kisrequest
import codecs, re, sys, os, getpass, datetime, time, subprocess

class JDAuto:
    def __init__(self, username, password=None):
        self.username = username
        self._password = password
        self.session = kisrequest.Session()
        cookie_path = os.path.join('cookies', self.username+'.txt')
        self.session.load_filecookiejar(cookie_path, style='lwp')
        #self.session.add_header('Referer', 'https://passport.jd.com/uc/login?ltype=logout')

    @property
    def password(self):
        if not self._password:
            self.log()
            self._password = getpass.getpass('请输入密码:').strip()
        return self._password

    def log(self, msg=''):
        print('[{0}][{1}]{2}'.format(datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'), self.username, msg))

    def save_cookie(self):
        self.session.cookiejar.save()

    def unicode_escape_decode(self, text):
        return codecs.unicode_escape_decode(text)[0]

    def get_server_datetime(self):
        time_str = self.session.get('http://passport.jd.com/loginservice.aspx?method=Login').get_header('Date')
        server_datetime = datetime.datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S GMT') + datetime.timedelta(hours=8)
        return server_datetime

    def time_stamp(self, key='yys'):
        return {key: int(time.time()*1000)}

    #def input_verify(self, url, params=None, data=None, saved='verify.jpg'):
    def input_verify(self, uuid, saved='verify.jpg'):
        img_url = 'https://authcode.jd.com/verify/image?a=1&acid={0}&uid={0}&yys={1}'.format(uuid, int(time.time()*1000))
        #request_params = {'yys': int(time.time()*1000)}
        #if params: request_params.update(params)
        with open(saved, 'wb') as f:
            f.write(self.session.get(img_url, headers=[('Referer', 'https://passport.jd.com/uc/login?ltype=logout')]).content)
            #f.write(self.session.request(url, params=request_params, data=data).content))
        subprocess.Popen('rundll32.exe shimgvw.dll,ImageView_Fullscreen '+os.path.abspath(saved))
        self.log()
        return input('请输入验证码:').strip()

    def pre_login_data(self):
        html = self.session.get('https://passport.jd.com/new/login.aspx', headers=[('Referer', 'https://passport.jd.com/uc/login?ltype=logout')]).get_text()
        uuid = re.search(r'name="uuid" value="([^"]+)', html).group(1)
        key, value = re.search(r'<input type="hidden" name="([^"]+)" value="([^"]+)', html).groups()
        return {'uuid': uuid, key: value}

    def need_verify(self, uuid):
        response = self.session.post('https://passport.jd.com/uc/showAuthCode?version=2015', data={'loginName': self.username}, headers=[('Referer', 'https://passport.jd.com/uc/login?ltype=logout')])
        return response.get_text().find('true')>=0

    def login(self):
        pre_data = self.pre_login_data()
        url = 'https://passport.jd.com/uc/loginService?ReturnUrl=http%3A%2F%2Fwww.jd.com%2F&version=2015&uuid={0}'.format(pre_data['uuid'])
        data = {
            'machineNet': '',
            'machineCpu': '',
            'machineDisk': '',
            'loginname': self.username,
            'nloginpwd': self.password,
            'loginpwd': self.password,
            'chkRememberMe': 'on',
            'authcode': '',
        }
        data.update(pre_data)
        while 1:
            if self.need_verify(pre_data['uuid']):
                while 1:
                    authcode = self.input_verify(pre_data['uuid'], saved=os.path.join('temp', 'verify_'+self.username+'.jpg'))
                    if authcode:
                        data['authcode'] = authcode
                        break
            response = self.session.post(url, data=data, headers=[('Referer', 'https://passport.jd.com/uc/login?ltype=logout')], encoding='gbk')
            u_text = self.unicode_escape_decode(response.get_text())
            if u_text.find('success')>=0: break
            if u_text.find('请输入验证码')<0: return False
        return True

    def check_logined(self):
        url = 'http://passport.jd.com/loginservice.aspx?method=Login'
        result = self.session.get(url, headers=[('Referer', 'https://passport.jd.com/uc/login?ltype=logout')]).get_json()
        #{"Identity":{"Unick":"南海居士","Name":"南海居士","IsAuthenticated":true}}
        return result.get('Identity').get('IsAuthenticated')

    def signin(self):
        """ 签到. """
        url = 'http://vip.jd.com/index.php?mod=Vip.Ajax&action=signIn'
        # jQuery9669098({"success":true,"result":{"jdnum":5}})
        return self.session.get(url).get_json()

    def pre_lottery_data(self, url):
        html = self.session.get(url).get_text(errors='ignore')
        #return {'lotteryCode': re.search(r'"lotterycode=\s*([^"]+)', html).group(1)}
        return dict(zip(('referer', 'lotteryCode'), re.search(r'classid=".+?src="([^"]+).+?lotterycode=([^"]+)', html).groups()))

    def lottery(self, page_url):
        """ 抽奖. """
        data = self.pre_lottery_data(page_url)
        #data.update(self.time_stamp(key='v'))
        headers = [('Referer', data.pop('referer'))]
        chance_url = 'http://l.activity.jd.com/lottery/lottery_chance.action'
        while 1:
            try:
                response = self.session.get(chance_url, params=data, headers=headers)
                print(response.get_text())
                #{"data":{"chances":0,"lotteryCode":"c364a4e9-bca8-42a1-934b-e923011a7686","promptMsg":"很遗憾，今日抽奖次数用完！","userPin":"南海居士"},"responseCode":"0000","responseMessage":"request_success"}
                result = response.get_json()
                if result.get('data').get('chances')<=0: return None
                start_url = 'http://l.activity.jd.com/lottery/lottery_start.action'
        #while 1:
            #try:
                result = self.session.get(start_url, params=data, headers=headers)
                print(result.get_text())
                result = result.get_json()
                break
            except:
                self.log('系统繁忙, 1秒后继续...')
                time.sleep(1)
        return result
