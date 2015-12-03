# coding=utf8

import collections

usernames  = ['风铃飘叶', ]

# 使用任务中的时间, 否则立即开始秒杀
action_time_check = True

# 使用京东默认自动提供的送货方式, True 时下面部分有关送货方式的参数将无效.
auto_order_pay_shipment = False

# 下单选用自提点, 按先后顺序
order_picksites = collections.OrderedDict([
    ('东方国际星座自提柜', 4087),
    #('虎门龙眼广场自提柜', 4092),
    ('鸿富楼自提柜', 5036),
    ('南城华凯大厦自提柜', 4095),
    ('东城金城大厦自提柜', 5035),
    ('东城中心A2区自提柜', 5034),
    ('虎门站', 731),
    #('时代广场站', 76),
])

# 京东配送
order_pay_shipment = {
    'order.shipmentId': 64, # 自提: 64; 京东快递: 65.
    'order.promiseType': 1,
    'order.promiseTimeRange': '09:00-15:00', # 京东快递送货时间段: 09:00-15:00, 15:00-19:00.
    'order.promiseSendPay': '{"1":1,"35":1,"30":1}', # 一般不用改
    'order.promiseMessage': '2015-12-4 (周五) 09:00-15:00',
    'order.promiseDate': '2015-12-4', # 京东快递送货日期
    'order.pickSiteId': '', # 自提点 ID
    'order.pickDateId': '2015-12-04', # 自提日期
    'order.paymentId': 4, # 在线支付: 4; 货到付款: 1.
}

# 第三方配送
#order_pay_shipment = {
    #'order.sopOtherShipmentId': 67,
    #'order.paymentId': 4,
#}

# 选择自提方式时, 当所选自提点全满, 参数设为 False 时, 自动转换为京东快递
order_just_picksite = True

tasks = [
    {
        'action_time': '20:00:00',
        'products': [
            #{
                #'product_id': '1208753', #
                #'num': 1, # 购买数量
                #'price': 39,
            #},
            {
                'product_id': '1084356', # 腾达路由 20:00
                'num': 1, # 购买数量
                'price': 13,
            },
        ],
    },
]

# 用于网络延迟时间
delay = -1

# 下单尝试次数
times = 3

# 重复时间间隔
interval = 1

# 最后X秒前重新获取服务器时间. 可以设置此时间点, 让程序暂时中止sleep等待, 处理一些事务
last_sleep_sceonds = 60
