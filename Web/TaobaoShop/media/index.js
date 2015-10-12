require(['EditableTable', 'paginate', 'products_navbar'], function(EditableTable){
    window.addEvent('domready', function(){
        document.getElements('table.editable-table').each(function(table){
            new EditableTable(table)
        })
    })
})
