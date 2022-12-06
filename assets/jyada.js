async function playScript(data) {
    $("#jyada").css({'top':'0px', 'left':$('body')[0].getBoundingClientRect().width - 30 - $("#jyada")[0].getBoundingClientRect().width})
    $('#jyada').removeClass('sleeping')
    escaped = false
    $(document).on('keydown', function() {
    if (event.key == 'Escape' || event.which == 27 || event.code == 'Escape') {
        escaped = true
        paused = false
    }})
    $('#jyada').on('click', function() {paused = false})
    for (y=0; y<data.length; y++) {
        if (!$('#'+data[y].target)[0]) {
            await delay(500)
        }
        if ($('#'+data[y].target)[0]) {
            $($('#'+data[y].target)[0]).toggleClass('highlighting')
            tBounds = $('#'+data[y].target)[0].getBoundingClientRect()
            $('#jyada').css({'top':tBounds.top + tBounds.height/4,
            'left':tBounds.left + tBounds.width/2.5})
            $('#jyada').attr('convo', data[y].convo)
            paused = true
            while (paused) {
                await delay(300)
            }
            if (escaped) {break}
            if ('action' in data[y]) {
                if (data[y]['action'] == 'click') {$('#'+data[y].target).click()}
            }
            $($('#'+data[y].target)[0]).toggleClass('highlighting')
        }
    }
    $(document).unbind('keydown')
    $('.highlighting').removeClass('highlighting')
    $('#jyada').unbind()
    $('#jyada').removeAttr('convo')
    $("#jyada").css({'top':'0px', 'left':$('body')[0].getBoundingClientRect().width - 30 - $("#jyada")[0].getBoundingClientRect().width})
    await delay(1000)
    $("#jyada").css({'top':'', 'left':''})
    $('#jyada').addClass('sleeping')
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}