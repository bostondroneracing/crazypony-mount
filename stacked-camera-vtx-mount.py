from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *
from droneparts.frame import *

from cameramount import CameraMount

class StackedCameraMount(CameraMount):

    BASE_THICKNESS = 1.5


    def __init__(self, camera, vtx, fc, angle):
        """ The camera to make the mount for """
        super(StackedCameraMount, self).__init__("stacked-camera-mount", camera, vtx, fc)
        self.angle = angle

        #This is the measurement of the top of the lens when titled at an angle
        min_h = (self.camera.depth * math.sin(math.radians(self.angle))) + (self.camera.h * math.cos(math.radians(self.angle)))
        
        self.vtx_holder_sidewall = 2

        self.h = min_h 
        self.l = self.vtx.h
        self.w = self.vtx.w + (self.vtx_holder_sidewall * 2.0)

        self.inside_w = max(camera.w, vtx.w)

        self.base_thickness = 1.5


        #The padding below and above the camera mount
        mount_height_padding = 2.0

        #This is the measurement of the highest point of the camera
        #when set at the target angle
        self.camera_mount_h = (self.camera.lens_r*2.0) + (mount_height_padding * 2.0)
        self.camera_mount_thickness = min(1.5, self.camera.barrel_h)
        self.camera_mount_face_h = math.cos(math.radians(self.angle)) * self.camera_mount_h
        self.camera_mount_top_w =  self.camera_mount_thickness/math.sin(math.radians(90-self.angle))

        protector_padding = 1.0
        #How wide the protectos is along the x
        self.protector_w = (self.camera.lens_h + protector_padding)/math.sin(math.radians(90-self.angle))

        #how high, when upright is the mount on an angle

    def _camera_mount(self):
        h = self.camera_mount_h
        w = self.inside_w + (self.vtx_holder_sidewall * 2.0)
        thickness = self.camera_mount_thickness 

        
        front_hyp = h
        self.front_o = math.sin(math.radians(self.angle)) * front_hyp 
        front_o = self.front_o
        front_a = self.camera_mount_face_h  
        top_o = thickness

        top_hyp = self.camera_mount_top_w 
        camera_face_plate = linear_extrude(height=w)(
            polygon([[0, 0], [front_o, front_a], [front_o + top_hyp, front_a], [top_hyp,0]]) 
        )
        camera_face_plate = translate([-w/2.0, 0, 0])(
            rotate([self.angle, 0, 0])(
            rotate([0, 90, 0])(
                camera_face_plate
        )))
 
