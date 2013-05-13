#!/usr/bin/env python

import math
from gimpfu import *

def create_bk2hp_gradient():
    req_grad_name = 'Back to My Homepage Gradient'
    pdb.gimp_gradient_delete( req_grad_name )
    name = pdb.gimp_gradient_new( req_grad_name )
    pdb.gimp_gradient_segment_range_split_uniform( name, 0, 0, 2)

    edges_color = (0x00,0x00,0xFF)
    mid_color = (0x00,0xDE,0xFF)
    fully_opaque = 100.0
    pdb.gimp_gradient_segment_set_left_color( name, 0, edges_color, fully_opaque)
    pdb.gimp_gradient_segment_set_right_color( name, 0, mid_color, fully_opaque)
    pdb.gimp_gradient_segment_set_left_color( name, 1, mid_color, fully_opaque)
    pdb.gimp_gradient_segment_set_right_color( name, 1, edges_color, fully_opaque)
    return

register(
        "create_bk2hp_gradient",
        "Create the Back to My Homepage Gradeint",
        "Create the Back to My Homepage Gradeint",
        "Shlomi Fish",
        "Shlomi Fish",
        "2013",
        "<Image>/File/Create/Gradients/Back to my Homepage",
        "RGB*, GRAY*",
        [
        ],
        [],
        create_bk2hp_gradient)

main()
