window.addEvent('domready', function(){
    var products_navbar = document.getElement('.products-navbar')
    if(!products_navbar) return

    var search_form = products_navbar.getElement('form')
    search_form.reset()
    var keywords_input = search_form.getElement('input[name=keywords]')
    search_form.getElement('button[role=clear]').addEvent('click', function(e){
        e.preventDefault()
        keywords_input.set('value', null)
    })

    var sort_select = products_navbar.getElement('select[name=sort_columns]')
    var desc_checkbox = products_navbar.getElement('input[name=desc]')
    document.getElement('.editable-table thead').addEvent('click:relay(th.sortable)', function(e, target){
        e.preventDefault()
        var column = target.get('text')
        sort_select.getElements('option').some(function(item){
            if(item.get('text')!=column) return false
            if(item.match(':selected')){
                desc_checkbox.set('checked', !desc_checkbox.get('checked'))
            }else{
                item.set('selected', true)
            }
            return true
        })
    })
})
