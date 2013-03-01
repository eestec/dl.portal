$(function() {
    $('#add-favorite, #add-watch-later').click(function(event) {
        event.preventDefault();
        var $this = $(this);
        var type = '';
        if ($this[0].id == 'add-favorite') {
            type = 'favorites';
        } else if ($this[0].id == 'add-watch-later') {
            type = 'watch later';
        }
        var url = $this.attr('href');
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'video_id': $('#video-id').html()
            },
            success: function(data) {
                if (data.status === 'ok') {
                    $this.siblings('a#remove-favorite, a#remove-watch-later').show();
                    $this.hide();
                }
            }
        });
    });

    $('#remove-favorite, #remove-watch-later').click(function(event) {
        event.preventDefault();
        var $this = $(this);
        var url = $this.attr('href');
        $.ajax({
            type: 'DELETE',
            url: url,
            success: function(data) {
                if (data.status === 'ok') {
                    $this.siblings('a#add-favorite, a#add-watch-later').show();
                    $this.hide();
                }
            }
        });
    });

    $('#video-description').linkify();
});
