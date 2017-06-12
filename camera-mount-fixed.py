from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *

SEGMENTS =  48
#Bigger than anything in the model
INFINITE = 50


class AdjustableCameraMount(object):
   
    # motor connected to motor connector 16.4


    bolt_hole_r = SCREW_R 
    base_thickness = 1

    bumper_offset = 2 
    cage_w = 2#2#0.8#2
    frame_padding_z = 2 

    #This is the depth of the sider and corresponding groove for the slider
    slider_h = 0.5#1 #depth
    #How wide is the slider and its groove
    slider_w = 2 
    
    low_mount_angle = 0
    high_mount_angle = 30

    #start_angle = 60
    #The end angle will go the entire way so the camera mount can 
    #slide 
    end_angle = 270
    



    #If ther should be any additional padding to the height
    mount_height_padding = 2.0
    #This is used for the  minkoski
    mount_rounding_r = 0.5
    #this must have the minkoski added to it otherwise the 


    def __init__(self, camera, fc, angle):
        """ The camera to make the mount for """
        self.fc = fc
        self.camera = camera


        #mounting the camera
        self.mount_height = (camera.lens_r*2.0) + (self.mount_rounding_r*2.0) + self.mount_height_padding


        self.frame_h = (self.camera.h/2.0)  + self.frame_padding_z
        self.w = self.camera.w + self.cage_w*2

        self.slider_r = camera.depth #slider_bolt_cut_r + slider_w/2.0
        self.cage_r = camera.depth + self.bumper_offset
        self.angle = angle

        padding = 2.0
        self.camera_snap_w = self.camera.w + (1.5*2.0)#(self.camera.lens_r + padding) * 2.0



    def camera_mount2(self):
        padding = 2.0
        #compensate for minkoski
        thickness = 1.5
        #Height of things before minkoski
        h = self.mount_height 
        minkowski_h = h - self.mount_rounding_r * 2
        minkowski_w = self.camera_snap_w - self.mount_rounding_r * 2

        insert_cut_h = 2


        #The snap is centered
        snap = union()(
            translate([0, 0, thickness/2.0])(
                cube([self.camera_snap_w , h, thickness], center=True)), 
            translate([0, 0, thickness])(cylinder(h=self.camera.lens_h + 1, r = self.camera.lens_r + 1)),
        )


        snap = difference()(
            snap,

            translate([0, 0, -INFINITE/2.0])(cylinder(h=INFINITE, r = self.camera.lens_r)),
        )

        #now connect the camera snap to the base mount
        #Add the rounding so we remove the minkowski from the bottom
        ext_gap = self.camera.h/2.0 - h/2.0
        ext_h = ext_gap +  self.mount_rounding_r
        
        ext = cube([self.camera_snap_w, ext_h, self.camera.lens_barrel_h]) 

        camera_support_thickness = 5
        camera_support_h = self.camera.depth - self.camera.lens_h
        camera_support = cube([self.camera_snap_w, camera_support_h, camera_support_thickness])

        camera_support_y = h - self.mount_rounding_r - self.camera.lens_r - self.camera.h/2.0 - camera_support_thickness
        # Now round out all the edges, heights are summed 


