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
            if(item==el){
                item.set('aria-expanded', true)
            }else{
                item.set('aria-expanded', false)
            }
        })

        var content = Moostrap.get_target(el)
        var active_content = content.getSiblings('.tab-pane.active')[0]
        if(active_content.hasClass('fade')){
            var hide_handler = function(e){
                active_content.removeClass('active')
                active_content.removeEventListener(Moostrap.transition, hide_handler)
            }
            active_content.addEventListener(Moostrap.transition, hide_handler)
        }else{
            active_content.removeClass('active')
        }
        active_content.removeClass('in');
        (function(){
            content.addClass('in')
                .addClass('active')
        }).delay(this.options.duration)
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
