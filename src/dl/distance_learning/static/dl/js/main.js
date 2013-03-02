$(function() {
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });

    /**
     * When clicking anywhere on the dimmed part of the page, the popup hides.
     */
    $('.lightbox').click(function() {
        var $this = $(this);
        $this.css('display', '');
        // Remove the anchor too
        window.location.replace('#');
    });
    /**
     * Make sure the undimmed part does not hide the popup.
     */
    $('.lightbox').children().click(function(event) {
        return false;
    }).children().click(function(event) {
        event.stopPropagation();
    });

    $('#search-input').autocomplete({
        source: function(request, response) {
            // Wraps the usual requests in a custom ajax call which uses "q"
            // instead of "term" for the query string parameter
            $.ajax({
                url: '/api/video/search/autocomplete/',
                data: {'q': request.term},
                success: function(value) {
                    response(value);
                }
            });
        },
        select: function(event, ui) {
            // Instead of just putting the value in the search box, selecting
            // an item triggers a search
            $('#search-input').val(ui.item.value);
            $('#search-form').submit();
        }
    });
    var fadeSpeed = 1500;

    /**
     * jQuery plugin to enable easy spinner creation.
     */
    $.fn.spin = function(opts) {
        this.each(function() {
            var $this = $(this),
            data = $this.data();
            if (data.spinner) {
                data.spinner.stop();
                delete data.spinner;
            }
            if (opts !== false) {
                data.spinner = new Spinner($.extend({color: $this.css('color')}, opts)).spin(this);
            }
        });
        return this;
    };
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
        top: 'auto', // Top position relative to parent in px
        left: '190px' // Left position relative to parent in px
    };

    /**
     * Populates the jQuery $container element with the videos from the videos
     * array.
     */
    var video_template = $('#video-template').html();
    function populateVideos(videos, $container) {
        $container.html(_.template(video_template, {videos: videos}))
                  .fadeTo(fadeSpeed, 1);
    }
    var fetchUrls = {
        'show-recent': '/api/video/recent/',
        'show-most-viewed': '/api/video/most-viewed/'
    };
    /**
     * The function loads videos from the endpoint found at the given url
     * and populates the destinationElement given by a jQuery object.
     */
    function loadVideos(url, $destinationElement) {
        $destinationElement.fadeTo(fadeSpeed, 0, function() {
            var $this = $(this);
            var $mySpinner = $("<div id='my-spinner'></div>");
            $mySpinner.css('margin-top', '40px');
            $this.before($mySpinner);
            $mySpinner.spin();
            $.ajax({
                url: url,
                data: {
                    'limit': 5
                },
                success: function(data) {
                    // Stop the spinner before populating the videos
                    $mySpinner.remove();
                    populateVideos(data.videos, $this);
                }
            });
        });
    }
    // Set up the callbacks for switching between the two video types.
    $('.show-recent').click(function() {
        var $this = $(this);
        $('.show-most-viewed').removeClass('selected');
        $('.show-recent').addClass('selected');
        var url = fetchUrls['show-recent'];
        loadVideos(url, $('.videos-column', $this.parents('.column')));
    });
    $('.show-most-viewed').click(function() {
        var $this = $(this);
        $('.show-most-viewed').addClass('selected');
        $('.show-recent').removeClass('selected');
        var url = fetchUrls['show-most-viewed'];
        loadVideos(url, $('.videos-column', $this.parents('.column')));
    });
    // FAQ
    $('ol#faq li').click(function() {
        $(this).next('div.answer').slideToggle();
    });
});
