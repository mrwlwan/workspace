Moostrap.TooltipTriggerMap = {
    'hover': ['mouseenter', 'mouseleave'],
    'mouseenter': ['mouseenter', 'mouseleave'],
    'focus': ['focus', 'blur']
}


Moostrap.Tooltip = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'tooltip',
        selector: '[data-toggle=tooltip]',
        //animation: true,
        placement: 'top', //top, bottom, left, right
        template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',
        triggers: ['click', 'hover', 'hover'], //click, hover, focus, manual
        title: '',
        delay: 0,
        html: false,
        container: false,
        viewport: {
            selector: 'body',
            padding: 0
        },
        duration: 150
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.viewport = this._get_viewport()
        this.state = {click: false, hover: false, focus: false},
        this.panel = this._create_panel()
        //this.type = undefined
        this.enabled = true
        this.fix_title()
        this.add_default_events(this.options.triggers)
    },

    add_default_events: function(triggers){
        if(!triggers.length) return
        var TooltipTriggerMap = Moostrap.TooltipTriggerMap
        if(!triggers.contains('focus')){
            triggers = Array.clone(triggers)
            triggers.push('focus') // 默认添加 focus 事件.
        }
        triggers.each(function(trigger){
            switch(trigger){
                case 'click':
                    this.element.addEvent('click', this._click_handler.bind(this))
                    break
                case 'manual':
                    break
                default:
                    this.element
                        .addEvent(TooltipTriggerMap[trigger][0], this._enter_handler.bind(this, TooltipTriggerMap[trigger][0]))
                        .addEvent(TooltipTriggerMap[trigger][1], this._leave_handler.bind(this, TooltipTriggerMap[trigger][1]))
            }
        }.bind(this))
    },

    _click_handler: function(e){
        if(this.state.focus) return
        if(!this.is_active()){
            this.show()
            this.state.click = true
        }
    },

    _enter_handler: function(event_type){
        if(event_type=='mouseenter'){
            this.state.hover = true
            if(!this.is_active()) this.show()
        }else if(event_type=='focus'){
            this.state.focus=true
            this.state.click=false
            if(!this.is_active()) this.show()
        }
    },

    _leave_handler: function(event_type){
        if(event_type=='mouseleave'){
            this.state.hover = false
            if(this.state.click || this.state.focus) return
            this.hide()
        }else if(event_type=='blur'){
            this.state.focus=false
            if(this.is_active()) this.hide()
        }
    },

    _get_viewport: function(){
        return typeOf(this.options.viewport)=='function' ? this.options.viewport.attempt(this, this) : $$(this.options.viewport.selector || this.options.viewport)[0]
    },

    _create_panel: function(){
        if(!this.panel){
            var temp = this.options.container && document.getElement(this.options.container) || new Element('div')
            temp.appendHTML(this.options.template)
            this.panel = temp.getChildren()
            if(!this.panel.length) throw new Error('`template` option must consist of exactly 1 top-level element!')
            this.panel = this.panel[0].dispose()
            temp.destroy()
            this.element.grab(this.panel, 'after')
        }
        return this.panel
    },
    
    get_title: function(){
        return this.element.get('data-original-title') || (typeOf(this.options.title)=='function' ? this.options.title.attempt(this, this) : this.options.title)
    },
    
    fix_title: function(){ // 优先级: title, data-original-title, options.title
        if(this.element.get('title')){
            this.element.set('data-original-title', this.element.get('title'))
        }
        this.element.set('title', '')
    },

    set_content: function(){
        this.panel.getElement('.tooltip-inner')
            .set(this.options.html ? 'html' : 'text', this.get_title())
    },

    is_active: function(){
        return this.panel.hasClass('in')
    },

    set_position: function(){
        this.panel.addClass('fade in '+this.options.placement)
        var placement = this.options.placement
        var coor = this.element.getCoordinates()
        var panel_coor = this.panel.getCoordinates()
        //var viewport_coor = document.getElement(this.viewport)
        //placement = placement == 'top'    && pos.top    - actualHeight < viewportDim.top    ? 'bottom' :
                    //placement == 'bottom' && pos.bottom + actualHeight > viewportDim.bottom ? 'top'    :
                    //placement == 'left'   && pos.left   - actualWidth  < viewportDim.left   ? 'right'  :
                    //placement == 'right'  && pos.right  + actualWidth  > viewportDim.width  ? 'left'   :
                    //placement
        switch(placement){
            case 'top':
                panel_coor.top = coor.top-panel_coor.height+1
                panel_coor.left = coor.left+(coor.width-panel_coor.width)/2
                break
            case 'bottom':
                panel_coor.top = coor.top+coor.height-1
                panel_coor.left = coor.left+(coor.width-panel_coor.width)/2
                break
            case 'left':
                panel_coor.top = coor.top+(coor.height-panel_coor.height)/2+1
                panel_coor.left = coor.left-panel_coor.width
                break
            case 'right':
                panel_coor.top = coor.top+(coor.height-panel_coor.height)/2-1
                panel_coor.left = coor.left+panel_cool.width
                break
        }
        this.panel.setStyles({
            'top': panel_coor.top,
            'left': panel_coor.left
        })
    },

    show: function(){
        if(this.is_active()) return false
        this.fireEvent('show')
        this.set_content()
        this.set_position.delay(this.options.delay, this)
        this.fireEvent.delay(Moostrap.transition && (this.options.delay+this.options.duration) || 0, this, 'shown')
        return true
    },

    hide: function(){
        if(!this.is_active()) return false
        this.fireEvent('hide')
        this.panel.removeClass.delay(this.options.delay, this.panel, 'in top bottom left right');
        (function(){
            this.panel.removeClass('fade')
            this.fireEvent('hidden')
        }).delay(Moostrap.transition && (this.options.delay+this.options.duration) || 0, this)
        return true
    },

    toggle: function(){
        if(this.is_active()){
            this.hide()
        }else{
            this.show()
        }
        return true
    }
});


