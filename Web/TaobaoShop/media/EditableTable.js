define(['Component', 'EditableControl'], function(Component, EditableControl){
    var EditableTable = new Class({
        Extends: Component,
        store_name: 'editable_table',
        selector: '.editable-table',
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
            }.bind(this)).getElement('tbody').addEvent('dblclick:relay(th.deletable)', function(e, target){
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

    return EditableTable
})
