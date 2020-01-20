// Copyright (c) 2019, Epoch and contributors
// For license information, please see license.txt
frappe.ui.form.on('Sales Order Review', {
    refresh: function(frm) {
	
	if(cur_frm.doc.docstatus ==1){
		cur_frm.add_custom_button(__('Accept Proposed Values'), function() {
			var role = "SO Creator";
			var check_role = get_roles(frappe.session.user, role);
			if (check_role != "" && check_role != undefined){
				 var doc_review = "Sales Order"
				var sales_order_review = "Sales Order Review"
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
				var sales_order_item_review = "Sales Order Item Review";
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
				var sales_order_taxes_review = "Sales Taxes and Charges Review";
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
				var sales_review_sales_team = [];
				var sales_order_team_review = "Sales Team Review";
				var current_team_doc = function_doc_details(sales_order_team_review);
				$.each(frm.doc.sales_team, function(i, item) {
					for (var i = 0; i < review_templates.length; i++) {
					    var reject_field = "reject_"+review_templates[i].fieldname;
					    for (var j = 0; j < current_team_doc.length; j++) {
						if (reject_field == current_team_doc[j].fieldname) {
							var propose_new_value = "propose_new_" + review_templates[i].fieldname;
							sales_review_sales_team.push({propose_new_value,reject_field});
						      
						    
						}
					    }
					}
				var update_sales_team = update_sales_order_team(sales_review_sales_team,cur_frm.doc.name,cur_frm.doc.sales_order);
				});
				//var update_sales = update_sales_order(sales_review,cur_frm.doc.name,cur_frm.doc.sales_order);
				var get_doc = create_sales_order(sales_review,cur_frm.doc.name,cur_frm.doc.sales_order);
				if(get_doc == true){
					frappe.model.open_mapped_doc({
                   				method: "nhance.nhance.doctype.sales_order_review.sales_order_review.mapped_sales_order",
                    				frm: cur_frm
               				 })
				}
				
			}
			else{
				frappe.msgprint('"'+frappe.session.user+'"'+" Don't have permission "+'"'+role+'"' +" to perform accept proposed value");
			}
			
		})
	}
        if (cur_frm.doc.sales_order != undefined) {
            var doctype = "Sales Order";
            var current_doc = function_doc_details(doctype);
            for (var i = 0; i < current_doc.length; i++) {

                cur_frm.set_df_property(current_doc[i].fieldname, "read_only", true);

            }
            var child_doc = "Sales Order Item";
            var child_doc_field = function_doc_details(child_doc);
            for (var i = 0; i < child_doc_field.length; i++) {
                if (child_doc_field[i].fieldname != "gst_hsn_code") {
                    cur_frm.fields_dict.items.grid.toggle_enable(child_doc_field[i].fieldname, false);
                }

            }
            var child_doc_tax = "Sales Taxes and Charges";
            var child_doc_tax_field = function_doc_details(child_doc_tax);
            for (var i = 0; i < child_doc_tax_field.length; i++) {
                cur_frm.fields_dict.taxes.grid.toggle_enable(child_doc_tax_field[i].fieldname, false);


            }
            var payment = "Payment Schedule";
            var payment_field = function_doc_details(payment);
            for (var i = 0; i < payment_field.length; i++) {
                cur_frm.fields_dict.payment_schedule.grid.toggle_enable(payment_field[i].fieldname, false);


            }


            var doc_review = "Sales Order"
            var review_templates = get_review_templates(doc_review);
            var doctype = "Sales Order";
            var current_doc = function_doc_details(doctype);
            for (var j = 0; j < current_doc.length; j++) {
                var accept_field = "accept_" + current_doc[j].fieldname;
                var reject_field = "reject_" + current_doc[j].fieldname
                cur_frm.set_df_property(accept_field, "hidden", true);
                cur_frm.set_df_property(reject_field, "hidden", true);

            }
            for (var j = 0; j < review_templates.length; j++) {
		if (review_templates[j].field_label == "Parent Field"){
		        var accept_field = "accept_" + review_templates[j].fieldname
		        var reject_field = "reject_" + review_templates[j].fieldname
		        cur_frm.set_df_property(accept_field, "hidden", false);
		        cur_frm.set_df_property(reject_field, "hidden", false);
		}

            }
            var doctype_item = "Sales Order Item";
            var review_child_doc = "Sales Order Item Review";
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
			if (review_templates[j].field_label == "Item Field"){
		                cur_frm.fields_dict.items.grid.toggle_display(accept_field, true);
		                cur_frm.fields_dict.items.grid.toggle_display(reject_field, true);
			}

                    }
                }
            }
            var doctype_tax = "Sales Taxes and Charges";
            var review_tax_doc = "Sales Taxes and Charges Review";
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
            var doctype_tema = "Sales Team";
            var review_team_doc = "Sales Team Review";
            var team_review_field = function_doc_details(review_team_doc);
            var current_doc_team = function_doc_details(doctype_tema);

            for (var i = 0; i < current_doc_team.length; i++) {
                var accept_field = "accept_" + current_doc_team[i].fieldname
                var reject_field = "reject_" + current_doc_team[i].fieldname
                for (var j = 0; j < team_review_field.length; j++) {
                    if (accept_field == team_review_field[j].fieldname) {
                        cur_frm.fields_dict.sales_team.grid.toggle_display(accept_field, false);
                        cur_frm.fields_dict.sales_team.grid.toggle_display(reject_field, false);
                    }
                }

            }
            for (var i = 0; i < team_review_field.length; i++) {
                for (var j = 0; j < review_templates.length; j++) {
                    var accept_field = "accept_" + review_templates[j].fieldname;
                    var reject_field = "reject_" + review_templates[j].fieldname;
                    if (accept_field == team_review_field[i].fieldname) {
                        cur_frm.fields_dict.sales_team.grid.toggle_display(accept_field, true);
                        cur_frm.fields_dict.sales_team.grid.toggle_display(reject_field, true);

                    }
                }
            }

        }

    },
    before_submit: function(frm, cdt, cdn) {
       
	var sales_order = cur_frm.doc.sales_order;
	//under_review_uncheck(sales_order);
	
       /* var review_templates = get_review_templates(doc_review);
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
        var sales_order_item_review = "Sales Order Item Review";
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
	var update_sales_items = update_sales_order_items(sales_review_item,cur_frm.doc.name,cur_frm.doc.sales_order,item.item_code);
	});
	var sales_review_taxes = [];
        var sales_order_taxes_review = "Sales Taxes and Charges Review";
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
	var update_sales_taxes = update_sales_order_taxes(sales_review_taxes,cur_frm.doc.name,cur_frm.doc.sales_order,item.account_head,cur_frm.doc.taxes_and_charges);
	});
	var sales_review_sales_team = [];
        var sales_order_team_review = "Sales Team Review";
        var current_team_doc = function_doc_details(sales_order_team_review);
	$.each(frm.doc.sales_team, function(i, item) {
		for (var i = 0; i < review_templates.length; i++) {
		    var reject_field = "reject_"+review_templates[i].fieldname;
		    for (var j = 0; j < current_team_doc.length; j++) {
		        if (reject_field == current_team_doc[j].fieldname) {
		                var propose_new_value = "propose_new_" + review_templates[i].fieldname;
		                sales_review_sales_team.push({propose_new_value,reject_field});
		              
		            
		        }
		    }
		}
	var update_sales_team = update_sales_order_team(sales_review_sales_team,cur_frm.doc.name,cur_frm.doc.sales_order);
	});
	var update_sales = update_sales_order(sales_review,cur_frm.doc.name,cur_frm.doc.sales_order);
	if(update_sales){
		frappe.msgpring(update_sales+" Sales order has been submitted with all proposed new value");
		}*/
    },
    before_save : function(frm){
		var sales_order = cur_frm.doc.sales_order;
	        // under_review_check(sales_order);
	}
});

