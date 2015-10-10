window.addEvent('domready', function(){
    // 阻止底部导航栏.disabled按钮的默认单击事件.
    document.getElements('nav li.disabled a').addEvent('click', function(e){
        e.preventDefault()
    })

    var sort_select = document.id('product_navbar').getElement('select[name=sort_columns]')
    var desc_checkbox = document.id('product_navbar').getElement('input[name=desc]')
    document.getElement('.products-table thead').addEvent('click:relay(th.sortable)', function(e, target){
        e.preventDefault()
        var column = target.get('text')
        sort_select.getElements('option').some(function(item){
            if(item.get('text')!=column) return false
            if(item.match(':selected')){
                desc_checkbox.set('checked', !desc_checkbox.get('checked'))
            }else{
                item.set('selected', true)
            }
            return true
        })
    })
})
