Moostrap.Collapse = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'collapse',
        selector: '[data-toggle=collapse]',
        target: null,
        duration: 350,
        delay: 10,
        accordion: null // Moostrap.Accordion
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.accordion = this.options.accordion
        this.panel = this._get_panel()
    },

    _get_panel: function(){
        return this.options.target ? (typeOf(this.options.target)=='function' && this.options.target(this) || document.getElement(this.options.target)) : this.get_target(this.element)
    },

    is_active: function(){
        return this.panel.hasClass('in')
    },

    show: function(ignore){
        if(!ignore && this.is_active()) return false
        this.fireEvent('show')
        this.element.removeClass('collapsed')
                    .set('aria-expanded', 'true')
        this.panel.addClass('in')
                  .addClass('collapsing')
        var panel_size = this.panel.getScrollSize()
        this.panel.setStyle('height', 0)
                  //.setStyle('height', 'auto')
        this.panel.setStyle.delay(this.options.delay, this.panel, ['height', panel_size.y]);
        (function(){
            this.panel.removeClass('collapsing')
            this.fireEvent('shown')
        }).delay(Moostrap.transition && (this.options.duration+this.options.delay) || 0, this)
        return true
    },

    hide: function(ignore){
        if(!ignore && !this.is_active()) return false
        this.fireEvent('hide')
        this.element.addClass('collapsed')
                    .set('aria-expanded', 'false')
        var panel_size = this.panel.getScrollSize()
        this.panel
            .setStyle('height', panel_size.y)
            .addClass('collapsing')
        this.panel.setStyle.delay(this.options.delay, this.panel, ['height', 0]);
        (function(){
            this.panel.removeClass('collapsing in')
            this.fireEvent('hidden')
        }).delay(Moostrap.transition && (this.options.duration+this.options.delay) || 0, this)
        return true
    },

    toggle: function(){
        if(this.is_active()){
            return this.hide(true)
        }else{
            return this.show(true)
        }
    }
})


Moostrap.Accordion = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'accordion',
        selector: '.panel-group'
    },

    initialize: function(element, options){
        this.parent(element, options)
    },

    retrieve_collapse: function(element){
        return element.retrieve(Moostrap.Collapse.prototype.options.store_name) || new Moostrap.Collapse(element, {accordion: this})
    },

    get_collapses: function(){
        return this.element.getElements(Moostrap.Collapse.prototype.options.selector).map(function(el){
            return this.retrieve_collapse(el)
        }.bind(this))
    },

    get_active: function(){
        var collapses = this.get_collapses()
        for(var i=0; i<collapses.length;i++){
            if(collapses[i].is_active()) return collapses[i]
        }
        return null
    },

    show: function(collapse, ignore){
        collapse = this.retrieve_collapse(collapse)
        if(!ignore && collapse.is_active()) return false
        collapse.show(ignore)
    },

    hide: function(collapse, ignore){
        collapse = this.retrieve_collapse(collapse)
        if(!ignore && !collapse.is_active()) return false
        collapse.hide(ignore)
    },

    toggle: function(collapse){
        collapse = this.retrieve_collapse(collapse)
        if(collapse.is_active()){
            collapse.hide(true)
        }else{
            var active = this.get_active()
            if(active) active.hide(true)
            collapse.show(true)
        }
    }
})


window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay([data-toggle=collapse])', function(e, target){
        e.preventDefault()
        if(target.get('data-parent')){
            var accordion = document.getElement(target.get('data-parent'))
            accordion = accordion.retrieve('accordion') || new Moostrap.Accordion(accordion)
            accordion.toggle(target)
        }else{
            var collapse = target.retrieve('collapse') || new Moostrap.Collapse(target)
            collapse.toggle()
        }
    })
})
