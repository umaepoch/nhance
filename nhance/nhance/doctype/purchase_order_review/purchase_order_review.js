// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Order Review', {
	refresh: function(frm) {
		if (cur_frm.doc.docstatus == 1){
		cur_frm.add_custom_button(__('Accept Proposed Values'), function() {
			var role = "PO Creator";
			var check_role = get_roles(frappe.session.user, role);
			if (check_role != "" && check_role != undefined){
				var doc_review = "Purchase Order"
				var sales_order_review = "Purchase Order Review"
				var sales_review = [];
			        var review_templates = get_review_templates(doc_review);
				var current_doc = function_doc_details(sales_order_review);
				for (var i = 0; i < review_templates.length; i++) {
				    var reject_field = "reject_"+review_templates[i].fieldname;
				    for (var j = 0; j < current_doc.length; j++) {
					if (reject_field == current_doc[j].fieldname) {
						var propose_new_value = "propose_new_" + review_templates[i].fieldname;
						    sales_review.push({propose_new_value,reject_field});
					    
					}
				    }
				}
				var sales_review_item = [];
				var sales_order_item_review = "Purchase Order Item Review";
				var current_item_doc = function_doc_details(sales_order_item_review);
				$.each(frm.doc.items, function(i, item) {
					for (var i = 0; i < review_templates.length; i++) {
					    var reject_field = "reject_"+review_templates[i].fieldname;
					    for (var j = 0; j < current_item_doc.length; j++) {
						if (reject_field == current_item_doc[j].fieldname) {
							var propose_new_value = "propose_new_" + review_templates[i].fieldname;
							sales_review_item.push({propose_new_value,reject_field});
						      
						    
						}
					    }
					}
				//var update_sales_items = update_sales_order_items(sales_review_item,cur_frm.doc.name,cur_frm.doc.sales_order,item.item_code);
				});
				var sales_review_taxes = [];
				var sales_order_taxes_review = "Purchase Taxes and Charges Review";
				var current_taxes_doc = function_doc_details(sales_order_taxes_review);
				$.each(frm.doc.taxes, function(i, item) {
					for (var i = 0; i < review_templates.length; i++) {
					    var reject_field = "reject_"+review_templates[i].fieldname;
					    for (var j = 0; j < current_taxes_doc.length; j++) {
						if (reject_field == current_taxes_doc[j].fieldname) {
							var propose_new_value = "propose_new_" + review_templates[i].fieldname;
							sales_review_taxes.push({propose_new_value,reject_field});
						      
						    
						}
					    }
					}
				//var update_sales_taxes = update_sales_order_taxes(sales_review_taxes,cur_frm.doc.name,cur_frm.doc.sales_order,item.account_head,cur_frm.doc.taxes_and_charges);
				});
				var get_doc = create_purchase_order(sales_review,cur_frm.doc.name,cur_frm.doc.purchase_order);
				if(get_doc == true){
					frappe.model.open_mapped_doc({
                   			method: "nhance.nhance.doctype.purchase_order_review.purchase_order_review.mapped_purchase_order",
                    			frm: cur_frm
               				 })
				}
				
			}
			else{
				frappe.msgprint("Logged in user "+'"'+frappe.session.user+'"'+" Don't have permission "+'"'+role+'"' +" to perform accept proposed value");
			}
		
			
		})
			}
		 if (cur_frm.doc.purchase_order != undefined) {
			var doctype = "Purchase Order";
			var current_doc = function_doc_details(doctype);
			for (var i = 0; i < current_doc.length; i++) {
				if (current_doc[i].fieldname != "doctype_name"){
					cur_frm.set_df_property(current_doc[i].fieldname, "read_only", true);
				}

			}
			var child_doc = "Purchase Order Item";
			var child_doc_field = function_doc_details(child_doc);
			for (var i = 0; i < child_doc_field.length; i++) {
				if (child_doc_field[i].fieldname != "gst_hsn_code" && child_doc_field[i].fieldname != "track_historical_prices") {
					cur_frm.fields_dict.items.grid.toggle_enable(child_doc_field[i].fieldname, false);
				}

			}
			var child_doc_tax = "Purchase Taxes and Charges";
			var child_doc_tax_field = function_doc_details(child_doc_tax);
			for (var i = 0; i < child_doc_tax_field.length; i++) {
				cur_frm.fields_dict.taxes.grid.toggle_enable(child_doc_tax_field[i].fieldname, false);


			}
			var payment = "Payment Schedule";
			var payment_field = function_doc_details(payment);
			for (var i = 0; i < payment_field.length; i++) {
				cur_frm.fields_dict.payment_schedule.grid.toggle_enable(payment_field[i].fieldname, false);
			
			}
			var doc_review = "Purchase Order"
			var review_templates = get_review_templates(doc_review);
			var doctype = "Purchase Order";
			var current_doc = function_doc_details(doctype);
			for (var j = 0; j < current_doc.length; j++) {
				var accept_field = "accept_" + current_doc[j].fieldname;
				var reject_field = "reject_" + current_doc[j].fieldname
				cur_frm.set_df_property(accept_field, "hidden", true);
				cur_frm.set_df_property(reject_field, "hidden", true);

			}
			for (var j = 0; j < review_templates.length; j++) {
				var accept_field = "accept_" + review_templates[j].fieldname
				var reject_field = "reject_" + review_templates[j].fieldname
				cur_frm.set_df_property(accept_field, "hidden", false);
				cur_frm.set_df_property(reject_field, "hidden", false);

			}
			var doctype_item = "Purchase Order Item";
			var review_child_doc = "Purchase Order Item Review";
			var child_review_field = function_doc_details(review_child_doc);
			var current_doc_child = function_doc_details(doctype_item);

			for (var i = 0; i < current_doc_child.length; i++) {
				var accept_field = "accept_" + current_doc_child[i].fieldname
				var reject_field = "reject_" + current_doc_child[i].fieldname
				for (var j = 0; j < child_review_field.length; j++) {
				    if (accept_field == child_review_field[j].fieldname) {
					cur_frm.fields_dict.items.grid.toggle_display(accept_field, false);
					cur_frm.fields_dict.items.grid.toggle_display(reject_field, false);
				    }
				}

			}
			for (var i = 0; i < child_review_field.length; i++) {
				for (var j = 0; j < review_templates.length; j++) {
				    var accept_field = "accept_" + review_templates[j].fieldname;
				    var reject_field = "reject_" + review_templates[j].fieldname;
				    if (accept_field == child_review_field[i].fieldname) {
					cur_frm.fields_dict.items.grid.toggle_display(accept_field, true);
					cur_frm.fields_dict.items.grid.toggle_display(reject_field, true);

				    }
				}
			}
			var doctype_tax = "Purchase Taxes and Charges";
			var review_tax_doc = "Purchase Taxes and Charges Review";
			var tax_review_field = function_doc_details(review_tax_doc);
			var current_doc_tax = function_doc_details(doctype_tax);

			for (var i = 0; i < current_doc_tax.length; i++) {
				var accept_field = "accept_" + current_doc_tax[i].fieldname
				var reject_field = "reject_" + current_doc_tax[i].fieldname
				for (var j = 0; j < tax_review_field.length; j++) {
				    if (accept_field == tax_review_field[j].fieldname) {
					cur_frm.fields_dict.taxes.grid.toggle_display(accept_field, false);
					cur_frm.fields_dict.taxes.grid.toggle_display(reject_field, false);
				    }
				}

			}
			for (var i = 0; i < tax_review_field.length; i++) {
				for (var j = 0; j < review_templates.length; j++) {
				    var accept_field = "accept_" + review_templates[j].fieldname;
				    var reject_field = "reject_" + review_templates[j].fieldname;
				    if (accept_field == tax_review_field[i].fieldname) {
					cur_frm.fields_dict.taxes.grid.toggle_display(accept_field, true);
					cur_frm.fields_dict.taxes.grid.toggle_display(reject_field, true);

				    }
				}
			}

		}
	}
});
function function_doc_details(doctype) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.purchase_order_review.purchase_order_review.get_doc_details',
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
function get_review_templates(doctype) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.purchase_order_review.purchase_order_review.get_review_templates',
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
function get_roles(user, role){
	var purchase = "";
    frappe.call({
        method: "nhance.nhance.doctype.purchase_order_review.purchase_order_review.get_roles",
        args: {
            "user": user,
	    "role":role
        },
        async: false,
        callback: function(r) {
	if (r.message.length > 0){
      
            purchase = r.message[0].role;
	}
        } 
    }); 
    return purchase;


}
function function_doc_details(doctype) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.purchase_order_review.purchase_order_review.get_doc_details',
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
function create_purchase_order(sales_review,name,sales_order) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.purchase_order_review.purchase_order_review.create_purchase_order',
        args: {
	    "sales_review":sales_review,
	    "name":name,
            "sales_order": sales_order
        },
        async: false,
        callback: function(r) {
		doc_details = r.message;
        }
    });
	return doc_details
}
