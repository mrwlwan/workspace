Moostrap.Affix = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'affix',
        selector: '[data-spy=affix]',
        target: document.body,
        offset: 10 // or {top: 10, bottom: 10} or {top: 10} or {bottom: 10}
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.offset_parent = this.element.getOffsetParent()
        this.state = ''
        this.target = this.options.target || this.get_target(this.element)
        this.offset = this._get_offset()
        if(this.offset.top==undefined || this.options.offset.bottom==undefined){this.element.addClass('affix');this.state='affix';}
        this.origin_class = this.element.get('class')
        this.element.setStyle('width', this.element.getSize().x)
        this.init_events()
        this.refresh_state()
    },

    _get_offset: function(){
        if(typeOf(this.options.offset)=='number'){
            return {top: this.options.offset, bottom: this.options.offset}
        }else{
            return this.options.offset
        }
    },

    refresh_state: function(){
        var scroll_y = this.target.getScroll().y
        if(this.offset.top!=undefined && scroll_y<=this.offset.top){
            if(this.state=='top') return false
            this.fireEvent('affix-top')
            this.element.set('class', this.origin_class)
            this.state = 'top'
            this.fireEvent('affixed-top')
        }else{
            var scroll_bottom = this.target.scrollHeight-(this.offset.bottom || 0)-document.getSize().y
            if(scroll_y>=scroll_bottom){
                if(this.offset.bottom==undefined || this.state=='bottom') return false
                this.fireEvent('affix-bottom')
                this.element.removeClass('affix affix-top')
                            .addClass('affix-bottom')
                            .setStyle('top', this.target.scrollHeight-(this.offset.top || this.offset_parent.getPosition().y)-this.offset.bottom-this.element.getSize().y)
                this.state = 'bottom'
                this.fireEvent('affixed-bottom')
            }else{
                if(this.state=='affix') return false
                this.fireEvent('affix')
                this.element.removeClass('affix-top affix-bottom')
                            .addClass('affix')
                            .setStyle('top', '')
                this.state='affix'
                this.fireEvent('affixed')
            }
       }
       return true
    },

    init_events: function(){
        var scroll_target = this.target==document.body ? $(window) : this.target
        scroll_target.addEvent('scroll', this.refresh_state.bind(this))
    }
})
