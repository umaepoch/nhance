// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Packing Item Inspection', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Packing Item Inspection", "before_save", function(frm, cdt, cdn) {
	var doc = frappe.get_doc(cdt, cdn);
	var pii_child2_doc = doc.packing_item_inspection_progress_wh;
	for (var i = 0; i < pii_child2_doc.length; i++) {
		if(pii_child2_doc[i].wrapped){
			pii_child2_doc[i].current_warehouse = pii_child2_doc[i].pi_target_warehouse;
			pii_child2_doc[i].current_rarb_id = pii_child2_doc[i].rarb_location_twh;
		}
	}
	update_packed_item_custom(pii_child2_doc)
});

function update_packed_item_custom(pii_child2_doc) {
    frappe.call({
        method: "nhance.nhance.doctype.packing_item_inspection.packing_item_inspection.update_packed_item_custom",
        args: {
            "pii_child2_doc": pii_child2_doc
        },
        async: false,
        callback: function(r) {}
    }); //end of frappe call..
}

/*
frappe.ui.form.on("Packing Item Inspection", "after_save", function(frm, cdt, cdn) {
	console.log("after save working")
	var doc = frappe.get_doc(cdt, cdn);
	var pii_child2_doc = doc.packing_item_inspection_progress_wh;
	update_packed_item_custom(pii_child2_doc)
});
*/



/* field trigger child doc
frappe.ui.form.on('Packing Item Inspection Progress WH', {
	wrapped: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.wrapped){
			console.log("checkbox clicked*****");
			//row.test_feield_pi = "checked"
			$.each(frm.doc.packing_item_inspection_progress_wh, function(i, d) {
					d.test_feield_pi = "allrow";
					refresh_field("test_feield_pi");
					}); //end of each...
			refresh_field(frm.doc.packing_item_inspection_progress_wh);
		}

	}
});
*/
