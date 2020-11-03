from . import create_app as app
from flask_assets import Bundle

def compile_static_assets(assets):
    assets.auto_build = True
    # set debug to False for production
    assets.debug = True
    main_css_bundle = Bundle(
        "css/libs/bootstrap.min.css",
        "css/offcanvas-main.css",
        "css/libs/fontawesome.min.css",
        "css/casc4de_typography.css",
        "css/style.css",
        filters="cssmin",
        output="gen/main_style.css",
        extra={"rel":"stylesheet/css", "id":"assetscss"}
    )
    main_js_bundle = Bundle(
        "js/libs/jquery-1.9.1.min.js",
        "js/libs/jquery-ui.min.js",
        "js/libs/popper.min.js",
        "js/libs/bootstrap.js",
        "js/libs/bootstrap-filestyle.min.js",
        "js/libs/jquery.navgoco.js",
        "js/libs/jquery.colorbox-min.js",
        # "js/libs/toastr.js",
        "js/libs/three.js",
        "js/libs/canvasrenderer.js",
        "js/libs/projector.js",
        "js/libs/stat.js",
        # "js/canvas_banner.js",
        "js/script.js",
        filters="jsmin",
        output="gen/main_script.js",
    )

    assets.register("main_css_bundle", main_css_bundle)
    assets.register("main_js_bundle", main_js_bundle)
    return assets