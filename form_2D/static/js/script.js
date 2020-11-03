$(document).ready(function(){
    // -----------------------------------------------------------------
    // Menu
    // -----------------------------------------------------------------
    // initialize Offcanvas menu
    //Navigation Menu Slider
    $('#nav-expander').on('click', function(e) {
        e.preventDefault();
        $('body').toggleClass('nav-expanded');
    });
    $('#nav-close').on('click', function(e) {
        e.preventDefault();
        $('body').removeClass('nav-expanded');
    });
    $('#menu-drawer-menu a').on('click', function(e) {
        e.preventDefault();
        $('body').removeClass('nav-expanded');
    });
    // Initialize navgoco with default options
    $(".main-menu").navgoco({
        caret: '<span class="caret"></span>',
        accordion: false,
        openClass: 'open',
        save: true,
        cookie: {
            name: 'navgoco',
            expires: false,
            path: '/'
        },
        slide: {
            duration: 300,
            easing: 'swing'
        }
    });
    // -----------------------------------------------------------------
    // SMOOTH SCROLL
    // -----------------------------------------------------------------
    $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') || location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: target.offset().top-80
                }, 500);
                return false;
            }
        }
    });
});