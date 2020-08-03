#!/usr/bin/env python2

import math
from gimpfu import *

def is_str_in_tuple(s, t):
    for x in t:
        if (x == s):
            return True
    return False

def create_bk2hp_gradient():
    req_grad_name = 'Back-to-My-Homepage-Gradient'

    existing_gradients = pdb.gimp_gradients_get_list(req_grad_name)
    if is_str_in_tuple(req_grad_name, existing_gradients[1]):
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
    N_("Create Gradient..."),
    "",
    [
    ],
    [],
    create_bk2hp_gradient,
    menu="<Image>/File/Create/Gradients/Back to my Homepage",
    domain=("gimp20-python", gimp.locale_directory)
)

main()
