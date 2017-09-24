/**
* This camera mount is compatible with the NewBeeDrone cockroach frame
* and the NewBeeDrone BeeBrain v1.
* 
* Cameras known to fit:
*   Crazypony split camera vtx https://www.amazon.com/gp/product/B072L21RPL/
*/

$fn = 90;
VERSION = 3;

// Must be defined larger than any other piece
INF = 100;

//Include a tolerance for the printing for parts that can be bigger or larger
TOL = 0.2;

//Angle of the camera
camera_angle = 20;

barrel_r = 7.91/2;
barrel_l = 4.5 - TOL;

//How thick the snap is
snap_thickness = 2;
snap_r = barrel_r + snap_thickness;

//This is the angle in which the camera barrell is applied
clip_opening_angle = 60;

//Height from the center of the snap to the longest leg
support_height = 10;

//PCB dimensions based on the NewBeeDrone BeeBrain
pcb_thickness = 0.8 + TOL;
pcb_w = 27.08 + TOL;

//This is the height of the components on the PCB
component_thickness = 1;

base_wall_thickness = 1;
base_thickness = pcb_thickness + component_thickness + (2*base_wall_thickness);
base_h = 5;

support_thickness = 2;

fc_thickness = pcb_thickness + component_thickness; 

base_front_w = 7.5;

// How far apart are the supports
supported_width = 5;

mounting_hole_r = 0.6 + TOL;


/**
* Helper function
*/
module inf_cube(){ cube([INF, INF, INF], center=true);}

module clip_solid() {
	difference(){
		union(){
			// Right leg
			translate([supported_width/2.0, -support_height, -barrel_l/2.0]){
				cube([support_thickness, support_height, barrel_l]);
			};
			//Left leg
			translate([-support_thickness -supported_width/2.0, -support_height, -barrel_l/2.0]){
				cube([support_thickness, support_height, barrel_l]);
			};
			
			cylinder(h=barrel_l, r = snap_r, center=true);

			translate([0, -support_height/2, 0]) cube([supported_width, support_height, support_thickness], center=true);
		};
		cylinder(h=INF, r = barrel_r, center=true);
	}
}

module cut_opening(angle){
	
	//make a triangle can cut from center
	x = tan(angle) * INF;

	difference(){
		clip_solid();
		linear_extrude(height=INF, center=true){
			polygon([ [0, 0], [-1*x, INF], [x, INF] ]);
		}
	}
}





/**
 * Solid diamond height of the pcb and the components
 */
module fc_stub_solid(){
	//narrow piece
	rotate([0, 0, 45]) cube([pcb_w, pcb_w, fc_thickness], center=true); 
}

/**
 * A model of the FC PCB. Cut away the part where are no components on the FC
 */
module pcb_model(){
	o = sin(45)*pcb_w;
	front_cut = base_front_w/2*tan(45);
	y = o - front_cut; 	

	z = (pcb_thickness + component_thickness)/2;

	difference(){
			fc_stub_solid();
		translate([0,-y,0]){ 
		translate([0, -INF/2 + 1.5, INF/2 + z - component_thickness]) inf_cube();
		}
	}
}


module outer_base(){
	r = 2;
	shell = base_wall_thickness;
	h = (fc_thickness + shell*2)/2;
	minkowski_x = pcb_w + shell*2 - r*2;
	minkowski_y = pcb_w + shell*2 - r*2;
	minkowski() {
		rotate([0, 0, 45]) cube([minkowski_x,minkowski_y, h ], center=true); 

		cylinder(h=h, r=r, center=true);
	}

}
module hollow(){
	difference(){
		outer_base();
		pcb_model();
	}
}
module cut_back_opening(){
	o = sin(45)*pcb_w;
	front_cut = base_front_w/2*tan(45);
	y = o - front_cut; 	
		difference(){
		translate([0,y,0]){ 
			hollow();
}
			//Cut back
			translate([0, INF/2 + base_h, 0]) inf_cube();
		}
}
module cut_front_opening(){
	mount_h = 1;

	//Since cube is centered when minkowski is used its half
	difference(){
		translate([0, 0,base_thickness/2]){
			cut_back_opening();
		};
		translate([0, -INF/2, -INF/2 + base_wall_thickness + pcb_thickness + mount_h]) inf_cube();
	}
}

module base(){
	//open the front and back
	//hull(){
		difference(){
			cut_front_opening();
			// Cut out the mounting hole
			translate([0, -3, 0]){
					cylinder(h=INF, r=mounting_hole_r, center=true);
			}
		};
//		translate([0, -3, base_thickness - 0.5 ]){
//			cylinder(h=1, r= 2.16, center=true);
//		}
//	}
}


/**
* Round out the end of the snap
*/
module clip_rounding(){
	cylinder(h=barrel_l, r= snap_thickness/2.0, center=true);
}

/**
* Create a snap with an opening defined by opening_angle
*/
module snap(opening_angle){
	rotate_to_0 = 90-opening_angle;
	round_x = barrel_r + (snap_thickness/2.0);

	//Now rotate back to center
	rotate(rotate_to_0){
		union(){
			rotate(-2 * rotate_to_0){
				union(){
					rotate(rotate_to_0){
						cut_opening(opening_angle);
					};
					//left
					translate([-round_x, 0, 0]) clip_rounding();		
				}
			}
			//right
			translate([round_x, 0, 0]) clip_rounding();
		}
	}
}

/**
* Take the snap, which is on the xy plane, and rotate it to the correct
* angle. Remove any access material.
*/
module apply_camera_mount_angle(angle) {

	difference(){
		rotate([90 - angle, 0, 0]){
			translate([0, support_height, -barrel_l/2.0]) snap(clip_opening_angle);
		};
		translate([0, 0, -INF/2]) inf_cube();
	}
}


/*
union(){
	base();
	//Add the camera_mount with the specified angle
	translate([0, 0, base_thickness]) apply_camera_mount_angle(camera_angle);
}
*/
snap(clip_opening_angle);
//apply_camera_mount_angle(20);
