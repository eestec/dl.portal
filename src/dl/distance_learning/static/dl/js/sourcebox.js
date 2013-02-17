/*
Copyright (C) 2011 by sourceLair Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software. The Software is provided without any kind of license.
*/

(function($){
$.fn.sourceBox = function(options , callback) {

var configuration = {
	"href" 		: "" , 
	"preload"	: true
}

if ( ( typeof options == "function" ) && ( typeof callback == "undefined" ) ) {
	callback = options ;
}else if (typeof options == "object") {
	$.extend ( configuration , options );
}

if ( ( configuration.preload == "true" ) || ( configuration.preload == true )) {
	$.sourceBox.preload();
}

this.each(function() {
$(this).click(function (e) {
	
	if ( ( $(this).attr("href") != "" ) && ( configuration.href == "" ) ) {
		configuration.href == $(this).attr("href");
	}
	
	if ( configuration.href == "") {
		return false;
	}
	
	e.preventDefault();
	$.sourceBox ( configuration , callback );

});
});
 };
})(jQuery);

(function($){
$.sourceBox= function(options , callback) {

var configuration = {
	"href" 		: "" , 
	"preload"	: true
}

if ( ( typeof options == "function" ) && ( typeof callback == "undefined" ) ) {
	callback = options ;
}else if (typeof options == "object") {
	$.extend ( configuration , options );
}

if (configuration.href == "") {
	return false ;
}

if ( ( configuration.preload == "true" ) || ( configuration.preload == true )) {
	$.sourceBox.preload();
}
			$("body").append('<div class="sourcebox-outer-container"></div>');
			$(".sourcebox-outer-container").append('<div class="sourcebox-fallback-layer"></div>');
			$(".sourcebox-outer-container").append('<div class="sourcebox-contents-container"></div>');
			$(".sourcebox-contents-container").append('<div class="sourcebox-contents"></div>');
			
			$(".sourcebox-fallback-layer").fadeIn("fast" , function () {
				$(".sourcebox-contents").html('<div class="sourcebox-loader"></div>');
			});
			$.sourceBox.center();
			$(".sourcebox-contents").load(configuration.href, function () {
				$.sourceBox.center(function () {
					$.sourceBox.center();
				});
				if (typeof callback == "function") {
					callback.call(this);
				}
			});
			$(".sourcebox-fallback-layer").click(function () {
				$.sourceBox.close ();
			});

};
})(jQuery);

(function($){
$.sourceBox.close = function(callback) {
	$(".sourcebox-outer-container").remove();
	if (typeof callback == "function") {
		callback.call(this);
	}
};
})(jQuery);

(function($){
$.sourceBox.preload = function(callback) {
	if ($(".sourcebox-loader-cache").length == 0) {
		$("body").append('<div class="sourcebox-loader-cache"></div>');
	}
	if (typeof callback == "function") {
		callback.call(this);
	}
};
})(jQuery);

(function($){
$.sourceBox.center = function(callback) {

	$('.sourcebox-contents-container').css({
		left: ($(window).width() - $('.sourcebox-contents-container').outerWidth())/2,
		top: ($(window).height() - $('.sourcebox-contents-container').outerHeight())/2
	});
	
	if (typeof callback == "function") {
		callback.call(this);
	}
};
})(jQuery);

$(window).resize(function(){
	$.sourceBox.center();	
});

$(document).keydown(function (e) {
	if (e.keyCode == 27) {
		$.sourceBox.close ();
	}
});
