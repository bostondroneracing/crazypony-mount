from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *
from droneparts.frame import *

from cameramount import CameraMount

"""

Mods 

Have a tolerance of around the printers layer height. 
try ~0.1

* Increase all widths to include tollerance
* Increase mount height by 1mm
* Decrease rear bumper in half
* Remove additoinal side frames, only have bumpers
* as of right now, doesnt seem like you can get the rubber band even under it
* Remove plastic from bottom and side walls


"""

class StackedCameraMount(CameraMount):


    BASE_THICKNESS = 0.75
    WALL_THICKNESS = 1
    TOLERANCE = 0.1


    def __init__(self, camera, vtx, fc, angle):
        """ The camera to make the mount for """
        CameraMount.VERSION = 3
        CameraMount.SEGMENTS = 12
        super(StackedCameraMount, self).__init__("stacked-camera-mount", camera, vtx, fc)
        self.angle = angle

        use("libs/hex_grid.scad")

        self.l = self.vtx.h

        self.inside_w = max(camera.w, vtx.w)
        self.max_component_w = self.inside_w


        #The padding below and above the camera mount
        mount_height_padding = 2.0


        self.camera_body_depth = 7.5
        self.camera_body_depth_inside = 6.57

        #The padding on the PCB that is flat and we can mount against
        self.inside_offset = 0.7
        self.camera_body_case_depth = self.camera_body_depth + self.WALL_THICKNESS


        self.camera_case_depth = (self.camera_body_depth + self.WALL_THICKNESS)
        self.camera_support_w = math.cos(math.radians(self.angle)) * self.camera_case_depth
        self.camera_case_w = self.max_component_w + (self.WALL_THICKNESS * 2.0)

        self.vtx_frame_thickness = 1.0
        self.vtx_bottom_pcb_h = 14.9 
        self.vtx_bottom_pcb_h = self.vtx_bottom_pcb_h + (self.WALL_THICKNESS * 2.0)
        vtx_frame_wall_h = 1.0
        self.vtx_frame_h = self.vtx_bottom_pcb_h + (vtx_frame_wall_h * 2.0)


    def _right_triangle(self, w, h, thickness):
        """ 90 degrees along x, y """
        
        return linear_extrude(height = thickness)(
            polygon([ [0,0], [0, h], [w, 0] ])
        )
    def _stamp(self, w, h, padding =1 ):
        cut = rotate([0, 0, -45])(
            difference()(
                rotate([0, 0, 45])(
                    cube([w, h, CameraMount.INFINITE], center=True)
                ),
                cube([padding, CameraMount.INFINITE, CameraMount.INFINITE], center=True)
            )
        )

        return cut




    def _camera_mount(self):

        lens_padding = 1
        lens_protector = translate([0, 0, (self.camera.lens_h + lens_padding)/2.0])(
            difference()(
                cylinder(r = self.camera.lens_r + lens_padding, h=self.camera.lens_h + lens_padding, center=True),
                cylinder(r = self.camera.lens_r, h=CameraMount.INFINITE, center=True)
                )
        )

        inset = self.camera_body_depth - self.camera_body_depth_inside
        camera_case_h = self.camera.h + (self.WALL_THICKNESS * 2.0)
        camera_case_body_depth  = self.camera_body_depth + self.WALL_THICKNESS

        camera_body = difference()(
            translate([0, 0, -(self.camera_body_depth + self.WALL_THICKNESS)/2.0 + self.WALL_THICKNESS])(
                cube([self.camera_case_w, 
                      camera_case_h, 
                      camera_case_body_depth], center=True),
            ),

            translate([0, 0, -CameraMount.INFINITE/2.0])(# - self.camera_body_depth_inside ])(
                cube([self.camera.w, 
                      self.camera.h, 
                      CameraMount.INFINITE], center=True),
            ),
            cylinder(r = self.camera.lens_r, h=CameraMount.INFINITE, center=True)

        )

        padding = 1 

        w = self.camera.w/2.0 - padding - padding/2.0
        h = (self.camera_body_depth - self.WALL_THICKNESS - inset) - (padding * 2.0)
        cut = translate([0, 0, -h/2.0])(rotate([90, 0, 0])(
            self._stamp(w, h)
        ))

        left_cut = translate([-w/2.0 - padding/2.0, 0, -padding])(
            cut
        )
        right_cut = mirror([1, 0, 0])(left_cut)
        top_cuts =union()(
            left_cut,
            right_cut,
        )

        side_cuts = rotate([0, 0, 90])(top_cuts)


        camera_body = difference()(
            camera_body,
            top_cuts,
            side_cuts,

        )

        #Cut out the bottom
        bottom_cut = translate([0, -CameraMount.INFINITE/2.0 - self.camera.h/2.0 + self.inside_offset, -CameraMount.INFINITE/2.0])(

        cube([self.camera.w, CameraMount.INFINITE, CameraMount.INFINITE], center=True)
        )
        #return camera_body
        # This is what the camera mounts against
        rim =  difference()(
                cube([self.camera.w, 
                      self.camera.h, 
                      self.WALL_THICKNESS], center=True),
                cube([self.camera.w - (self.inside_offset * 2.0), 
                      self.camera.h - (self.inside_offset * 2.0), 
                      CameraMount.INFINITE], center=True),

        )

        rim_z = -self.WALL_THICKNESS/2.0 - self.camera_body_depth + (self.WALL_THICKNESS ) + inset 
        # times 2, one to even out, scond to set back as inset
        camera_body += translate([0, 0, rim_z])(rim)

        camera_body -= bottom_cut
        #Angled walls
        wall_w = CameraMount.INFINITE#self.camera_body_case_depth
        wall_h =  self.camera_body_case_depth
        wall_thickness = 1 
        wall_right = translate([self.max_component_w/2.0, -wall_w, 0])(
            cube([wall_thickness, wall_w, wall_h])
        )

        wall_left = mirror([1, 0, 0])(wall_right)

        camera_case = translate([0, (self.camera.h + (self.WALL_THICKNESS * 2.0))/2.0, self.camera_body_depth])( 
            union()(
                lens_protector,
                camera_body,
        ))

        camera_case_z = 3#5
        camera_case_asm = translate([0, 0, camera_case_z])(
            rotate([90-self.angle, 0, 0])(
                union()(
                    camera_case,
                    wall_right,
                    wall_left,
            )
        )
        )

        return difference()(
            translate([0, self.camera_support_w/2.0, 0])( camera_case_asm),
                            translate([0, 0, -CameraMount.INFINITE/2.0])(
                                cube([CameraMount.INFINITE, CameraMount.INFINITE, CameraMount.INFINITE], center=True)
                            )
        )

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

        minkowski_thickness = self.BASE_THICKNESS/2.0

        base = translate([0, 0, minkowski_thickness/2.0])(
            cube([INDUCTRIX_HOLE_TO_HOLE_D,INDUCTRIX_HOLE_TO_HOLE_D, minkowski_thickness], center=True)
        )
