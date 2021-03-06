// 返回支持的CSS3 transitionend 事件名. 文件 include 在 moostrap.js 之后
Moostrap.transition = function(){
    var transitionend_event_names = {
      WebkitTransition : 'webkitTransitionEnd',
      MozTransition    : 'transitionend',
      OTransition      : 'oTransitionEnd otransitionend',
      transition       : 'transitionend'
    }
    var transitionend = null
    for(var name in transitionend_event_names){
        if(document.body.style[name] !== undefined){
            transitionend = transitionend_event_names[name]
            break
        }
    }
    if(!transitionend) return false // explicit for ie8 (  ._.)
    Element.NativeEvents[transitionend] = 2
    return transitionend
}();

Moostrap.emulate_transition = function(duration, target){
    (function(){
        target.fireEvent(Moostrap.transition)
    }).delay(duration)
}
