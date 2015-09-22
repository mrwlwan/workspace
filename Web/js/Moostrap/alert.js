Moostrap.Alert = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'alert',
        selector: '[data-dismiss=alert]',
        duration: 150
    },

    initialize: function(element){
        this.parent(element)
        this.container = this.get_container()
    },

    get_container: function(){
        return this.get_target(this.element) || this.element.getParent('.alert')
    },

    close: function(){
        this.fireEvent('close')
        this.container.removeClass('in')
        if(Moostrap.transition && this.container.hasClass('fade')){
            (function(){
                this.container.destroy()
                this.fireEvent('closed')
            }).delay(this.options.duration, this)
        }else{
            this.container.destroy()
            this.fireEvent('closed')
        }
        return true
    }
});


window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay([data-dismiss=alert])', function(e, target){
        e.preventDefault()
        var alert_window = target.retrieve('alert') || new Moostrap.Alert(target)
        alert_window.close()
    })
})
