Moostrap.Popover = new Class({
    Extends: Moostrap.Tooltip,
    options: {
        store_name: 'popover',
        selector: '[data-toggle=popover]',
        placement: '',
        triggers: ['click'],
        title: '',
        content: '',
        template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
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
    },

    get_content: function(){
        return this.element.get('data-content') || (typeOf(this.options.content)=='function' ? this.options.content.attempt(this, this) : this.options.content)
    },
        
    set_content: function(title, content){
        title = title || this.get_title()
        content = content || this.get_content()
        this.panel.getElement('.popover-title').set(this.options.html ? 'html' : 'text', title)
        this.panel.getElement('.popover-content').set(this.options.html ? 'html' : 'text', content)
    }
})
