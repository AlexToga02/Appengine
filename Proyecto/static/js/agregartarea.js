(function ( $ ) {
    $.fn.feedback = function(success, fail) {
    	self=$(this);
		self.find('.dropdown-menu-form').on('click', function(e){e.stopPropagation()})


		self.find('.do-close').on('click', function(){
			self.find('.dropdown-toggle').dropdown('toggle');
			self.find('.reported, .failed').hide();
			self.find('.report').show();
			self.find('.cam').removeClass('fa-check').addClass('fa-camera');
		    self.find('.screen-uri').val('');
		    self.find('textarea').val('');
		});

		failed = function(){
			self.find('.loading').hide();
			self.find('.failed').show();
			if(fail) fail();
		}

		self.find('form').on('submit', function(){
			self.find('.report').hide();
			self.find('.loading').show();
			$.post( $(this).attr('action'), $(this).serialize()).done(function(res){
        if(res.result == 'success'){
          self.find('.loading').hide();
          self.find('.reported').show();
          	if(success) success();
        }

			});

		});
	};
}( jQuery ));

$(document).ready(function () {
	$('.feedback').feedback();
});