from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *

SEGMENTS = 12 
#Bigger than anything in the model
INFINITE = 50

VERSION = 5 

"""
Improvements for next version

* Decrease thickness of base, can not get a good fix to the frame
  or alternatively get longer screws or use bolt
* The VTX is still not staying put, its shifting side-to-side. 
  Increase sidewalls
* Decrease weight
* The front alignment supports did not print, consider chaning this


"""

class FixedCameraMount(object):
   

    base_thickness = 1


    #If ther should be any additional padding to the height

    #This is used for the  minkoski
    mount_rounding_r = 0.5
    #this must have the minkoski added to it otherwise the 


    def __init__(self, camera, fc, angle):
        """ The camera to make the mount for """
        self.fc = fc
        self.camera = camera

        self.slider_r = camera.depth #slider_bolt_cut_r + slider_w/2.0
        self.angle = angle

        padding = 2.0
        self.camera_snap_w = self.camera.w + (1.5*2.0)#(self.camera.lens_r + padding) * 2.0


    def _protector(self, h, camera_origin_y):
        #Add protectors
        wall_w = 1.5
        wall_thickness = self.camera.lens_h + 1

        center_wall_inner_w = self.camera.lens_r * 2.0
        center_wall_w = center_wall_inner_w + (wall_w * 2)

        wall_l = (h - camera_origin_y) + (math.hypot(center_wall_w,center_wall_w)/2.0 - (self.camera.lens_r + wall_w)) / math.tan(math.radians(45))

        hollow_diamond = translate([0, 0, wall_thickness/2.0])(
            rotate([0, 0, 45])(
                difference()(
                    union()(
                        cube([center_wall_w, center_wall_w, wall_thickness], center=True),

                        #Add the bottom suppport. Add it here so the center gets cut
                        rotate([0, 0, -45])(
                        translate([0, -INFINITE/2.0, 0])(
                            cube([wall_w, INFINITE, wall_thickness], center=True),
                        )
                        ),


                    ),
                    cube([center_wall_inner_w, center_wall_inner_w, INFINITE], center=True),
                )
            )
            )
        v = intersection()(
            hollow_diamond,
            translate([0, -INFINITE/2.0, 0])(
            cube([(self.camera.lens_r + wall_w) * 2.0, INFINITE, INFINITE], center=True)
            )
        )



        wall = cube([wall_w, wall_l, wall_thickness])

        wall_y = (h - camera_origin_y) - wall_l
        protector = union()(
            translate([self.camera.lens_r, wall_y, 0])(
                wall
            ),
        
            translate([-self.camera.lens_r-wall_w, wall_y, 0])(
                wall,
            ),
            v

        )

        #normalize
        return protector

    def _camera_mount(self):
        mount_height_padding = 2.0
        h = (camera.lens_r*2.0) + (self.mount_rounding_r*2.0) + mount_height_padding
        w = self.camera_snap_w 
        thickness = self.camera.lens_barrel_h
 
        #We have a little give here with this value, this determines
        # How high the camera is mounted
        camera_support_thickness = 5

        camera_face_plate = translate([-w/2.0, 0, 0])(
                cube([w , h, thickness])
        ) 

        #Create cut
        camera_cut = hull()(
                    translate([0, INFINITE, 0])(
                        cube([self.camera.lens_barrel_r *2.0, 1, INFINITE], center=True)
                    ),
                    translate([0, 0, -INFINITE/2.0])(
                        cylinder(h=INFINITE, 
                                 r=self.camera.lens_barrel_r),
                    )

        )

        camera_face_plate -= translate([0, self.camera.h/2.0, 0])(camera_cut)

        camera_face_plate += translate([0, self.camera.h/2.0, thickness])(self._protector(h, self.camera.h/2.0))

        #now connect the camera snap to the base mount with an extension piece
        #Add the rounding so we remove the minkowski from the bottom
        ext_gap = self.camera.h/2.0 - h/2.0
        ext_h = ext_gap 
        ext = cube([w, ext_h, self.camera.lens_barrel_h]) 


        camera_support_h = self.camera.depth - self.camera.lens_h
        camera_support = cube([w, camera_support_h, camera_support_thickness])

        camera_support_y = h - self.camera.lens_r - self.camera.h/2.0 - camera_support_thickness

        # Add all the sub components together 
        mount =  union()(
               color([1, 1, 1, 1])(camera_face_plate),
#            translate([-w/2.0, -ext_h, 0])(
#                ext
#            ),
            translate([0, 0, self.camera.lens_barrel_h-camera_support_h ])(
            rotate([90, 0, 0])(
            translate([-w/2.0, 0, 0])(
                camera_support
            )
            )
            ),
        )


        #mount += self._vtx_holder()

        # Add the angle we want
        mount2 = rotate([-self.angle, 0, 0])(
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
        mount2 -= angle_cut
        

        return mount

    def _vtx_holder(self):
        holder = difference()(
            translate([-holder_w/2.0, 0, 0])(
                cube([holder_w, holder_h, holder_thickness])
            ), 
            translate([-self.camera.w/2.0, -INFINITE/2.0, -INFINITE/2.0])(
                cube([self.camera.w, INFINITE, INFINITE])
            )
        )
        return holder 

    def _vtx_holder(self):


        camera_support_thickness = 5.0
        camera_pcb_depth = self.camera.depth - self.camera.lens_h
        b = math.tan(math.radians(self.angle)) * camera_pcb_depth

        holder_thickness  =  5
        #math.sin(math.radians(90-self.angle)) * (camera_support_thickness - b)
    
        padding = 1.5
        holder_w = self.camera.w + padding * 2
        holder_h = self.camera.h/2.0 + padding
        brace = difference()(
            translate([-holder_w/2.0, 0, 0])(
                cube([holder_w, holder_h, holder_thickness])
            ), 
            translate([-self.camera.w/2.0, -INFINITE/2.0, -INFINITE/2.0])(
                cube([self.camera.w, INFINITE, INFINITE])
            )
        )

        a  = math.cos(math.radians(90-self.angle)) * (camera_support_thickness - b)
        y = camera_pcb_depth/ math.cos(math.radians(self.angle))

        #back_angle_cut = #
        #back_angle_cut  =  translate([0, INFINITE/2.0 + holder_h, -INFINITE/2.0 + holder_thickness])(

        front_angle_cut = rotate([-self.angle, 0, 0])(
            translate([0, -INFINITE/2.0, INFINITE/2.0])(
            cube([INFINITE, INFINITE, INFINITE], center=True)
        )
        )

        back_angle_cut  =translate([0, holder_h, holder_thickness])(
            rotate([-self.angle, 0, 0])(
            translate([0, INFINITE/2.0, -INFINITE/2.0 ])(
                cube([INFINITE, INFINITE, INFINITE], center=True)

            )
        )
        )

        brace -= front_angle_cut
        brace -= back_angle_cut

        #compute position to be behind the camera mount

        return translate([0, y + a - padding, 0])(brace)

    def _base(self):
        w = 7
        h = 8

        #This will be the front of the mount
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

#        base += fixed
#        base -= fixed_cut

#        hole_r = 0.75
#        hole = translate([0, fixed_h + hole_r, -INFINITE/2.0])(
#            cylinder(h = INFINITE, r = hole_r) 
#        )
#
#        base -= hole
        return translate([0, -h, 0])( base)


    def asm(self):
        mount = union()(
            self._camera_mount(),
#            self._vtx_holder(),
            #self._base(),
        )

        return mount

    def camera_test(self):
        camera = translate([0, self.camera.h/2.0, -self.camera.depth + self.camera.lens_h + self.camera_lens_barrel_h])(
            rotate([0, 0, 0])(
            color([0, 0, 0, 0.2])(self.camera.make())
        )
        )

        return union()(
            camera,
            self._camera_mount()
        )

    def test(self):
        """ Test assembly with camera and other components """
#        camera = translate([0, 11, 8,])(
#            rotate([90-self.angle, 0, 0])(
#            color([0, 0, 0, 0.2])(self.camera.make())
#        )
#        )

        fc = BeeBrain()
        return union()(
            translate([0, -12, 0])(self.asm()),
            translate([0, -12, 0])(camera),
            #color([0, 0, 0, 0.2])(translate([0, 0, -self.fc.pcb_thickness -1])(rotate([0, 0, -45])(fc.make()))),
        )

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

    mount = FixedCameraMount(camera, fc, 20)
    #all = mount.camera_mount()

    #all = mount.camera_test()
    #all = mount.test()
    #all = mount._vtx_holder()
    #all = mount._camera_mount()
    #all = mount._protector()
    all = mount.asm()

    scad_render_to_file(all,  filepath= "camera-mount-fixed_{}-v{}.scad".format(mount.angle,VERSION), file_header='$fn = %s;' % SEGMENTS)
