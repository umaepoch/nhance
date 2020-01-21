frappe.ui.form.on("Purchase Order", "refresh", function(frm, cdt, cdn) {
    if (cur_frm.doc.status == "Draft") {
        var role = "PO Reviewer";
        var check_role = get_roles(frappe.session.user, role);
       // console.log("check_role------------" + check_role)
        cur_frm.add_custom_button(__('Make Purchase Order Review'), function() {
            //under_review_check(cur_frm.doc.doctype,cur_frm.doc.name);
            if (check_role != "" && check_role != undefined) {
                frappe.model.open_mapped_doc({
                    method: "nhance.nhance.doctype.purchase_order_review.purchase_order_review.make_purchase_order_review",
                    frm: cur_frm
                })
            } else {
                frappe.msgprint(frappe.session.user + " Don't have permission " + role + " to create Purchase Order Review");
            }
        });
    }

    if (cur_frm.doc.under_review == 1) {
        var fields_name = get_fields(cur_frm.doc.doctype);
        var item_fields = "";
        var tax_fields = "";
        var payment_fields = "";
      //  console.log("cur_frm.doc.doctype-----------");
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
    }

});

function get_roles(user, role) {
    var purchase = "";
    frappe.call({
        method: "nhance.nhance.doctype.purchase_order_review.purchase_order_review.get_roles",
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
