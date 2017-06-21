from solid import *
from solid.utils import *

from parts import *
from droneparts import *

SEGMENTS = 32#24#12 #48
DEFAULT_THICKNESS = 0.5


class CrazyponyInductrixCameraMount(object):
    clip_thickness = 0.5
    clip_radius = 0.5
    clip_barrel_length = 1.5/2.0

    tx_mount_support_w = 2
    tx_mount_w = 3
    tx_mount_slot = 2
    tx_mount_h =  DEFAULT_THICKNESS * 2 +  tx_mount_slot + clip_barrel_length + clip_thickness
    tx_mount_clip_l = CRAZYPONY_CAMERA_PCB_H #/2.0
    tx_mount_mounting_h = 0.5 + tx_mount_slot/2.0 + clip_barrel_length + clip_thickness 

    def __init__(self, angle=20):
        self.angle = angle

    def tx_mount_snap(self, clip_w, slot_h, thickness = 0.5):

        snap_r = thickness
        clip_l = CRAZYPONY_CAMERA_PCB_H + (snap_r*2)
        
        bottom_support_h = DIPOLE_ANTENNA_R - (slot_h/2.0  + thickness)
        clip_h = thickness * 2.0 + slot_h
        bracket_thickness = thickness
        bracket_w = self.tx_mount_support_w 
        bottom_bracket_h = bottom_support_h - thickness 

        #Bottom support
        bottom_support = translate([-CRAZYPONY_CAMERA_PCB_W/2.0, 0, 0 ])(
                cube([CRAZYPONY_CAMERA_PCB_W, self.tx_mount_support_w, bottom_support_h])
        )
        #Top support
        top_support = translate([-CRAZYPONY_CAMERA_PCB_W/2.0, 0, bottom_support_h + slot_h])(
            cube([CRAZYPONY_CAMERA_PCB_W, self.tx_mount_support_w, self.tx_mount_support_w])
        )

        #Main piece where the tx will fit
        tx_clip =  difference()(
            cube([clip_w, clip_l, clip_h]),
            translate([0, thickness, thickness])(
                cube([clip_w+2, clip_l, slot_h])
            )
        )
        #Add snaps at the ends
        top_snap = translate([0,  clip_l-snap_r, clip_h-snap_r])(
            rotate([0, 90, 0])(
                cylinder(h=clip_w, r=thickness)
            )
        )
        bottom_snap = translate([0, clip_l-snap_r, snap_r])(
            rotate([0, 90, 0])(
                cylinder(h=clip_w, r=thickness)
            )
        )

        #Bracket top
        top_bracket = translate([bracket_thickness/2.0 + clip_w/2.0, bracket_w + self.tx_mount_support_w, clip_h])(
            rotate([0, 0, 180])(
                    prism( bracket_thickness, bracket_w,  self.tx_mount_support_w - thickness)
            )
        )

        #Bracket bottom
        bottom_bracket = translate([clip_w/2.0 - bracket_thickness/2.0, bracket_w + self.tx_mount_support_w, 0])(
            rotate([0, 180, 180])(
                prism( bracket_thickness, bracket_w,  bottom_bracket_h)
            )
        )
        
        clip_asm = translate([-clip_w/2.0, 0, bottom_support_h-thickness]) (
            union()(tx_clip, top_snap, bottom_snap,  bottom_bracket, top_bracket) 
        )

        return rotate([0, 0, 180])(union()(bottom_support, clip_asm, top_support))


    def camera_mount_snap(self, height, barrel_radius, barrel_length):

        thickness = barrel_length/ 2.0
#CRAZYPONY_LENS_H +
        h1 = math.sin(math.radians(self.angle)) * (CRAZYPONY_LENS_BARREL_H +  CRAZYPONY_CAMERA_PCB_THICKNESS)
        h2 = math.sin(math.radians(90 - self.angle)) * (CRAZYPONY_CAMERA_PCB_H/2.0)
        height = (h1 + h2)/math.sin(math.radians(90-self.angle))
