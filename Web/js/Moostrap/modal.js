Moostrap.Modal = new Class({
    Extends: Moostrap.Component,
    store_name: 'modal',
    selector: '.modal',
    options: {
        store_name: 'modal',
        selector: '.modal',
        duration: '250',
        backdrop: true,
        keyboard: true,
        show: true,
        remote: false
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.dialog = this.element.getElement('.modal-dialog')
        this.content = this.dialog.getElement('.modal-content')
        this.header = this.content.getElement('.modal-header')
        this.title = this.header.getElement('.modal-title')
        this.body = this.content.getElement('.modal-body')
        this.footer = this.content.getElement('.modal-footer')
        this.backdrop = null
        this.init_events()
    },

    init_events: function(){
        if(this.options.backdrop && this.options.backdrop!='static'){
            this.element.addEvent('click', function(e){
                if(e.target==this.element) this.hide()
            }.bind(this))
        }

        this.dialog.addEvent('click:relay([data-dismiss=modal])', function(e, target){
            e.preventDefault()
            this.hide()
        }.bind(this))
    },

    show_backdrop: function(){
        if(!this.options.backdrop) return false
        if(!this.backdrop){
            this.backdrop = new Element('div')
            this.backdrop.addClass('modal-backdrop fade')
            document.body.grab(this.backdrop)
        }
        this.backdrop.setStyle('display', 'block')
        this.backdrop.addClass.delay(10, this.backdrop, 'in')
        return true
    },

    hide_backdrop: function(){
        this.backdrop.removeClass('in').setStyle('display', 'none')
    },

    hide_modal: function(){
        this.element
            .removeClass('in')
            .setStyle('display', 'none')
    },

    hide: function(){
        this.hide_backdrop()
        this.hide_modal()
    },

    show: function(){
        this.show_backdrop()
        document.body.addClass('modal-open')
        this.element
            .addClass('in')
            .setStyle('display', 'block')

    }
})


window.addEvent('domready', function(){
    document.body.addEvent('click:relay([data-toggle=modal])', function(e, target){
        target = Moostrap.get_target(target)
        var modal = target.retrieve(Moostrap.Modal.prototype.store_name) || new Moostrap.Modal(target)
        modal.show()
    })
})
