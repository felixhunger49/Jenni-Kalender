#!/usr/bin/env python3
"""Erzeugt Vorlagen (PDF + SVG) und die bebilderte Anleitung (PDF).

Aufruf:  python3 tools/build.py [ausgabeordner]
Benoetigt: Python 3, Node mit Playwright (Chromium) fuer den PDF-Druck.
"""
import base64
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from vorlagen import build_pages, page_chrome, check_pages  # noqa: E402
import anleitung  # noqa: E402

OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'ausgabe')


def font_css():
    css = []
    for fam, fn in (('Patrick Hand', 'PatrickHand.ttf'), ('Nunito', 'Nunito.ttf')):
        data = base64.b64encode(open(os.path.join(ROOT, 'fonts', fn), 'rb').read()).decode()
        css.append("@font-face{font-family:'%s';src:url(data:font/ttf;base64,%s) format('truetype');font-weight:100 900;}" % (fam, data))
    return '\n'.join(css)


def html_doc(body, extra_css=''):
    return '''<!doctype html><html lang="de"><head><meta charset="utf-8"><style>
%s
@page { size: A4 portrait; margin: 0; }
@page land { size: A4 landscape; margin: 0; }
html, body { margin: 0; padding: 0; }
.page { width: 210mm; height: 297mm; overflow: hidden; page-break-after: always; break-after: page; position: relative; }
.page.land { page: land; width: 297mm; height: 210mm; }
.page > svg { display: block; width: 100%%; height: 100%%; }
%s
</style></head><body>%s</body></html>''' % (font_css(), extra_css, body)


def print_pdf(html_path, pdf_path, png_dir=None):
    script = os.path.join(HERE, 'print.js')
    subprocess.run(['node', script, html_path, pdf_path] + ([png_dir] if png_dir else []), check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    svg_dir = os.path.join(OUT, 'svg')
    druck_dir = os.path.join(svg_dir, 'druck')
    plot_dir = os.path.join(svg_dir, 'plotter')
    for d in (druck_dir, plot_dir):
        os.makedirs(d, exist_ok=True)
    work = os.path.join(OUT, '.work')
    os.makedirs(work, exist_ok=True)

    pages = build_pages()
    probs = check_pages(pages)
    for pr in probs:
        print('WARNUNG:', pr)

    body = []
    for i, p in enumerate(pages, 1):
        chrome = page_chrome(p) + anleitung.page_footer(p, i, len(pages))
        svg = p.svg('print', chrome)
        name = '%02d-%s.svg' % (i, p.key)
        open(os.path.join(druck_dir, name), 'w').write(svg)
        open(os.path.join(plot_dir, name), 'w').write(p.svg('plot'))
        land = ' land' if p.size[0] > p.size[1] else ''
        body.append('<div class="page%s">%s</div>' % (land, svg.split('?>')[-1]))
    vor_html = os.path.join(work, 'vorlagen.html')
    open(vor_html, 'w').write(html_doc('\n'.join(body)))

    anl_html = os.path.join(work, 'anleitung.html')
    open(anl_html, 'w').write(html_doc(anleitung.body(pages), anleitung.CSS))

    json.dump([dict(nr=i, key=p.key, titel=p.title, kopien=p.copies) for i, p in enumerate(pages, 1)],
              open(os.path.join(work, 'seiten.json'), 'w'), ensure_ascii=False, indent=1)

    print_pdf(vor_html, os.path.join(OUT, 'Vorlagen-Eisenbahn-Adventskalender.pdf'),
              os.path.join(work, 'png-vorlagen') if os.environ.get('PNG') else None)
    print_pdf(anl_html, os.path.join(OUT, 'Anleitung-Eisenbahn-Adventskalender.pdf'),
              os.path.join(work, 'png-anleitung') if os.environ.get('PNG') else None)
    print('fertig:', OUT)


if __name__ == '__main__':
    main()
