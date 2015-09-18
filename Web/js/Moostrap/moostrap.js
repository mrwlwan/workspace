var Moostrap = {
    transition: null,

    get_target: function(el){
        var selector = el.get('data-target')
        if(!selector){
            selector = el.get('href')
            selector = selector && /#[A-Za-z]/.test(selector) && selector.replace(/.*(?=#[^\s]*$)/, '') // strip for ie7
        }
        return selector && $$(selector)[0] || null
    },

    // like jQuery one
    add_event_once: function(el, event_name, func){
        var f = function(){
            func()
            el.removeEvent(event_name, f)
        }
        el.addEvent(event_name, f)
        return el
    }        
};