#        camera_face_plate = translate([0, 0, 0])(
#                cube([w , h, thickness], center=True)
#        ) 

        #Create cut
        camera_cut = hull()(
                    translate([0, CameraMount.INFINITE, 0])(
                        cube([self.camera.barrel_r *2.0, 1, CameraMount.INFINITE], center=True)
                    ),
                    translate([0, 0, -CameraMount.INFINITE/2.0])(
                        cylinder(h=CameraMount.INFINITE, 
                                 r=self.camera.barrel_r),
                    )

        )

        camera_cut_y = h/2.0

        camera_face_plate -= translate([0, camera_cut_y, 0])(camera_cut)

        # Add supports here so they are positioned correctly
        #
        support_overhang = 1.5
        support_y = -support_overhang + camera_cut_y - self.camera.h/2.0
        support_x = self.camera.w/2.0 - support_overhang
        support_z = -self.camera.barrel_h - thickness - (self.camera.barrel_h/2.0)
        support = linear_extrude(height=self.camera.barrel_h)(
            polygon([[0,0],[0, support_overhang], [support_overhang, support_overhang]])
        )
        right_support = translate([self.inside_w/2.0, support_y, support_z])(
            mirror([1, 0, 0])(
            support
        ))

        left_support = mirror([1, 0, 0])(right_support)
        return camera_face_plate + right_support + left_support
        #return translate([0, 0, thickness/2.0])(camera_face_plate)


    def _add_mounting_holes(self, part):
        part = rotate([0, 0, 45])(
            part
        )
        part = inductrix_hole_punch(part, r=1.5/2.0 )

        part = rotate([0, 0, -45])(
            part
        )
        return part

    def _base(self):

        minkowski_thickness = self.base_thickness/2.0
        base = translate([0, 0, minkowski_thickness/2.0])(
            rotate([0, 0, 45])(
            cube([INDUCTRIX_HOLE_TO_HOLE_D,INDUCTRIX_HOLE_TO_HOLE_D, minkowski_thickness], center=True)
        ))

        cut = translate([0, CameraMount.INFINITE/2.0 +  self.l/2.0 - SCREW_HEAD_R, 0])(
            cube([CameraMount.INFINITE, CameraMount.INFINITE, CameraMount.INFINITE], center = True)
        )
        base -= cut

        rounding_r = cylinder(h = minkowski_thickness, r=SCREW_HEAD_R )

        base = minkowski()(
            base,
            rounding_r
        )

        base = self._add_mounting_holes(base)


        #Add a slit for velcro
        strap_thickenss = 2
        strap_w = 10
        base -= translate([0, -self.l/2.0  - strap_thickenss/2.0 , 0])(
        cube([strap_w, strap_thickenss, CameraMount.INFINITE], center=True)
        )

        return base

    def _camera_mount_scaffold(self):
        h = self.h - self.camera_mount_face_h # + self.vtx.thickness + self.base_thickness
        scaffold = translate([-self.inside_w/2.0, 0, 0])(
            cube([self.inside_w, h, self.camera_mount_thickness])
        )
        left_scaffold = translate([-self.inside_w/2.0, 0, 0])(
            linear_extrude(height=self.camera_mount_top_w)(
            polygon([ [0, 0], [0, h], [self.inside_w/2.0, h]])#, [self.inside_w, 0], [self.inside_w/2.0, h], [0, 0]])
        ))


        right_scaffold = mirror([1, 0, 0])(left_scaffold)

        scaffold = union()(
            left_scaffold,
            right_scaffold,
        )
        return scaffold

    def _vtx_holder(self):


        # Whatever the vtx thickness is will be the space available inside
        bottom_thickness = self.base_thickness 
        holder = difference()(
            translate([-(self.inside_w + (self.vtx_holder_sidewall * 2))/2.0, 0, 0])(
                cube([self.inside_w + (self.vtx_holder_sidewall * 2), 
                      self.vtx.h, 
                      self.vtx.thickness + bottom_thickness]),
            ),
            translate([-self.inside_w/2.0, -CameraMount.INFINITE/2.0, bottom_thickness])(
                cube([self.inside_w, CameraMount.INFINITE, CameraMount.INFINITE])
            )
        )
        return holder

    def _protector(self):

        #This is the hypotnus length of the edge providing the camera protection
        protector_length = self.h/math.sin(math.radians(90-self.angle))

        #For the given angle this is how wide the leading edge is
        #along the x
        o = math.sin(math.radians(self.angle)) * protector_length

        self.protector_top_right = o + self.protector_w + self.camera_mount_top_w
        return linear_extrude(height=2)(
            polygon([[0, 0], 
                     [o, self.h], 
                     [self.protector_top_right, self.h], 
                     [self.vtx.h, 0]])
        )


    def asm(self):

        right_protector = translate([self.inside_w/2.0, 0, 0])(
            rotate([90, 0, 90])(
                self._protector(),
            )),
        left_protector = mirror([1, 0, 0])(right_protector),
        self._camera_mount()

        protector_camera_mount_asm = union()(
            right_protector,
            left_protector,
            translate([0, self.protector_top_right - self.camera_mount_top_w - self.front_o ,0])( 
            translate([0,0 ,self.h - self.camera_mount_face_h])( #+ self.camera_mount_top_w, 
            rotate([90 - self.angle, 0, 0])(
                self._camera_mount(),
            )
        ),
        ))

        mount_asm = union()(

            self._vtx_holder(),

            translate([0, self.protector_w + self.camera_mount_thickness + self.camera_mount_top_w, self.vtx.thickness + self.base_thickness])(
            rotate([90, 0, 0])(
                self._camera_mount_scaffold(),
            )),

            translate([0, 0, self.vtx.thickness + self.base_thickness])(
                protector_camera_mount_asm
            ),
        )

        full_asm = union()(
            translate([0, -self.l/2.0, 0])(
                mount_asm,
            ),
            self._base(),
        )

        return full_asm 

    def test(self):
        """ Test with components """
        return union()(
            translate([0, 0, -self.fc.pcb_thickness-0.5])(
            rotate([0, 0, 45])(
                self.fc.make()
            )),
            translate([0, -self.l/2.0, 0])(
                mount.asm()
            )
        )


class VTX(object):
    def __init__(self, w, h, thickness):
        self.w = w
        self.h = h
        self.thickness = thickness

class Camera(object):
    def __init__(self, w, h, depth, lens_r, lens_h, barrel_r, barrel_h):
        self.w = w
        self.h = h
        self.depth = depth
        self.lens_r = lens_r
        self.lens_h = lens_h
        self.barrel_r = barrel_r
        self.barrel_h = barrel_h



if __name__ == "__main__":

    fc = BeeBrain()
    vtx = VTX(14, 19, 5)# 2.7)
    fx806 = Camera(14.2, 14.04, 12, 10.0/2.0, 2.75, 7.96/2.0, 4.5)
    mount = StackedCameraMount(fx806, vtx, fc, 20)
    all = mount.asm()
    #all = mount._camera_mount()
    #all = mount._protector()
    #all = mount._base()
    #all = mount.test()
    mount.build()

    #scad_render_to_file(all,  filepath= "build/stacked-camera-mount-fixed_{}-v{}.scad".format(mount.angle,VERSION), file_header='$fn = %s;' % SEGMENTS)
