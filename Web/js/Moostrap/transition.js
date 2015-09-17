// 返回支持的CSS3 transitionend 事件名. 文件 include 在 moostrap.js 之后
Moostrap.transitionend = function(){
    var transitionend_event_names = {
      WebkitTransition : 'webkitTransitionEnd',
      MozTransition    : 'transitionend',
      OTransition      : 'oTransitionEnd otransitionend',
      transition       : 'transitionend'
    }
    for(var name in transitionend_event_names){
      if(document.body.style[name] !== undefined) return transitionend_event_names[name]
    }
    return false // explicit for ie8 (  ._.)
}();
