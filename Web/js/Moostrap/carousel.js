Moostrap.Carousel = new Class({
    Extends: Moostrap.Component,
    store_name: 'carousel',
    selector: '[data-ride=carousel]',
    options: {
        interval: false,
        pause: 'hover',
        duration: 350
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.indicators = this.element.getElements('.carousel-indicators > li')
        this.items = this.element.getElements('.carousel-inner item')
        this.controls = this.element.getElements('.carousel-control')
        this.active_item = this.get_active(this.items) || this.items[0]
        this.active_indicator = this.get_active(this.indicators) || this.indicators[0]
    },

    get_active: function(items){
        var filter_items = items.filter(function(el){
            return el.hasClass('active')
        })
        return filter_items.length && filter_items[0] || null
    },
})

window.addEvent('domready', function(e){
    document.getElements(Moostrap.Carousel.store_name).each(function(el){
        new Moostrap.Carousel(el)
    });
})


