define({
    colors_map: {
        '紧张': 'info',
        '缺货': 'warning',
        '卖空': 'danger',
        '下架': 'warning',
        '回收站': 'danger'
    },
    category_list: ['未分类', '夏装', '春秋冬装', '饰品', '邮费', '其它'],
    status_list: ['上架', '下架'], // 删除'回收站'项, 非个人操作项, 更新时自动判断
    sku_status_list: ['正常', '紧张', '缺货', '卖空']
})
