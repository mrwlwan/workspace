# coding=utf8

import config_m as config
import jdmlib
import sys, multiprocessing, datetime, time, sys


class JDMProcess(multiprocessing.Process):
    def __init__(self, username):
        super().__init__()
        self.jd = jdmlib.JDMAuto(username)

    def login(self):
        self.jd.login()
        return self.jd.check_logined()

    def get_timedelta(self, target_datetime=None):
        """ 返回服务器的时间差. """
        timedelta = (target_datetime or datetime.datetime.now())-self.jd.get_server_datetime()
        #return timedelta.total_seconds()
        return timedelta

    def from_time_string(self, time_string):
        today = datetime.date.today()
        return datetime.datetime.strptime(time_string, '%H:%M:%S').replace(today.year, today.month, today.day)

    def timedelta_str(self, timedelta):
        minutes, seconds = divmod(timedelta.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return '%d天%d小时%d分钟%d秒' % (days, hours, minutes, seconds)

    def check_price(self, sid, product):
        for i in range(config.times):
            price = self.jd.refresh_ordered_price(sid)
            if price<=product.get('price'): return True
            self.jd.log('价格不符1秒后继续(目前价格: %s, 目标价格: %s).' % (price, product.get('price')))
            time.sleep(config.interval)
        return False

    def parse_pay_shipment(self, sid):
        order_pay_shipment = config.order_pay_shipment.copy()
        if order_pay_shipment.get('order.shipmentId')==64:
            picksite = self.jd.pick_used_picksite(config.order_picksites.values(), sid)
            if not picksite:
                self.jd.log('自提点已满!')
                if config.order_just_picksite:
                    return None
                order_pay_shipment['order.shipmentId'] = 65
            else:
                order_pay_shipment['order.pickSiteId'] = picksite
        return order_pay_shipment

    def save_pay_shipment(self, sid):
        if not config.auto_order_pay_shipment:
            order_pay_shipment = self.parse_pay_shipment(sid)
            if not order_pay_shipment: return False
            self.jd.save_pay_shipment(sid, order_pay_shipment)
        return True

    def wait4action(self, task, last_sleep=False):
        if config.action_time_check:
            target_datetime = self.from_time_string(task.get('action_time'))
            timedelta = self.get_timedelta(target_datetime)
            sleep = max(0, timedelta.total_seconds()+config.delay)
            if sleep<=0: return False
            self.jd.log('离开始还剩'+self.timedelta_str(timedelta)+'...')
            if last_sleep:
                if sleep>config.last_sleep_sceonds:
                    time.sleep(sleep-config.last_sleep_sceonds)
            else:
                time.sleep(sleep)
        return True

    def asert_exit(self, value, msg=None):
        if not value:
            msg and self.jd.log(msg)
            sys.exit()

    def order(self, sid, product):
        result = -1
        for i in range(config.times):
            result = self.jd.order(sid, product.get('product_id'), product.get('num'))
            if result>=0: break
            time.sleep(config.interval)
        return result

    def task_action(self, task):
        self.jd.log('抢购时间: {0}'.format(task.get('action_time')))
        for product in task.get('products'):
            self.jd.log('任务目标: {0}'.format(self.jd.get_product_name(product.get('product_id'))))
        self.asert_exit(self.wait4action(task, last_sleep=True), '过期, 请重新设置任务!')
        for product in task.get('products'):
            sid = self.jd.get_order_sid(product.get('product_id'), product.get('num'))
            self.asert_exit(self.save_pay_shipment(sid), '配送方式不符, 请重新设置任务!')
            self.jd.log('匹配配送方式成功...')
            self.asert_exit(self.wait4action(task), '过期, 请重新设置任务!')
            self.jd.log('开始抢购中...')
            if not self.check_price(sid, product):
                self.jd.log('价格不符, 请重新设置任务!')
                break
            self.jd.log('匹配价格成功...')
            result = self.order(sid, product)
            if result==1:
                self.jd.log('下单成功!')
            elif result==0:
                self.jd.log('重复下单!')
            elif result==-1:
                self.jd.log('下单失败! 请查看 log 文件!')

    def run(self):
        self.jd.load_context('temp/jd.pem') # 先调用
        self.asert_exit(self.login(), 'Cookies 失效, 请重新获取!')
        self.jd.log('登录成功!')
        for task in config.tasks:
            self.task_action(task)


if __name__ == '__main__':
    processes = []
    for username in config.usernames:
        process = JDMProcess(username)
        processes.append(process)
        process.start()
    for process in processes:
        process.join()