#        angle_cut = translate([-INFINITE/2.0, -INFINITE - camera_support_thickness, 
#                               -INFINITE + self.camera.lens_barrel_h])(
#                                   rotate([self.angle, 0, 0])(
#            cube([INFINITE, INFINITE, INFINITE])
#                                   )
#        )
        angle_cut = translate([-INFINITE/2.0, 0, 
                               -INFINITE ])(

        cube([INFINITE, INFINITE, INFINITE])
        )

        
        mount =  union()(
            translate([0, h/2.0, 0])(snap),
            translate([0, -ext_gap, self.camera.lens_barrel_h-camera_support_h ])(
            rotate([90, 0, 0])(
                translate([-self.camera_snap_w/2.0, 0, 0])(camera_support)
)
            ),
            translate([-self.camera_snap_w/2.0,   -ext_gap, 0])(
                ext
            ),
            #angle_cut
        )

        mount = rotate([-self.angle, 0, 0])(
                translate([0, 
                           self.camera.lens_barrel_h, 
                           ext_gap + camera_support_thickness])(
                rotate([90, 0, 0])(
                    mount
                )
                )
                )

        mount -= angle_cut
        

        return mount


    def camera_mount(self):
        h = self.mount_height 
        w = self.camera_snap_w 
        thickness = self.camera.lens_barrel_h
 
        #We have a little give here with this value, this determines
        # How high the camera is mounted
        camera_support_thickness = 5

        minkowski_thickness = self.camera.lens_barrel_h/ 2.0
        minkowski_h = h - self.mount_rounding_r * 2
        minkowski_w = w - self.mount_rounding_r * 2

        #The snap is centered
        snap = difference()(
            translate([0, 0, minkowski_thickness/2.0])(
                cube([minkowski_w , minkowski_h, minkowski_thickness], center=True)), 
                #Cut out the hole for the camera
                    cylinder(h=self.camera.lens_barrel_h, 
                             r=self.camera.lens_barrel_r+self.mount_rounding_r),
        )


        # Remove the snap entry
        insert_cut_h =1
        #Cut out the top insert
        insert_cut_y = insert_cut_h + math.cos(math.radians(45)) * INFINITE 
        snap -= translate([0, insert_cut_y, 0])(
                   rotate([0, 0, 45])(
                        cube([INFINITE,INFINITE, INFINITE], center=True)
                    )
                )

        #Round out the snap
        snap = minkowski()(
                snap,  
                cylinder(h=minkowski_thickness , r=self.mount_rounding_r)
        )

        #Add protectors
        support_w = 1.5
#        snap += translate([-support_w/2.0, -INFINITE -self.camera.lens_r, thickness])(cube([support_w, INFINITE, self.camera.lens_h + 1]))
        snap += translate([self.camera.lens_r, -INFINITE + h/2.0, thickness])(cube([support_w, INFINITE, self.camera.lens_h + 1]))
        snap += translate([-self.camera.lens_r-support_w, -INFINITE + h/2.0, thickness])(cube([support_w, INFINITE, self.camera.lens_h + 1]))

        #now connect the camera snap to the base mount with an extension piece
        #Add the rounding so we remove the minkowski from the bottom
        ext_gap = self.camera.h/2.0 - h/2.0
        ext_h = ext_gap +  self.mount_rounding_r
        ext = cube([w, ext_h, self.camera.lens_barrel_h]) 


        camera_support_h = self.camera.depth - self.camera.lens_h
        camera_support = cube([w, camera_support_h, camera_support_thickness])

        camera_support_y = h - self.mount_rounding_r - self.camera.lens_r - self.camera.h/2.0 - camera_support_thickness

        # Add all the sub components together 
        mount =  union()(
            translate([0, h/2.0, 0])(
                snap
            ),
            translate([-w/2.0,   -ext_gap, 0])(
                ext
            ),
            translate([0, -ext_gap, self.camera.lens_barrel_h-camera_support_h ])(
            rotate([90, 0, 0])(
            translate([-w/2.0, 0, 0])(
                camera_support
            )
            )
            ),
        )

        # Add the angle we want
        mount = rotate([-self.angle, 0, 0])(
                translate([0, 
                           self.camera.lens_barrel_h, 
                           ext_gap + camera_support_thickness])(
                rotate([90, 0, 0])(
                    mount
                )
                )
                )

        #Remove anything below our target angle
        angle_cut = translate([-INFINITE/2.0, -INFINITE/2.0, 
                               -INFINITE ])(

                    cube([INFINITE, INFINITE, INFINITE])
                    )
        mount -= angle_cut
        

        return mount

    def _vtx_holder(self):


        camera_support_thickness = 5.0
        camera_pcb_depth = self.camera.depth - self.camera.lens_h
        b = math.tan(math.radians(self.angle)) * camera_pcb_depth

        holder_thickness  = math.sin(math.radians(90-self.angle)) * (camera_support_thickness - b)

        padding = 1.5
        holder_w = self.camera.w + padding * 2
        holder_h = self.camera.h/2.0 + padding
        #holder_thickness = 2
        brace = difference()(
            translate([-holder_w/2.0, 0, 0])(
                cube([holder_w, holder_h, holder_thickness])
            ), 
            translate([-self.camera.w/2.0, padding, -INFINITE/2.0])(
                cube([self.camera.w, INFINITE, INFINITE])
            )
        )
        
