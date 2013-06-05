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
'''

import inkex, os, simplepath, cubicsuperpath, simpletransform, sys
import simplestyle
import tempfile
import shutil
import subprocess
import string
from ffgeom import *

from os.path import expanduser, join

def p2s(x,y):
    return str(x) + ',' + str(y)

#draw an SVG line segment between the given (raw) points
def draw_path( (x,y), (w,h), bez_w_percent, bez_h_percent, name, my_id, parent):
    style = {   'stroke'        : '#000000',
                'stroke-width'  : '1',
                'fill'          : 'none'            }

    bez_w = (h * bez_w_percent) / 100
    bez_h = (h * bez_h_percent) / 100
    d_s = 'm '
    d_s += p2s(x,y) + ' '
    d_s += p2s(w,0) + ' '
    d_s += p2s(0,h) + ' '
    d_s += p2s(-w,0) + ' '
    d_s += 'c ' + p2s(bez_w,-bez_h) + ' ' + p2s(bez_w,-(h-bez_h)) + ' ' + p2s(0,-h) + ' '
    d_s += 'z'

    line_attribs = {'style' : simplestyle.formatStyle(style),
                    inkex.addNS('label','inkscape') : name,
                    'id': my_id,
                    'd' : d_s}

    line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

def draw_perspective_path( p1, p2, p3, p4, name, my_id, parent):
    style = {   'stroke'        : '#000000',
                'stroke-width'  : '1',
                'fill'          : 'none'            }

    d_list = ['M'] + [p2s(*p) for p in [p1,p2,p3,p4]] + ['z']
    d_s = string.join(d_list, ' ')

    line_attribs = {'style' : simplestyle.formatStyle(style),
                    inkex.addNS('label','inkscape') : name,
                    'id': my_id,
                    'd' : d_s}

    line = inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )

class AddPathEffect(inkex.Effect):

    def __init__(self):
            inkex.Effect.__init__(self)

    def get_path_id(self):
        return 'for_envelope_path'

    def effect(self):
        draw_path( (150.0, 400.0), (300.0, 100.0), 30.0, 20.0, 'MyPath', self.get_path_id(), self.current_layer )


class AddPerspectivePathEffect(inkex.Effect):

    def __init__(self):
            inkex.Effect.__init__(self)

    def get_path_id(self):
        return 'for_persepctive_path'

    def effect(self):
        draw_perspective_path( (500,500), (450,450), (600,400), (650, 550), 'MyPerspectivePath', self.get_path_id(), self.current_layer )

e = AddPathEffect()
e.affect(args=sys.argv[1:],output=False)

temp_dir = tempfile.mkdtemp()
with_path__filename = join(temp_dir, 'with_path.svg');
with open(with_path__filename, 'w') as fh:
    e.document.write(fh)

def main_path_id():
    return 'back'

def id_arg(my_id):
    return '--id=' + my_id

with_envelope_text = subprocess.check_output(
        ['python',
            join(expanduser('~'), '.config', 'inkscape', 'extensions', 'bezierenvelope.py'),
            id_arg(main_path_id()),
            id_arg(e.get_path_id()),
            with_path__filename
        ]
)

with_envelope__filename = join(temp_dir, 'with_envelope.svg');

with open(with_envelope__filename, 'w') as fh:
    fh.write(with_envelope_text)

e = AddPerspectivePathEffect()
e.affect(args=[with_envelope__filename],output=False)

with_pers_path__filename = join(temp_dir, 'with_persepctive_path.svg');
with open(with_pers_path__filename, 'w') as fh:
    e.document.write(fh)

with_pers_path__text = open(with_pers_path__filename).read()

shutil.rmtree(temp_dir)

sys.stdout.write(with_pers_path__text)
