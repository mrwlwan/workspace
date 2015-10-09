window.addEvent('domready', function(){
    // 阻止底部导航栏.disabled按钮的默认单击事件.
    document.getElements('nav li.disabled a').addEvent('click', function(e){
        e.preventDefault()
    })
})
