// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Packing Box Inspection', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Packing Box Inspection", "before_save", function(frm, cdt, cdn) {
	console.log(" before save ******  ")
	var doc = frappe.get_doc(cdt, cdn);
	var pbi_child1_doc = doc.packing_box_inspection_child;
	for (var i = 0; i < pbi_child1_doc.length; i++) {
		if(pbi_child1_doc[i].wrapped){
			pbi_child1_doc[i].current_warehouse = pbi_child1_doc[i].pb_target_warehouse;
		}
	}
	console.log(" before update_packed_box_custom ******  ")
	update_packed_box_custom(pbi_child1_doc,doc.voucher_name);
	console.log(" before aftr*  ")

});

function update_packed_box_custom(pbi_child1_doc,voucher_name) {
	console.log("came inside update_packed_box_custom")
    frappe.call({
        method: "nhance.nhance.doctype.packing_box_inspection.packing_box_inspection.update_packed_box_custom",
        args: {
            "pbi_child1_doc": pbi_child1_doc,
						"voucher_name" : voucher_name
        },
        async: false,
        callback: function(r) {}
    }); //end of frappe call..
}