#        b = 2
#        y = 1
#        h = 1
#        alpha = 45
#        flat = 1
#        cantilever = polygon([
#            [0,0],
#            [0, b],
#            [-y, b],
#            [-y, b + flat],
#        ])
#
        
        a  = math.cos(math.radians(90-self.angle)) * (camera_support_thickness - b)
        y = camera_pcb_depth/ math.cos(math.radians(self.angle))


        #Add notches for rubber bands
        clip_w = 1.5
        clip_h = 2
        clip_thickness = 1
        band_clip = translate([holder_w/2.0, holder_h - clip_h, holder_thickness-clip_thickness])(
            cube([clip_w, clip_h, clip_thickness])
        )

        brace -= translate([-INFINITE/2.0, holder_h - 3.0, -INFINITE + 1])(cube([INFINITE, 1.5, INFINITE]))
        #brace += band_clip

        #left_band_clip = mirror([1, 0, 0])(band_clip)
        #brace += left_band_clip

            
        return translate([0, y + a - padding, 0])(brace)

    def _base(self):
        w = 7
        h = 8
        base_narrow = translate([-w/2.0, 0, 0])(
            cube([w, h, self.base_thickness])
        )

        
        padding = 2
        h1 = 1
        base_wide = translate([-self.camera_snap_w/2.0, h, 0])(
            cube([self.camera_snap_w, h1, self.base_thickness])
        )


        fixed_h = 1
        fixed_w = w 
        fixed_thickness  = 2.0

        fixed = translate([-fixed_w/2.0, 0, -fixed_thickness])(
            cube([fixed_w, fixed_h, fixed_thickness])
        )

        fixed_cut = translate([-3/2.0, -INFINITE/2.0, -INFINITE])(
            cube([3, INFINITE, INFINITE])
        )
        base = hull()(
            base_narrow,
            base_wide,
        )

        base += fixed
        base -= fixed_cut

        hole = translate([0, fixed_h + SCREW_R, -INFINITE/2.0])(
            cylinder(h = INFINITE, r = SCREW_R) 
        )

        base -= hole
        return translate([0, -h, 0])( base)



    def _sidewall(self, w, h, thickness=2.0):

        cut = rotate([0, 0, -self.angle])(
                translate([-INFINITE, 0, -INFINITE/2.0])(
                    cube([INFINITE, INFINITE, INFINITE])
                )
        )
        wall = cube([w, h, thickness])

        return wall - cut 

    def _protector2(self):
        padding = 1

        left_wall = translate([self.camera.w/2.0 + padding, 0, 0])(
            rotate([90, 0, 90])(
            self._sidewall(18, 18)
        )
        )


        base = rotate([0, 0, 45])(
            cube([self.fc.width, self.fc.height, self.base_thickness], center=True)
        )
        base = rotate([0, 0, -45])(
            inductrix_hole_punch(rotate([0, 0, 45])(base
                                                    ))),

        
        #right_wall = mirror([1, 0, 0])(left_wall)

        return union()(
            translate([0, -16, 0])( left_wall),
            translate([0, 0, self.base_thickness/2.0])(base)
        )

    def _protector(self):
        padding = 1
        side_wall_h = 18
        side_wall_w = 18
        side_wall_thickness = 2

        left_wall = translate([self.camera.w/2.0 + padding, 0, 0])(
            rotate([90, 0, 90])(
                difference()(
                    self._sidewall(side_wall_w, side_wall_h),
                    translate([side_wall_thickness, side_wall_thickness, -1])(
                        self._sidewall(side_wall_w - side_wall_thickness*2, 
                                       side_wall_h - side_wall_thickness*2, INFINITE))
                )
        )
        )




        
        #right_wall = mirror([1, 0, 0])(left_wall)

        return union()(
            translate([0, 0, 0])( left_wall),
        )

        

    def frame(self):

        right_sidewall = self._sidewall()
        right_sidewall = rotate([90, 0, 90])(
            right_sidewall
        )
        right_sidewall = translate([self.camera.w/2.0, 0, 0])(
            right_sidewall
        )

        left_sidewall = self._sidewall()
        left_sidewall = mirror([1, 0, 0])(left_sidewall)
        left_sidewall = rotate([90, 0, -90])(
            left_sidewall
        )
        left_sidewall = translate([-self.camera.w/2.0, 0, 0])(
            left_sidewall
        )

        inner_r = self.slider_r - self.slider_w -self.bumper_offset
        cage_h = self.cage_r - inner_r
        bar_r = 1
        bar = translate([0, 0, self.cage_r - cage_h/2.0])(
            rotate([0, 90, 0])(
            cylinder(h = self.camera.w, r = bar_r, center=True)
        )
        )

        top = union()(
            left_sidewall,
            right_sidewall,
#            bar,
        )
        #Before this action the frame is centered
        top = translate([0, 0, self.frame_h ])(top)

        bottom_support_ring = rotate([0, 90, 0])(
            difference()(
                cylinder(r = self.cage_r, h = self.camera.w, center=True),
                cylinder(r = self.cage_r - self.bumper_offset, h = self.camera.w, center=True),
                translate([0, INFINITE/2.0, 0])(cube([INFINITE, INFINITE, INFINITE], center=True))
            )
        )


        bottom_support_h = self.frame_h - self.camera.lens_r 
        bottom_support_intersect = translate([0, 0, bottom_support_h/2.0])(
            cube([self.camera.w, INFINITE, bottom_support_h], center=True)
        )
        print "Bottom support", bottom_support_h
        bottom_support = intersection()(
            translate([0, 0, self.frame_h ])(bottom_support_ring),
            bottom_support_intersect,
        )

        x = math.sqrt(math.pow(self.cage_r, 2) - math.pow(self.camera.lens_r, 2))
        flat_support = translate([0, -x + self.cage_r/2.0, bottom_support_h /2.0])(
            cube([self.w, self.cage_r, bottom_support_h], center=True))

        flat_support_cut = translate([0, 0, self.frame_h])(
            rotate([0, 90, 0])(
                cylinder(r = self.slider_r, h = self.w, center=True))
        )

        top = union()(
            top,
#            difference()(
#                flat_support,
#                flat_support_cut,
#            ),
        )
        return union()(
        #    translate([0, SCREW_HEAD_R, 0])(top),
            #top,
            #bottom_support,
            self.front_base(),

        )
    def front_base(self):
        base_h = self.base_thickness
        
        #base = cylinder(h = base_h, r = SCREW_HEAD_R)
        rounding_r = SCREW_HEAD_R
        fc_h_before = self.fc.height - rounding_r*2.0
        fc_w_before = self.fc.width - rounding_r*2.0
        thickness_before  = base_h/2.0

        keep = cube([self.camera.w + self.cage_w*2 - rounding_r*2.0, INFINITE, thickness_before], center=True) 

        fc_base = rotate([0, 0, 45])(
            cube([fc_w_before, fc_h_before, thickness_before], center=True)
        )

