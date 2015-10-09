window.addEvent('domready', function(){
    var search_form = $('product_navbar').getElement('form')
    search_form.reset()

    var input = search_form.getElement('input[name=keywords]')
    search_form.getElement('button[role=clear]').addEvent('click', function(e){
        e.preventDefault()
        input.set('value', null)
    })
})
