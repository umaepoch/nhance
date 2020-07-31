frappe.ui.form.on("Sales Order", "refresh", function(frm) {
    var role = "SO Reviewer";
    var role_creator = "SO Creator";
    var check_role = get_roles(frappe.session.user, role);
    var check_role_creator = get_roles(frappe.session.user, role_creator);
    var so_doctype = cur_frm.doc.doctype;
    var so_document_review = get_review_templates(so_doctype);
    
   if(so_document_review.length != 0){
    if (cur_frm.doc.docstatus == 0) {
        frm.add_custom_button(__("Make Sales Order Review"), function() {
            if (check_role_creator != "" && check_role_creator != undefined) {
                frappe.model.open_mapped_doc({
                    method: "nhance.nhance.doctype.sales_order_review.sales_order_review.make_document_review_detials",
                    frm: cur_frm
                })
            }
		else if (check_role != "" && check_role != undefined) {
                frappe.model.open_mapped_doc({
                    method: "nhance.nhance.doctype.sales_order_review.sales_order_review.make_document_review_detials",
                    frm: cur_frm
                })
            } else {
                frappe.msgprint("Access Rights Error! You do not have permission to perform this operation!");
            }
        });
    }
	}
    if (cur_frm.doc.under_review == 1) {
        var fields_name = get_fields(cur_frm.doc.doctype);
        var item_fields = "";
        var tax_fields = "";
        var payment_fields = "";
        for (var pf = 0; pf < fields_name.length; pf++) {
            cur_frm.set_df_property(fields_name[pf].fieldname, "read_only", 1);

            if (fields_name[pf].fieldname == "items") {
                var child_field = fields_name[pf].options;
                item_fields = get_fields(child_field);
            } else if (fields_name[pf].fieldname == "taxes") {
                var child_field = fields_name[pf].options;
                tax_fields = get_fields(child_field);
            } else if (fields_name[pf].fieldname == "payment_schedule") {
                var child_field = fields_name[pf].options;
                payment_fields = get_fields(child_field);
            }
        }
        for (var itm_f = 0; itm_f < item_fields.length; itm_f++) {
            cur_frm.fields_dict.items.grid.toggle_enable(item_fields[itm_f].fieldname, false);

        }

        for (var tf = 0; tf < tax_fields.length; tf++) {
            cur_frm.fields_dict.taxes.grid.toggle_enable(tax_fields[tf].fieldname, false);

        }
        for (var pf = 0; pf < payment_fields.length; pf++) {
            cur_frm.fields_dict.payment_schedule.grid.toggle_enable(payment_fields[pf].fieldname, false);

        }
    } else if (cur_frm.doc.under_review == 0) {
        var fields_name = get_fields(cur_frm.doc.doctype);
        var item_fields = "";
        var tax_fields = "";
        var payment_fields = "";
        for (var pf = 0; pf < fields_name.length; pf++) {
            cur_frm.set_df_property(fields_name[pf].fieldname, "read_only", 0);

            if (fields_name[pf].fieldname == "items") {
                var child_field = fields_name[pf].options;
                item_fields = get_fields(child_field);
            } else if (fields_name[pf].fieldname == "taxes") {
                var child_field = fields_name[pf].options;
                tax_fields = get_fields(child_field);
            } else if (fields_name[pf].fieldname == "payment_schedule") {
                var child_field = fields_name[pf].options;
                payment_fields = get_fields(child_field);
            }
        }
        for (var itm_f = 0; itm_f < item_fields.length; itm_f++) {
            cur_frm.fields_dict.items.grid.toggle_enable(item_fields[itm_f].fieldname, true);

        }

        for (var tf = 0; tf < tax_fields.length; tf++) {
            cur_frm.fields_dict.taxes.grid.toggle_enable(tax_fields[tf].fieldname, true);

        }
        for (var pf = 0; pf < payment_fields.length; pf++) {
            cur_frm.fields_dict.payment_schedule.grid.toggle_enable(payment_fields[pf].fieldname, true);

        }
    } else {
        cur_frm.refresh_fields();
    }
    cur_frm.set_query("control_bom", "items", function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var bom_list = [];
        console.log("Item Code:: " + d.item_code);
        frappe.call({
            method: "nhance.api.get_bom_list_for_so",
            args: {
                "item_code": d.item_code,
            },
            async: false,
            callback: function(r) {
                console.log("Length" + r.message.length);
                console.log("bom_list :" + bom_list);
                for (var i = 0; i < r.message.length; i++) {
                    console.log("r.message::" + r.message[i].name);
                    bom_list.push(r.message[i].name);
                    console.log("bom_list" + bom_list);
                }
            }
        });

        return {
            "filters": [
                ["BOM", "name", "in", bom_list]
            ]
        }

        refresh_field("control_bom");
        refresh_field("items");
    });

});
frappe.ui.form.on("Sales Order", "before_submit", function(cdt, cdn, frm) {
        var role = "SO Reviewer";
	var role_creator = "SO Creator";
	var role_overriter = "SO Overwriter";
        var check_role = get_roles(frappe.session.user, role);
        var check_role_creator = get_roles(frappe.session.user, role_creator);
        var check_role_overriter = get_roles(frappe.session.user, role_overriter);
	//console.log("check_role_overriter==============="+check_role_overriter.length);
	 var so_doctype = cur_frm.doc.doctype;
         var so_document_review = get_review_templates(so_doctype);
    
        if(so_document_review.length != 0){
	if (check_role_overriter.length == 0){
	  if(check_role_creator){
	    if (cur_frm.doc.so_reviewed){
		var removed_perm = remove_submit_permission_with_so(frappe.session.user,cur_frm.doc.so_reviewed,cur_frm.doc.name);
			//console.log("revierw--------------------"+removed_perm);
			if (removed_perm == false){
				frappe.validated = false;
			}
		}
	   else {
		if(cur_frm.doc.name){
			//console.log("hey i am here")
	    		var removed_perm = remove_submit_permission(frappe.session.user,cur_frm.doc.name);
			//console.log("creator--------------------"+removed_perm);
			if (removed_perm == false){
				frappe.validated = false;
			}
		}
	    }
	}
	else{
		 frappe.msgprint("Access Rights Error! You do not have permission to perform this operation!");
		frappe.validated = false;
		}
	}	
 }

})

