/*
 * jdMenu 1.4.0 (2008-01-25)
 *
 * Copyright (c) 2006,2007 Jonathan Sharp (http://jdsharp.us)
 * Dual licensed under the MIT (MIT-LICENSE.txt)
 * and GPL (GPL-LICENSE.txt) licenses.
 *
 * http://jdsharp.us/
 *
 * Built upon jQuery 1.2.1 (http://jquery.com)
 * This also requires the jQuery dimensions >= 1.2 plugin
 */
$(function() {
	$('ul.jd_menu').jdMenu();
});

(function($){
	$.jdMenu = {
		settings: 	[],
		getSettings: 	function( element ) {
							var t = $(element).parents('ul.jd_menu:eq(0)')[0];
							return this.settings[ t && t.$jdSettings ? t.$jdSettings : 0 ];	
						}
	};
	
	function activateMenu(ul) {
		var ul = $(ul);
		var li = ul.parent();
		ul	.trigger('jdMenuShow')
			.positionBy({ 	target: 	li[0], 
							targetPos: 	( li.parent().is('.jd_menu') ? 3 : 1 ), 
							elementPos: 0 
							});
		li	.addClass('jdm_active')
			// Hide any adjacent menus
			.siblings('li').find('ul:eq(0):visible')
				.each(function(){
					hideMenu( this ); 
				});
	}
	
	function hideMenu(ul) {
		$(ul)
			.filter(':not(.jd_menu)')
			.find('> li ul:eq(0):visible')
				.each(function() {
					hideMenu( this );
				})
			.end()
			.hide()
			.trigger('jdMenuHide')
			.parents('li:eq(0)')
				.removeClass('jdm_active jdm_hover')
			.end()
				.find('> li')
				.removeClass('jdm_active jdm_hover');
	}
	
	function getSettings(element) {
		return $.data( $(element).is('.jd_menu') ? element : $(element).parents('ul.jd_menu')[0], 'jdMenuSettings');;
	}
	
	// Public methods
	$.fn.jdMenu = function(settings) {
		var settings = $.extend({	activateDelay: 	500,
					showDelay: 		450, 
					hideDelay: 		1000
					}, settings);
		return this.filter('ul.jd_menu').each(function() {
			$.data(this, 'jdMenuSettings', settings);
			$('li', this)
				.bind('mouseenter.jdmenu', function() {
					$(this).addClass('jdm_hover');
					var ul = $('ul:eq(0)', this);
					if ( ul.length == 1 ) {
						var me = this;
						clearTimeout( this.$jdTimer );
						this.$jdTimer = setTimeout(function() {
							activateMenu( ul );
						}, getSettings(this).showDelay );
					}
				})
				.bind('mouseleave.jdmenu', function(){
					$(this).removeClass('jdm_hover');
					var ul = $('ul:eq(0)', this);
					if ( ul.length == 1 ) {
						var settings = $.jdMenu.getSettings( this );
						var me = this;
						clearTimeout( this.$jdTimer );
						this.$jdTimer = setTimeout(function() {
							hideMenu( ul );
						}, getSettings(this).hideDelay );
					}
				})
				.bind('click.jdmenu', function(evt) {
					var ul = $('> ul', this);
					if ( ul.length == 1 ) {
						activateMenu( ul );
						return false;
					}
					
					// The user clicked the li and we need to trigger a click for the a
					if ( evt.target == this ) {
						var link = $('> a', evt.target).not('.accessible');
						if ( link.length > 0 ) {
							var a = link[0];
							if ( !a.onclick ) {
								window.open( a.href, a.target || '_self' );
							} else {
								$(a).trigger('click');
							}
						}
					}
					$(this).parent().jdMenuHide();
					evt.stopPropagation();
				})
				.bind('keydown.jdmenu', function(e) {
					if ( e.which == 27 ) {
						if ( !$(this).parent().is('.jd_menu') ) {
							hideMenu( $(this).parent()[0] );
						}
						$(this).parents('li:eq(0)').find('a:eq(0)').trigger('focus');
						return false;
					}
				})
				.find('> a')
					.bind('focus.jdmenu', function() {
						$(this).parents('li:eq(0)').addClass('jdm_hover');
					})
					.bind('blur.jdmenu', function() {
						$(this).parents('li:eq(0)').removeClass('jdm_hover');
					})
					.filter('.accessible')
						.bind('click.jdmenu', function(evt) {
							evt.preventDefault();
						});
		});
	};
	
	$.fn.jdMenuUnbind = function() {
		$('li', this)
			.unbind('mouseenter.jdmenu mouseleave.jdmenu click.jdmenu keydown.jdmenu')
			.find('> a').unbind('focus.jdmenu blur.jdmenu click.jdmenu');
		return this;
	};
	
	$.fn.jdMenuHide = function() {
		return this.filter('ul').each(function(){ hideMenu( this ); });
	};

	// Private methods and logic
	$(window)
		// Bind a click event to hide all visible menus when the document is clicked
		.bind('click.jdmenu', function(){
			$('ul.jd_menu ul:visible').jdMenuHide();
		});
})(jQuery);
