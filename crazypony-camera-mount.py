from solid import *
from solid.utils import *

from solidpythonlib import *


SEGMENTS = 48
DEFAULT_THICKNESS = 0.5

pcb_width =  14.6
pcb_thickness = 5.4 #0.88
pcb_height = 12.09

lens_barrel_radius = (7.06/2.0)
lens_barrel_height =1.5 
lens_radius = 5.0
lens_height = 3.42 

antenna_length = 27
antenna_radius = (5.23/2.0)

fc_width = 28
fc_height = 28
fc_thickness = DEFAULT_THICKNESS #1.3
mount_angle = 20

h = math.hypot(pcb_thickness , pcb_height/2.0)

camera_y =  -7 

clip_thickness = 0.5
clip_radius = 0.5
clip_barrel_length = 1.5/2.0

tx_mount_w = 3
tx_mount_slot = 2
tx_mount_h =  DEFAULT_THICKNESS * 2 +  tx_mount_slot + clip_barrel_length + clip_thickness
tx_mount_clip_l = pcb_height/2.0
tx_mount_mounting_h = 0.5 + tx_mount_slot/2.0 + clip_barrel_length + clip_thickness 


camera_yy =  (pcb_thickness) / math.cos(math.radians(20))


#TODO define antenna 
def camera_tx(antenna_length, antenna_radius, pcb_width, pcb_height, pcb_thickness): 
    tx = union()(
        translate([0, 0, 0]) (
            cube([pcb_width, pcb_height, pcb_thickness ], True)
        ),
        translate([-pcb_width/2 + antenna_radius, pcb_height/2, 0])(
            rotate([-90, 0, 0]) (
                cylinder(h=antenna_length, r=antenna_radius)
            )
        )
    )
    return tx


def camera(lens_barrel_height, lens_barrel_radius, lens_height, lens_radius, pcb_width, pcb_depth, pcb_thickness = 0.88): 
    camera = union()(
        translate([0, 0, pcb_thickness/2.0])(
            cube([pcb_width, pcb_depth, pcb_thickness ], True)
        ),
        translate([0, 0, pcb_thickness])(
            cylinder(h=lens_barrel_height, r=lens_barrel_radius)
        ),
        translate([0, 0, lens_barrel_height + pcb_thickness])(
            cylinder(h=lens_height, r=lens_radius)
        )
    )
    return camera

def camera_mount_clip(clip_barrel_length, clip_barrel_radius, stopper_thickness):
    clip = rotate([0, 90, 0]) (
        cylinder(h=clip_barrel_length, r=clip_barrel_radius)
    )
    clip += translate([clip_barrel_length, 0, 0])(
                hull()(rotate([0, 90, 0]) (cylinder(h=stopper_thickness, r=clip_barrel_radius)),
                down(clip_barrel_radius*2)(
                    rotate([0, 90, 0]) (cylinder(h=stopper_thickness, r=clip_barrel_radius))
                )
            )
    )
    return clip

def tx_mount(w, h, slot_h, angle=5):
    thickness = 0.5 
    l = thickness *2 + slot_h
    tx_clip = cube([w, h, l], center=True)
     #translate([0, thickness*2, 0])(
    tx_clip -=  cube([w+2, h+2, slot_h], center=True)

    clip_thickness = 0.5
    clip_radius = 0.5
    clip_barrel_length = 1.5/2.0
    clip = camera_mount_clip(clip_barrel_length, clip_radius, clip_thickness) 

    tx_clip += color(Red)(
                translate([0, h/2-clip_radius, l/2.0])(
                    rotate([-90, -90, 0])(clip))
                )

    tx_clip += color(Red)(
                translate([0, h/2-clip_radius, -l/2.0])(
                    rotate([-90, 90, 0])(clip))
                )

    base = 10
    tx_mount_h = l + clip_barrel_length + clip_thickness 
    tx_clip += translate([0, -h/2.0, -tx_mount_h+l/2.0])(
    rotate([90,0,0])(linear_extrude(height=thickness*2.0)(
        polygon(points=[[-base/2.0, 0], [-w/2.0, tx_mount_h], [w/2.0, tx_mount_h], [base/2.0, 0]])
    ))
    )
    return tx_clip 

