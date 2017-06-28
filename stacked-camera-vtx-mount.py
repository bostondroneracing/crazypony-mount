from solid import *
from solid.utils import *

from droneparts.camera import *
from droneparts.hardware import *
from droneparts.fc import *
from droneparts.frame import *

from cameramount import CameraMount

class StackedCameraMount(CameraMount):


    BASE_THICKNESS = 0.75


    def __init__(self, camera, vtx, fc, angle):
        """ The camera to make the mount for """
        CameraMount.VERSION = 2
        CameraMount.SEGMENTS = 48
        super(StackedCameraMount, self).__init__("stacked-camera-mount", camera, vtx, fc)
        self.angle = angle

        #This is the measurement of the top of the lens when titled at an angle
        min_h = (self.camera.depth * math.sin(math.radians(self.angle))) + (self.camera.h * math.cos(math.radians(self.angle)))
        
        self.vtx_holder_sidewall = 2

        self.h = min_h 
        self.l = self.vtx.h
        self.w = self.vtx.w + (self.vtx_holder_sidewall * 2.0)


        self.inside_w = max(camera.w, vtx.w)
        self.max_component_w = self.inside_w


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

        self.front_o = math.sin(math.radians(self.angle)) * self.camera_mount_h 


        self.body_padding = 1
        self.camera_body_depth = 7.5
        self.camera_body_depth_inside = 6.57
        self.inside_offset = 0.7
        self.camera_body_case_depth = self.camera_body_depth + self.body_padding


        self.frame_padding = 1
        self.frame_outside_w = self.max_component_w + (self.frame_padding * 2.0)

        self.camera_case_depth = (self.camera_body_depth + self.body_padding)
        self.camera_support_w = math.cos(math.radians(self.angle)) * self.camera_case_depth
        self.camera_case_w = self.max_component_w + (self.body_padding * 2.0)

        self.vtx_frame_inside_h = 14.9 
        self.vtx_frame_h = self.vtx_frame_inside_h + (self.frame_padding * 2.0)

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
        camera_case_h = self.camera.h + (self.body_padding * 2.0)
        camera_case_body_depth  = self.camera_body_depth + self.body_padding

        camera_body = difference()(
            translate([0, 0, -(self.camera_body_depth + self.body_padding)/2.0 + self.body_padding])(
                cube([self.camera_case_w, 
                      camera_case_h, 
                      camera_case_body_depth], center=True),
            ),

            #Inset
#            translate([0, 0, -CameraMount.INFINITE/2.0 - self.body_padding])(
#                cube([self.camera.w - (self.inside_offset * 2.0), 
#                      self.camera.h - (self.inside_offset * 2.0), 
#                      CameraMount.INFINITE], center=True),
#            ),

            translate([0, 0, -CameraMount.INFINITE/2.0])(# - self.camera_body_depth_inside ])(
                cube([self.camera.w, 
                      self.camera.h, 
                      CameraMount.INFINITE], center=True),
            ),
            cylinder(r = self.camera.lens_r, h=CameraMount.INFINITE, center=True)

        )

        padding = 1 
        num = 2
        #tri_w = (self.camera.w -  (padding  * 3.0)) / num
        #tri_h = self.camera_body_depth - (self.body_padding * 2.0) - padding

        w = self.camera.w/2.0 - padding - padding/2.0
        #h = self.camera_body_depth - (padding * 2.0)
        h = (self.camera_body_depth - self.body_padding - inset) - (padding * 2.0)
        cut = translate([0, 0, -h/2.0])(rotate([90, 0, 0])(
            self._stamp(w, h)
        ))

        left_cut = translate([-w/2.0 - padding/2.0, 0, -padding])(
            cut
        )
