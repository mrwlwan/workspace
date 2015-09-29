Moostrap.ScrollSpyItem = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'scrollspy_item',
        offset: 0
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.target = this.get_target(this.element)
        this.container = this.element.getParent()
        this.dropdown = this._get_dropdown() // 判断是否dropdown里的项, 返回element
    },

    // 判断是否dropdown里的项, 返回element
    _get_dropdown: function(){
        return this.element.getParent('.dropdown')
    },

    get_top: function(){
        return this.target.getPosition().y-this.options.offset
    },

    is_active: function(){
        return this.container.hasClass('active')
    },

    activate: function(){
        if(this.is_active()) return false
        this.container.addClass('active');
        this.dropdown && this.dropdown.addClass('active');
        this.fireEvent('activate')
        return true
    },

    deactivate: function(){
        if(!this.is_active()) return false
        this.container.removeClass('active');
        this.dropdown && this.dropdown.removeClass('active');
        this.fireEvent('deactivate')
        return true
    }
})


Moostrap.ScrollSpy = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'scrollspy',
        selector: '[data-spy=scroll]',
        offset: null, // 计算滚动位置时相对于顶部的偏移量
        item_selector: 'li > a:not(.dropdown-toggle)'
    },
    
    initialize: function(element, options){
        this.parent(element, options)
        this.scroll_element = this.element.match(document.body) && $(window) || this.element
        this.offset = typeOf(this.options.offset)=='number' ? this.options.offset : this.element.get('data-offset').toInt()
        this.scrollspy_items = this.get_scrollspy_items()
        this.active = this.get_scroll_target()
        if(this.active) this.active.activate()
        this.init_events()
    },

    init_events: function(){
        this.scroll_element.addEvent('scroll', function(e){
            var scroll_target = this.get_scroll_target()
            if(scroll_target){
                if(scroll_target == this.activate) return
                this.active && this.active.deactivate()
                scroll_target.activate()
                this.active = scroll_target
            }else if(this.active){
                this.active.deactivate()
                this.active = null
            }
        }.bind(this))
    },

    _sort_scrollspy_items: function(items){
        items.sort(function(a, b){
            return a.get_top()-b.get_top()
        })
    },

    get_scroll_target: function(){
        var scroll_top = this.scroll_element.getScroll().y
        var items = this.scrollspy_items
        for(var i=0; i<items.length; i++){
            if(scroll_top<items[0].get_top()) return null
            if(scroll_top>=items[items.length-1].get_top()) return items[items.length-1]
            if(scroll_top>=items[i].get_top() && scroll_top<items[i+1].get_top()) return items[i]
        }
        return null
    },
    
    get_create_item: function(el){
        return el.retrieve(Moostrap.ScrollSpyItem.prototype.options.store_name) || new Moostrap.ScrollSpyItem(el, {offset: this.offset})
    },

    get_scrollspy_items: function(){
        var items = document.getElements(this.element.get('data-target')+' '+ this.options.item_selector)
                            .map(function(el){
                                return this.get_create_item(el)
                            }.bind(this))
        this._sort_scrollspy_items(items)
        return items
    },

    get_scroll_height: function(){
        return this.element.scrollHeight
    },

    // html结构发生变化时,可以调用
    refresh: function(){
        this.scrollspy_items = this.get_scrollspy_items()
    },
})


window.addEvent('domready', function(){
    $$(Moostrap.ScrollSpy.prototype.options.selector).each(function(el){
        new Moostrap.ScrollSpy(el)
    })
})