#)

        # Cut away  the sides to set the mount inward to make room 
        # for the ducted fans
        w = 17 + (SCREW_HEAD_R*2.0)
        for i in range(4):
            base = difference()(
                rotate([0, 0, 90])(
                    base
                ),
                translate([-w/2.0, INDUCTRIX_HOLE_TO_HOLE_D/2.0 - 1 , -CameraMount.INFINITE/2.0])(
                    cube([w, CameraMount.INFINITE, CameraMount.INFINITE])
                )
            )
        base = rotate([0, 0, 45])(base)


        # Keep only the center
        base = intersection()(
            base,
            cube([self.camera_case_w - (SCREW_HEAD_R*2.0), CameraMount.INFINITE, CameraMount.INFINITE], center=True)
        )


        # Round out all the corners
        rounding_r = cylinder(h = minkowski_thickness, r=SCREW_HEAD_R )
        base = minkowski()(
            base,
            rounding_r
        )


        # Add the holes


        rear_rubberband_holder = translate([0, self.vtx.h/2.0, 0])( 
            self._rubberband_holder()
        )
        front_rubberband_holder = mirror([0, 1, 0])(rear_rubberband_holder)

        base = difference()(
            base, 
            #rear_rubberband_holder,
            #front_rubberband_holder
        )

        hole_w = cube([CameraMount.INFINITE, INDUCTRIX_HOLE_TO_HOLE_W - (SCREW_HEAD_R*2.0), CameraMount.INFINITE], center=True)

        base_center = intersection()(
            base,
            hole_w
        )
        base_inside = self._shrink(base_center, 2)
        return self._hexagon_grill(base_inside)
        base_center = self._shell(base_center, 2)

        base_center_removed = difference()(
            base,
            hole_w,
        )

        outline = union()(
            base_center_removed,
            base_center,
        )
        #base = self._shell(base, 2)
        base = self._add_mounting_holes(outline)

        return base

    def _hexagon_grill(self, part):
        grid = linear_extrude(height=4)(
          lattice(10, 10, 3, 1)
            #shell(5,1)
        )

        inverse_grid = difference()(
            cube([CameraMount.INFINITE, CameraMount.INFINITE, 1], center=True),
            grid,
        )
        return inverse_grid 


    def _shrink(self, part, thickness):
        """ Shirk by thickness """
        #just needs to be smaller than the part thickness
        inverse_thickness = 0.001
        inverse = difference()(
            translate([0, 0, inverse_thickness/2.0])(
                cube([CameraMount.INFINITE, CameraMount.INFINITE, inverse_thickness ], center=True)
            ),
            part, 
        )

        expanded = minkowski()(
            inverse,
            cylinder(h = CameraMount.INFINITE, r=thickness)
        )

        part_smaller = difference()(
            translate([0, 0, CameraMount.INFINITE/2.0])(
            cube([CameraMount.INFINITE * 2.0, CameraMount.INFINITE * 2.0, CameraMount.INFINITE  ], center=True),
            ),
            expanded,
        )


        return intersection()(
            part,
            part_smaller,
        )
        return  part_smaller


    def _shell(self, part, thickness):
        shrunk_part = self._shrink(part, thickness)

        shelled_part = difference()(
            part, 
            shrunk_part,
        )

        return shelled_part

    def _rubberband_holder(self):
        w = 4
        h = 4
        band_holder_l = 3 
        band_thickness =1 
        left = linear_extrude(height=CameraMount.INFINITE)(
        polygon([ [0, band_thickness/2.0], [0, w/2.0], [0, h], [h-band_holder_l, 0], [h-band_holder_l, band_thickness/2.0] ])
        )

        a = self._right_triangle(w, h, 1)

        a = difference()(
        cylinder(h = CameraMount.INFINITE/4.0, r = w/2.0),
            translate([0, -band_holder_l/2.0, 0])(
            cube([band_thickness, band_holder_l, CameraMount.INFINITE], center=True)
            )
        )

        return union()(
            translate([0, w/2.0, 0])(
            a
            )

        )


    def _vtx_frame(self):

        frame = difference()(
                translate([0, 0, self.vtx_frame_thickness/2.0])(
                    cube([self.camera_case_w, 
                          self.vtx_frame_h, 
                          self.vtx_frame_thickness], center=True),
                ),
                cube([CameraMount.INFINITE, 
                      self.vtx_bottom_pcb_h, 
                      CameraMount.INFINITE], center=True),
            )


        return  frame




    def asm(self):
        return union()(
            translate([0,-4.5, self.BASE_THICKNESS])(
            self._camera_mount(),
            ),
            translate([0, 0, self.BASE_THICKNESS])(
                self._vtx_frame(),
            ),
            self._base(),
        )

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
    fx806 = Camera(14.05, 14.15, 12, 10.0/2.0, 2.75, 7.96/2.0, 4.5)
    mount = StackedCameraMount(fx806, vtx, fc, 20)
    #mount.build(part=mount._camera_mount())
    #mount.build(part=mount._vtx_frame3())
    mount.build(part=mount._base())
    #mount.build(part=mount._rubberband_holder())
    #mount.build()

    #scad_render_to_file(all,  filepath= "build/stacked-camera-mount-fixed_{}-v{}.scad".format(mount.angle,VERSION), file_header='$fn = %s;' % SEGMENTS)