#        right_cut = translate([w/2.0 + padding/2.0, 0, -padding])(
#            rotate([0, 180, 0])(cut)
#        )
        right_cut = mirror([1, 0, 0])(left_cut)

        

        #t1 = rotate([90, 0,0])(self._triangle(tri_w, tri_h, CameraMount.INFINITE))

        #camera_body -= translate([0, CameraMount.INFINITE/2.0, -tri_h - padding ])(t1)
        top_cuts =union()(
            #camera_body,
            left_cut,
            right_cut,
        )

        side_cuts = rotate([0, 0, 90])(top_cuts)

        #camera_body += top_cuts
        #camera_body += side_cuts

        camera_body = difference()(
            camera_body,
            top_cuts,
            side_cuts,

        )

        #return camera_body

        rim =  difference()(
                cube([self.camera.w, 
                      self.camera.h, 
                      self.body_padding], center=True),
                cube([self.camera.w - (self.inside_offset * 2.0), 
                      self.camera.h - (self.inside_offset * 2.0), 
                      CameraMount.INFINITE], center=True),

        )

        # times 2, one to even out, scond to set back as inset
        camera_body += translate([0, 0, -self.body_padding/2.0 - self.camera_body_depth + (self.body_padding ) + inset ])(rim)

        angle_h = math.sin(math.radians(self.angle)) * self.camera_case_depth

        wall_w = self.camera_support_w 
        wall_h =  5
        wall_thickness = 1 
        wall_offset = 0
        wall_right = translate([self.vtx.w/2.0 + wall_offset, -wall_w, 0])(
            cube([wall_thickness, wall_w, wall_h])
        )

        #Angled walls
        wall_w = CameraMount.INFINITE#self.camera_body_case_depth
        wall_h =  self.camera_body_case_depth
        wall_thickness = 1 
        wall_right = translate([self.max_component_w/2.0 + wall_offset, -wall_w, 0])(
            cube([wall_thickness, wall_w, wall_h])
        )




        wall_left = mirror([1, 0, 0])(wall_right)

        camera_case = translate([0, (self.camera.h + (self.body_padding * 2.0))/2.0, self.camera_body_depth])( union()(
            lens_protector,
            camera_body,
        ))

#        brace = rotate([linear_extrude(height=1)(
#        polygon([ [0, 0], [0, 1], [camera_case_h, 0]])
#        )


        

        right_angle = translate([self.camera_case_w/2.0 - 1, -self.camera_support_w, 0])(rotate([0, 0, 90])(rotate([90, 0, 0])(linear_extrude(height=1)(
        polygon([ [0, 0], [0, angle_h], [self.camera_support_w, 0]])
        )
        )))
        left_angle = mirror([1, 0, 0])(right_angle)

        camera_case_asm = rotate([90-self.angle, 0, 0])(
           # translate([0, + wall_h, -(wall_thickness)])(
            union()(
            camera_case,
            wall_right,
            wall_left,
                #brace,
        )
        #)
        )

        camera_case_z = 5

        #wall_h = 0
        camera_case_asm = union()(
            translate([0, 0, camera_case_z])(
                union()(
                    camera_case_asm,
#                    right_angle,
#                    left_angle,
                ),
            ),
#            wall_left,
#            wall_right,
        )


        body_w = self.camera_body_case_depth/math.sin(math.radians(90-self.angle))

        return difference()(
            translate([0, self.camera_support_w/2.0, 0])( camera_case_asm),
                            translate([0, 0, -CameraMount.INFINITE/2.0])(
                                cube([CameraMount.INFINITE, CameraMount.INFINITE, CameraMount.INFINITE], center=True)
                            )
        )


#        return translate([0, -body_w/2.0, 0])(
#                          difference()(
#                            camera_case_asm,
                            #Cut the overhang
#                            translate([0, 0, -CameraMount.INFINITE/2.0])(
#                                cube([CameraMount.INFINITE, CameraMount.INFINITE, CameraMount.INFINITE], center=True)
#                            )
#        ))



    def _camera_mount2(self):
        h = self.camera_mount_h
        w = self.inside_w + (self.vtx_holder_sidewall * 2.0)
        thickness = self.camera_mount_thickness 

        
        front_hyp = h
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

        minkowski_thickness = self.BASE_THICKNESS/2.0
        base = translate([0, 0, minkowski_thickness/2.0])(
            #rotate([0, 0, 45])(
            cube([INDUCTRIX_HOLE_TO_HOLE_D,INDUCTRIX_HOLE_TO_HOLE_D, minkowski_thickness], center=True)
        )
