/**
* This camera mount is compatible with the NewBeeDrone cockroach frame
* and the NewBeeDrone BeeBrain v1.
* 
* Cameras known to fit:
*   Crazypony split camera vtx https://www.amazon.com/gp/product/B072L21RPL/
*/

$fn = 90;
VERSION = 4.0;

// Must be defined larger than any other piece
INF = 100;

//Include a tolerance for the printing for parts that can be bigger or larger
TOL = 0.2;

//Angle of the camera
camera_angle = 20;

// HARDWARE measurements
screw_r = 4.23/2.0;
gasket_r = 4.3/2.0;
gasket_h = 1.4;


barrel_r = 7.91/2;
barrel_l = 4.5 - TOL;
//How thick the snap is
snap_thickness = 2;//1.75; 
snap_r = barrel_r + snap_thickness;

//This is the angle in which the camera barrell is applied
snap_opening_angle = 60;
//The distance of the snap parellel to the fc clip
snap_mounting_l = (barrel_l/ cos(camera_angle));

//Height from the center of the snap to the longest leg
support_height = 7;

support_thickness = 2;

// How far apart are the supports
supported_width = 4;

//PCB dimensions based on the NewBeeDrone BeeBrain
pcb_thickness = 0.8;//1.4 + TOL;
pcb_w = 27.08 + TOL;
pcb_h = pcb_w;

//This is the height of the components on the PCB
component_thickness = 1;

fc_thickness = pcb_thickness + component_thickness; 

base_wall_thickness = 1;
base_thickness = pcb_thickness + component_thickness + (2*base_wall_thickness);
base_h = 5;


base_front_w = 7.5;

base_mount_thickness = 1;
fc_clip_thickness = 1.25;
//Width of the clip that goes underneath the FC to hold it in place
fc_clip_w = 3; 

mounting_hole_r = 0.6 + TOL;
mounting_plate_thickness = 1;
mounting_plate_w = pcb_w + (fc_clip_thickness * 2.0);
//The length is the diameter of the screw mount + camera mount
mounting_plate_l = screw_r * 2 + snap_mounting_l; 


/**
* Helper function
*/
module inf_cube(){ cube([INF, INF, INF], center=true);}

////////////////////////////////////////////////////////
// CAMERA CLIP

/**
* Round out the end of the snap
*/
module clip_rounding(){
	cylinder(h=barrel_l, r= snap_thickness/2.0, center=true);
}

/**
* Create a snap with an opening defined by opening_angle
*/
module rounded_snap_mount(opening_angle){
	rotate_to_0 = 90-opening_angle;
	round_x = barrel_r + (snap_thickness/2.0);

	//Now rotate back to center
	rotate(rotate_to_0){
		union(){
			rotate(-2 * rotate_to_0){
				union(){
					rotate(rotate_to_0){
						snap_mount(opening_angle);
					};
					//left
					translate([-round_x, 0, 0]) clip_rounding();		
				}
			}
			//right
			translate([round_x, 0, 0]) clip_rounding();
		}
	}
ext_h = 4;
theta = 90 - snap_opening_angle;// snap_opening_angle;//(180 - snap_opening_angle)/2.0;
echo("A=", theta);
r = barrel_r + snap_thickness/2.0;
x = cos(theta) * r; 
y = sin(theta) * r;
//y = 
x1 = 6;
y1 = y + ext_h;
hull(){
	translate([x, y, 0]) cylinder(h=barrel_l, r=snap_thickness/2.0, center=true);
	translate([x1, y1, 0]) cylinder(h=barrel_l, r=snap_thickness/2.0, center=true);
}

hull(){
	translate([-x, y, 0]) cylinder(h=barrel_l, r=snap_thickness/2.0, center=true);
	translate([-x1, y1, 0]) cylinder(h=barrel_l, r=snap_thickness/2.0, center=true);

}
}

/**
* Take the snap, which is on the xy plane, and rotate it to the correct
* angle. Remove any access material.
*/
module apply_camera_mount_angle(angle) {

	difference(){
		rotate([90 + angle, 0, 0]) translate([0, support_height, barrel_l/2.0]) rounded_snap_mount(snap_opening_angle);
		translate([0, 0, -INF/2]) inf_cube();
	}
}


module mount_legs(){


	// Right leg
	translate([supported_width/2.0, -support_height, -barrel_l/2.0]){
		cube([support_thickness, support_height, barrel_l]);
	};
	//Left leg
	translate([-support_thickness -supported_width/2.0, -support_height, -barrel_l/2.0]){
		cube([support_thickness, support_height, barrel_l]);
	};

}
/**
 * This is a full circle with mounting legs
 */
