"""Bundled user-supplied B Nazanin for Persian, with Latin glyph fallback."""
from pathlib import Path
import base64,html,json,os
import markdown

def font_css(root,location,embedded=False):
    root=Path(root).resolve();location=Path(location).resolve();font=root/'assets/fonts/B-NAZANIN.TTF'
    url=('data:font/ttf;base64,'+base64.b64encode(font.read_bytes()).decode()) if embedded else os.path.relpath(font,location).replace(os.sep,'/')
    return '@font-face {font-family:"B Nazanin";src:url("'+url+'") format("truetype");font-weight:400;font-style:normal;}\n'

BASE_CSS='''body{font-family:"B Nazanin","DejaVu Sans",sans-serif;direction:rtl;text-align:right;color:#111111;background:white;line-height:1.82;font-size:18px;max-width:1100px;margin:32px auto;padding:0 22px}h1,h2{color:#000000}h3{color:#000000}table{border-collapse:collapse;width:100%;font-size:.9em;margin:1em 0}th{background:#eeeeee;color:#000000}td,th{padding:6px;border-bottom:1px solid #cccccc;vertical-align:top}code,pre{font-family:"B Nazanin","DejaVu Sans Mono",monospace;direction:ltr;text-align:left;unicode-bidi:embed}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#111111}img{max-width:100%;height:auto}'''

def notebook_style(root):
    return '<style>'+font_css(root,root,True)+'''.jp-RenderedHTMLCommon,.rendered_html,.output_area,.text_cell_render,.jp-RenderedText pre,.jp-RenderedHTMLCommon *,.rendered_html *,.output_area *,.text_cell_render *{font-family:"B Nazanin","DejaVu Sans",sans-serif !important;color:#111111 !important}</style>'''
