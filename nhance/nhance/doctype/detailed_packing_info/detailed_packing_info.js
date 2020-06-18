// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Detailed Packing Info', {
	refresh: function(frm,cdt, cdn) {
		//	console.log("refresh 1 working");

		frm.add_custom_button(__("Make Packing Items"), function() {
            //console.log("Make Packing Items Button clicked");
            create_packing_item_custom_doc(cur_frm.doc.packing_details_review,cur_frm.doc.voucher_type, cur_frm.doc.voucher_no);
          });

		frm.add_custom_button(__("Make Packing Boxes"), function() {
      //console.log("Make Packing Boxes Button clicked");
			create_packing_box_custom_doc(cur_frm.doc.detailed_packing_box,cur_frm.doc.packing_details_review,cur_frm.doc.voucher_type, cur_frm.doc.voucher_no);
		});
}
});
//rarb_start
//pi_rarb_start
frappe.ui.form.on("Detailed Packing Item Child", {
pi_progress_warehouse: function (frm, cdt , cdn) {
		var row = locals[cdt][cdn];
		var pi_progress_warehouse = row.pi_progress_warehouse ;

		if(pi_progress_warehouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(pi_progress_warehouse);
			if(pi_progress_warehouse == rarb_warehouse){
				cur_frm.fields_dict.packing_details_review.grid.toggle_display("rarb_location_pwh", true);
				cur_frm.fields_dict.packing_details_review.grid.toggle_reqd("rarb_location_pwh", true)
				var rarb_warehouse_list = []
				cur_frm.set_query("rarb_location_pwh", "items", function(frm, cdt, cdn) {
					var d = locals[cdt][cdn];
					var pi_progress_warehouse = d.warehouse;
					rarb_warehouse_list = get_rarb_warehouse_item_name(pi_progress_warehouse);
					return {
					"filters": [
					["RARB ID", "name", "in", rarb_warehouse_list]
					]
					}
					refresh_field("rarb_location_pwh");
					refresh_field("items")
					});

			}else{
				cur_frm.fields_dict.packing_details_review.grid.toggle_display("rarb_location_pwh", false);
				cur_frm.fields_dict.packing_details_review.grid.toggle_reqd("rarb_location_pwh", false)
			}
		}else{
			cur_frm.fields_dict.packing_details_review.grid.toggle_display("rarb_location_pwh", false);
			 cur_frm.fields_dict.packing_details_review.grid.toggle_reqd("rarb_location_pwh", false)
		}
	} ,// end pi_progress_warehouse

	pi_target_warehouse: function (frm, cdt , cdn) {
	    var row = locals[cdt][cdn];
	    var pi_target_warehouse = row.pi_target_warehouse ;

	    if(pi_target_warehouse != undefined){
	      var rarb_warehouse = get_rarb_warehouse(pi_target_warehouse);
	      if(pi_target_warehouse == rarb_warehouse){
	        cur_frm.fields_dict.packing_details_review.grid.toggle_display("rarb_location_twh", true);
	        cur_frm.fields_dict.packing_details_review.grid.toggle_reqd("rarb_location_twh", true)
	        var rarb_warehouse_list = []
	        cur_frm.set_query("rarb_location_twh", "items", function(frm, cdt, cdn) {
	          var d = locals[cdt][cdn];
	          var pi_target_warehouse = d.warehouse;
	          rarb_warehouse_list = get_rarb_warehouse_item_name(pi_target_warehouse);
	          return {
	          "filters": [
	          ["RARB ID", "name", "in", rarb_warehouse_list]
	          ]
	          }
	          refresh_field("rarb_location_twh");
	          refresh_field("items")
	          });

	      }else{
	        cur_frm.fields_dict.packing_details_review.grid.toggle_display("rarb_location_twh", false);
	        cur_frm.fields_dict.packing_details_review.grid.toggle_reqd("rarb_location_twh", false)
	      }
	    }else{
	      cur_frm.fields_dict.packing_details_review.grid.toggle_display("rarb_location_twh", false);
	       cur_frm.fields_dict.packing_details_review.grid.toggle_reqd("rarb_location_twh", false)
	    }
	  } // end pi_target_warehouse
});

//pi_rarb_end

