window.addEvent('domready', function(){
    // 阻止底部导航栏.disabled按钮的默认单击事件.
    document.getElements('.pagination li.disabled a, .pagination li.active a').addEvent('click', function(e){
        e.preventDefault()
    })
})
