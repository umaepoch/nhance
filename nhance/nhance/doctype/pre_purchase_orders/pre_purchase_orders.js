// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pre Purchase Orders', {
	refresh: function(frm) {
		if(cur_frm.doc.docstatus == 1){
			 frm.add_custom_button(__("Make Approved Pre Purchase Order"), function() {
				/*
				frappe.model.open_mapped_doc({
				    method: "nhance.nhance.doctype.pre_purchase_orders.pre_purchase_orders.make_approved_pre_purchase_order",
				    frm: cur_frm
				})*/
				var verification = get_verification(cur_frm.doc.name);
				if (verification == undefined){
					make_approved_pre_purchase_order(cur_frm.doc.name);
				}else{
					frappe.msgprint("Approved Pre Purchase Order already created "+verification[0]['name']);
				}
			});
			
		}
		if(cur_frm.doc.project_being_ordered != undefined){
			cur_frm.set_df_property("date", "read_only", true);
			var doctype = "Pre Purchase Item"
			var child_docfields = function_doc_details(doctype)
			for (var i =0;  i < child_docfields.length; i++){
				if(child_docfields[i].fieldname != "recommended_supplier" && child_docfields[i].fieldname != "recommended_qty" && child_docfields[i].fieldname != "recommended_rate"){
					 cur_frm.fields_dict.items.grid.toggle_enable(child_docfields[i].fieldname, false);
				}
			}
			
		}
	}
});
function function_doc_details(doctype) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.pre_purchase_orders.pre_purchase_orders.get_doc_details',
        args: {
            "doctype": doctype

        },
        async: false,
        callback: function(r) {
            doc_details = r.message;
        }
    });
    return doc_details;
}
function make_approved_pre_purchase_order(name){
  var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.pre_purchase_orders.pre_purchase_orders.make_approved_pre_purchase_order',
        args: {
            "source_name": name

        },
        async: false,
        callback: function(r) {
            doc_details = r.message;
	    console.log("doc_details----------------"+doc_details)
	    frappe.set_route("List", doc_details);
        }
    });
    return doc_details;
}
function get_verification(name){
  var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.pre_purchase_orders.pre_purchase_orders.get_verification',
        args: {
            "source_name": name

        },
        async: false,
        callback: function(r) {
            doc_details = r.message;
	    console.log("doc_details----------------"+doc_details)
	    //frappe.set_route("List", doc_details);
        }
    });
    return doc_details;
}