function get_roles(user, role) {
    var purchase = "";
    frappe.call({
        method: "nhance.nhance.doctype.sales_order_review.sales_order_review.get_roles",
        args: {
            "user": user,
            "role": role
        },
        async: false,
        callback: function(r) {
            if (r.message.length > 0) {

                purchase = r.message[0].role;
            }
        }
    });
    return purchase;


}

function get_fields(doctype) {
    var fields = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.get_doc_details',
        args: {
            "doctype": doctype
        },
        async: false,
        callback: function(r) {
            fields = r.message;
        }
    });
    return fields;
}

function get_sales_order_review(name) {
    var sales_order_review = "";
    frappe.call({
        method: "nhance.nhance.doctype.sales_order_review.sales_order_review.get_sales_order_review",
        args: {
            "name": name
        },
        async: false,
        callback: function(r) {
            if (r.message) {

                sales_order_review = r.message
            }
        }
    });
    return sales_order_review;

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

function get_check_before_submit(doctype, name) {
    var doc_details = "";
    frappe.call({
        method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.get_check_before_submit',
        args: {
            "doctype": doctype,
            "name": name

        },
        async: false,
        callback: function(r) {
            doc_details = r.message;
        }
    });
    return doc_details;
}
function remove_submit_permission(user,name){
	 var remove_perm = "";
	    frappe.call({
		method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.remove_submit_permission',
		args: {
		    "user": user,
		    "name":name,
		},
		async: false,
		callback: function(r) {
		    remove_perm = r.message;
		}
	    });
	    return remove_perm;
}
function remove_submit_permission_with_so(user,so_reviewed,name){
	 var remove_perm = "";
	    frappe.call({
		method: 'nhance.nhance.doctype.sales_order_review.sales_order_review.remove_submit_permission_with_so',
		args: {
		    "user": user,
		    "so_reviewed":so_reviewed,
		    "name":name
		},
		async: false,
		callback: function(r) {
		    remove_perm = r.message;
		}
	    });
	    return remove_perm;
}


//SMS sending
frappe.ui.form.on("Sales Order", "refresh", function(frm, cdt, cdn) {
    console.log("Entered------");
    var d = locals[cdt][cdn];
    var customer = d.customer;
    console.log("customer", customer);
    var name=frm.doc.name;
    console.log("name",name);
    var so_status=frm.doc.so_status;
    console.log("so_status",so_status);
    
    var salutation_of_customer = fetch_salutation_id(customer);
    console.log("salutation_of_customer", salutation_of_customer);
    
    var send_sms_to_customer = fetch_do_not_sms(customer);
    console.log("send_sms_to_customer", send_sms_to_customer);
    
    if(send_sms_to_customer===0){
console.log("message will send to this customer");
    
   var message1;
   if(so_status==="Dispatched" || so_status==="Production Complete" || so_status==="Production - Coloring" || so_status==="Production - Pre-Assembly" || so_status==="Production - Welding" || so_status==="Production - Bending" || so_status==="Production - Cutting" || so_status==="Production Drawing"){
     console.log("entered in if");
     message1 ='Hi '+salutation_of_customer+' '+frm.doc.customer+'%nFollowing is the status of order %nOrder number:'+frm.doc.name+'%nProject Status:'+frm.doc.so_status+'%nThank you';
     console.log("message1",message1);
     var apikey='+kEqIhqpZYo-dOuC4UVnZgSMbGLJNlFX4lWiNA67iJ';
     var sender='CRMTCA';
     var numbers=fetch_mobile_no(customer);
    console.log("numbers",numbers);
      var message_sent=send_sms(apikey,numbers,sender,message1);
     console.log("message_sent",message_sent);
     
}else if(so_status==="Installation in Process"){
     console.log("entered in else if");
    
     message1 ='Hi '+salutation_of_customer+' '+frm.doc.customer+'%nAs scheduled our team will be present at you site for first phase of installation.Your presence at the site is kindly requested. For further information, feel free to contact us at +91 76187 78067.';
     console.log("message1",message1);
     var apikey='+kEqIhqpZYo-dOuC4UVnZgSMbGLJNlFX4lWiNA67iJ';
     var sender='CRMTCA';
     var numbers=fetch_mobile_no(customer);
    console.log("numbers",numbers);
     var message_sent=send_sms(apikey,numbers,sender,message1);
     console.log("message_sent",message_sent);
   }
   else if(so_status==="Financial Clearance Obtained"){
     console.log("entered in Financial Clearance Obtained");
    
     message1 ='Hi '+salutation_of_customer+' '+frm.doc.customer+'%nWe are delighted to inform you that your project has been cleared for manufacturing. Order number:'+frm.doc.name+'%nProject Status :'+frm.doc.so_status+'%nThank you';
     console.log("message1",message1);
     var apikey='+kEqIhqpZYo-dOuC4UVnZgSMbGLJNlFX4lWiNA67iJ';
     var sender='CRMTCA';
     var numbers=fetch_mobile_no(customer);
    console.log("numbers",numbers);
      var message_sent=send_sms(apikey,numbers,sender,message1);
     console.log("message_sent",message_sent);
   }  
   
    }//end of sent to sms if block
   else{
console.log("message will not send to this customer");
}
    
});
function fetch_salutation_id(customer) {
    console.log("entered into function");
    var salutation = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Customer',
            'fieldname': 'salutation',

            'filters': {
                customer_name: customer,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                salutation = r.message.salutation;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return salutation
}

function fetch_do_not_sms(customer) {
    console.log("entered into function");
    var do_not_sms = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Customer',
            'fieldname': 'do_not_sms',

            'filters': {
                customer_name: customer,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                do_not_sms = r.message.do_not_sms;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return do_not_sms
}

function fetch_mobile_no(customer) {
    console.log("entered into fetch_mobile_no function");
    var mobile_no = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Customer',
            'fieldname': 'mobile_no',

            'filters': {
                customer_name: customer,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                mobile_no = r.message.mobile_no;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return mobile_no
}


function send_sms(apikey,numbers,sender,message1) {
    console.log("entered into function");
     frappe.call({
    method: "ashirwad.api.sendSMS",
    args: {
      "apikey": apikey,
      "numbers":numbers,
       "sender":sender,
       "message":message1
    },
    callback: function(r) {
      if(r.exc) {
       msgprint(r.exc);
     
      console.log("message");
       return;
      }
    }
  });
}  


