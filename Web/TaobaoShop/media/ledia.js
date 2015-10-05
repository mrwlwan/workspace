var EditableControl = new Class({
    Extends: Moostrap.Component,
    store_name: 'editable_contraol',
    selector: 'td',
    options: {
        'type': '',
        'select_options': ['']
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.type = this.options.type || this.get_type()
        this.control = this.create_control()
        this.value = this.element.get('text')
        this.active = false
    },

    get_type: function(){
        return this.element.hasClass('selectable') && 'select' || 'textarea'
    },

    create_control: function(){
        switch(this.type){
            case 'select':
                var element = new Element('select', {'class': 'form-control'})
                element.set('html', this.options.select_options.map(function(item){
                    return '<option>'+item+'</option>'
                }.bind(this)).join(''))
                break
            default:
                var element = new Element('textarea', {
                    'class': 'form-control',
                    'rows': 2
                })
        }
        element.addEvent('blur', function(e){
            this.hide()
        }.bind(this))
        return element
    },

    set_control_value: function(value){
        switch(this.type){
            case 'select':
                this.control.getElements('option').some(function(el){
                    if(el.get('text')==this.value){
                        el.set('selected', 'selected')
                        return true
                    }
                }.bind(this))
                break
            default:
                this.control.set('text', value==undefined ? this.value : value)
        }
    },

    show: function(){
        if(this.active) return false
        //this.control.setStyle('display', 'block')
        this.element.empty()
            .grab(this.control)
        this.set_control_value()
        var element_size = this.element.getSize()
        if(element_size.x<80){this.control.setStyle('width', 60)}
        if(this.type!='select') this.control.setStyle('height', element_size.y-20)
        this.control.focus()
        this.active = true
        return true
    },

    hide: function(){
        if(!this.active) return false
        //this.control.setStyle('display', 'none')
        this.control.dispose()
        this.element.set('text', this.value)
        this.active = false
        return true
    }
})
        

var EditableTable = new Class({
    Extends: Moostrap.Component,
    store_name: 'editable_table',
    selector: 'table',
    options:{},
    
    initialize: function(element, options){
        this.parent(element, options)
        this.active_control = null
        this.init_events()
    },

    init_events: function(){
        this.element.addEvent('dblclick:relay(td.editable)', function(e, target){
            var control = target.retrieve(EditableControl.prototype.store_name) || new EditableControl(target)
            if(control.show()) this.active_control = control
        }.bind(this))
    }
})

window.addEvent('domready', function(){
    // 阻止底部导航栏.disabled按钮的默认单击事件.
    document.getElements('nav li.disabled a').addEvent('click', function(e){
        e.preventDefault()
    })

    // 实时编辑事件
    document.getElements('table').each(function(table){
        new EditableTable(table)
    })
})
