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

    $('#add-favorite, #add-watch-later').click(function() {
        var $this = $(this);
        var url = $this.attr('href');
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'video_id': $('#video-id').html()
            },
            success: function(data) {
                alert(data);
            }
        });
        return false;
    });

    /**
     * Toggles the visibility of the jQuery element passed as the parameter.
     * It uses the slide up/down effect to do it.
     * @param $element a jQuery object 
     * @return boolean indicating the new visibility state of the element.
     */
    function toggleVisibility($element) {
        if ($element.hasClass('visible')) {
            $element.slideUp();
            $element.removeClass('visible');
        } else {
            $element.slideDown();
            $element.addClass('visible');
        }
        return $element.hasClass('visible');
    }
    // Show and hide the login form
    $('#login').click(function() {
        var $slidedown = $('#slidedown');
        var x = $('#login').offset().left - 55;
        $slidedown.css('left', x);
        // If this showed the form, focus the username field of the form
        if (toggleVisibility($slidedown)) {
            $('#username').focus();
        }
    });
    // Show and hide the user options
    $('#user').click(function() {
        var $tools = $('#tools');
        var x = $('#user').offset().left;
        $tools.css('left', x)
              .css('top', '40px');  // TODO: Move this to actual css?
        toggleVisibility($tools);
    });
    // Show and hide the sign up drop down
    $('#signup').click(function() {
        var $signup = $('#signup_options');
        var x = $('#signup').offset().left;
        $signup.css('left', x)
              .css('top', '40px');
        toggleVisibility($signup);
    });
    // Show and hide the about menu options
    $('#about_menu').click(function() {
        var $about = $('#about');
        var x = $('#about_menu').offset().left;
        $about.css('left', x)
              .css('top', '40px');
        toggleVisibility($about);
    });
    // TODO: Login form field validation
    // Form submit validation
    $('#login_form').submit(function(e) {
        // TODO: Check if all fields are valid before allowing a submit
        return true;
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
});