module clip_solid() {
	difference(){
		//combine the mounting legs and place for barrel lens
		union(){
			mount_legs();	
			cylinder(h=barrel_l, r = snap_r, center=true);
			//translate([0, -support_height/2, 0]) cube([supported_width, support_height, support_thickness], center=true);
		};
		//Remove materal for barrel
		cylinder(h=INF, r = barrel_r, center=true);
	}
}

module snap_mount(angle){
	
	//make a triangle can cut from center
	x = tan(angle) * INF;

	difference(){
		clip_solid();
		//Remove triangle
		linear_extrude(height=INF, center=true){
			polygon([ [0, 0], [-1*x, INF], [x, INF] ]);
		}
	}
}




////////////////////////////////////////////////////
// FC CLIP 


/**
 * Add support for the camera mount to sit on top the FC
 */

module mount_fc_support(){
	sit_w = 1; // the measured width from where the gasket is to when the pcb compeonts start on the board
	difference(){
		mounting_plate(gasket_h);
		translate([0, -INF/2.0 + mounting_plate_l - (gasket_r * 2) - sit_w , 0]) inf_cube();
	}

}

module add_fc_clip(){

	h = gasket_h + pcb_thickness + fc_clip_thickness;
	echo("H=", h);
	
	difference(){
		//Combine the plate, resting support, and clip
		union(){
			mounting_plate_with_screw_hole();
			translate([0, 0, -gasket_h])	mount_fc_support();
			translate([0, 0,  -h]) fc_clip(h);
		}

		translate([0,  mounting_plate_l - gasket_r, -INF/2.0]) {
			 hull(){ 
				cylinder(h=INF, r=gasket_r, center=true);
				translate([0, INF]) cylinder(h=INF, r=gasket_r, center=true);
			}
		}
	}
}
/**
 * The plate mounted to the drone and where the camera sits
 */
module mounting_plate(h){

	//thickness of the clip to the FC
	//h = base_mount_thickness;  
	
	//Need the width and height to include the clip widths that attaches to the FC
	//Subtrack the radius of the rounding on both sides
	minkowski_x = mounting_plate_w - (screw_r*2);
	minkowski_y = mounting_plate_w - (screw_r*2);
	o = sin(45)*minkowski_y + screw_r;

	difference(){
		translate([0, -o + mounting_plate_l, h/2]){	
			rotate([0, 0, 45]){
				minkowski() {
					cube([minkowski_x, minkowski_y, h/2.0 ], center=true); 
					cylinder(h=h/2, r=screw_r, center=true);
				}
			}
		}
	translate([0, -INF/2.0, 0]) inf_cube();
}
}

/**
 * Add the screw hole to plate
 */
module mounting_plate_with_screw_hole(){

	difference(){
		mounting_plate(mounting_plate_thickness);
		translate([0, mounting_plate_l - screw_r, 0]) cylinder(h=INF, r=mounting_hole_r, center=true);
	}

}
/** The clip to attach the camera to the FC
 h: The entire height of the clip
**/
module fc_clip(h){
	

	//Need to do some calculations to get what the actual distance
	//is if the part was not rounded
	minkowski_y = mounting_plate_w - (screw_r*2);
	o1 = sin(45)*minkowski_y + screw_r;
	o = sin(45) * mounting_plate_w;
	d = o - o1;

	difference(){
		translate([0, -o + mounting_plate_l + d, 0]){
			rotate([0, 0, 45]){
				difference(){
					translate([0, 0, h/2.0]) cube([mounting_plate_w, mounting_plate_w, h], center=true); 
					translate([0, 0, INF/2.0 + fc_clip_thickness]) cube([pcb_w, pcb_h, INF], center=true); 
					cube([pcb_w - fc_clip_w, pcb_h - fc_clip_w, INF], center=true);
				}
			}
		}

		translate([0, -INF/2.0,0]) inf_cube();
	}
}


module fc_single_mount(){

	h = gasket_h + pcb_thickness + fc_clip_thickness;
	echo("H=", h);
	
	intersection(){
	difference(){
		//Combine the plate, resting support, and clip
		union(){
			mounting_plate_with_screw_hole();
			translate([0, 0, -gasket_h])	mount_fc_support();
		}
		//Remove the gasket piece
		translate([0,  mounting_plate_l - gasket_r, -INF/2.0]) {
			 hull(){ 
				cylinder(h=INF, r=gasket_r, center=true);
				translate([0, INF]) cylinder(h=INF, r=gasket_r, center=true);
			}
		}
	}
	translate([0, 0, -INF/2 + base_mount_thickness]) cube([supported_width*2, INF, INF], center=true);
	}
}

echo("Part length", mounting_plate_l);
union(){
	fc_single_mount();
	//Add the camera_mount with the specified angle
	translate([0, snap_mounting_l, mounting_plate_thickness]) apply_camera_mount_angle(camera_angle);
}
//hull(){

//}
