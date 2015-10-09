#coding=utf8

# 分类名称
category_list = ('未分类', '夏装', '春秋冬装', '饰品', '邮费', '其它')

# 库存状态名称
sku_status_list = ('正常', '紧张', '缺货', '卖空')

# 状态名称
status_list = ('上架', '下架', '回收站')

# 搜索字段
query_columns_list = (("货号", 'code'), ("标题", 'subject'), ("品牌", 'brand'), ("面料", 'fabric'), ("成分", 'fabric_content'), ("图案", 'pattern'), ("备注", 'remarks'))

# 背景色映射
color = {
    '紧张': 'info',
    '缺货': 'warning',
    '卖空': 'danger',
    '下架': 'warning',
    '回收站': 'danger',
}
