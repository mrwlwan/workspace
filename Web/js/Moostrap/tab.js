Moostrap.Tab = new Class({
    Implements: [Options, Events],
    options: {
        duration: 150
    },

    initialize: function(nav_container){
        this.nav_container = nav_container
    },

    toElement: function(){
        return this.nav_container
    },

    is_active: function(el){
        return el.getParent('li').hasClass('active')
    },

    get_togglers: function(el){
        el = el || this.nav_container
        return el.getElements('[data-toggle=tab], [data-toggle=pill]')
    },

    show: function(el){
        if(this.is_active(el)) return
        this.nav_container.getChildren().each(function(item){
            var is_contains = item.contains(el)
            if(item.hasClass('dropdown')){
                if(is_contains){
                    item.getElements('.dropdown-menu > li').each(function(i){
                        if(i.contains(el)){
                            i.addClass('active')

                        }else{
                            i.removeClass('active')
                        }
                    })
                    item.hasClass('active') || item.addClass('active')
                }else{
                    item.getElements('.dropdown-menu > li').removeClass('active')
                    item.removeClass('active')
                }
            }else{
                if(is_contains){
                    item.addClass('active')
                }else{
                    item.removeClass('active')
                }
            }
        }.bind(this));
        this.get_togglers().each(function(item){
            item.set('aria-expanded', item==el)
        })

        var content = Moostrap.get_target(el)
        var active_content = content.getSiblings('.tab-pane.active')[0]
        active_content.removeClass('in')
        if(active_content.hasClass('fade')){
            (function(){
                active_content.removeClass('active')
                content.addClass('active')
                       .addClass('in')
            }).delay(this.options.duration)
        }else{
            active_content.removeClass('active')
            content.addClass('active')
                   .addClass('in')
        }
    }
});


window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay(ul.nav-tabs, ul.nav-pills)', function(e, target){
        e.preventDefault()
        if(!e.target.match('[data-toggle=tab], [data-toggle=pill]')) return
        var tab = target.retrieve('tab')
        if(!tab){
            tab = new Moostrap.Tab(target)
            target.store('tab', tab)
        }
        tab.show(e.target)
    });
});
