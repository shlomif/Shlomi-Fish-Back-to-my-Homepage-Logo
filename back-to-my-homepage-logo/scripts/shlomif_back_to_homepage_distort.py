#!/usr/bin/env python
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

import inkex, os, simplepath, cubicsuperpath, simpletransform, sys
import simplestyle
import tempfile
import shutil
import subprocess
import string
from ffgeom import *

from os.path import expanduser, join

temp_dir = tempfile.mkdtemp()

def param(name):
    Params = {
            'distort_wh_ratio': 3,
            'bez_w_percent': 30,
            'bez_h_percent': 20,
            'perspective_wh_ratio': 2,
            'perspective_edge_percent': 50,
    }
    ret = Params[name]
    if (isinstance(ret, (int, long))):
        return float(ret)
    else:
        return ret

def temp_svg_fn(basename):
    global temp_dir
    return join(temp_dir, basename + '.svg')

def p2s(x,y):
    return str(x) + ',' + str(y)

def draw_generic_style_path(name, my_id, parent, d_s):
    style = {   'stroke'        : '#000000',
                'stroke-width'  : '1',
                'fill'          : 'none'            }

    path_attribs = {'style' : simplestyle.formatStyle(style),
                    inkex.addNS('label','inkscape') : name,
                    'id': my_id,
                    'd' : d_s}

    path = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), path_attribs )

    return path

def calc_distort_path((x,y), (w,h), bez_w_percent, bez_h_percent):
    bez_w = (h * bez_w_percent) / 100
    bez_h = (h * bez_h_percent) / 100
    d_s = 'm '
    d_s += p2s(x,y) + ' '
    d_s += p2s(w,0) + ' '
    d_s += p2s(0,h) + ' '
    d_s += p2s(-w,0) + ' '
    d_s += 'c ' + p2s(bez_w,-bez_h) + ' ' + p2s(bez_w,-(h-bez_h)) + ' ' + p2s(0,-h) + ' '
    d_s += 'z'

    return d_s;

class GenericAddPathEffect(inkex.Effect):

    def __init__(self, basename):
        self.basename = basename
        inkex.Effect.__init__(self)

    def effect(self):
        draw_generic_style_path(self.get_path_name(), self.get_path_id(), self.current_layer,
            self.calc_d_s()
        )

    def calc_out_fn(self):
        return temp_svg_fn(self.basename)

    def write_to_temp(self, input_fn):
        self.affect(args=[input_fn], output=False)
        with open(self.calc_out_fn(), 'w') as fh:
            self.document.write(fh)

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

def calc_perspective_path( p1, p2, p3, p4):
    d_list = ['M'] + [p2s(*p) for p in [p1,p2,p3,p4]] + ['z']
    d_s = string.join(d_list, ' ')

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
            (orig_x,orig_y),
            (orig_x,orig_y-h),
            (orig_x+w,orig_y-h+edge_h),
            (orig_x+w,orig_y-edge_h)
        )

def main_path_id():
    return 'back'

def id_arg(my_id):
    return '--id=' + my_id

distort_e = AddDistortPathEffect('with_path')
distort_e.write_to_temp(sys.argv[-1])

with_envelope_text = subprocess.check_output(
        ['python',
            join(expanduser('~'), '.config', 'inkscape', 'extensions', 'bezierenvelope.py'),
            id_arg(main_path_id()),
            id_arg(distort_e.get_path_id()),
            distort_e.calc_out_fn()
        ]
)

with_envelope__filename = temp_svg_fn('with_envelope');

with open(with_envelope__filename, 'w') as fh:
    fh.write(with_envelope_text)

pers_e = AddPerspectivePathEffect('with_persepctive_path')
pers_e.write_to_temp(with_envelope__filename)

# with_pers_path__text = open(with_pers_path__filename).read()

with_perspective_applied_text = subprocess.check_output(
        ['python',
            '/usr/share/inkscape/extensions/perspective.py',
            id_arg(main_path_id()),
            id_arg(pers_e.get_path_id()),
            pers_e.calc_out_fn()
        ]
)

shutil.rmtree(temp_dir)

sys.stdout.write(with_perspective_applied_text)