#        base = intersection()(
#            fc_base,
#            keep,
#        )
        x = math.sqrt(math.pow(self.cage_r, 2) - math.pow(self.camera.lens_r, 2))

        center_cut = translate([0, INFINITE/2.0 , 0])(
            cube([self.camera.w , INFINITE, INFINITE], center=True))
        back_cut = translate([0, INFINITE/2.0 , 0])(
            cube([INFINITE, INFINITE, INFINITE], center=True))


        fc_base = difference()(
                fc_base,
                #center_cut,
                back_cut,
        )
        base_minkowski = minkowski()(
            fc_base,
            cylinder(h=thickness_before, r=SCREW_HEAD_R, center=True),
        )
        center_cut = hull()(
            translate([0, INFINITE/2.0 - x + SCREW_HEAD_R , 0])(
            cube([self.camera.w  , INFINITE, INFINITE], center=True)),

            translate([0, -13, 0])(
                cylinder(r = SCREW_HEAD_R, h=INFINITE, center=True)
            )
        )

        base_minkowski -= center_cut


#        base_minkowski +=translate([self.camera.w/2.0, SCREW_HEAD_R, self.frame_h])(
#rotate([90, 0, 90])(
#slider_groove))

        base = rotate([0, 0, -45])(
            inductrix_hole_punch(rotate([0, 0, 45])(base_minkowski
                                                    ))),


        return translate([0, 0, base_h/2.0])(base)

    def sidewall_brace(self):

        rounding_r = SCREW_HEAD_R
        base_thickness = 1
        w = h = 5.66
        x = math.sqrt(math.pow(self.fc.width, 2)/2.0)  - math.sqrt(math.pow(w, 2)/2.0)

        #This is where we mount to the board/frame
        bottom_cage_interface = minkowski()(
            rotate([0, 0, 45])(
                cube([w-rounding_r*2, h-rounding_r*2, base_thickness/2.0], center=True)
            ),
            cylinder(h=base_thickness/2.0, r=SCREW_HEAD_R, center=True),
        )
        bottom_cage_interface = translate([x, 0,  base_thickness/2.0])(
            bottom_cage_interface)


        cage_angle = -31
        connector_h = 4
        top_cage_interface = translate([x-2, 0, 7])(
            rotate([0, cage_angle, 0])(
             cylinder(h = 0.1, r = 1))
        )

        cage_interface = hull()(
            top_cage_interface,
            bottom_cage_interface,
        )

        # Remove to get to tap
        cage_interface = rotate([0, 0, -45])(
            inductrix_hole_punch(rotate([0, 0, 45])(cage_interface), r=SCREW_HEAD_R)
        )
        cage_interface = translate([0, 0, base_thickness])(cage_interface)
        
        base = union()(
            rotate([0, 0, -45])(
                inductrix_hole_punch(
                    rotate([0, 0, 45])(
                        bottom_cage_interface
                    )
                )
            ),
            cage_interface,
        )

        connector = translate([x-2, 0, 8])(
            rotate([0, cage_angle, 0])(
             cylinder(h = 15, r = 1))
        )

        base += connector
        
        #base = rotate([0, 0, -45])(inductrix_hole_punch(rotate([0, 0, 45])(base)))
        return base 


    def asm(self):
        mount = union()(
            self.camera_mount(),
            self._vtx_holder(),
            self._base(),
    #        self._protector(),
        )

        return mount
    def test(self):
        """ Test assembly with camera """
#        camera =   translate([0, 4, DEFAULT_THICKNESS])(
#            rotate([-(90-mount_angle), 0, 0])(
#            translate([0, -CRAZYPONY_CAMERA_PCB_H/2.0, 0])(
#
        camera = translate([0, 11, 8,])(
            rotate([90-self.angle, 0, 0])(
            color([0, 0, 0, 0.2])(self.camera.make())
        )
        )

        fc = BeeBrain()
        return union()(
             translate([0, -12, 0])(self.asm()),
#
            translate([0, -12, 0])(camera),
            color([0, 0, 0, 0.2])(translate([0, 0, -self.fc.pcb_thickness -1])(rotate([0, 0, -45])(fc.make()))),
            #color(White)(self.sidewall_brace()),

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

    mount = AdjustableCameraMount(camera, fc, 20)
    #all = mount.camera_mount()

    #all = mount.test()
    #all = mount._vtx_holder()#camera_mount()
    #all = mount.frame()
    #all = mount._protector()
    all = mount.asm()

    scad_render_to_file(all,  filepath= "crazypony-mount-fixed.scad", file_header='$fn = %s;' % SEGMENTS)
