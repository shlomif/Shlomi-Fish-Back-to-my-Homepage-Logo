#!/usr/bin/env python3
'''
Back to Homepage Distort

Shlomi Fish

Under the MIT/X11 License. ( http://en.wikipedia.org/wiki/MIT_License ).

Copyright (C) 2013 Shlomi Fish

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Requires:

* https://github.com/shlomif/Bezier-Envelope-for-Inkscape - to be installed
under ~/.config/inkscape/extensions

* Inkscape 0.48 or above.

'''

import re
import shutil
import subprocess
import sys
import tempfile
from os.path import expanduser, join

import inkex

from lxml import etree

# from ffgeom import *

temp_dir = tempfile.mkdtemp()


def param(name):
    _params = {
            'distort_wh_ratio': 3,
            'bez_w_percent': 20,
            'bez_h_percent': 20,
            'perspective_wh_ratio': 2,
            'perspective_edge_percent': 50,
    }
    ret = _params[name]
    if (isinstance(ret, int)):
        return float(ret)
    else:
        return ret


def temp_svg_fn(basename):
    global temp_dir
    return join(temp_dir, basename + '.svg')


def p2s(x, y):
    return str(x) + ',' + str(y)


def draw_generic_style_path(name, my_id, parent, d_s):
    style = {
            'stroke': '#000000',
            'stroke-width': '1',
            'fill': 'none'
            }

    path_attribs = {'style': str(inkex.Style(style)),
                    inkex.addNS('label', 'inkscape'): name,
                    'id': my_id,
                    'd': d_s}

    path = etree.SubElement(
        parent, inkex.addNS('path', 'svg'), path_attribs)

    return path


def calc_distort_path(xy, wh, bez_w_percent, bez_h_percent):
    x, y = xy
    w, h = wh
    bez_w = (h * bez_w_percent) / 100
    bez_h = (h * bez_h_percent) / 100
    d_s = 'm '
    d_s += p2s(x, y) + ' '
    d_s += p2s(w, 0) + ' '
    d_s += p2s(0, h) + ' '
    d_s += p2s(-w, 0) + ' '
    d_s += 'c ' + p2s(bez_w, -bez_h) + ' ' + \
        p2s(bez_w, -(h-bez_h)) + ' ' + p2s(0, -h) + ' '
    d_s += 'z'

    return d_s


class GenericAddPathEffect(inkex.Effect):

    def __init__(self, basename, input_fn):
        self.basename = basename
        self.input_fn = input_fn
        inkex.Effect.__init__(self)

    def effect(self):
        draw_generic_style_path(
            self.get_path_name(), self.get_path_id(),
            self.svg.get_current_layer(),
            self.calc_d_s()
        )

    def calc_out_fn(self):
        return temp_svg_fn(self.basename)

    def write_to_temp(self):
        with open(self.calc_out_fn(), 'wb') as fh:
            self.run(args=[self.input_fn], output=fh)

        return


class AddDistortPathEffect(GenericAddPathEffect):

    def get_path_name(self):
        return 'MyPath'

    def get_path_id(self):
        return 'for_envelope_path'

    def calc_d_s(self):
        h = 100.0
        w = h * param('distort_wh_ratio')
        return calc_distort_path(
            (150.0, 400.0),
            (w, h),
            param('bez_w_percent'), param('bez_h_percent')
        )


def calc_perspective_path(p1, p2, p3, p4):
    d_list = ['M'] + [p2s(*p) for p in [p1, p2, p3, p4]] + ['z']
    d_s = ' '.join(d_list)

    return d_s


class AddPerspectivePathEffect(GenericAddPathEffect):

    def get_path_name(self):
        return 'MyPerspectivePath'

    def get_path_id(self):
        return 'for_persepctive_path'

    def calc_d_s(self):
        orig_x = 500.0
        orig_y = 500.0

        h = 200.0
        w = param('perspective_wh_ratio') * h

        half_h = h * 0.5
        edge_h = (half_h * param('perspective_edge_percent')) / 100

        return calc_perspective_path(
            (orig_x, orig_y),
            (orig_x, orig_y-h),
            (orig_x+w, orig_y-h+edge_h),
            (orig_x+w, orig_y-edge_h)
        )


