from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *

SEGMENTS =  12 
INFINITE = 100


class AdjustableCameraMount(object):
   
    # motor connected to motor connector 16.4

    bolt_hole_r = SCREW_R 

    bumper_offset = 1
    cage_w = 1#2#0.8#2
    cage_r = CRAZYPONY_CAMERA_DEPTH + bumper_offset
    
    low_mount_angle = 0
    high_mount_angle = 30

    #start_angle = 60
    #The end angle will go the entire way so the camera mount can 
    #slide 
    end_angle = 270
    

    slider_h = 0.5#1 #depth
    slider_w = 2 
    slider_r = CRAZYPONY_CAMERA_DEPTH #slider_bolt_cut_r + slider_w/2.0

    slider_bolt_cut_r = CRAZYPONY_CAMERA_DEPTH - slider_w/2.0 +  bolt_hole_r 


    #If ther should be any additional padding to the height
    mount_height_padding = 1.0
    #This is used for the  minkoski
    mount_rounding_r = 0.5
    #this must have the minkoski added to it otherwise the 


    def __init__(self, camera, fc):
        """ The camera to make the mount for """
        self.fc = fc
        self.camera = camera
        self.mount_height = (camera.lens_barrel_r*2.0) + (self.mount_rounding_r*2.0) + self.mount_height_padding

        angle = math.degrees(math.atan((self.mount_height/2.0) / (camera.depth - camera.lens_h - camera.lens_barrel_h)))
        self.start_angle = (180 - angle) - self.high_mount_angle

    def camera_mount(self):
        padding = 1.0
        #compensate for minkoski
        thickness = self.camera.lens_barrel_h/ 2.0
        #Height of things before minkoski
        height = self.mount_height - (self.mount_rounding_r*2.0)

        w = self.camera.w - self.mount_rounding_r * 2
        true_w = w +  self.mount_rounding_r * 2

        top_cut_h = 2

        mount = difference()(
            translate([0, 0, thickness/2.0])(
                cube([w , height, thickness], center=True)), 
                #Cut out the hole for the camera
                    cylinder(h=self.camera.lens_barrel_h, 
                             r=self.camera.lens_barrel_r+self.mount_rounding_r),
        )
        #Cut out the top
        cut_y = top_cut_h + math.cos(math.radians(45)) * INFINITE 
        mount -=         translate([0, cut_y, 0])(
                   rotate([0, 0, 45])(
                        cube([INFINITE,INFINITE, INFINITE], center=True)
                    )
                )

        # Now round out all the edges, heights are summed 
        mount =   minkowski()(
                mount,  
                cylinder(h=thickness , r=self.mount_rounding_r)
        )

        #This is the part for the peice that will go into the groove and    
        # will have the tap
        # Dont extend past the lens
        tap_h = 1
        start_angle =0 
        end_angle = 180
        slider = translate([true_w/2.0, 0, self.camera.lens_h + self.camera.lens_barrel_h -self.slider_w/2.0])(
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
        side_wall = translate([self.camera.w/2.0 - side_wall_w, 0, -self.slider_r + self.camera.lens_barrel_h + self.camera.lens_h])(
            rotate([90, 0, 90])(
                cylinder(h=side_wall_w, r=self.slider_r)
            )
        )
        side_wall_include = translate([CRAZYPONY_CAMERA_PCB_W/2.0 - side_wall_w, -self.mount_height/2.0, 0])(
                cube([INFINITE, self.mount_height, INFINITE])
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
        # NOTE solidpython doesnt have angle for rotate extrude
        #
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

        end_x = math.cos(math.radians(end_angle)) * max_d
        end_y = math.sin(math.radians(end_angle)) * max_d
        # Cut the angle away
        cutter = translate([0, 0, depth/2.0])(
            cube([max_d, max_d, depth], center=True)) - linear_extrude(height=max_d+INFINITE)(
            polygon([ [0, 0],[start_x, start_y],[middle_x, middle_y], [end_x, end_y] ])
        )

        #Round it off
        start_x = math.cos(math.radians(start_angle)) * (r-w/2.0)
        start_y = math.sin(math.radians(start_angle)) * (r-w/2.0)
        round_off = translate([start_x, start_y, 0])(
            cylinder(h = depth, r = w/2.0)
        )
        end_x = math.cos(math.radians(end_angle)) * (r-w/2.0)
        end_y = math.sin(math.radians(end_angle)) * (r-w/2.0)
        round_off_end = translate([end_x, end_y, 0])(
            cylinder(h = depth, r = w/2.0)
        )
        
        return (ring - cutter) + round_off + round_off_end


    def _tick_letter(self, letter, x, z):
        font = "Liberation Sans"
        letter_size = 1 
        letter_h = 5
        segment = 16
        letter = translate([x  , 0, z])(
            linear_extrude(height=letter_h)(
            text(letter, size=letter_size, font = font, halign="center", valign="center", segments=segment)
            )
        )
        return letter

    def _add_ticks(self, part, inverse=False):
        tick_depth = 0.2
        tick_h = 0.2
        major_tick_w = 1
        letter_padding = 1

        x =  -self.slider_bolt_cut_r + self.bolt_hole_r*2.0
        letter_x = x + major_tick_w + letter_padding
        angle_sign = -1
        if inverse:
            x = self.slider_bolt_cut_r - self.bolt_hole_r*2.0 - major_tick_w
            letter_x = x - letter_padding
            angle_sign = 1


        major_tick_max = 4
        z = self.cage_w - tick_depth
        major_tick = translate([x , -tick_h/2.0, z])(
                    cube([major_tick_w, tick_h, INFINITE])
        )
        letters = ["0", "1", "2", "3"]

        for i in range(major_tick_max):
            part -= rotate([0, 0, i*10*angle_sign])( 
                union()(
                    major_tick,
                    self._tick_letter(letters[i], letter_x, z)    
                )
            )

        return part


    def _frame_adjustable_sidewall(self):
        offset = 5 
        cage = cylinder(h = self.cage_w, r = self.cage_r)
        bolt_groove = self.groove(INFINITE, self.slider_bolt_cut_r, 
                                  self.bolt_hole_r*2.0, 180 + offset, 
                                  180 - self.high_mount_angle - offset)
        slider_groove = self.groove(self.slider_h, self.slider_r, 
                                    self.slider_w, self.start_angle, 
                                    self.end_angle)


        c = translate([0, 0, -1])(cylinder(h = INFINITE, r = self.slider_r - self.slider_w -self.bumper_offset))
        #Cut the bottom
        bottom_cut = translate([0, -INFINITE/2.0 - self.camera.h/2.0])(
            cube([INFINITE, INFINITE, INFINITE], center=True)
        )
        #offset -1 to cut threw all the way
        cage = difference()(
            cage, 
            translate([0, 0, -1])(bolt_groove), 
            slider_groove,
            bottom_cut,
            c,
        )
        return cage

    def frame(self):

        right_sidewall = self._frame_adjustable_sidewall()
        right_sidewall = self._add_ticks(right_sidewall)
        right_sidewall = rotate([90, 0, 90])(
            right_sidewall
        )
        right_sidewall = translate([self.camera.w/2.0, 0, 0])(
            right_sidewall
        )

        left_sidewall = self._frame_adjustable_sidewall()
        left_sidewall = mirror([1, 0, 0])(left_sidewall)
        left_sidewall = self._add_ticks(left_sidewall, inverse=True)
        left_sidewall = rotate([90, 0, -90])(
            left_sidewall
        )
        left_sidewall = translate([-self.camera.w/2.0, 0, 0])(
            left_sidewall
        )

        bar_r = 1
        bar = translate([0, 0, self.cage_r - bar_r])(
            rotate([0, 90, 0])(
            cylinder(h = self.camera.w, r = bar_r, center=True)
        )
        )
        return union()(
            left_sidewall,
            right_sidewall,
            bar,
        )

    def base(self):
        base_h = 1
        
        #base = cylinder(h = base_h, r = SCREW_HEAD_R)
        rounding_r = SCREW_HEAD_R
        fc_h_before = self.fc.height - rounding_r*2.0
        fc_w_before = self.fc.width - rounding_r*2.0
        thickness_before  = base_h/2.0

        keep = cube([self.camera.w + self.cage_w*2 - rounding_r*2.0, INFINITE, thickness_before], center=True) 
        fc_base = rotate([0, 0, 45])(
            cube([fc_w_before, fc_h_before, thickness_before], center=True)
        )

        base = intersection()(
            fc_base,
            keep,
        )
        base_minkowski = minkowski()(
            base,
            cylinder(h=thickness_before, r=SCREW_HEAD_R),
        )
        return base_minkowski 

    def test(self):
        """ Test assembly with camera """
#        camera =   translate([0, 4, DEFAULT_THICKNESS])(
#            rotate([-(90-mount_angle), 0, 0])(
#            translate([0, -CRAZYPONY_CAMERA_PCB_H/2.0, 0])(
#
        camera_angle = 30
        camera = rotate([90-camera_angle, 0, 0])(
            color(Black)(self.camera.make())
        )

        camera_holder = rotate([-camera_angle, 0, 0])(
            translate([0, -CRAZYPONY_CAMERA_PCB_THICKNESS, 0])(
                rotate([90, 0, 0])(
                        self.camera_mount()
                    )
            )
        )

        camera_asm = union()(
            camera,
            camera_holder
        )

        all = union()(
            camera_asm,
            color([0, 0, 1, 1])(self.frame()),
        #    color([0, 0, 1])(self.base())
        )
        fc = BeeBrain()
        return union()(
            translate([0, 0, self.camera.h/2.0 + self.fc.pcb_thickness/2.0])(all),
            rotate([0, 180, -45])(fc.make()),
            #translate([0, -7, 7])(color(FiberBoard)(crazypony_camera_tx()))

        )
#            )
#        )
#        )

if __name__ == "__main__":

    camera = CrazyponyCamera()
    fc = BeeBrain()
#    #Camera profile
#    camera.w = CRAZYPONY_CAMERA_PCB_W
#    camera.h = CRAZYPONY_CAMERA_PCB_H
#    camera.lens_barrel_r = CRAZYPONY_LENS_BARREL_R 
#    #this will be the thickness of the snap
#    camera.lens_barrel_h = CRAZYPONY_LENS_BARREL_H
#    camera.lens_r = CRAZYPONY_LENS_R
#    camera.lens_h = CRAZYPONY_LENS_H
#    camera.depth = CRAZYPONY_CAMERA_DEPTH

    mount = AdjustableCameraMount(camera, fc)
    #all = mount.camera_mount()

    all = mount.test()

    scad_render_to_file(all,  filepath= "crazypony-mount-adjustable.scad", file_header='$fn = %s;' % SEGMENTS)
