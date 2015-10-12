define(['Component', 'Const'], function(Component, Const){
    var EditableControl = new Class({
        Extends: Component,
        store_name: 'editable_control',
        selector: 'td.editable',
        options: {
            'type': ''
            //'select_options': ['']
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
                    var element = new Element('select', {'class': 'form-control'})
                    element.set('html', Const[this.element.get('role')+'_list'].map(function(item){
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
                var request_url = this.element.getParent('tr').get('data-url')
                this.request = new Request.JSON({
                    url: request_url,
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
            var color = Const.colors_map[this.value]
            if(color) this.element.removeClass(color)
            color = Const.colors_map[value]
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

    return EditableControl
})
