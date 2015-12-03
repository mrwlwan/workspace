# coding=utf8

import jdlib, config
import sys, multiprocessing, datetime, time, sys

class JDProcess(multiprocessing.Process):
    def __init__(self, username, password=None):
        super().__init__()
        self.jd = jdlib.JDAuto(username, password)
        self.login_action()

    def login_action(self):
        if not self.jd.check_logined():
            self.jd.log('Cookie失效, 正重新密码登录...')
            self.jd.login()
            if not self.jd.check_logined():
                self.jd.log('登录失败!')
                sys.exit()
            else:
                self.jd.save_cookie()
        self.jd.log('登录成功!')

    def get_timedelta(self, target_datetime=None):
        """ 返回服务器的时间差. """
        timedelta = (target_datetime or datetime.datetime.now())-self.jd.get_server_datetime()
        #return timedelta.total_seconds()
        return timedelta

    def from_time_string(self, time_string=None):
        if not time_string:
            time_string = config.action_time
        today = datetime.date.today()
        return datetime.datetime.strptime(time_string, '%H:%M:%S').replace(today.year, today.month, today.day)

    def timedelta_str(self, timedelta):
        minutes, seconds = divmod(timedelta.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return '%s天%s小时%s分钟%s秒' % (days, hours, minutes, seconds)

    def signin_action(self):
        result = self.jd.signin()
        print(result)
        if result.get('success'):
            self.jd.log('签到成功获得%s个京币!' % result.get('result').get('jdnum'))
        else:
            self.jd.log('已经签到或者等级不够!')

    def lottery_action(self):
        target_datetime = self.from_time_string()
        timedelta = self.get_timedelta(target_datetime)
        sleep = max(0, timedelta.total_seconds()+config.delay)
        if sleep>0:
            self.jd.log('将在%s后开始抽奖...' % self.timedelta_str(timedelta))
            time.sleep(sleep)
        else:
            self.jd.log('过期, 请重新设置抽奖时间.')
            sys.exit()
        #result = self.jd.lottery('http://sale.jd.com/act/p0l6LogbW5ZskA.html?cpdad=1DLSUE')
        result = self.jd.lottery(config.url)
        if result:
            self.jd.log(result.get('data').get('promptMsg'))
        else:
            self.jd.log('抽奖机会已经用完, 请等下一个整点机会!')

    def run(self):
        for action in config.actions:
            getattr(self, action+'_action')()


if __name__ == '__main__':
    processes = []
    for account in config.accounts:
        process = JDProcess(*account)
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
