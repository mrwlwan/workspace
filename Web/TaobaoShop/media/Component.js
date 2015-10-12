define([], function(){
    var Component = new Class({
        Implements: [Options],
        store_name: 'component',
        selector: undefined,
        options: {},

        initialize: function(element, options){
            this.element = element
            this.setOptions(options)
            this.store()
        },

        toElement: function(){
            return this.element
        },

        store: function(){
            this.element.store(this.store_name, this)
        },

        retrieve: function(name){ // 方便取得参数target的component. target为Elemnet或者Component,都可以直接调用.retrieve
            return this;
        }
    })

    return Component
})