#
        #Main body to hold lens

        rounding_r = 0.5
        #height = 10 #barrel_radius * 3 
        w_spacing = 2
        above_h = barrel_radius
        mount_width = barrel_radius*2.0 + 1 #*2.0 + w_spacing
        center_w = w_spacing
        insert_w = mount_width 
        w = mount_width + rounding_r * 2

        insert_x = 4.0
        top_offset =2 


        mount = translate([0, 0, 0]) (
                    cube([mount_width, height + above_h, thickness])
                #Have some overhang for the cut so it goes all the way through
                ) - translate([mount_width/2.0, height, 0]) (
                    cylinder(h=barrel_length , 
                             r=barrel_radius+rounding_r)
                #Cut out the top
                ) - translate([mount_width/2.0, height + above_h + top_offset, 0])(rotate([0, 0, 45])(
                    cube([insert_w, insert_w , insert_w], center=True)
                )                 )

        # heights are summed 
        mount = translate([rounding_r, rounding_r, 0])(
            minkowski()(
                mount,  
                    cylinder(h=thickness , 
                             r=rounding_r)
        )
        )

        support_w = 2
        mount += translate([0, 0, 0])(
            cube([w, support_w, 10])
        )

        #
        base_w =20#2 
        base_thickness = 4 
        back_l =3  
        base_l =20 #barrel_length + 3
        # mount = translate([0, height/2.0, 0])(mount)
        base = rotate([-self.angle, 0, 0])(
            translate([0, -base_w,  0])(
                cube([w, base_w, base_l])
            ))

        mount -= base
        mount = rotate([90 + self.angle, 0, 0])( mount)

        slit_w = 3 
        mount -= translate([w/2.0 - slit_w/2.0 , -500, 2])(
            cube([slit_w, 1000, 1000])
        )

        return translate([-w/2.0, 0, 0])(mount)


    def base(self, thickness):

        c = cylinder(h = thickness, r= INDUCTRIX_FC_MOUNTING_HOLE_OR)
        base = hull()(
            translate([0, INDUCTRIX_HOLE_TO_HOLE_W/2.0, 0]) (
                c
            ), 

            #sides
            translate([-INDUCTRIX_HOLE_TO_HOLE_W/2.0, 0, 0]) (
                c
            ), 
            translate([INDUCTRIX_HOLE_TO_HOLE_W/2.0, 0, 0]) (
                c
            ), 

            #Back
            translate([CRAZYPONY_CAMERA_PCB_W/2.0+2, -3, 0]) (
                c
            ),
            translate([-CRAZYPONY_CAMERA_PCB_W/2.0-2, -3, 0]) (
                c
            )
            
        ) 
        base = inductrix_fc_hole_puncher(base)

        side_cut = minkowski()(cube([20, 20, 5]), c)

        base -= translate([7, 5, 0])( side_cut)
        base -= translate([-27, 5, 0])( side_cut)
        return translate([0,  INDUCTRIX_FC_MOUNTING_HOLE_OR, 0])(base)


    def _lift(self, w, h, l, angle):

        a =rotate([angle, 180, 0])(
            difference()(
            translate([-w/2.0, 0, 0])(
                cube([w, h, l])
            ),
            rotate([-mount_angle, 0, 0])(
                translate([-w/2.0, -h, 0])(
                    color(Blue)(cube([w + 2, h, l + 2]))
                )
            )
        )
        )

        z = h * math.cos(math.radians(90-angle))
        b = translate([0, 0, z])(a)
        c = translate([-w/2.0 - 1, 0,  -l])(cube([w+2, h, l]))

        return difference()(b, c)


    def _bumper(self, depth, h):

        #This is how far the bumper sticks out
        l = 6.0

        r = 1.0
        top_z = 13
        second_z = 10


        #side piece attaching to body
        a = color(Red)(
                translate([0, h/2.0, depth/2.0])(
                cube([depth, h, depth], center=True))
            )

        # higher
        b = translate([-depth/2.0, h, second_z])(
                rotate([0, 90, 0])(
            cylinder(h = depth, r = r),
        ))

        #low
        b2 = translate([-depth/2.0, h/4, top_z])(
                rotate([0, 90, 0])(
            cylinder(h = depth, r = r),
        ))

        #bottom
        c= translate([0, depth/2.0, l/2.0])(
            cube([depth, depth, l], center=True)
        )

        outside = hull()(a,b,b2,c)


        return shell(outside)

    def _backing(self, w, h, depth):

        top_offset = 1
        r = 1.0
        back =    hull()(
        #part = union()(
                translate([0, h/2.0, depth/2.0])(
                    cube([w, h, depth], center=True)
                ),
                translate([0, h+top_offset, 0])(
                    cylinder(h = depth, r = r)
                )
                )

        t = 2 
        h -= t
        w -= t

        cut =    hull()(
                translate([0, h/2.0, depth/2.0])(
                    cube([w, h, depth], center=True)
                ),
                translate([0, h+top_offset, 0])(
                    cylinder(h = depth, r = r)
                )
                )
        backing = difference()(
            back, 
            translate([0, 0, 0])(color(Blue)(cut)))
        return backing


    def cage(self):
        #height part of the camera
        lift_o = math.tan(math.radians(mount_angle)) *
             CRAZYPONY_LENS_BARREL_H + 
             CRAZYPONY_LENS_H + 
             CRAZYPONY_CAMERA_PCB_THICKNESS

        lens_hyp = lift_o + (CRAZYPONY_CAMERA_PCB_H/2.0) + CRAZYPONY_LENS_R 
        lens_o = lens_hyp * math.sin(math.radians(90 - mount_angle))
        h = lens_o 
        depth = 2 
        w = CRAZYPONY_CAMERA_PCB_W + (depth * 2)#Add bumbers

        return  rotate([90, 0, 180])(union()(
        self._backing(w, h, depth),  
                     translate([w/2.0 - depth/2.0, 0, 0])(
                         self._bumper(depth, h)
                     ),
                     translate([-w/2.0 + depth/2.0, 0, 0])(
                         self._bumper(depth, h)
                     ),
                )
        )

    def make(self):    
        h1 = math.hypot(CRAZYPONY_CAMERA_PCB_THICKNESS , CRAZYPONY_CAMERA_PCB_H/2.0)
        camera_y =  -5 
        base_thickness = DEFAULT_THICKNESS
        camera_tx_z = base_thickness + DIPOLE_ANTENNA_R

        # Add TX Mount
        tx_mount = translate([0, self.tx_mount_support_w, base_thickness])(# tx_mount_mounting_h + fc_thickness/2.0])( 
            self.tx_mount_snap(self.tx_mount_w,  self.tx_mount_slot)
        )

        base = rotate([0, 0, 0])(
            color(Green)(
                self.base(base_thickness)
            )
        )
        
        camera_mount = translate([0, 11, base_thickness])(

            self.camera_mount_snap(h1 , CRAZYPONY_LENS_BARREL_R, CRAZYPONY_LENS_BARREL_H)
        ),

        # Add cage
        cage = back(0)(
            up(base_thickness)(
                #rotate([90, 0, 0])(
                    debug(self.cage())
                #)
            )
        )

        a = union()(
            tx_mount, 
                      camera_mount,
                      cage,
        # Add camera mount
        )

        all = union()(back(3)(a), base)
        return all

