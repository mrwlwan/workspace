Moostrap.DropDown = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'dropdown',
        selector: '[data-toggle=dropdown]',
        backdrop: '.dropdown-backdrop' // 手机端
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.container = this.get_container();
        this.menu = this.get_menu();
        this.menu.addEvent('keydown:relay(a)', this._menu_keydown_handler.bind(this))
    },
    
    _menu_keydown_handler: function(e, targer){
        if(e.code==27){
            this.clear()
            this.element.focus()
            return
        }
        if(this.is_active() && (e.code==38 || e.code==40)){ // up or down
            var items = this.menu.getElements('li:not(.disabled) a')
            if(!items.length) return
            var index = items.indexOf(e.target).max(0)
            if (e.code == 38 && index > 0)                 index--         // up
            if (e.code == 40 && index < items.length - 1) index++         // down
            if (!~index)                                    index = 0
            items[index].focus()
        }
    },

    get_container: function(toggler){
        toggler = toggler || this.element // clear() 须要带参数
        var container = this.get_target(toggler)
        return container || toggler.getParent()
    },

    get_menu: function(){
        return this.container.getElement('.dropdown-menu')
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

    clear: function(){
        $$(this.options.backdrop).destroy(); // 手机端
        //$$(this.options.selector).each(function(toggler){
            //var container = this.get_container(toggler);
            //if(!container.hasClass('open')) return;
            //toggler.set('aria-expanded', false);
            //container.removeClass('open');
        //}.bind(this));
        // 下面性能更好点,但存在使用限制
        if(Moostrap.DropDown.active){
            Moostrap.DropDown.active.element.set('aria-expanded', false);
            Moostrap.DropDown.active.container.removeClass('open');
            Moostrap.DropDown.active = null
        }
    },

    toggle: function(){
        if(this.element.match('.disabled, :disabled')) return
        if(this.is_active()){
            this.fireEvent('hide')
            this.clear()
            this.fireEvent('hidden')
        }else{
            this.clear()
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
            this.fireEvent('shown')
        }
        return false
    },
});

Moostrap.DropDown.active = null


window.addEvent('domready', function(){
    $(document).addEvent('click', function(e){
        //if(/input|textarea/i.test(e.target.tagName) && e.target.getParent('.dropdown')) return
        //Moostrap.DropDown.prototype.clear()
        // 下面的性能好, 但有使用限制, 尤其与其它库一起使用可能会出问题,留意!
        if(!Moostrap.DropDown.active || /input|textarea/i.test(e.target.tagName) && e.target.getParent('.dropdown')) return
        Moostrap.DropDown.active.clear()
        
    })
    $(document.body).addEvent('click:relay([data-toggle=dropdown])', function(e, target){
        e.stop()
        var dropdown = target.retrieve('dropdown')
        if(!dropdown){
            dropdown = new Moostrap.DropDown(target);
            target.store('dropdown', dropdown)
        }
        dropdown.toggle()
    }).addEvent('keydown:relay([data-toggle=dropdown])', function(e, target){
        if(!/(38|40|27|32)/.test(e.code) || /input|textarea/i.test(e.target.tagName)) return
        e.stop()
        var dropdown = target.retrieve('dropdown')
        if(!dropdown){
            dropdown = new Moostrap.DropDown(target);
            target.store('dropdown', dropdown)
        }
        if(dropdown.is_active()){
            var items = dropdown.menu.getElements('li:not(.disabled) a')
            if(!items.length) return
            switch(e.code){
                case 38:
                    items[items.length-1].focus()
                    break
                case 40:
                    items[0].focus()
            }
        }else{
            dropdown.toggle()
        }
    })
});