//pb_rarb_start
frappe.ui.form.on("Detailed Packing Box Child", {
pb_progress_warehouse: function (frm, cdt , cdn) {
		var row = locals[cdt][cdn];
		var pb_progress_warehouse = row.pb_progress_warehouse ;

		if(pb_progress_warehouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(pb_progress_warehouse);
			if(pb_progress_warehouse == rarb_warehouse){
				cur_frm.fields_dict.detailed_packing_box.grid.toggle_display("pb_rarb_location_pwh", true);
				cur_frm.fields_dict.detailed_packing_box.grid.toggle_reqd("pb_rarb_location_pwh", true)
				var rarb_warehouse_list = []
				cur_frm.set_query("pb_rarb_location_pwh", "items", function(frm, cdt, cdn) {
					var d = locals[cdt][cdn];
					var pb_progress_warehouse = d.warehouse;
					rarb_warehouse_list = get_rarb_warehouse_item_name(pb_progress_warehouse);
					return {
					"filters": [
					["RARB ID", "name", "in", rarb_warehouse_list]
					]
					}
					refresh_field("pb_rarb_location_pwh");
					refresh_field("detailed_packing_box")
					});

			}else{
				cur_frm.fields_dict.detailed_packing_box.grid.toggle_display("pb_rarb_location_pwh", false);
				cur_frm.fields_dict.detailed_packing_box.grid.toggle_reqd("pb_rarb_location_pwh", false)
			}
		}else{
			cur_frm.fields_dict.detailed_packing_box.grid.toggle_display("pb_rarb_location_pwh", false);
			 cur_frm.fields_dict.detailed_packing_box.grid.toggle_reqd("pb_rarb_location_pwh", false)
		}
	} ,// end pb_progress_warehouse

	pb_target_warehouse: function (frm, cdt , cdn) {
	    var row = locals[cdt][cdn];
	    var pb_target_warehouse = row.pb_target_warehouse ;

	    if(pb_target_warehouse != undefined){
	      var rarb_warehouse = get_rarb_warehouse(pb_target_warehouse);
	      if(pb_target_warehouse == rarb_warehouse){
	        cur_frm.fields_dict.detailed_packing_box.grid.toggle_display("pb_rarb_location_twh", true);
	        cur_frm.fields_dict.detailed_packing_box.grid.toggle_reqd("pb_rarb_location_twh", true)
	        var rarb_warehouse_list = []
	        cur_frm.set_query("pb_rarb_location_twh", "items", function(frm, cdt, cdn) {
	          var d = locals[cdt][cdn];
	          var pb_target_warehouse = d.warehouse;
	          rarb_warehouse_list = get_rarb_warehouse_item_name(pb_target_warehouse);
	          return {
	          "filters": [
	          ["RARB ID", "name", "in", rarb_warehouse_list]
	          ]
	          }
	          refresh_field("pb_rarb_location_twh");
	          refresh_field("detailed_packing_box")
	          });

	      }else{
	        cur_frm.fields_dict.detailed_packing_box.grid.toggle_display("pb_rarb_location_twh", false);
	        cur_frm.fields_dict.detailed_packing_box.grid.toggle_reqd("pb_rarb_location_twh", false)
	      }
	    }else{
	      cur_frm.fields_dict.detailed_packing_box.grid.toggle_display("pb_rarb_location_twh", false);
	       cur_frm.fields_dict.detailed_packing_box.grid.toggle_reqd("pb_rarb_location_twh", false)
	    }
	  } // end pb_target_warehouse
});

//pb_rarb_end