def mount_camera():

    h1 = math.hypot(CRAZYPONY_CAMERA_PCB_THICKNESS , CRAZYPONY_CAMERA_PCB_H/2.0)

    m = union()(
        debug(
            crazypony_camera(CRAZYPONY_LENS_BARREL_H, CRAZYPONY_LENS_BARREL_R, CRAZYPONY_LENS_H, CRAZYPONY_LENS_R, CRAZYPONY_CAMERA_PCB_W, CRAZYPONY_CAMERA_PCB_H, CRAZYPONY_CAMERA_PCB_THICKNESS=CRAZYPONY_CAMERA_PCB_THICKNESS)),

        translate([0, 0, CRAZYPONY_CAMERA_PCB_THICKNESS])(
            camera_mount_snap(h1 , CRAZYPONY_LENS_BARREL_R, CRAZYPONY_LENS_BARREL_H)
        )
    )
    return translate([0, CRAZYPONY_CAMERA_PCB_H/2.0, 0])(m)



if __name__ == "__main__":

    mount_angle = 20
    mount = CrazyponyInductrixCameraMount(mount_angle)

    h1 = math.hypot(CRAZYPONY_CAMERA_PCB_THICKNESS , CRAZYPONY_CAMERA_PCB_H/2.0)
    all = translate([-0, 0, 0])(mount.camera_mount_snap(h1, CRAZYPONY_LENS_BARREL_R, CRAZYPONY_LENS_BARREL_H))

    all = mount.make()
     #debug(
    camera =   translate([0, 4, DEFAULT_THICKNESS])(
        rotate([-(90-mount_angle), 0, 0])(
        translate([0, -CRAZYPONY_CAMERA_PCB_H/2.0, 0])(
            crazypony_camera()
        )
    )
    )
    scad_render_to_file(all,  filepath= "crazypony-mount.scad", file_header='$fn = %s;' % SEGMENTS)