#)

        cut = translate([0, CameraMount.INFINITE/2.0 +  self.l/2.0 - SCREW_HEAD_R, 0])(
            cube([CameraMount.INFINITE, CameraMount.INFINITE, CameraMount.INFINITE], center = True)
        )
#        base -= cut

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


        base = intersection()(
            base,
            cube([self.camera_case_w - (SCREW_HEAD_R*2.0), CameraMount.INFINITE, CameraMount.INFINITE], center=True)
        )

        rounding_r = cylinder(h = minkowski_thickness, r=SCREW_HEAD_R )

        base = minkowski()(
            base,
            rounding_r
        )

        base = self._add_mounting_holes(base)

        cut_vtx = cube([self.frame_outside_w, self.vtx.h, CameraMount.INFINITE], center=True)
#        base -= cut_vtx

        rear = translate([0, self.vtx.h/2.0, 0])( self._rubberband_holder())
        front = mirror([0, 1, 0])(rear)

        base = difference()(
            base, 
            rear,
            front
        )
        return base


    def _vtx_cover(self):
        cover_h = 8
        cover_w = self.camera_body_case_depth/math.sin(math.radians(90-self.angle))
        cover_thickness = 1

        x = math.tan(math.radians(self.angle)) * cover_thickness

        cover = linear_extrude(height= self.vtx.w)(
            polygon([ [0, 0], [x, cover_thickness], [x + cover_w, cover_thickness], [cover_w, 0]])
        )
        return translate([-self.vtx.w/2.0, x + cover_w, cover_thickness])(
            rotate([0, 0, -90])(rotate([-90, 0, 0])(
            cover
        )))

    def _vtx_rear_clip(self):
        thickness = 1
        rear_bumper_w = 2#5
    def _vtx_front_clip(self):
        frame_front_thickness = 1
        front_bumper_w = 2#5
        pcb_overhang = 1.5
        front_bumper_h = pcb_overhang + frame_front_thickness
        bottom_thickness = 1.8
        front_bumper = cube([front_bumper_w, front_bumper_h, bottom_thickness])

        clip_w = 2
        clip_h = 1.5
        top = cube([clip_w, clip_h, frame_front_thickness])
        
        pcb_thickness = 0.9
        pcb_spacer = cube([clip_w, frame_front_thickness, pcb_thickness + frame_front_thickness])

        clip_asm = union()(
                front_bumper,
                translate([0, front_bumper_h - frame_front_thickness - clip_h, bottom_thickness + pcb_thickness])(
                    top,
                ),
                translate([0, front_bumper_h - frame_front_thickness, bottom_thickness])(
                    pcb_spacer,
                ),
            )
        return clip_asm



    def _vtx_frame4(self):
        return translate([2, -self.vtx.h/2.0 + 1, 0])(
            rotate([0, 0, 180])(self._vtx_front_clip()))

    def _vtx_frame(self):
        frame_h = 14.9 
        frame_front_thickness = 1.0
        bumper_thickness = 0.5
        bumper_z = 2.7

        front_bumper = translate([-self.vtx.w/2.0, -frame_front_thickness - (frame_h/2.0), 0])(
        cube([self.vtx.w, frame_front_thickness, frame_front_thickness])
        )

        right_side_bumper = translate([self.max_component_w/2.0 - bumper_thickness, -self.camera_support_w/2.0, bumper_z ])(
            cube([bumper_thickness, self.camera_support_w, frame_front_thickness])
        )

        front_clip = translate([])(
            cube([2, 2, 1])

        )
        front_bumper_w = 2#5
        pcb_overhang = 1.5
        front_bumper_h = pcb_overhang + frame_front_thickness
        bottom_thickness = 1.8
        front_bumper = cube([front_bumper_w, front_bumper_h, bottom_thickness])
        clip_w = 2
        clip_h = 1.5
        clip = cube([clip_w, clip_h, frame_front_thickness])
        
        pcb_thickness = 0.9
        pcb_spacer = cube([clip_w, frame_front_thickness, pcb_thickness + frame_front_thickness])

        return translate([self.vtx.w/2.0 - 7, -frame_front_thickness-self.vtx.h/2.0, 0])(
            union()(
            front_bumper,
            translate([0, frame_front_thickness, bottom_thickness + pcb_thickness])(
            clip,
            ),
            translate([0, 0, bottom_thickness])(
                pcb_spacer,
            ),
           # front_bumper,
           # right_side_bumper,
        ))

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
    def _vtx_frame3(self):

        frame_w = self.max_component_w #self.vtx.w 
        frame_h = 14.9 
        frame_side_thickness = 2.0
        frame_front_thickness = 1.0

        self.vtx_frame_h = frame_h + (self.frame_padding * 2.0)

        frame = translate([0, 0, 0])(
            difference()(

                union()(
                    translate([0, 0, frame_front_thickness/2.0])(
                        cube([self.frame_outside_w, 
                              self.vtx_frame_h, 
                              frame_front_thickness], center=True),
                            ),
                    translate([0, 0, frame_side_thickness/2.0])(
                        cube([self.frame_outside_w, 
                              frame_h, 
                              frame_side_thickness], center=True),
                    )
                ),
            cube([frame_w, frame_h, CameraMount.INFINITE], center=True),
#                translate([0, CameraMount.INFINITE/2.0, 0])(
#                cube([CameraMount.INFINITE, CameraMount.INFINITE, CameraMount.INFINITE], center=True)
#                )
            )
        )

