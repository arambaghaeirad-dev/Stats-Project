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

def export_views(root):
    root=Path(root).resolve();(root/'assets/project.css').write_text('@font-face{font-family:"B Nazanin";src:url("fonts/B-NAZANIN.TTF") format("truetype");font-weight:400;}\n'+BASE_CSS)
    paths=[root/'README.md',root/'PROJECT_CARD.md',root/'data/README.md',*sorted((root/'docs').glob('*.md'))]
    for p in paths:
        body=markdown.markdown(p.read_text(),extensions=['tables','fenced_code']);css=font_css(root,p.parent)+BASE_CSS
        p.with_suffix('.html').write_text('<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>'+html.escape(p.stem)+'</title><style>'+css+'</style></head><body>'+body+'</body></html>')
    p=root/'notebooks/phase1_executed.ipynb'
    if p.exists():
        nb=json.loads(p.read_text());parts=[]
        for c in nb['cells']:
            src=''.join(c['source']) if isinstance(c['source'],list) else c['source']
            if c['cell_type']=='markdown':parts.append(markdown.markdown(src,extensions=['tables','fenced_code']))
            else:
                parts.append('<pre><code>'+html.escape(src)+'</code></pre>')
                for o in c.get('outputs',[]):
                    if o['output_type']=='stream':
                        val=o.get('text','');val=''.join(val) if isinstance(val,list) else val;parts.append('<pre>'+html.escape(val)+'</pre>')
                    else:
                        data=o.get('data',{})
                        if 'image/png' in data:
                            val=data['image/png'];val=''.join(val) if isinstance(val,list) else val;parts.append('<img src="data:image/png;base64,'+val+'">')
                        elif 'text/html' in data:
                            val=data['text/html'];parts.append(''.join(val) if isinstance(val,list) else val)
                        elif 'text/plain' in data:
                            val=data['text/plain'];val=''.join(val) if isinstance(val,list) else val;parts.append('<pre>'+html.escape(val)+'</pre>')
        css=font_css(root,p.parent,True)+BASE_CSS
        p.with_suffix('.html').write_text('<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>فاز اول</title><style>'+css+'</style></head><body>'+''.join(parts)+'</body></html>')
