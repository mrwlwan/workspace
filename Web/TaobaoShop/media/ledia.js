var EditableControl = new Class({
    Extends: Moostrap.Component,
    store_name: 'editable_contraol',
    selector: 'td',
    options: {
        'type': '',
        //'select_options': ['']
        colors: {'下架': 'warning', '回收站': 'danger'}
    },

    initialize: function(element, options){
        this.parent(element, options)
        this.type = this.options.type || this.get_type()
        this.control = this.create_control()
        this.value = this.element.get('text')
        this.active = false
        this.request = null
    },

    get_type: function(){
        return this.element.hasClass('selectable') && 'select' || 'textarea'
    },

    create_control: function(){
        switch(this.type){
            case 'select':
                var options = {
                    'category': ['未分类', '夏装', '春秋冬装', '饰品', '邮费', '其它'],
                    'status': ['上架', '下架']
                }
                var element = new Element('select', {'class': 'form-control'})
                element.set('html', options[this.element.get('role')].map(function(item){
                    return '<option>'+item+'</option>'
                }.bind(this)).join(''))
                break
            default:
                var element = new Element('textarea', {
                    'class': 'form-control',
                    'autocomplete': 'off'
                    //'rows': 2
                })
        }
        element.addEvent('blur', function(e){
            this.submit()
        }.bind(this)).addEvent('keypress', function(e){
            if(e.code==27) this.hide()
        }.bind(this))
        return element
    },

    submit: function(){
        var value = this.get_control_value()
        if(value==this.value.trim()) return this.hide()
        var key = this.element.get('role')
        if(!this.request){
            var product_id = this.element.getParent('tr').get('data-id')
            this.request = new Request.JSON({
                url: '/product/'+product_id,
                method: 'post',
                onSuccess: function(response){
                    if(response.error) return
                    if(this.type=='select') this.toggle_color(response.data[key])
                    this.value = response.data[key]
                    this.hide()
                }.bind(this)
            })
        }
        this.request.send(key+'='+ encodeURI(value))
    },
    
    toggle_color: function(value){
        var color = this.options.colors[this.value]
        if(color) this.element.removeClass(color)
        color = this.options.colors[value]
        if(color) this.element.addClass(color)
    },        

    get_control_value: function(){
        switch(this.type){
            case 'select':
                return this.control.getSelected()[0].get('text').trim()
            default:
                return this.control.get('value').trim()
        }
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
                this.control.set('value', value==undefined ? this.value : value)
        }
    },

    show: function(){
        if(this.active) return false
        this.element.empty()
            .grab(this.control)
        this.set_control_value()
        var element_size = this.element.getSize()
        if(this.type!='select'){
            this.control.setStyle('height', element_size.y-20)
            this.control.setStyle('width', Math.max(element_size.x-20, 80))
        }else{this.control.setStyle('width', element_size.x+30)}
        this.control.focus()
        this.type!='select' && this.control.select()
        this.active = true
        return true
    },

    hide: function(){
        if(!this.active) return false
        this.control.setStyle('width', 0)
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
        }.bind(this)).getElement('tbody').addEvent('dblclick:relay(th)', function(e, target){
            if(!confirm('确定删除商品?')) return
            var row = target.getParent('tr')
            var product_id = row.get('data-id')
            var request = new Request.JSON({
                url: 'product/'+product_id,
                method: 'delete',
                emulation: false,
                onSuccess: function(response){
                    console.log(response)
                    if(response.error) return
                    row.destroy()
                }                    
            })
            request.send()
        })
    },
})

window.addEvent('domready', function(){
    // 阻止底部导航栏.disabled按钮的默认单击事件.
    //document.getElements('nav li.disabled a').addEvent('click', function(e){
        //e.preventDefault()
    //})

    // 实时编辑事件
    document.getElements('table').each(function(table){
        new EditableTable(table)
    })
})
