Moostrap.Button = new Class({
    Extends: Moostrap.Component,
    options: {
        store_name: 'button',
        selector: '[data-toggle=button]'
    },

    initialize: function(element, options){
        this.parent(element, options)
    },

    release: function(){
        if(this.is_pressed()){
            this.element.removeClass('active')
            this.element.set('aria-pressed', false)
            this.fireEvent('release')
            return true
        }
        return false
    },

    press : function(){
        if(!this.is_pressed()){
            this.element.hasClass('active') || this.element.addClass('active')
            this.element.set('aria-pressed', true);
            this.fireEvent('press')
            return true
        }
        return false
    },

    toggle: function(){
        var action = this.is_pressed() ? this.release() : this.press()
        this.fireEvent('toggle')
        return action
    },

    is_pressed: function(){
        return this.element.hasClass('active');
    }
});


Moostrap.ButtonGroup = new Class({
    Extends: Moostrap.Component,
    options: {
        selector: '[data-toggle=button]',
        store_name: 'button_group',
        'type': undefined
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.type = this.check_type();
    },

    get_create_button: function(target){
        return target.retrieve(Moostrap.Button.prototype.options.store_name) || new Moostrap.Button(target)
    },

    // 检查ButtonGroup类型：checkbox 或者 radio. 如未指定，检查首个 input 元素.
    check_type: function(){
        return this.options.type || this.element.getElement('input[type]').get('type').toLowerCase();
    },

    // 只获取已创建的对象
    get_buttons: function(){
        return this.get_components(this.element.getElements('.btn'), Moostrap.Button.prototype.options.store_name)
    },
    
    // 获取按下状态的buttons, 返回[]
    get_active: function(){
        return this.get_buttons().filter(function(item){
            return item.is_pressed
        });
    },

    // 释放所有buttons
    clear: function(){
        var buttons = []
        this.get_buttons().each(function(item){
            if(item.is_pressed()){
                buttons.push(item)
                item.release()
            }
        });
        if(buttons.length){
            this.fireEvent('clear', buttons) // 将释放的按钮作参数传递
        }
        return buttons
    },

    release: function(target){
        var button = this.get_create_button(target)
        var action = false
        switch(this.type){
            case 'radio': // radio 不存在释放状态的改变. 约定至少有一个被按下的状态. 
                 break;
            default:
                button.release()
                action = true
        }
        return action
    },

    press: function(target){
        var button = this.get_create_button(target)
        var action = false
        switch(this.type){
            case 'radio':
                if(button.is_pressed()) break;
                this.get_buttons().each(function(item){
                    item!=button && item.release()
                });
            default:
                button.press()
                action = true
        }
        return action
    },

    toggle: function(target){
        var button = this.get_create_button(target)
        var action = button.is_pressed() ? this.release(button) : this.press(button)
        this.fireEvent('toggle')
        return action
    },
});
    

window.addEvent('domready', function(){
    $(document.body).addEvent('click:relay([data-toggle^="button"])', function(e, target){
        e.stop();
        switch(target.get('data-toggle')){
            case 'button':
                var btn = target.retrieve('button') || new Moostrap.Button(target);
                btn.toggle();
                break;
            case 'buttons':
                var group = target.retrieve('button_group') || new Moostrap.ButtonGroup(target);
                group.toggle(e.target);
        }
    });
});
