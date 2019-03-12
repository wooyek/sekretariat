# coding=utf-8
# Copyright 2014 Janusz Skonieczny

from pathlib import PosixPath

from django_assets import Bundle, register

assets_css = PosixPath('assets') / 'css'
assets_js = PosixPath('assets') / 'js'

CSS = (
    assets_css / "bootstrap4.css",
    # assets_css / "font-awesome4.css",
    assets_css / "font-awesome5.css",
    assets_css / "default.css",
)

JS = (
    # assets_js / "jquery.js",
    # assets_js / "jquery.min.js",
    assets_js / "bootstrap.js",
    # assets_js / "moment-with-locales.js",
    # assets_js / "bootstrap-datetimepicker.js",
    assets_js / "main.js",
)

JS = [str(f) for f in JS]
CSS = [str(f) for f in CSS]

register('js', Bundle(*JS, filters='yui_js', output='script.%(version)s.js'))
register('css', Bundle(*CSS, filters='yui_css', output='style.%(version)s.css'))
