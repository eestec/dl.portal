$(function() {
    var contentWidth = $('#content').width();
    var History = window.History;
    var fadeSpeed = 1500;
    History.Adapter.bind(window, 'statechange', function() {
        var state = History.getState();
        var $element = $('#' + state.data.id);
        $('.sec-nav-item.selected').removeClass('selected');
        $element.addClass('selected');
        $('.messages').remove();
        var url = state.url;
        // Some logic has to be special-cased for the settings menu since it
        // is different than the others (doesn't show videos)
        var isSettings = state.data.id === 'settings';
        var format = isSettings ? 'html' : 'json';
        $.ajax({
            url: url,
            data: {
                format: format
            },
            success: function(data) {
                if (format === 'json') {
                    // JSON is checked for an additional indicator of success
                    if (data.status === 'ok') {
                        $('#main-content').fadeOut(fadeSpeed, function() {
                            populateVideos(data);
                        });
                    }
                } else if (format === 'html') {
                    // HTML is simply embedded in the right place...
                    $('#main-content').fadeOut(fadeSpeed, function() {
                        showForm(data);
                    });
                }
            }
        });
        History.log(state.data, state.title, state.url);
    });
    function showForm(data) {
        $('.videos-column').html('');
        $('.column').hide();
        $('.pagination').hide();
        $('#main-content').append($('<div class="wrapper"></div>').html(data))
                          .fadeIn(fadeSpeed);
        initFormAjax();
    }
    function populateVideos(data) {
        // First get the container divs back (if they were hidden by settings)
        $('#main-content > .wrapper').remove();
        if ($('.column').length == 0) {
            var $column = $(
                '<div class="column"><div class="videos-column"></div></div>');
            $('#main-content').append($column.clone())
                              .append($column.clone())
                              .append($('<div class="clear"></div>'));
        }
        $('.column').show();
        var video_template = $('#video-template').html();
        var pageNumber = data.page;
        if ($('.pagination').length == 0) {
            $('.sec-nav').after(
                '<div class="pagination"></div><div class="clear"></div>');
        }
        $('.pagination').fadeIn(fadeSpeed);
        var $pagination = $($('.pagination')[0]);
        var radio_buttons = '';
        var pages = (data.total / 6) + 0.5;
        pages = pages.toFixed();
        for (var i = 0; i < pages; ++i) {
            radio_buttons += '<div class="radiobutton"></div>';
        }
        var radiobutton_offset =
            ($('#content').width() - pages * (
                 $('.radiobutton').width() +
                 parseInt($('.radiobutton').css('margin-right')))) / 2;
        $pagination.html(radio_buttons)
                   .css('margin-left',  radiobutton_offset + 'px');
        $($pagination.children()[pageNumber - 1]).addClass('selected');
        $('.videos-column').each(function(index) {
            $(this).html(_.template(
                    video_template,
                    {videos: data.videos.slice(3 * index, 3 * index + 3)}))
        });
        $('#main-content').fadeIn(fadeSpeed);
    }
    $('.sec-nav-item a').click(function() {
        var $this = $(this);
        var url = $this.attr('href');
        History.pushState({
            id: $this.parent().attr('id'),
            path: url
        }, '', url);
        return false;
    });
    function getFavorites(pageNumber) {
        var getFavoritesUrl = "/profile/favorites/";
        $.ajax({
            url: getFavoritesUrl + pageNumber + '/',
            success: function(data) {
                if (data.status === 'ok') {
                    populateVideos(data);
                }
            }
        });
    }
    function getWatchLater(pageNumber) {
        var getWatchLaterUrl = "/profile/watch-later/";
        $.ajax({
            url: getWatchLaterUrl + pageNumber + '/',
            success: function(data) {
                if (data.status === 'ok') {
                    populateVideos(data);
                }
            }
        });
    }
    var errorListTemplate =
        "<div class='errors'><ul class='errorlist'> \
        <% _.each(errors, function(error) { %> \
                <li><%= error %></li> \
        <% }); %> \
        </ul></div>";

    /**
     * The function hooks up the settings form submit event to a custom
     * callback.
     */
    function initFormAjax() {
        $('#settings-form').submit(function() {
            var $this = $(this);
            $.post(
                $this.attr('action'), $this.serialize(),
                function(data) {
                    $('.errors').remove();
                    if (data.status === 'ok') {
                        $('#main-content').prepend(
                            $('<div class="messages"></div>').html(data.message));
                    }
                    if (data.status === 'validation failed') {
                        $.each(data.errors, function(key, value) {
                            $('input[name="' + key + '"]').parent().after(
                                _.template(errorListTemplate,
                                           {errors: value}));
                        });
                    }
                },
                "json");
            return false;
        });
    }
    initFormAjax();
});