frappe.ui.form.on("Detailed Packing Info","before_save", function(frm,cdt,cdn){

	//console.log("before save is workings")

	 $.each(frm.doc.packing_details_review, function(i, d) {
		var packing_item = d.packing_item;
		var pi_progress_warehouse = d.pi_progress_warehouse;
		var pi_target_warehouse = d.pi_target_warehouse;
		var rarb_location_pwh = d.rarb_location_pwh;
		var rarb_location_twh = d.rarb_location_twh;
		if(rarb_location_pwh != undefined){
		var item_details = get_rarb_items_detail(pi_progress_warehouse,rarb_location_pwh);
		if(item_details != undefined){
			if(item_details != packing_item){
				frappe.msgprint('"'+rarb_location_pwh+'"'+"(PI) This RARB Location(Progress Warehouse) is reserved for specific item "+'"'+item_details+'"');
				frappe.validated = false;
			}
		}
	}//end of Progress valid
		if(rarb_location_twh != undefined){
		var item_details = get_rarb_items_detail(pi_target_warehouse,rarb_location_twh);
		if(item_details != undefined){
			if(item_details != packing_item){
				frappe.msgprint('"'+rarb_location_pwh+'"'+" (PI) This RARB Location(Target Warehouse) is reserved for specific item "+'"'+item_details+'"');
				frappe.validated = false;
			}
		}
	}//end of target valid
}) //end of pi item table

$.each(frm.doc.detailed_packing_box, function(i, d) {
 var packing_box = d.packing_box;
 var pb_progress_warehouse = d.pb_progress_warehouse;
 var pb_target_warehouse = d.pb_target_warehouse;
 var pb_rarb_location_pwh = d.pb_rarb_location_pwh;
 var pb_rarb_location_twh = d.pb_rarb_location_twh;
 if(pb_rarb_location_pwh != undefined){
 var item_details = get_rarb_items_detail(pb_progress_warehouse,pb_rarb_location_pwh);
 if(item_details != undefined){
	 if(item_details != packing_box){
		 frappe.msgprint('"'+pb_rarb_location_pwh+'"'+"(PB) This RARB Location(Progress Warehouse) is reserved for specific item "+'"'+item_details+'"');
		 frappe.validated = false;
	 }
 }
}//end of Progress valid
 if(pb_rarb_location_twh != undefined){
 var item_details = get_rarb_items_detail(pb_target_warehouse,pb_rarb_location_twh);
 if(item_details != undefined){
	 if(item_details != packing_box){
		 frappe.msgprint('"'+pb_rarb_location_pwh+'"'+" (PB) This RARB Location(Target Warehouse) is reserved for specific item "+'"'+item_details+'"');
		 frappe.validated = false;
	 }
 }
}//end of target valid
}) //end of pb item table



})
//rarb_end



function create_packing_item_custom_doc(packing_items_data,voucher_type,voucher_no){
	frappe.call({
        method: "nhance.nhance.doctype.detailed_packing_info.detailed_packing_info.create_packing_item_custom_doc",
        args: {
            "packing_items_data": packing_items_data,
						"voucher_type":voucher_type,
						"voucher_no":voucher_no
        },
        async: false,
        callback: function(r) {
           if (r.message) {
              // console.log("response came :"+JSON.stringify( r.message ));
               frappe.set_route('List', "Packing Item Inspection");
           } else {
               console.log("problem in making  create_packing_item_custom_doc");
           }
       } //end of call back
    }); // end of frappe call
}

function create_packing_box_custom_doc(packing_boxes_data,packing_items_data,voucher_type,voucher_no){
	frappe.call({
        method: "nhance.nhance.doctype.detailed_packing_info.detailed_packing_info.create_packing_box_custom_doc",
        args: {
            "packing_boxes_data": packing_boxes_data,
						"packing_items_data":packing_items_data,
						"voucher_type":voucher_type,
						"voucher_no":voucher_no

        },
        async: false,
        callback: function(r) {
           if (r.message) {
              // console.log("response came :"+JSON.stringify( r.message ));
               frappe.set_route('List', "Packing Box Inspection");
           } else {
               console.log("problem in making  create_packing_box_custom_doc");
           }
       } //end of call back
    }); // end of frappe call
}

//rarb_functions_start
function get_rarb_warehouse(warehouse){
	var supplier_criticality = "";
	frappe.call({
		method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_rarb_warehouse',
		args: {
		   "warehouse":warehouse
		},
		async: false,
		callback: function(r) {
		   if(r.message != undefined){
			    //console.log("supplier criticality..." + JSON.stringify(r.message));
			   supplier_criticality = r.message[0].warehouse;
			  // //console.log("warehnouse=============="+supplier_criticality);
			}
		}
    });
    return supplier_criticality;
}

function get_rarb_warehouse_item_name(warehouse){
	var supplier_criticality = [];
	frappe.call({
		method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_rarb_warehouse_item_name',
		args: {
		   "warehouse":warehouse
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
			 for (var i = 0; i < r.message.length; i++) {
				    supplier_criticality.push(r.message[i].rarb_id);

				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
    return supplier_criticality;
}


function get_rarb_items_detail(warehouse,pch_rarb_location_src){
	var supplier_criticality = ""
	frappe.call({
		method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_rarb_items_detail',
		args: {
		   "warehouse":warehouse,
		   "pch_rarb_location_src":pch_rarb_location_src
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
			 for (var i = 0; i < r.message.length; i++) {
				    supplier_criticality = r.message[i].rarb_item;

				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
    return supplier_criticality
}

//rarb_functions_end
