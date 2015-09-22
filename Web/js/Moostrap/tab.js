Moostrap.Tab = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'tab',
        selector: '[data-toggle=tab], [data-toggle=pill]',
        duration: 150
    },

    initialize: function(element, tab_nav, options){
        this.parent(element, options)
        this.tab_nav = tab_nav
        this.container = this._get_container() // getParent('li')
        this.content = this._get_content()
        this.dropdown = this._get_dropdown() // 判断是否Dropdown里的项. 返回的是一个 $(.dropdown)
    },

    toElement: function(){
        return this.container
    },

    _get_container: function(){
        return this.element.getParent('li')
    },

    _get_content: function(){
        return this.get_target(this.element)
    },

    // 判断是否dropdown里的项, 返回element
    _get_dropdown: function(){
        return this.element.getParent('.dropdown')
    },

    is_active: function(){
        return this.container.hasClass('active')
    },

    is_disabled: function(){
        return this.element.match('.disabled, :disabled')
    },

    hide: function(){
        if(!this.is_active() || this.is_disabled()) return false
        this.fireEvent('hide')
        this.element.set('aria-expanded', false)
        this.container.removeClass('active')
        if(this.dropdown) this.dropdown.removeClass('active') 
        if(this.content.hasClass('fade')){
            this.content.removeClass('in');
            (function(){
                this.content.removeClass('active')
                this.fireEvent('hidden')
            }).delay(this.options.duration, this)
        }else{
            this.content.removeClass('active')
            this.fireEvent('hidden')
        }
        return true
    },

    show: function(){
        if(this.is_active()|| this.is_disabled()) return false
        this.fireEvent('show')
        this.element.set('aria-expanded', true)
        this.container.addClass('active');
        if(this.dropdown) this.dropdown.addClass('active') 
        if(this.content.hasClass('fade')){
            (function(){
                this.content.addClass('active')
                this.content.addClass('in')
                this.fireEvent('shown')
            }).delay(this.options.duration, this)
        }else{
            this.content.addClass('active')
            this.fireEvent('shown')
        }
        return true
    }
})


Moostrap.TabNav = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'tab_nav',
        selector: '.nav-tabs',
        duration: 150
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.active = this._get_active_tab()
    },

    _get_active_tab: function(){
        var tabs = this.element.getElements(Moostrap.Tab.prototype.options.selector).filter('.active')
        if(tabs.length) return this.get_create_tab(tab[0])
        return null
    },

    get_create_tab: function(tab){
        return tab.retrieve(Moostrap.Tab.prototype.options.store_name) || new Moostrap.Tab(tab, this)
    },

    get_tabs: function(){
        var tabs = this.element.getElements(Moostrap.Tab.prototype.options.selector)
        return tabs.map(function(item){
            return this.get_create_tab(item)
        }.bind(this))
    },

    hide: function(){
        if(!this.active) return false
        var action = this.active.hide()
        this.active = null
        return action
    },

    show: function(tab){
        tab = this.get_create_tab(tab)
        console.log(tab)
        console.log(this.active)
        if(tab==this.active) return false
        this.active && this.active.hide()
        var action = tab.show()
        this.active = tab
        return action
    }
})


window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay(ul.nav-tabs, ul.nav-pills)', function(e, target){
        e.preventDefault()
        if(!e.target.match('[data-toggle=tab], [data-toggle=pill]')) return
        var tab_nav = target.retrieve('tab_nav') || new Moostrap.TabNav(target)
        tab_nav.show(e.target)
    });
});
