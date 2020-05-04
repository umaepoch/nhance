// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Detailed Packing Info', {
	refresh: function(frm) {

		frm.add_custom_button(__("Make Packing Items"), function() {
            console.log("Make Packing Items Button clicked");
            make_packing_item_doc(cur_frm.doc.packing_details_review,cur_frm.doc.si_name);
          });

		frm.add_custom_button(__("Make Packing Boxes"), function() {
      console.log("Make Packing Boxes Button clicked");
			make_packed_box_doc(cur_frm.doc.detailed_packing_box,cur_frm.doc.packing_details_review,cur_frm.doc.si_name);
	});
}
});


function make_packing_item_doc(packing_items_data,si_name){
	frappe.call({
        method: "nhance.nhance.doctype.detailed_packing_info.detailed_packing_info.make_packing_item_doc",
        args: {
            "packing_items_data": packing_items_data,
						"si_name":si_name
        },
        async: false,
        callback: function(r) {
           if (r.message) {
               console.log("response came :"+JSON.stringify( r.message ));
               frappe.set_route('List', "Packed Item Custom");
           } else {
               console.log("problem in making  make_packing_item_doc");
           }
       } //end of call back
    }); // end of frappe call
}

function make_packed_box_doc(packing_boxes_data,packing_items_data,si_name){
	frappe.call({
        method: "nhance.nhance.doctype.detailed_packing_info.detailed_packing_info.make_packed_box_doc",
        args: {
            "packing_boxes_data": packing_boxes_data,
						"packing_items_data":packing_items_data,
						"si_name":si_name
        },
        async: false,
        callback: function(r) {
           if (r.message) {
               console.log("response came :"+JSON.stringify( r.message ));
               frappe.set_route('List', "Packed Box Custom");
           } else {
               console.log("problem in making  make_packed_box_doc");
           }
       } //end of call back
    }); // end of frappe call
}
