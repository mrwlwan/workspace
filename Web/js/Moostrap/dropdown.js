Moostrap.DropDownMenu = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'dropdown_menu',
        selector: '.dropdown-menu'
    },

    initialize: function(element, dropdown, options){
        this.parent(element, options)
        this.dropdown = dropdown
        this.element.addEvent('keydown:relay(li)', this._keydown_listener.bind(this))
    },

    // enabled参数指定返回非.disabled的items
    get_items: function(ignore){
        if(ignore){
            return this.element.getElements('li:not(.disable)').filter(function(item){
                return item.getElement('a') 
            })
        }
        return this.element.getElements('li')
    },

    focus: function(index, items){ // items 方便其它内部方法调用
        items = items || this.get_items(true)
        if(!items.length) return
        if(index<0) index = items.length+index
        items[index].getElement('a').focus()
    },

    _keydown_listener: function(e, target){
        target = target
        if(e.code==27){ // ESC
            this.dropdown.hide()
            return
        }
        if(this.dropdown.is_active() && (e.code==38 || e.code==40)){ // up or down
            var items = this.get_items(true)
            if(!items.length) return
            var index = items.indexOf(target).max(0)
            if (e.code == 38 && index > 0)                 index--         // up
            if (e.code == 40 && index < items.length - 1) index++         // down
            if (!~index)                                    index = 0
            //items[index].focus()
            this.focus(index)
        }
    }
})        


Moostrap.DropDown = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'dropdown',
        selector: '[data-toggle=dropdown]',
        backdrop: '.dropdown-backdrop' // 手机端
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.container = this._get_container();
        this.menu = this._get_menu();
    },
    
    _get_container: function(){
        var container = this.get_target(this.element)
        return container || this.element.getParent()
    },

    _get_menu: function(){
        var el = this.container.getElement('.dropdown-menu')
        return el.retrieve(Moostrap.DropDownMenu.prototype.options.store_name) || new Moostrap.DropDownMenu(el, this)
    },

    get_previous: function(ignore){ // 搜寻左边的dropdown.
        var previous = this.container.getPrevious('.dropdown')
        if(!previous) return null
        var other_target = previous.getElement('[data-toggle=dropdown]')
        var dropdown = other_target.retrieve(Moostrap.DropDown.prototype.options.store_name) || new Moostrap.DropDown(other_target)
        if(ignore && dropdown.is_disabled()) return dropdown.get_previous(ignore)
        return dropdown
    },

    get_next: function(ignore){ // 搜寻右边的dropdown.
        var next = this.container.getNext('.dropdown')
        if(!next) return null
        var other_target = next.getElement('[data-toggle=dropdown]')
        var dropdown = other_target.retrieve(Moostrap.DropDown.prototype.options.store_name) || new Moostrap.DropDown(other_target)
        if(ignore && dropdown.is_disabled()) return dropdown.get_next(ignore)
        return dropdown
    },

    get_items: function(enable){
        if(enable){
            return this.menu.getElements('li:not(.disable)')
        }
        return this.menu.getElements('li')
    },


    is_active: function(){
        return this.container.hasClass('open')
    },

    is_disabled: function(){
        return this.element.match('.disabled, :disabled')
    },

    focus: function(){
        return this.element.focus()
    },

    hide: function(){
        if(!this.is_active() || this.is_disabled()) return false
        this.fireEvent('hide')
        $$(this.options.backdrop).destroy(); // 手机端
        this.element.set('aria-expanded', false)
        this.container.removeClass('open')
        Moostrap.DropDown.active = null
        this.focus()
        this.fireEvent('hidden')
        return true
    },

    show: function(){
        if(this.is_active() || this.is_disabled()) return false
        this.fireEvent('show')
        Moostrap.DropDown.clear()
        this.fireEvent('show')
        if('ontouchstart' in document.documentElement && !this.container.match('.navbar-nav') && !this.container.getParent('.navbar-nav')){
            // if mobile we use a backdrop because click events don't delegate
            var new_el = new Element(document.createElement('div'))
            new_el.addClass('dropdown-backdrop')
                .inject(this.element, 'after')
                .addEvent('click', this.clear.bind(this))
        }
        //this.element.fireEvent('focus')
        this.element.set('aria-expanded', true)
        this.container.addClass('open')
        Moostrap.DropDown.active = this
        this.focus()
        this.fireEvent('shown')
        return true
    },

    toggle: function(){
        var action = this.is_active() ? this.hide() : this.show()
        this.fireEvent('toggle')
        return action
    }
});

Moostrap.DropDown.active = null

Moostrap.DropDown.clear = function(){
    if(!Moostrap.DropDown.active) return false
    var dropdown = Moostrap.DropDown.active
    dropdown.hide()
    Moostrap.DropDown.active = null
    return true
}


window.addEvent('domready', function(){
    $(document).addEvent('click', function(e){
        if(!Moostrap.DropDown.active || /input|textarea/i.test(e.target.tagName) && e.target.getParent('.dropdown')) return
        Moostrap.DropDown.clear()        
    })
    $(document.body).addEvent('click:relay([data-toggle=dropdown])', function(e, target){
        e.stop()
        var dropdown = target.retrieve(Moostrap.DropDown.prototype.options.store_name) || new Moostrap.DropDown(target)
        dropdown.toggle()
    }).addEvent('keydown:relay([data-toggle=dropdown])', function(e, target){
        if(!/(37|38|39|40|27|32|13)/.test(e.code) || /input|textarea/i.test(e.target.tagName)) return
        e.stop()
        var dropdown = target.retrieve(Moostrap.DropDown.prototype.options.store_name) || new Moostrap.DropDown(target)
        if(e.code==37) dropdown = dropdown.get_previous(true)
        if(e.code==39) dropdown = dropdown.get_next(true)
        if(!dropdown) return
        if(dropdown.is_active()){
            switch(e.code){
                case 27:
                    dropdown.hide()
                    break
                case 38:
                    dropdown.menu.focus(-1)
                    break
                case 40:
                    dropdown.menu.focus(0)
            }
        }else{
            dropdown.show()
        }
    })
});