def camera_mount(height, barrel_radius, barrel_length, angle=20):
    #Main body to hold lens
    #height = height/2.0
    w_spacing = 2
    mount_width = barrel_radius*2.0 + w_spacing
    mount = translate([0, 0, barrel_length/2.0]) (
                cube([mount_width, height, barrel_length], True)
            #Have some overhang for the cut so it goes all the way through
            ) - translate([0, height/2.0, -1]) (
                cylinder(h=barrel_length + 2, 
                         r=barrel_radius)
            )


    #Add the clips
    clip_thickness = 0.5
    clip_radius = 0.5
    clip_barrel_length = 1.5/2.0
    clip = camera_mount_clip(clip_barrel_length, clip_radius, clip_thickness) 

    mount += color(Red)(
        translate([mount_width/2.0,height/2.0 - clip_radius, barrel_length/2.0])(
            rotate([-90, 0, 0])(clip))
        )
    mount += color(Red)(
        translate([-mount_width/2.0, height/2.0 - clip_radius, barrel_length/2.0])(
            rotate([-90, 180, 0])(clip))
        )


    #Add in the lift
    lift_h = barrel_length #
    lift_w = math.tan(math.radians(angle)) * lift_h 
    lift_l = mount_width 
    mount += color(Blue)(translate([mount_width/2, (height/2 + lift_w)*-1, barrel_length])(
                rotate([0, 180, 0])(
                    prism(lift_l, lift_w, lift_h)
                )
    ))

    #Brackets
    bracket_h = 2.0 
    bracket_l = bracket_h / math.tan(math.radians(angle)) 

    brackets_x = [DEFAULT_THICKNESS/2.0, mount_width/2.0,  -mount_width/2.0  +  DEFAULT_THICKNESS]

    for x in brackets_x:
        mount += color(Blue)(translate([x, (height/2 )*-1, 0])(
                    rotate([0, 180, 0])(
                        prism(DEFAULT_THICKNESS, bracket_h, bracket_l)
                    )
        ))

    #recenter
    return  translate([0, -height/2.0, 0])(mount)

def base(height, width, thickness, mounting_hole_radius=4.32/2.0):

    hole_r = 1.2/2.0

    hole_w = math.hypot(25, 25)
    hole_h = hole_w
    
    w = hole_w 
    h =  hole_h  
    base = hull()(
        translate([0, h/2.0, 0]) (
            cylinder(h = thickness, r=mounting_hole_radius)
        ), 
        translate([-w/2.0, 0, 0]) (
            cylinder(h = thickness, r=mounting_hole_radius)
        ), 
        translate([w/2.0, 0, 0]) (
            cylinder(h = thickness, r=mounting_hole_radius)
        ), 
    )

    base = base - translate([0, hole_h/2.0, -1]) (
            cylinder(h = thickness+2, r=hole_r)
        ) - translate([-hole_w/2.0, 0, -1]) (
            cylinder(h = thickness+2, r=hole_r)
        ) - translate([hole_w/2.0, 0, -1]) (
            cylinder(h = thickness+2, r=hole_r)
        ) 
#    fc = cube([width, height, thickness], True)
#    for i in range(4):
#        fc -= translate([0, 10, 0])(
#                rotate([i*90, 0, 0])(
#                    cylinder(h = thickness, r=mounting_hole_radius)
#                )
#        )

    return base 

def roll_cage():
    w=3
    r = 1
    base_w = math.hypot(25, 25)

    top = hull()(
    translate([0, -9, 9])(
        rotate([0, 90, 0])(
            cylinder(h = w, r=7)
        )
    ),
    translate([0, -base_w/2.0, r +DEFAULT_THICKNESS])(
        rotate([0, 90, 0])(
            cylinder(h = w, r=1)
        )
    ),
    translate([0, base_w/2.0, r + DEFAULT_THICKNESS])(
        rotate([0, 90, 0])(
            cylinder(h = w, r=r)
        )
    )
    )

    #cage = difference()(
    #    top, 
    cage = shell(2)(top) 
    #)
    return cage

class cage():
    def __init__(self):
        self.h = None


    def _bumper(self, depth, h):


        l = h-3 
        a = color(Red)(
            translate([0, h/2.0, depth/2.0])(
            cube([depth, h, depth], center=True))
            )
