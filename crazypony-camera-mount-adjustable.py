from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *

SEGMENTS =12
INFINITE = 20

class AdjustableCameraMount(object):
    bolt_hole_r = SCREW_R 

    bumper_offset = 1
    cage_w = 2
    cage_r = CRAZYPONY_CAMERA_DEPTH + bumper_offset
    
    start_angle = 60
    end_angle = 180 + 30
    

    slider_h = 1 #depth
    slider_w = 2 
    slider_r = CRAZYPONY_CAMERA_DEPTH #slider_bolt_cut_r + slider_w/2.0

    slider_bolt_cut_r = CRAZYPONY_CAMERA_DEPTH - slider_w/2.0 +  bolt_hole_r 

    def __init__(self):
        pass

    def camera_mount(self):
        barrel_radius = CRAZYPONY_LENS_BARREL_R 
        barrel_length = CRAZYPONY_LENS_BARREL_H
        padding = 1.0
        #This is used for the 
        rounding_r = 0.5
        #compensate for minkoski
        thickness = barrel_length/ 2.0
        #this must have the minkoski added to it otherwise the 
        true_height = (barrel_radius*2.0) + (rounding_r*2.0) + padding
        #Height of things before minkoski
        height = true_height - (rounding_r*2.0)

        w = CRAZYPONY_CAMERA_PCB_W - rounding_r * 2
        true_w = w +  rounding_r * 2

        mount = difference()(
            translate([0, 0, thickness/2.0])(
                cube([w , height, thickness], center=True)), 
                #Cut out the hole for the camera
                    cylinder(h=barrel_length , 
                             r=barrel_radius+rounding_r),
        )
        #Cut out the top
        cut_y = 2 + math.cos(math.radians(45)) * INFINITE 
        mount -=         translate([0, cut_y, 0])(
                   rotate([0, 0, 45])(
                        cube([INFINITE,INFINITE, INFINITE], center=True)
                    )
                )

        # Now round out all the edges, heights are summed 
        mount =   minkowski()(
                mount,  
                cylinder(h=thickness , r=rounding_r)
        )

        #This is the part for the peice that will go into the groove and    
        # will have the tap
        # Dont extend past the lens
        tap_h = 1
        start_angle =0 
        end_angle = 180
        slider = translate([true_w/2.0, 0, CRAZYPONY_LENS_H + barrel_length -self.slider_w/2.0])(
            rotate([90, 0, 90])(
                   difference()(
                        #move to to center to punch hole
                        translate([0, -self.slider_r + self.slider_w/2.0, 0])(
                            self.groove(self.slider_h, self.slider_r, self.slider_w, start_angle, end_angle)
                        ), 
                            # This is the tap
                            cylinder(h=tap_h, r=SCREW_R)
                        )
                )
        )


        #This is the support for the grooved piece
        side_wall_w = 2
        side_wall = translate([CRAZYPONY_CAMERA_PCB_W/2.0 - side_wall_w, 0, -self.slider_r + barrel_length + CRAZYPONY_LENS_H])(
            rotate([90, 0, 90])(
                cylinder(h=side_wall_w, r=self.slider_r)
            )
        )
        side_wall_include = translate([CRAZYPONY_CAMERA_PCB_W/2.0 - side_wall_w, -true_height/2.0, 0])(
                cube([INFINITE, true_height, INFINITE])
        )
        right_slider = union()(
            intersection()(
                side_wall,
                side_wall_include,
            ),
            intersection()(
                slider,
                side_wall_include
            )
        )
        left_slider = rotate([0, 0, 180])(right_slider)
        return union()(
            mount,
            right_slider,
            left_slider,
          #  slider


        )

    def groove(self, depth, r, w, start_angle, end_angle):
        #First create a ring
        r_inside = r - w
        ring = cylinder(h = depth, r = r )
        ring -= cylinder(h = depth, r = r_inside)

        #Second, counter clockwise cut it away
        max_d = r + INFINITE 
        start_x = math.cos(math.radians(start_angle)) * max_d
        start_y = math.sin(math.radians(start_angle)) * max_d

        middle_x = math.cos(math.radians((end_angle-start_angle)/2.0+start_angle)) * max_d
        middle_y = math.sin(math.radians((end_angle-start_angle)/2.0+start_angle)) * max_d

        print middle_x , ",", middle_y
        end_x = math.cos(math.radians(end_angle)) * max_d
        end_y = math.sin(math.radians(end_angle)) * max_d
        # Cut the angle away
        cutter = translate([0, 0, depth/2.0])(
            cube([max_d, max_d, depth], center=True)) - linear_extrude(height=max_d+INFINITE)(
            polygon([ [0, 0],[start_x, start_y],[middle_x, middle_y], [end_x, end_y] ])
        )
        return ring - cutter

    

    def adjustable_support(self):
        cage = cylinder(h = self.cage_w, r = self.cage_r)
        bolt_groove = self.groove(INFINITE, self.slider_bolt_cut_r, self.bolt_hole_r*2.0, self.start_angle, self.end_angle)
        slider_groove = self.groove(self.slider_h, self.slider_r, self.slider_w, self.start_angle, self.end_angle)
        #offset -1 to cut threw all the way
        cage = difference()(cage, translate([0, 0, -1])(bolt_groove), slider_groove)
        return cage

    def frame(self):

        support = rotate([90, 0, 90])(
            self.adjustable_support()
        )
        right_support = translate([CRAZYPONY_CAMERA_PCB_W/2.0, 0, 0])(
            support
        )
         #= 
        left_support  = mirror([1, 0, 0])(
            translate([CRAZYPONY_CAMERA_PCB_W/2.0, 0, 0])(support)
        )
        return union()(
            #left_support,
            right_support
        )

    def test(self):
        """ Test assembly with camera """
#        camera =   translate([0, 4, DEFAULT_THICKNESS])(
#            rotate([-(90-mount_angle), 0, 0])(
#            translate([0, -CRAZYPONY_CAMERA_PCB_H/2.0, 0])(
        camera = color(Black)(crazypony_camera())
        camera_holder = translate([0, 0, 0])(#CRAZYPONY_CAMERA_PCB_THICKNESS])(
            self.camera_mount()
        )

        camera_asm = union()(
            #camera,
            camera_holder
        )


        z = 0#self.slider_r - CRAZYPONY_CAMERA_DEPTH 
        frame_asm = union()(
            translate([0, 0, 0])(debug(self.frame())),
            #rotate([0, 0, 0])(
            #    translate([0, 0, z])(camera_asm))
        )
        return union()(
            #camera_asm,
            frame_asm,
    #        rotate([0, 180, -45])(BeeBrain().make()),
            #translate([0, -7, 7])(color(FiberBoard)(crazypony_camera_tx()))

        )
#            )
#        )
#        )

if __name__ == "__main__":

    mount = AdjustableCameraMount()
    #all = mount.camera_mount()

    all = mount.test()

    scad_render_to_file(all,  filepath= "crazypony-mount-adjustable.scad", file_header='$fn = %s;' % SEGMENTS)
