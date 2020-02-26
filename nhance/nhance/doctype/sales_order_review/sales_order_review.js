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
				frappe.msgprint("Access Rights Error! You do not have permission to perform this operation!");
			}
			
		})
	}
        if (cur_frm.doc.sales_order != undefined) {
	    var role = "SO Reviewer";
	    var check_role = get_roles(frappe.session.user, role);
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
	   if (check_role != "" && check_role != undefined){ 
		    for (var j = 0; j < review_templates.length; j++) {
			if (review_templates[j].field_label == "Parent Field"){
				var accept_field = "accept_" + review_templates[j].fieldname
				var reject_field = "reject_" + review_templates[j].fieldname
				cur_frm.set_df_property(accept_field, "hidden", false);
				cur_frm.set_df_property(reject_field, "hidden", false);
			}

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
				//console.log("current_doc_child-------------"+accept_field)
		                cur_frm.fields_dict.items.grid.toggle_display(accept_field, false);
		                cur_frm.fields_dict.items.grid.toggle_display(reject_field, false);
                    }
                }

            }
	    if (check_role != "" && check_role != undefined){
		    for (var i = 0; i < child_review_field.length; i++) {
		        for (var j = 0; j < review_templates.length; j++) {
		            var accept_field = "accept_" + review_templates[j].fieldname;
		            var reject_field = "reject_" + review_templates[j].fieldname;
		            if (accept_field == child_review_field[i].fieldname) {
				if (review_templates[j].field_label == "Item Field"){
					//console.log("unhide_child-------------"+accept_field)
				        cur_frm.fields_dict.items.grid.toggle_display(accept_field, true);
				        cur_frm.fields_dict.items.grid.toggle_display(reject_field, true);
				}

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
	    if (check_role != "" && check_role != undefined){
		    for (var i = 0; i < tax_review_field.length; i++) {
		        for (var j = 0; j < review_templates.length; j++) {
		            var accept_field = "accept_" + review_templates[j].fieldname;
		            var reject_field = "reject_" + review_templates[j].fieldname;
		            if (accept_field == tax_review_field[i].fieldname) {
				if (review_templates[j].field_label == "Tax Field"){
					console.log("reject_field-------------",reject_field)
				        cur_frm.fields_dict.taxes.grid.toggle_display(accept_field, true);
				        cur_frm.fields_dict.taxes.grid.toggle_display(reject_field, true);
				}

		            }
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
	var doc_review = "Sales Order"
	var review_templates = get_review_templates(doc_review);
	var doctype = "Sales Order Review";
        var current_doc = function_doc_details(doctype);
	var parent_validation = check_parent_review_field(doctype,doc_review,cur_frm.doc.name);
	
	if (parent_validation != undefined){
		if(parent_validation == false){
			frappe.validated = false;
		}
		else if(parent_validation == true){
			 var review_child_doc = "Sales Order Item Review";
			   var item_validation =  check_item_review_field(review_child_doc,doc_review,cur_frm.doc.name);
			   if (item_validation != undefined){
				if(item_validation == false){
					frappe.validated = false;
				}
				else if(item_validation == true)
					 var review_tax_doc = "Sales Taxes and Charges Review";
					  var tax_validation =  check_taxes_review_field("Sales Taxes and Charges Review",doc_review,cur_frm.doc.name);
					 if (tax_validation != undefined){
						if(tax_validation == false){
							frappe.validated = false;
						}
					}
				}
			 
		}
	}
	/*
	 for (var j = 0; j < review_templates.length; j++) {
		if (review_templates[j].field_label == "Parent Field"){
		        var accept_field = "accept_" + review_templates[j].fieldname
		        var reject_field = "reject_" + review_templates[j].fieldname
			console.log("field value-----------"+cur_frm.doc.accept_field)
		}
	  }
	*/
	   
           
	    //frappe.validated = false;
           /*
	    $.each(frm.doc.items, function(i, d) {
		for (var i = 0; i < current_doc_child.length; i++) {
		        var accept_field = "accept_" + current_doc_child[i].fieldname
		        var reject_field = "reject_" + current_doc_child[i].fieldname
		        for (var j = 0; j < child_review_field.length; j++) {
		            if (accept_field == child_review_field[j].fieldname) {
					console.log("item field -----------------"+d.accept_field)
					frappe.validated = false;
				}
			}
		}
	  })

	*/	
           
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
	},
	accept_customer:function(frm){
		if (cur_frm.doc.accept_customer == 1){
                	cur_frm.set_value('reject_customer', 0);
		}
	},
	reject_customer:function(frm){
		if (cur_frm.doc.reject_customer == 1){
                	cur_frm.set_value('accept_customer', 0);
		}
	},
	accept_order_type:function(frm){
		if (cur_frm.doc.accept_order_type == 1){
                	cur_frm.set_value('reject_order_type', 0);
		}
	},
	reject_order_type:function(frm){
		if (cur_frm.doc.reject_order_type == 1){
                	cur_frm.set_value('accept_order_type', 0);
		}
	},
	accept_company:function(frm){
		if (cur_frm.doc.accept_company == 1){
                	cur_frm.set_value('reject_company', 0);
		}
	},
	reject_company:function(frm){
		if (cur_frm.doc.reject_company == 1){
                	cur_frm.set_value('accept_company', 0);
		}
	},
	accept_delivery_date:function(frm){
		if (cur_frm.doc.accept_delivery_date == 1){
                	cur_frm.set_value('reject_delivery_date', 0);
		}
	},
	reject_delivery_date:function(frm){
		if (cur_frm.doc.reject_delivery_date == 1){
                	cur_frm.set_value('accept_delivery_date', 0);
		}
	},
	accept_customer_address:function(frm){
		if (cur_frm.doc.accept_customer_address == 1){
                	cur_frm.set_value('reject_customer_address', 0);
		}
	},
	reject_customer_address:function(frm){
		if (cur_frm.doc.reject_customer_address == 1){
                	cur_frm.set_value('accept_customer_address', 0);
		}
	},
	accept_contact_person:function(frm){
		if (cur_frm.doc.accept_contact_person == 1){
                	cur_frm.set_value('reject_contact_person', 0);
		}
	},
	reject_contact_person:function(frm){
		if (cur_frm.doc.reject_contact_person == 1){
                	cur_frm.set_value('accept_contact_person', 0);
		}
	},
	accept_company_address:function(frm){
		if (cur_frm.doc.accept_company_address == 1){
                	cur_frm.set_value('reject_company_address', 0);
		}
	},
	reject_company_address:function(frm){
		if (cur_frm.doc.reject_company_address == 1){
                	cur_frm.set_value('accept_company_address', 0);
		}
	},
	accept_shipping_address_name:function(frm){
		if (cur_frm.doc.accept_shipping_address_name == 1){
                	cur_frm.set_value('reject_shipping_address_name', 0);
		}
	},
	reject_shipping_address_name:function(frm){
		if (cur_frm.doc.reject_shipping_address_name == 1){
                	cur_frm.set_value('accept_shipping_address_name', 0);
		}
	},
	accept_set_warehouse:function(frm){
		if (cur_frm.doc.accept_set_warehouse == 1){
                	cur_frm.set_value('reject_set_warehouse', 0);
		}
	},
	reject_set_warehouse:function(frm){
		if (cur_frm.doc.reject_set_warehouse == 1){
                	cur_frm.set_value('accept_set_warehouse', 0);
		}
	},
	accept_taxes_and_charges:function(frm){
		if (cur_frm.doc.accept_taxes_and_charges == 1){
                	cur_frm.set_value('reject_taxes_and_charges', 0);
		}
	},
	reject_taxes_and_charges:function(frm){
		if (cur_frm.doc.reject_taxes_and_charges == 1){
                	cur_frm.set_value('accept_taxes_and_charges', 0);
		}
	},
	accept_apply_discount_on:function(frm){
		if (cur_frm.doc.accept_apply_discount_on == 1){
                	cur_frm.set_value('reject_apply_discount_on', 0);
		}
	},
	reject_apply_discount_on:function(frm){
		if (cur_frm.doc.reject_apply_discount_on == 1){
                	cur_frm.set_value('accept_apply_discount_on', 0);
		}
	},
	accept_additional_discount_percentage:function(frm){
		if (cur_frm.doc.accept_additional_discount_percentage == 1){
                	cur_frm.set_value('reject_additional_discount_percentage', 0);
		}
	},
	reject_additional_discount_percentage:function(frm){
		if (cur_frm.doc.reject_additional_discount_percentage == 1){
                	cur_frm.set_value('accept_additional_discount_percentage', 0);
		}
	},
	accept_tc_name:function(frm){
		if (cur_frm.doc.accept_tc_name == 1){
                	cur_frm.set_value('reject_tc_name', 0);
		}
	},
	reject_tc_name:function(frm){
		if (cur_frm.doc.reject_tc_name == 1){
                	cur_frm.set_value('accept_tc_name', 0);
		}
	},
	accept_project:function(frm){
		if (cur_frm.doc.accept_project == 1){
                	cur_frm.set_value('reject_project', 0);
		}
	},
	reject_project:function(frm){
		if (cur_frm.doc.reject_project == 1){
                	cur_frm.set_value('accept_project', 0);
		}
	},
	accept_source:function(frm){
		if (cur_frm.doc.accept_source == 1){
                	cur_frm.set_value('reject_source', 0);
		}
	},
	reject_source:function(frm){
		if (cur_frm.doc.reject_source == 1){
                	cur_frm.set_value('accept_source', 0);
		}
	},
	accept_campaign:function(frm){
		if (cur_frm.doc.accept_campaign == 1){
                	cur_frm.set_value('reject_campaign', 0);
		}
	},
	reject_campaign:function(frm){
		if (cur_frm.doc.reject_campaign == 1){
                	cur_frm.set_value('accept_campaign', 0);
		}
	},
	accept_base_discount_amount:function(frm){
		if (cur_frm.doc.accept_base_discount_amount == 1){
                	cur_frm.set_value('reject_base_discount_amount', 0);
		}
	},
	reject_base_discount_amount:function(frm){
		if (cur_frm.doc.reject_base_discount_amount == 1){
                	cur_frm.set_value('accept_base_discount_amount', 0);
		}
	},
	accept_discount_amount:function(frm){
		if (cur_frm.doc.accept_discount_amount == 1){
                	cur_frm.set_value('reject_discount_amount', 0);
		}
	},
	reject_discount_amount:function(frm){
		if (cur_frm.doc.reject_discount_amount == 1){
                	cur_frm.set_value('accept_discount_amount', 0);
		}
	}
});
frappe.ui.form.on("Sales Order Item Review",{
	accept_item_code:function(frm){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_item_code == 1){
				d.reject_item_code = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_item_code:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_item_code == 1){
				d.accept_item_code = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_item_name:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_item_name == 1){
				d.reject_item_name = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_item_name:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_item_name == 1){
				d.accept_item_name = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_description:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_description == 1){
				d.reject_description = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_description:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_description == 1){
				d.accept_description = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_delivery_date:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_delivery_date == 1){
				d.reject_delivery_date = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_delivery_date:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_delivery_date == 1){
				d.accept_delivery_date = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_image:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_image == 1){
				d.reject_image = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_image:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_image == 1){
				d.accept_image = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_qty:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_qty == 1){
				d.reject_qty = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_qty:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_qty == 1){
				d.accept_qty = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_uom:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_uom == 1){
				d.reject_uom = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_uom:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_uom == 1){
				d.accept_uom = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_conversion_factor:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_conversion_factor == 1){
				d.reject_conversion_factor = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_conversion_factor:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_conversion_factor == 1){
				d.accept_conversion_factor = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_price_list_rate:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_price_list_rate == 1){
				d.reject_price_list_rate = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_price_list_rate:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_price_list_rate == 1){
				d.accept_price_list_rate = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_rate:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_rate == 1){
				d.reject_rate = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_rate:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_rate == 1){
				d.accept_rate = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_discount_percentage:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_discount_percentage == 1){
				d.reject_discount_percentage = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_discount_percentage:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_discount_percentage == 1){
				d.accept_discount_percentage = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_margin_type:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_margin_type == 1){
				d.reject_margin_type = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_margin_type:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_margin_type == 1){
				d.accept_margin_type = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_margin_rate_or_amount:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_margin_rate_or_amount == 1){
				d.reject_margin_rate_or_amount = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_margin_rate_or_amount:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_margin_rate_or_amount == 1){
				d.accept_margin_rate_or_amount = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_rate_with_margin:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_rate_with_margin == 1){
				d.reject_rate_with_margin = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_rate_with_margin:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_rate_with_margin == 1){
				d.accept_rate_with_margin = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_weight_per_unit:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_weight_per_unit == 1){
				d.reject_weight_per_unit = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_weight_per_unit:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_weight_per_unit == 1){
				d.accept_weight_per_unit = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_weight_uom:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_weight_uom == 1){
				d.reject_weight_uom = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_weight_uom:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_weight_uom == 1){
				d.accept_weight_uom = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	accept_warehouse:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.accept_warehouse == 1){
				d.reject_warehouse = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	},
	reject_warehouse:function(frm,cdt,cdn){
 		$.each(frm.doc.items, function(i, d) {
			if (d.reject_warehouse == 1){
				d.accept_warehouse = 0;
			
			}
			cur_frm.refresh_field("items");
		})
	}



})

frappe.ui.form.on("Sales Taxes and Charges Review",{
	accept_rate:function(frm,cdt,cdn){
 		$.each(frm.doc.taxes, function(i, d) {
			if (d.accept_rate == 1){
				d.reject_rate = 0;
			
			}
			cur_frm.refresh_field("taxes");
		})
	},
	reject_rate:function(frm,cdt,cdn){
 		$.each(frm.doc.taxes, function(i, d) {
			if (d.reject_rate == 1){
				d.accept_rate = 0;
			
			}
			cur_frm.refresh_field("taxes");
		})
	}
})
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
function check_item_review_field(current_doc,review_doc,name){
	 var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.check_item_review_field',
        args: {
	    "current_doc":current_doc,
	    "review_doc":review_doc,
	    "name":name
        },
        async: false,
        callback: function(r) {
		doc_details = r.message;
        }
    });
	return doc_details
}
function check_parent_review_field(current_doc,review_doc,name){
	 var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.check_parent_review_field',
        args: {
	    "current_doc":current_doc,
	    "review_doc":review_doc,
	    "name":name
        },
        async: false,
        callback: function(r) {
		doc_details = r.message;
		console.log("doc_details---------------"+doc_details)
        }
    });
	return doc_details
}
function check_taxes_review_field(review_tax_doc,review_doc,name){
	console.log("current_doc--------------"+review_tax_doc)
	console.log("review_doc--------------"+review_doc)
	console.log("name--------------"+name)
	 var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.check_taxes_review_field',
        args: {
	    "current_doc":review_tax_doc,
	    "review_doc":review_doc,
	    "name":name
        },
        async: false,
        callback: function(r) {
		doc_details = r.message;
        }
    });
	return doc_details
}