Moostrap.TooltipDelegate = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'tooltip_delegate',
        selector: '[data-delegate=tooltip]',
        delegate_selector: '[data-toggle=tooltip]',
        //animation: true,
        placement: 'top', //top, bottom, left, right
        template: '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',
        triggers: ['click', 'hover', 'focus'], //click, hover, focus, manual
        title: '',
        delay: 0,
        html: false,
        container: false,
        viewport: {
            selector: 'body',
            padding: 0
        },
        duration: 150
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.tooltip_options = this._get_tooltip_options()
        this.add_default_events(this.options.triggers)
    },

    _get_tooltip_options: function(){
        var options = Object.clone(this.options)
        options.triggers = ''
        options.selector = options.delegate_selector
        delete options['store_name']
        delete options['delegate_selector']
        return options
    },

    add_default_events: function(){
        if(!this.options.triggers.length) return
        var triggers = this.options.triggers
        if(!triggers.contains('focus')){
            triggers = Array.clone(triggers)
            triggers.push('focus') // 默认添加 focus 事件.
        }
        var TooltipTriggerMap = Moostrap.TooltipTriggerMap
        triggers.each(function(trigger){
            switch(trigger){
                case 'click':
                    this.element.addEvent('click'+':relay('+this.options.delegate_selector+')', function(e, target){
                        var tooltip = target.retrieve(Moostrap.Tooltip.prototype.options.store_name) || new Moostrap.Tooltip(target, this.tooltip_options)
                        tooltip._click_handler()
                    }.bind(this))
                    break
                case 'manual':
                    break
                default:
                    this.element.addEvent(TooltipTriggerMap[trigger][0]+':relay('+this.options.delegate_selector+')', function(e, target){
                        var tooltip = target.retrieve(Moostrap.Tooltip.prototype.options.store_name) || new Moostrap.Tooltip(target, this.tooltip_options)
                        tooltip._enter_handler(TooltipTriggerMap[trigger][0])
                    }.bind(this))
                    this.element.addEvent(TooltipTriggerMap[trigger][1]+':relay('+this.options.delegate_selector+')', function(e, target){
                        var tooltip = target.retrieve(Moostrap.Tooltip.prototype.options.store_name) || new Moostrap.Tooltip(target, this.tooltip_options)
                        tooltip._leave_handler(TooltipTriggerMap[trigger][1])
                    }.bind(this))
            }
        }.bind(this))
    }
})


window.addEvent('domready', function(){
    $$(Moostrap.TooltipDelegate.prototype.options.selector).each(function(el){
        new Moostrap.TooltipDelegate(el)
    })
})