#
#        return hull()(
#
#
        b = translate([-depth/2.0, h, 10])(
                rotate([0, 90, 0])(
            cylinder(h = depth, r = 1.0),
        ))

        b2 = translate([-depth/2.0, h/4, 14])(
                rotate([0, 90, 0])(
            cylinder(h = depth, r = 1.0),
        ))

        c= translate([0, depth/2.0, l/2.0])(
            cube([depth, depth, l], center=True)
        )
#
#            translate([-depth/2.0, -4, h/2.0])(
#                rotate([0, 90, 0])(
#            cylinder(h = depth, r = 2.0)
#                ))
#            translate([-depth/2.0, 1, h/2.0])(
#                rotate([0, 90, 0])(
#                    cylinder(h = depth, r = h/2.0)
#                )
#            )
#        )
#
        return hull()(a,b,b2,c)
    def __call__(self):
        #height part of the camera
        lift_o = math.tan(math.radians(mount_angle)) * (lens_barrel_height + lens_height + pcb_thickness)
        lens_hyp = lift_o + (pcb_height/2.0) + lens_radius 
        lens_o = lens_hyp * math.sin(math.radians(90 - mount_angle))
        h = lens_o 
        depth = 2 
        w = pcb_width + (depth * 2)#Add bumbers

        part =    hull()(
        #part = union()(
                translate([0, h/2.0, depth/2.0])(
                    cube([w, lens_o, depth], center=True)
                ),
                translate([0, h+1, 0])(
                    cylinder(h = depth, r = 1.0)
                )
                )
        #Bumper
            #translate([0, 0, h/2.0])(
            #
            #)
        #)
        return                 union()(
part,  
                     translate([w/2.0 - depth/2.0, 0, 0])(
                         self._bumper(depth, h)
                     ),
                     translate([-w/2.0 + depth/2.0, 0, 0])(self._bumper(depth, h)),
                     )
    
def asm_cage(part):
    return back(3)(up(fc_thickness)(
        rotate([90, 0, 0])(part)))


def mount_camera():

    
    # (pcb_thickness / math.cos(math.radians(45.0))   #math.tan(math.radians(mount_angle)) * pcb_thickness
    m = union()(
                        debug(camera(lens_barrel_height, lens_barrel_radius, lens_height, lens_radius, pcb_width, pcb_height, pcb_thickness=pcb_thickness)),
        translate([0, 0, pcb_thickness])(
            camera_mount(h , lens_barrel_radius, lens_barrel_height)
        )
#            )
        #Add the camera
#        translate([0,  -camera_yy, fc_thickness/2.0])(
#            rotate([90 - mount_angle, 0, 0])(
#                color(Blue)(
#                    translate([0, pcb_height/2.0, 0])(
#                        camera(lens_barrel_height, lens_barrel_radius, lens_height, lens_radius, pcb_width, pcb_height, pcb_thickness=pcb_thickness)))
#            )
#        )
#    ,
#        # Add the camera mount
#        translate([0, camera_y , fc_thickness/2.0])( 
#            rotate([90-mount_angle, 0, 0])(
#            camera_mount(pcb_height, lens_barrel_radius, lens_barrel_height)
#            )
#        ),
    )
    return translate([0, pcb_height/2.0, 0])(m)




def assembly():
    all = union()(
            #Add Camera TX
            translate([0, 3, (fc_thickness/2.0) + tx_mount_slot/2.0 + tx_mount_h - tx_mount_slot - DEFAULT_THICKNESS ])(
                color(Blue)(
                    debug(camera_tx(antenna_length, antenna_radius, pcb_width, pcb_height, tx_mount_slot)))
            ),
#        # Add TX Mount
            translate([0, 0, tx_mount_mounting_h + fc_thickness/2.0])( 
                tx_mount(tx_mount_w, tx_mount_clip_l, tx_mount_slot)),
#
#
#        # Add the base 
            rotate([0, 0, 180])(
                color(Green)(
                base(fc_width, fc_height, fc_thickness)
                )
            ),
#        
#

        translate([0, camera_y, fc_thickness])(
                rotate([90 - mount_angle, 0, 0])(
            mount_camera()
        )),

        debug(asm_cage(cage()()))
    )
    return all
all = assembly()
#all = cage()()
#all = camera_mount(h , lens_barrel_radius, lens_barrel_height)

#all = base(fc_width, fc_height, fc_thickness)

scad_render_to_file(all,  filepath= "crazypony-mount.scad", file_header='$fn = %s;' % SEGMENTS)



