var Moostrap = {
    transition: null,

    // like jQuery one
    add_event_once: function(el, event_name, func){
        var f = function(){
            func()
            el.removeEvent(event_name, f)
        }
        el.addEvent(event_name, f)
        return el
    },

    get_target: function(el){
        var selector = el.get('data-target')
        if(!selector){
            selector = el.get('href')
            selector = selector && /#[A-Za-z]/.test(selector) && selector.replace(/.*(?=#[^\s]*$)/, '') // strip for ie7
        }
        return selector && document.getElement(selector) || null
    },

    get_outer_height: function(el){
        return el.getSize().y+el.getStyle('margin-top').toInt()+el.getStyle('margin-bottom').toInt()
    }
};

Moostrap.Component = new Class({
    Implements: [Options, Events],
    options: {
        duration: 150,
        store_name: 'component',
        selector: undefined
    },

    // element 是必传参数. 一般与 options.selector 匹配. 
    initialize: function(element, options){
        this.element = element
        this.setOptions(options)
        this.store()
    },

    toElement: function(){
        return this.element
    },

    store: function(){
        this.element.store(this.options.store_name, this)
    },

    retrieve: function(name){ // 方便取得参数target的component. target为Elemnet或者Component,都可以直接调用.retrieve
        return this;
    },

    // 只获取已创建的对象(考虑取代这个方法)
    get_components: function(els, name){
        var components = []
        els.each(function(item){
            var component = item.retrieve(name)
            if(component) components.push(component)
        })
        return components
    },

    get_target: Moostrap.get_target
});
