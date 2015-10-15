window.addEvent('domready', function(){
    var form_create = document.getElement('.backup-create')
    form_create.getElement('button').addEvent('click', function(e){
        e.preventDefault()
        form_create.set('send', {
            emulation: false,
            onSuccess: function(response){
                location.reload()
            }
        })
        form_create.send()
    })

    var backup_list = document.getElement('.backup-list')
    backup_list.addEvent('click:relay(.list-group-item)', function(e, target){
        if(!e.target.hasClass('glyphicon')) return;
        var request = new Request.JSON({
            emulation: false,
            url: backup_list.get('data-url'),
            data: 'backup='+target.getElement('.backup-value').get('text').trim()
        })
        if(e.target.hasClass('glyphicon-remove')){
            request.addEvent('success', function(response){
                    if(!response.error) target.destroy()
            })
            request.delete()
        }else if(e.target.hasClass('glyphicon-import')){
            request.addEvent('success', function(response){
                if(response.error) return
                target.getSiblings('.list-group-item-success').removeClass('list-group-item-success')
                target.addClass('list-group-item-success')
            })
            request.put()
        }
    })
})
