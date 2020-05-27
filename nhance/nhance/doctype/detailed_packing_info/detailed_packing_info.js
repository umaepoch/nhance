// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Detailed Packing Info', {
	refresh: function(frm) {

		frm.add_custom_button(__("Make Packing Items"), function() {
            console.log("Make Packing Items Button clicked");
            create_packing_item_custom_doc(cur_frm.doc.packing_details_review,cur_frm.doc.si_name);
          });

		frm.add_custom_button(__("Make Packing Boxes"), function() {
      console.log("Make Packing Boxes Button clicked");
			create_packing_box_custom_doc(cur_frm.doc.detailed_packing_box,cur_frm.doc.packing_details_review,cur_frm.doc.si_name);
	});
}
});


function create_packing_item_custom_doc(packing_items_data,si_name){
	frappe.call({
        method: "nhance.nhance.doctype.detailed_packing_info.detailed_packing_info.create_packing_item_custom_doc",
        args: {
            "packing_items_data": packing_items_data,
						"si_name":si_name
        },
        async: false,
        callback: function(r) {
           if (r.message) {
               console.log("response came :"+JSON.stringify( r.message ));
               frappe.set_route('List', "Packing Item Inspection");
           } else {
               console.log("problem in making  create_packing_item_custom_doc");
           }
       } //end of call back
    }); // end of frappe call
}

function create_packing_box_custom_doc(packing_boxes_data,packing_items_data,si_name){
	frappe.call({
        method: "nhance.nhance.doctype.detailed_packing_info.detailed_packing_info.create_packing_box_custom_doc",
        args: {
            "packing_boxes_data": packing_boxes_data,
						"packing_items_data":packing_items_data,
						"si_name":si_name
        },
        async: false,
        callback: function(r) {
           if (r.message) {
               console.log("response came :"+JSON.stringify( r.message ));
               frappe.set_route('List', "Packing Box Inspection");
           } else {
               console.log("problem in making  create_packing_box_custom_doc");
           }
       } //end of call back
    }); // end of frappe call
}
