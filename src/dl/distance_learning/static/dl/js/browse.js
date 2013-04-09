$(function() {
    var contentWidth = $('#content').width();
    var History = window.History;
    var fadeSpeed = 750;
    var spinnerOpts = {
        lines: 13, // The number of lines to draw
        length: 7, // The length of each line
        width: 4, // The line thickness
        radius: 10, // The radius of the inner circle
        corners: 1, // Corner roundness (0..1)
        rotate: 0, // The rotation offset
        color: '#000', // #rgb or #rrggbb
        speed: 1, // Rounds per second
        trail: 60, // Afterglow percentage
        shadow: false, // Whether to render a shadow
        hwaccel: false, // Whether to use hardware acceleration
        className: 'spinner', // The CSS class to assign to the spinner
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        top: '20px', // Top position relative to parent in px
        left: '565px' // Left position relative to parent in px
    };
    /**
     * Handling navigation by using HTML5's history.
     */
    History.Adapter.bind(window, 'statechange', function() {
        var state = History.getState();
        // The ID of the clicked element is a part of the state.
        var $element = $('#' + state.data.id);
        // Keep the selected item from the sec-nav-menu if a submenu item was
        // chosen.
        if (state.data.id.substr(0, 8) !== 'scroller') {
            $('.sec-nav-item.selected').removeClass('selected');
        }
        $('.scroller-option.selected').removeClass('selected');
        $element.addClass('selected');
        $('.messages').remove();
        var url = state.url;
        $('#nav-dropdown').slideUp();
        $('#main-content').fadeTo(fadeSpeed, 0, function() {
            $('#main-content .column, #main-content .wrapper').fadeTo(0, 0);
            $('#main-content').spin(spinnerOpts).fadeTo(0, 1);
            $.ajax({
                url: url,
                data: {
                    format: "json"
                },
                success: function(data) {
                    $('#main-content').spin(false).fadeTo(0, 0);
                    $('#main-content .column, #main-content .wrapper').fadeTo(0, 1);
                    if (data.status === 'ok') {
                        if (data.categories === undefined) {
                            if (state.data.id.substr(0, 8) === 'scroller') {
                                // Show the submenu if one of its options was
                                // chosen
                                $('#nav-dropdown').slideDown();
                            }
                            populateVideos(data);
                        } else {
                            $('#nav-dropdown').slideDown();
                            populateCategories(data.categories);
                        }
                    }
                }
            });
        });
    });

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
            radio_buttons += '<a href="' + document.URL + '?page=' + (i + 1) + '"><div class="radiobutton"></div></a>';
        }
        var radiobutton_offset =
            ($('#content').width() - pages * (
                 $('.radiobutton').width() +
                 parseInt($('.radiobutton').css('margin-right')))) / 2;
        $pagination.html(radio_buttons)
                   .css('margin-left',  radiobutton_offset + 'px');
        $($pagination.find('.radiobutton')[pageNumber - 1]).addClass('selected');
        $('.videos-column').each(function(index) {
            $(this).html(_.template(
                    video_template,
                    {videos: data.videos.slice(3 * index, 3 * index + 3)}))
        });
        $('#main-content').fadeTo(fadeSpeed, 1);
    }

    var categoryTemplate =
        '<% _.each(categories, function(category, index) { %>' + 
        '<span class="scroller-option" id="scroller-option-<%= index %>"><a href="<%= category.url %>"><%= category.name %></a></span>'+
        '<% }); %>';
    function populateCategories(categories) {
        $('#scroller-inner').html(_.template(
                    categoryTemplate,
                    {'categories': categories}));
        adjustScroller();
        $('#scroller-inner').slideDown();
        $('#scroller-inner a').click(clickHandler);
    }

    function centerElements() {
        // Main navigation
        var elementWidth = 0;
        $('.sec-nav-items').children().each(function(i, element) {
            var $element = $(element);
            elementWidth +=
                $element.width() + parseInt($element.css('margin-right'));
        });
        $('.sec-nav-items').width(elementWidth);
    }
    function adjustScroller() {
        var elementWidth = 0;
        $('#nav-dropdown').show();
        $('#scroller-inner').width(1000);
        $('#scroller-inner').children().each(function(i, element) {
            var $element = $(element);
            elementWidth +=
                $element.width() + parseInt($element.css('margin-right'));
        });
        $('#scroller-inner').width(elementWidth);
        if (elementWidth > 1000) elementWidth = 1000;
        $('#scroller-wrap').width(elementWidth);
        $('#scroller').width(elementWidth);
        $('#nav-dropdown').width(elementWidth + 2 * (23 + 10));
        if ($('.scroller-option').length == 0) {
            $('#nav-dropdown').hide();
        }
    }
    // Event handlers
    function clickHandler(event) {
        event.preventDefault();
        var $this = $(this);
        var url = $this.attr('href');
        History.pushState({
            id: $this.parent().attr('id'),
            path: url
        }, '', url);
    }
    $('.sec-nav-item a, .scroller-option a').click(clickHandler);

    // Do work
    centerElements();
    adjustScroller();
});

/**
 * Initializes the horizontally scrollable div.
 * Used for displaying the list of searchable categories.
 */
$(document).ready(function() {
    var animateTime = 10,
    offsetStep = 5,
    scrollWrapper = $('#scroller-wrap');

    //event handling for buttons "left", "right"
    $('.bttR, .bttL')
        .mousedown(function() {
            scrollWrapper.data('loop', true);
            loopingAnimation($(this), $(this).is('.bttR') );
        })
        .bind("mouseup mouseout", function(){
            scrollWrapper.data('loop', false).stop();
            $(this).data('scrollLeft', this.scrollLeft);
        });

    scrollWrapper
        .mousedown(function(event) {
            $(this)
                .data('down', true)
                .data('x', event.clientX)
                .data('scrollLeft', this.scrollLeft);
            return false;
        })
        .mouseup(function (event) {
            $(this).data('down', false);
        })
        .mousemove(function (event) {
            if ($(this).data('down')) {
                this.scrollLeft = $(this).data('scrollLeft') + $(this).data('x') - event.clientX;
            }
        })
        .mousewheel(function (event, delta) {
            this.scrollLeft -= (delta * 30);
        })
        .css({
            'overflow' : 'hidden'
        });

    loopingAnimation = function(el, dir){
        if(scrollWrapper.data('loop')){
            var sign = (dir) ? offsetStep : -offsetStep;
            scrollWrapper[0].scrollLeft += sign;
            setTimeout( function(){ loopingAnimation(el,dir) }, animateTime );
                                   }
                        return false;
        }; 
});
