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
snap_opening_angle = 60;

//Height from the center of the snap to the longest leg
support_height = 7;

support_thickness = 2;

// How far apart are the supports
supported_width = 4;

//PCB dimensions based on the NewBeeDrone BeeBrain
pcb_thickness = 0.8 + TOL;
pcb_w = 27.08 + TOL;

//This is the height of the components on the PCB
component_thickness = 1;

fc_thickness = pcb_thickness + component_thickness; 

base_wall_thickness = 1;
base_thickness = pcb_thickness + component_thickness + (2*base_wall_thickness);
base_h = 5;


base_front_w = 7.5;


mounting_hole_r = 0.6 + TOL;


/**
* Helper function
*/
module inf_cube(){ cube([INF, INF, INF], center=true);}


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
		translate([0, -INF/2 + 1.5 -y, INF/2 + z - component_thickness]) inf_cube();
	}
}


module fc_casing_solid(w){

	r = 2; //rounding radius
	shell = base_wall_thickness;
	h = (fc_thickness + shell*2)/2;
	minkowski_x = w + shell*2 - r*2;
	minkowski_y = w + shell*2 - r*2;
	minkowski() {
		rotate([0, 0, 45]) cube([minkowski_x,minkowski_y, h ], center=true); 
		cylinder(h=h, r=r, center=true);
	}

}
/**
 * Create a casing for the FC 
 */
module fc_casing(){
	difference(){
		fc_casing_solid(pcb_w);
		pcb_model();

		// Remove material from the bottom
		translate([0, 0, -fc_thickness]) fc_casing_solid(pcb_w-5);
	}
}


module cut_back_opening(){
	o = sin(45)*pcb_w;
	front_cut = base_front_w/2*tan(45);
	y = o - front_cut; 	
	difference(){
		translate([0, y, 0]) fc_casing();
		//Cut back
		translate([0, INF/2 + base_h, 0]) inf_cube();
	}
}
/**
 * Base that attaches to the FC
 */
module base(){
	mount_h = 1;
	difference(){
		translate([0, 0,base_thickness/2]) cut_back_opening();
		translate([0, -INF/2, -INF/2 + base_wall_thickness + pcb_thickness + mount_h]) inf_cube();
	}
}
/**
 * Base that attaches to the FC with mounting hole
 */
module base_with_mounting_hole(){
	hole_offset = -3;	
	difference(){
		base();
		// Cut out the mounting hole
		translate([0, hole_offset, 0]) cylinder(h=INF, r=mounting_hole_r, center=true);

	};
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
}

/**
* Take the snap, which is on the xy plane, and rotate it to the correct
* angle. Remove any access material.
*/
module apply_camera_mount_angle(angle) {

	difference(){
		translate([0, -1, 0]){
		rotate([90 - angle, 0, 0]){
			translate([0, support_height, -barrel_l/2.0]) rounded_snap_mount(snap_opening_angle);
		}
};
		translate([0, 0, -INF/2]) inf_cube();
	}
}


union(){
	base_with_mounting_hole();
	//Add the camera_mount with the specified angle
	translate([0, 0, base_thickness]) apply_camera_mount_angle(camera_angle);
}

