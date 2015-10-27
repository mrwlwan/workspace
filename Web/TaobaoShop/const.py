#coding=utf8

# 默认值
default_value = {
    'category': '未分类',
    'sku_status': '正常',
    'status': '上架',
    'per_page': 20,
    'urgent_threshold': 30,
    'normal_begin': 3,
    'expiry_days': 1,
    'good_sale_threshold': 10, #销售好评销售量
}

# 尺码排序
size_order = {'xs': 0, 's': 1, 'm': 2, 'l': 3, 'xl': 4, 'xxl': 5, 'xxxl': 6, 'xxxxl': 7}

# 分类名称
category_list = ('未分类', '夏装', '春秋冬装', '饰品', '邮费', '其它')

# 库存状态名称
sku_status_list = ('正常', '紧张', '缺货', '卖空')

# 状态名称
status_list = ('上架', '下架', '回收站')

# 搜索字段
query_columns_dict = (("货号", 'code'), ("标题", 'subject'), ("品牌", 'brand'), ("面料", 'fabric'), ("成分", 'fabric_content'), ("图案", 'pattern'), ("备注", 'remarks'))

# 排序字段
sort_columns_dict = (('标题', 'subject'), ('分类', 'category'), ('货号', 'code'), ('品牌', 'brand'), ('图案', 'pattern'), ('面料', 'fabric'), ('成分', 'fabric_content'), ('含量', 'fabric_scale'), ('库存', 'sku_status'), ('销量', 'sale_count_diff'), ('状态', 'status'))

# 背景色映射
color = {
    '紧张': 'info',
    '缺货': 'warning',
    '卖空': 'danger',
    '下架': 'warning',
    '回收站': 'danger',
}