#        bracket = difference()(
#            translate([0, 0, self.frame_padding/2.0])(
#                        cube([self.frame_outside_w, 
#                              self.vtx_frame_h, 
#                              self.frame_padding], center=True),
#                            ),
#                        cube([frame_w - (self.frame_padding * 2.0), 
#                              frame_h - (self.frame_padding * 2.0), 
#                              CameraMount.INFINITE], center=True),
#        )
#
#        frame_mount_w = 2
#        frame_mount_h = 2
#        frame_mount_thickness = frame_side_thickness
#        frame_mount = translate([0, 0, frame_mount_thickness/2.0])(
#            cube([frame_mount_w, frame_mount_h, frame_mount_thickness], center=True)
#        )
#        right_mount = translate([frame_mount_w/2.0 + frame_w/2.0, 0, 0])(frame_mount)
#        left_mount = translate([-frame_mount_w/2.0 - frame_w/2.0, 0, 0])(frame_mount)
#
#        left_holder = translate([-self.frame_outside_w/2.0 + 1, 1, frame_side_thickness + self.frame_padding])(rotate([0, 0, -90])(rotate([90, 0, 0])(linear_extrude(height=1)(
#        polygon([ [0, 0], [1, 1], [2, 0] ])
#        ))))
#
#        right_holder = mirror([1,0, 0])(left_holder)


        return union()(
            translate([0, 0, 0])(
                union()(
                    frame,
#                    right_mount,
#                    left_mount,
                ),
            ),
            #self._vtx_rear_clip(),
                #bracket,
#            left_holder,
#            right_holder,
            )



    def _vtx_frame2(self):
        frame_w = self.vtx.w 
        frame_side_thickness = 2.0
        frame_front_thickness = 1.0


        frame = translate([0, 0, 0])(
            difference()(

                union()(
                    translate([0, 0, frame_front_thickness/2.0])(
                        cube([self.frame_outside_w, 
                              self.vtx_frame_h, 
                              frame_front_thickness], center=True),
                            ),
                    translate([0, 0, frame_side_thickness/2.0])(
                        cube([self.frame_outside_w, 
                              self.vtx_frame_inside_h, 
                              frame_side_thickness], center=True),
                    )
                ),
            cube([frame_w, self.vtx_frame_inside_h, CameraMount.INFINITE], center=True)
        )
        )

        bracket = difference()(
            translate([0, 0, self.frame_padding/2.0])(
                        cube([self.frame_outside_w, 
                              self.vtx_frame_h, 
                              self.frame_padding], center=True),
                            ),
                        cube([frame_w - (self.frame_padding * 2.0), 
                              frame_h - (self.frame_padding * 2.0), 
                              CameraMount.INFINITE], center=True),
        )

        frame_mount_w = 2
        frame_mount_h = 2
        frame_mount_thickness = frame_side_thickness
        frame_mount = translate([0, 0, frame_mount_thickness/2.0])(
            cube([frame_mount_w, frame_mount_h, frame_mount_thickness], center=True)
        )
        right_mount = translate([frame_mount_w/2.0 + frame_w/2.0, 0, 0])(frame_mount)
        left_mount = translate([-frame_mount_w/2.0 - frame_w/2.0, 0, 0])(frame_mount)

        left_holder = translate([-self.frame_outside_w/2.0 + 1, 1, frame_side_thickness + self.frame_padding])(rotate([0, 0, -90])(rotate([90, 0, 0])(linear_extrude(height=1)(
        polygon([ [0, 0], [1, 1], [2, 0] ])
        ))))

        right_holder = mirror([1,0, 0])(left_holder)
        return union()(
            translate([0, 0, self.frame_padding])(
                union()(
                    frame,
#                    right_mount,
#                    left_mount,
                ),
            ),
#                bracket,
            left_holder,
            right_holder,
            )

    def _vtx_holder2(self):


        # Whatever the vtx thickness is will be the space available inside
        front_clip_thickness = 1
        front_clip_w = 1
        front_clip_h = self.vtx_holder_sidewall + 1

        bottom_thickness = self.BASE_THICKNESS 
        holder = difference()(
            translate([-(self.inside_w + (self.vtx_holder_sidewall * 2))/2.0, 0, 0])(
                cube([self.inside_w + (self.vtx_holder_sidewall * 2), 
                      self.vtx.h + self.vtx_holder_sidewall, 
                      self.vtx.thickness + bottom_thickness]),
            ),
            translate([-self.inside_w/2.0, self.vtx_holder_sidewall, -CameraMount.INFINITE/2.0])(
                cube([self.inside_w, CameraMount.INFINITE, CameraMount.INFINITE])
            )
        )

        clip = translate([])(
        cube([front_clip_w, front_clip_h, front_clip_thickness])
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
        return union()(
            translate([0,0, self.BASE_THICKNESS])(
            self._camera_mount(),
            ),
            translate([0, 0, self.BASE_THICKNESS])(
                self._vtx_frame3(),
            ),
            #self._vtx_cover(),
            color([0,0,0,0.5])(self._base()),
        )

    def asm2(self):

        right_protector = translate([self.inside_w/2.0, 0, 0])(
            rotate([90, 0, 90])(
                self._protector(),
            )),
        left_protector = mirror([1, 0, 0])(right_protector),
        self._camera_mount()

        protector_camera_mount_asm = union()(
            rotate([90 - self.angle, 0, 0])(
                self._camera_mount(),
            )
        )

        mount_asm = union()(

            self._vtx_cover,

            translate([0, 0, self.vtx.thickness + self.BASE_THICKNESS])(
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
    fx806 = Camera(14.05, 14.15, 12, 10.0/2.0, 2.75, 7.96/2.0, 4.5)
    mount = StackedCameraMount(fx806, vtx, fc, 20)
    #mount.build(part=mount._camera_mount())
    #mount.build(part=mount._vtx_frame3())
    #mount.build(part=mount._vtx_cover())
    #mount.build(part=mount._base())
    #mount.build(part=mount._rubberband_holder())
    mount.build()

    #scad_render_to_file(all,  filepath= "build/stacked-camera-mount-fixed_{}-v{}.scad".format(mount.angle,VERSION), file_header='$fn = %s;' % SEGMENTS)
