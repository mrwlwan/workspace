$(document).ready(function(){
    // 阻止底部导航栏.disabled按钮的默认单击事件.
    $('nav li.disabled a').on('click', function(e){
        e.preventDefault();
    });

    // 实时编辑事件
    $('table').on('dblclick', 'td.editable', function(e){
        var $tb = $(this);
        if($tb.data('active')){return;}
        $tb.data('active', true);
        var last_value = $tb.html();
        if($tb.hasClass('selectable')){
            var $new_control = $('<select class="form-control"><option></option><option>正常</option><option>缺货</option><option>下架</option></select>');
            $new_control.children('option').each(function(i, item){
                item = $(item);
                if(item.text()==last_value){
                    item.attr('selected', 'selected');
                    return false;
                }
            });
        }else{
            var $new_control = $('<textarea class="form-control" rows="2">'+last_value +'</textarea>');
        }
        if($tb.width()<80){$new_control.width(60);}
        $tb.html($new_control);
        $new_control.focus();
        $new_control.on('blur', function(e){
            $new_control.remove();
            $tb.html(last_value);
            $tb.data('active', false);
        });
    });
});
