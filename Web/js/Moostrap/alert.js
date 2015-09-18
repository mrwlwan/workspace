Moostrap.Alert = new Class({
    Implements: [Options, Events],
    options: {
        duration: 150
    },

    initialize: function(closer){
        this.closer= closer
        this.container = this.get_container()
    },

    toElement: function(){
        return this.container
    },

    get_container: function(){
        return Moostrap.get_target(this.closer) || this.closer.getParent('.alert')
    },

    close: function(){
        this.fireEvent('close')
        this.container.removeClass('in')
        if(Moostrap.transition && this.container.hasClass('fade')){
            //this.container.addEventListener(Moostrap.transition, function(){
                (function(){
                    this.container.destroy()
                    this.fireEvent('closed')
                }).delay(this.options.duration, this)
            //}.bind(this))
        }else{
            this.container.destroy()
            this.fireEvent('closed')
        }
    }
});


window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay([data-dismiss=alert])', function(e, target){
        e.preventDefault()
        var alert_window = target.retrieve('alert')
        if(!alert_window){
            alert_window = new Moostrap.Alert(target)
            target.store('alert', alert_window)
        }
        alert_window.close()
    })
})