class StyleEffect(GenericAddPathEffect):
    def effect(self):
        svg_start = '<svg:linearGradient ' + \
            'xmlns:svg="http://www.w3.org/2000/svg"' + \
            ' xmlns="http://www.w3.org/2000/svg" id="bk2hp_grad">'
        self.svg.getElement(u'svg:defs').insert(
            0,
            etree.XML('''{svg_start}
                <stop style="stop-color:#0000ff;stop-opacity:1"
                    offset="0"
                    id="b2h_0" />
                <stop style="stop-color:#00deff;stop-opacity:1"
                    offset="0.4"
                    id="b2h_1" />
                <stop style="stop-color:#00deff;stop-opacity:1"
                    offset="0.6"
                    id="b2h_2" />
                <stop style="stop-color:#0000ff;stop-opacity:1"
                    offset="1"
                    id="b2h_3" />
                </svg:linearGradient>'''.format(svg_start=svg_start))
                )

        # Query the bounding box of main_path_id()
        q = {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        for param in q.keys():
            param_val_from_input = subprocess.check_output(
                ['inkscape', ('--query-'+param),
                 ('--query-id=' + main_path_id()), self.input_fn]
            )
            q[param] = float(param_val_from_input)

        svg_start = \
            '<svg:linearGradient xmlns:svg="http://www.w3.org/2000/svg" ' + \
            'xmlns="http://www.w3.org/2000/svg" ' + \
            'xmlns:xlink="http://www.w3.org/1999/xlink" id="bk2hp_grad_rot"'
        self.svg.getElement(u'svg:defs').insert(
            1,
            etree.XML(
                ('''%(svg_start)s xlink:href="#bk2hp_grad" x1="%(x)f" ''' +
                 '''y1="%(start_y)f" x2="%(x)f" y2="%(end_y)f" ''' +
                 '''gradientUnits="userSpaceOnUse" />''')
                % {
                    'x': (q['x'] + q['width']*0.5),
                    'svg_start': svg_start,
                    'start_y': q['y'],
                    'end_y': (q['y']+q['height']),
                })
        )
        self.svg.getElement(u'//*[@id="' + main_path_id() + '"]').set(
                'style', str(inkex.Style({
                    'stroke': '#888888',
                    'stroke-width': '1pt',
                    'fill': 'url(#bk2hp_grad_rot)',
                    }
                    )))


def main_path_id():
    return 'back'


def id_arg(my_id):
    return '--id=' + my_id


distort_e = AddDistortPathEffect('with_path', sys.argv[-1])
distort_e.write_to_temp()
# assert 0

with_envelope_text = subprocess.check_output(
        [
            'python',
            join(expanduser('~'), '.config', 'inkscape',
                 'extensions', 'bezierenvelope.py'),
            id_arg(main_path_id()),
            id_arg(distort_e.get_path_id()),
            distort_e.calc_out_fn()
        ]
)

with_envelope__filename = temp_svg_fn('with_envelope')

with open(with_envelope__filename, 'wb') as fh:
    fh.write(with_envelope_text)

pers_e = AddPerspectivePathEffect(
    'with_persepctive_path',
    with_envelope__filename
)
pers_e.write_to_temp()

# with_pers_path__text = open(with_pers_path__filename).read()

with_perspective_applied_text = subprocess.check_output(
        [
            'python',
            '/usr/share/inkscape/extensions/perspective.py',
            id_arg(main_path_id()),
            id_arg(pers_e.get_path_id()),
            pers_e.calc_out_fn()
        ]
)

with_perspective_applied__filename = temp_svg_fn('with_pers_applied')

# print('LLLLLLLLLLLLLLLLLLLLLL' +
#    with_perspective_applied_text.decode('utf-8'))
# assert 0
with open(with_perspective_applied__filename, 'wb') as fh:
    fh.write(with_perspective_applied_text)

style_e = StyleEffect('after_styling', with_perspective_applied__filename)
# style_e.run()
style_e.write_to_temp()
with open(style_e.calc_out_fn(), 'rt') as fh:
    text = fh.read()

output_fn = None
for i, arg in enumerate(sys.argv):
    if arg == '--output':
        output_fn = sys.argv[i+1]
        break
    m = re.match("\\A--output=(.*)", arg)
    if m:
        output_fn = m.group(1)
        break

if output_fn is None:
    sys.stdout.write(text)
else:
    with open(output_fn, 'wt') as fh:
        fh.write(text)
shutil.rmtree(temp_dir)