function function_doc_details(doctype) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.get_doc_details',
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
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.get_review_templates',
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
function update_sales_order(sales_review,name,sales_order) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.update_sales_order',
        args: {
            "sales_review": sales_review,
	    "name":name,
	    "sales_order":sales_order
        },
        async: false,
        callback: function(r) {
            doc_details = r.message.name;
        }
    });
    return doc_details;
}
function update_sales_order_items(sales_review_item,name,sales_order,item_code){
	 var doc_details = "";
	    frappe.call({
		method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.update_sales_order_items',
		args: {
		    "sales_review_item": sales_review_item,
		    "name":name,
		    "sales_order":sales_order,
		    "item_code":item_code
		},
		async: false,
		callback: function(r) {
		    doc_details = r.message;
		}
	    });
	    return doc_details;
}
function update_sales_order_taxes(sales_review_taxes,name,sales_order,account_head,taxes_and_charges){
	 var doc_details = "";
	    frappe.call({
		method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.update_sales_order_taxes',
		args: {
		    "sales_review_taxes": sales_review_taxes,
		    "name":name,
		    "sales_order":sales_order,
		    "account_head":account_head,
		    "taxes_and_charges":taxes_and_charges
		},
		async: false,
		callback: function(r) {
		    doc_details = r.message;
		}
	    });
	    return doc_details;
}
function update_sales_order_team(sales_review_sales_team,name,sales_order){
	 var doc_details = "";
	    frappe.call({
		method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.update_sales_order_team',
		args: {
		    "sales_review_sales_team": sales_review_sales_team,
		    "name":name,
		    "sales_order":sales_order
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
        method: "nhance.nhance.doctype.sales_order_review.sales_order_review.get_roles",
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
function get_currenct_base_doc_details(sales_order){
	 var sales_order_details = "";
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Sales Order",
            filters: {
                name: ["=", sales_order]
            },
        },
        async: false,
        callback: function(r) {
            if (r.message) {
               sales_order_details = r.message;
		
            }
        }
    })
	//console.log("sales_order_details-------------"+JSON.stringify(sales_order_details));
	return sales_order_details
}
function get_currenct_doc_details(name){
	 var sales_order_details = "";
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Sales Order Review",
            filters: {
                name: ["=", name]
            },
        },
        async: false,
        callback: function(r) {
            if (r.message) {
               sales_order_details = r.message;
            }
        }
    })
	return sales_order_details
}
function under_review_check(sales_order) {
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.get_check_box_cheched',
        args: {
            "sales_order": sales_order
        },
        async: false,
        callback: function(r) {
        }
    });
    
}
function under_review_uncheck(sales_order) {
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.get_check_box_uncheck',
        args: {
            "sales_order": sales_order
        },
        async: false,
        callback: function(r) {
        }
    });
}
function create_sales_order(sales_review,name,sales_order) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.create_sales_order',
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
