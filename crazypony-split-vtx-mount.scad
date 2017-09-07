VERSION = 1;
INF = 50;

$fn = 48;
MOUNT_PATTERN_LENGTH = 26; 
SCREW_R = 0.6;
SCREW_HEAD_R = 2.16;

mount_r = SCREW_HEAD_R;
frame_w = 2.0;
thickness = 1.0;

//For #00 screw, 3/32in
tap_r = 2; //0.05in r  
tap_h = 2.38125; //3/32in 
vtx_h = 15;//18;
vtx_w = 18;
//cylinder(h=thickness, r = SCREW_HEAD_R);

sidewall_h = 2;
y_offset = 6;
module wall(length){
	cube([thickness, length,2]);
}

module shell(){


	minkowski_h = thickness/2.0;
	intersection(){
		minkowski(){
			difference(){
				cube([INF, INF, minkowski_h], center=true);
				arm(INF);
			}
			cylinder(h=minkowski_h, r = frame_w, center=true);
		}
		arm(thickness);
		}

}

module add_mount(){
	difference(){
		union(){
			cylinder(h=thickness, r = mount_r, center=true);
			shell();
		}
		cylinder(h=INF, r = SCREW_R, center=true);
	}
}



module arm(_thickness){

	y_offset = 6;
	x = sin(45)*MOUNT_PATTERN_LENGTH;
	//Create solid arm
	hull(){
		cylinder(h=_thickness, r = mount_r, center=true);
		translate([x, vtx_h/2.0 - y_offset , 0]) cube([1, vtx_h, _thickness], center=true);
	}
}

module vtx_case_brace(){
	brace_w = 2;
	rotation = atan(vtx_w/vtx_h);
	intersection(){
		union(){
			rotate([0, 0, rotation]) cube([brace_w, INF, thickness], center=true);
			rotate([0, 0, -rotation]) cube([brace_w, INF, thickness], center=true);
		}
		cube([vtx_w, vtx_h, thickness], center=true);
	}
}
module vtx_case(){
	union(){
		difference(){
			cube([vtx_w, vtx_h, thickness], center=true);
			cube([vtx_w-(2*frame_w), vtx_h-(2*frame_w), INF], center=true);
		}
	vtx_case_brace();
	}
}
module sidewalls(){
	x = 4;
	y = 1.5;
	z = sidewall_h + thickness;

	translate([0, -y/2.0 - vtx_h/2.0 , z/2.0]) cube([x, y,z ], center=true);
}

//arm();
//shell();
//add_mount();


module frame(){
	x = sin(45)*MOUNT_PATTERN_LENGTH;
	union(){
		translate([0, vtx_h/2.0 - y_offset, 0]) vtx_case();
		//Remove the excess 
		difference(){
			union(){
				translate([-x, 0, 0]) add_mount();
				mirror([1, 0, 0])translate([-x, 0, 0])  add_mount();
			}
			cube([vtx_w, INF, INF], center=true);
		}
	}
}
//vtx_case_brace();

/*
union(){
	//import("libs/screw.stl");
	translate([0, 0, thickness/2.0]) frame();
	//sidewalls();
	//Add taps
	cylinder(h=tap_h, r= tap_r);
}
*/


w = sin(45)*MOUNT_PATTERN_LENGTH;
i =  w - vtx_w/2.0;
y_mount2 = 6;

module left_mount(){
	translate([-w, 0, 0]) cylinder(h=thickness, r = mount_r, center=true);
}
module right_mount(){
	translate([w, 0, 0]) cylinder(h=thickness, r = mount_r, center=true);
}

module bottom_tap(h){
	translate([vtx_w/2.0 - 1, -y_mount2, 0]) cylinder(h=h, r= tap_r, center=true);
}
module top_tap(h){
	translate([-vtx_w/2.0 + 5.18, 13, 0]) cylinder(h=h, r= tap_r, center=true);
}

module simple_frame(){
	hull(){
		left_mount();
		top_tap(thickness);
	}
	hull(){
		right_mount();
		bottom_tap(thickness);
	}

	hull(){
		top_tap(thickness);
		bottom_tap(thickness);
	}
}

union(){
	translate([0, 0, thickness/2.0]) simple_frame();
	translate([0, 0, tap_h/2.0 + thickness]){
	top_tap(tap_h);
	bottom_tap(tap_h);
	}
}
