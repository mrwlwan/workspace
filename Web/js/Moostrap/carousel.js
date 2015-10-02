Moostrap.Carousel = new Class({
    Extends: Moostrap.Component,
    store_name: 'carousel',
    selector: '[data-ride=carousel]',
    options: {
        interval: 3000,
        interval_direction: 'left',
        pause: 'hover',
        duration: 600
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.indicators = this.element.getElements('.carousel-indicators > li')
        this.items = this.element.getElements('.carousel-inner .item')
        this.controls = this.element.getElements('.carousel-control')
        this.active_index= this.get_active_index(this.items) || 0
        this.action = false
        this.paused = false
        this.init_events()
    },

    init_events: function(){
        if(this.options.interval!=false){
            this.cycle(this.options.interval, this.options.interval_direction || 'left')
            this.element.addEvent('mouseenter', function(e){
                this.paused = true
            }.bind(this))
            .addEvent('mouseleave', function(e){
                this.paused = false
            }.bind(this))
        }

        this.controls.each(function(control){
            control.addEvent('click', function(e){
                e.preventDefault()
                this._control_handler(control)
            }.bind(this))
        }.bind(this))

        this.element.getElement('.carousel-indicators').addEvent('click:relay(li)', function(e, target){
            e.preventDefault()
            this._indicator_handler(target)
        }.bind(this))
    },

    _control_handler: function(control){
        this.slide(control.hasClass('left') && 'right' || 'left')
    },

    _indicator_handler: function(indicator){
        var next_index = this.indicators.indexOf(indicator)
        if(this.active_index==next_index) return
        this.slide(next_index>this.active_index && 'left' || 'right', this.active_index, next_index)
    },

    get_next_index: function(direction, index, els){
        switch(direction){
            case 'left':
                return index<els.length-1 ? index+1 : 0
            case 'right':
                return index>0 ? index-1 : els.length-1
        }
        return -1
    },

    get_next_item: function(direction, item){
        var index = this.get_next_index(direction, this.items.indexOf(item), this.items)
        if(index>=0) return this.items[index]
        return null
    },

    get_next_indicator: function(direction, indicator){
        var index = this.get_next_index(direction, this.indicators.indexOf(indicator), this.indicators)
        if(index>=0) return this.indicators[index]
        return null
    },

    get_active_index: function(els){
        for(var index=0; index<els.length; i++){
            if(els[index].hasClass('active')) return index
        }
        return -1
    },

    get_active_item: function(){
        var index = this.get_active_index(this.items)
        if(index>=0) return this.items[index]
        return null
    },

    get_active_indicator: function(){
        var index = this.get_active(this.indicators)
        if(index>=0) return this.indicators[index]
        return null
    },

    slide_indicator: function(index, next_index){
        this.indicators[index].removeClass('active')
        this.indicators[next_index].addClass('active')
        return true
    },

    slide_item: function(direction, index, next_index){
        if(this.action) return false 
        this.action = true
        this.fireEvent('slide', [direction, index, next_index])
        this.active_index = index
        var item = this.items[index]
        var next_item = this.items[next_index]
        var sign = direction=='left' && 'next' || 'prev'
        next_item.addClass(sign)
        next_item.offsetWidth // force reflow
        item.addClass(direction);
        next_item.addClass(direction);
        (function(){
            item.removeClass(direction+' active')
            next_item.removeClass(direction+' '+sign ).addClass('active')
            this.active_index = next_index
            this.action = false
            this.fireEvent('slid', [direction, index, next_index])
        }).delay(Moostrap.transition && this.options.duration || 0, this)
        return true
    },

    slide: function(direction, index, next_index){
        if(this.action) return false
        if(index==undefined){
            index=this.active_index
            next_index = this.get_next_index(direction, index, this.items)
        }
        if(index==next_index) return false
        this.slide_indicator(index, next_index)
        this.slide_item(direction, index, next_index)
    },

    cycle: function(period, direction){
        (function(){
            if(this.paused) return
            this.slide(direction)
        }).periodical(period, this)
    }
})

window.addEvent('domready', function(){
    document.getElements(Moostrap.Carousel.prototype.selector).each(function(el){
        new Moostrap.Carousel(el)
    });
})
