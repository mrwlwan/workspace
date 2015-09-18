Moostrap.Button = new Class({
    Implements: [Options, Events],
    options: {},

    initialize: function(element, options){
        this.element = element;
        this.setOptions(options);
    },

    toElement: function(){
        return this.element;
    },

    toggle: function(){
        this.element.toggleClass('active');
        this.element.set('aria-pressed', this.element.hasClass('active'));
    },

    is_pressed: function(){
        return this.element.hasClass('active');
    }
});


Moostrap.ButtonGroup = new Class({
    Implements: [Options, Events],
    Options: {},

    initialize: function(element, options){
        this.element = element;
        this.type = this._check_type();
    },

    toElement: function(){
        return this.element;
    },

    _check_type: function(){
        return this.element.getElement('input[type]').get('type').toLowerCase();
    },

    clear: function(){
        this.element.getElements('.btn').each(function(button){
            button.removeClass('active');
        });
    },

    toggle: function(target){
        switch(this.type){
            case 'radio':
                this.clear();
            default:
                target.toggleClass('active');
        }
    },

    get_toggle: function(){
        return this.element.getElements('.btn.active');
    }
});
    

window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay([data-toggle^="button"])', function(e, target){
        e.stop();
        switch(target.get('data-toggle')){
            case 'button':
                var btn = target.retrieve('button');
                if(!btn){
                    btn = new Moostrap.Button(target);
                    target.store('button', btn);
                }
                btn.toggle();
                break;
            case 'buttons':
                var group = target.retrieve('button_group');
                if(!group){
                    group = new Moostrap.ButtonGroup(target);
                    target.store('button_group', group);
                }
                group.toggle(e.target);
                break;
        }
    });
});
