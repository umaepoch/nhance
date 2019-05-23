// Copyright (c) 2019, Epoch and contributors
// For license information, please see license.txt
frappe.ui.form.on('Document Review Details', {
    refresh: function(frm) {
        if (cur_frm.doc.__islocal) {
            console.log("doc name =======" + cur_frm.doc.doctype_name);
            /*
            if(cur_frm.doc.doctype_name == "Sales Order"){
            		document_template_name = get_document_template_name(cur_frm.doc.doctype_name);
            		//console.log("document_template_name=========="+JSON.stringify(document_template_name));
            	}*/
            var fields = [];
            var msg = {
                "label": "Please Select Document Template for Review",
                "fieldname": "tax_level_fields1",
                "fieldtype": "Section Break"
            }
            var data = {
                "label": "Template Name",
                "fieldname": "template_name",
                "fieldtype": "Link",
                "options": "Document Review Templates",
                "get_query": function() {
                    var docName = cur_frm.doc.doctype_name;


                    return {
                        "doctype": "Document Review Templates",
                        "filters": {
                            "doc_type": docName
                        }
                    }
                }

            }
            fields.push(msg);
            fields.push(data);
            var dialog = new frappe.ui.Dialog({
                // msgprint("Please Select Document Template Want to Reveiew");
                'fields': fields,
                primary_action: function() {
                    dialog.hide();
                    var dialog_json = dialog.get_values();
                    Object.keys(dialog_json).forEach(function(key) {
                        console.log("selected fields ===========" + dialog_json[key]);
                        var document_review_template_fields = "";
                        var sales_order_values = "";
                        if (cur_frm.doc.doctype_name == "Sales Order") {
                            if (cur_frm.doc.doctype_name != undefined && cur_frm.doc.doctype_name != "") {
                                //  console.log("doctype name=========" + cur_frm.doc.sales_order)
                                document_review_template_fields = get_fields_of_document_review(dialog_json[key]);
                                //   console.log("fieldssssss======"+JSON.stringify(document_review_template_fields));
                            }
                            if (cur_frm.doc.sales_order != undefined && cur_frm.doc.sales_order != "") {

                                sales_order_values = get_sales_order_details(cur_frm.doc.sales_order, cur_frm.doc.doctype_name);
                                //console.log("fieldssssss======"+JSON.stringify(sales_order_values));
                            }
                        } else if (cur_frm.doc.doctype_name == "Purchase Order") {
                            if (cur_frm.doc.doctype_name != undefined && cur_frm.doc.doctype_name != "") {
                                // console.log("doctype name=========" + cur_frm.doc.purchase_order)
                                document_review_template_fields = get_fields_of_document_review(dialog_json[key]);
                                //   console.log("fieldssssss======"+JSON.stringify(document_review_template_fields));
                            }
                            if (cur_frm.doc.purchase_order != undefined && cur_frm.doc.purchase_order != "") {

                                sales_order_values = get_sales_order_details(cur_frm.doc.purchase_order, cur_frm.doc.doctype_name);
                                //console.log("fieldssssss======"+JSON.stringify(sales_order_values));
                            }
                        }


                        var order = sales_order_values['order'];
                        var items_details = sales_order_values['item'];
                        var taxes = sales_order_values['taxes'];
                        var tax_list = [];
                        for (var i = 0; i < document_review_template_fields.length; i++) {

                            if (document_review_template_fields[i].field_label == "Parent Field") {
                                for (var j = 0; j < order.length; j++) {
                                    var values_d = order[j];
                                    Object.keys(values_d).forEach(function(key) {
                                        if (document_review_template_fields[i].fieldname == key) {
                                            //console.log("review parameters"+document_review_template_fields[i].review_parameters);
                                            if (values_d[key] != null && values_d[key] != 0) {
                                                var child = cur_frm.add_child("document_fields");
                                                frappe.model.set_value(child.doctype, child.name, "field_name", document_review_template_fields[i].label);

                                                frappe.model.set_value(child.doctype, child.name, "values", values_d[key]);
                                                frappe.model.set_value(child.doctype, child.name, "review_parameter", document_review_template_fields[i].review_parameters);
                                                //console.log("fieldtype========"+document_review_template_fields[i].fieldtype);
                                                frappe.model.set_value(child.doctype, child.name, "field_type", document_review_template_fields[i].fieldtype);
                                                frappe.model.set_value(child.doctype, child.name, "field_label", document_review_template_fields[i].field_label);
                                                if (document_review_template_fields[i].fieldtype == "Link") {
                                                    frappe.model.set_value(child.doctype, child.name, "document_type", document_review_template_fields[i].options);
                                                }
                                                cur_frm.refresh_field('document_fields');
                                            }

                                        }
                                    })

                                }

                            } else if (document_review_template_fields[i].field_label == "Item Field") {
                                for (var j = 0; j < items_details.length; j++) {
                                    var values_d = items_details[j];
                                    Object.keys(values_d).forEach(function(key) {
                                        if (document_review_template_fields[i].fieldname == key) {
                                            if (values_d[key] != null && values_d[key] != 0) {
                                                var child = cur_frm.add_child("document_fields");
                                                frappe.model.set_value(child.doctype, child.name, "field_name", document_review_template_fields[i].label);

                                                frappe.model.set_value(child.doctype, child.name, "values", values_d[key]);
                                                frappe.model.set_value(child.doctype, child.name, "review_parameter", document_review_template_fields[i].review_parameters);
                                                //console.log("fieldtype========"+document_review_template_fields[i].fieldtype);
                                                frappe.model.set_value(child.doctype, child.name, "field_type", document_review_template_fields[i].fieldtype);
                                                frappe.model.set_value(child.doctype, child.name, "field_label", document_review_template_fields[i].field_label);
                                                if (document_review_template_fields[i].fieldtype == "Link") {
                                                    frappe.model.set_value(child.doctype, child.name, "document_type", document_review_template_fields[i].options);
                                                }
                                                cur_frm.refresh_field('document_fields');
                                            }
                                        }
                                    })
                                }
                            } else if (document_review_template_fields[i].field_label == "Tax Field") {
                                for (var j = 0; j < taxes.length; j++) {
                                    var values_d = taxes[j];
                                    Object.keys(values_d).forEach(function(key) {
                                        if (document_review_template_fields[i].fieldname == key) {
                                            if (values_d[key] != null && values_d[key] != 0 && !tax_list.includes(key)) {
                                                tax_list.push(key);
                                                console.log("key===========" + key);
                                                var child = cur_frm.add_child("document_fields");
                                                frappe.model.set_value(child.doctype, child.name, "field_name", document_review_template_fields[i].label);

                                                frappe.model.set_value(child.doctype, child.name, "values", values_d[key]);
                                                frappe.model.set_value(child.doctype, child.name, "review_parameter", document_review_template_fields[i].review_parameters);
                                                //console.log("fieldtype========"+document_review_template_fields[i].fieldtype);
                                                frappe.model.set_value(child.doctype, child.name, "field_type", document_review_template_fields[i].fieldtype);
                                                frappe.model.set_value(child.doctype, child.name, "field_label", document_review_template_fields[i].field_label);
                                                if (document_review_template_fields[i].fieldtype == "Link") {
                                                    frappe.model.set_value(child.doctype, child.name, "document_type", document_review_template_fields[i].options);
                                                }
                                                cur_frm.refresh_field('document_fields');
                                            }
                                        }
                                    })
                                }
                            }
                        }
                    })
                }
            })

            dialog.show();
            var document_review_template_fields = "";
            var sales_order_values = "";
            if (cur_frm.doc.doctype_name == "Sales Order") {
                if (cur_frm.doc.doctype_name != undefined && cur_frm.doc.doctype_name != "") {
                    //  console.log("doctype name=========" + cur_frm.doc.sales_order)
                    document_review_template_fields = get_fields_of_document_review(cur_frm.doc.doctype_name);
                    //   console.log("fieldssssss======"+JSON.stringify(document_review_template_fields));
                }
                if (cur_frm.doc.sales_order != undefined && cur_frm.doc.sales_order != "") {

                    sales_order_values = get_sales_order_details(cur_frm.doc.sales_order, cur_frm.doc.doctype_name);
                    //console.log("fieldssssss======"+JSON.stringify(sales_order_values));
                }
            } else if (cur_frm.doc.doctype_name == "Purchase Order") {
                if (cur_frm.doc.doctype_name != undefined && cur_frm.doc.doctype_name != "") {
                    // console.log("doctype name=========" + cur_frm.doc.purchase_order)
                    document_review_template_fields = get_fields_of_document_review(cur_frm.doc.doctype_name);
                    //   console.log("fieldssssss======"+JSON.stringify(document_review_template_fields));
                }
                if (cur_frm.doc.purchase_order != undefined && cur_frm.doc.purchase_order != "") {

                    sales_order_values = get_sales_order_details(cur_frm.doc.purchase_order, cur_frm.doc.doctype_name);
                    //console.log("fieldssssss======"+JSON.stringify(sales_order_values));
                }
            }


            var order = sales_order_values['order'];
            var items_details = sales_order_values['item'];
            var taxes = sales_order_values['taxes'];
            var tax_list = [];
            for (var i = 0; i < document_review_template_fields.length; i++) {

                if (document_review_template_fields[i].field_label == "Parent Field") {
                    for (var j = 0; j < order.length; j++) {
                        var values_d = order[j];
                        Object.keys(values_d).forEach(function(key) {
                            if (document_review_template_fields[i].fieldname == key) {
                                //console.log("review parameters"+document_review_template_fields[i].review_parameters);
                                if (values_d[key] != null && values_d[key] != 0) {
                                    var child = cur_frm.add_child("document_fields");
                                    frappe.model.set_value(child.doctype, child.name, "field_name", document_review_template_fields[i].label);

                                    frappe.model.set_value(child.doctype, child.name, "values", values_d[key]);
                                    frappe.model.set_value(child.doctype, child.name, "review_parameter", document_review_template_fields[i].review_parameters);
                                    //console.log("fieldtype========"+document_review_template_fields[i].fieldtype);
                                    frappe.model.set_value(child.doctype, child.name, "field_type", document_review_template_fields[i].fieldtype);
                                    frappe.model.set_value(child.doctype, child.name, "field_label", document_review_template_fields[i].field_label);
                                    if (document_review_template_fields[i].fieldtype == "Link") {
                                        frappe.model.set_value(child.doctype, child.name, "document_type", document_review_template_fields[i].options);
                                    }
                                    cur_frm.refresh_field('document_fields');
                                }

                            }
                        })

                    }

                } else if (document_review_template_fields[i].field_label == "Item Field") {
                    for (var j = 0; j < items_details.length; j++) {
                        var values_d = items_details[j];
                        Object.keys(values_d).forEach(function(key) {
                            if (document_review_template_fields[i].fieldname == key) {
                                if (values_d[key] != null && values_d[key] != 0) {
                                    var child = cur_frm.add_child("document_fields");
                                    frappe.model.set_value(child.doctype, child.name, "field_name", document_review_template_fields[i].label);

                                    frappe.model.set_value(child.doctype, child.name, "values", values_d[key]);
                                    frappe.model.set_value(child.doctype, child.name, "review_parameter", document_review_template_fields[i].review_parameters);
                                    //console.log("fieldtype========"+document_review_template_fields[i].fieldtype);
                                    frappe.model.set_value(child.doctype, child.name, "field_type", document_review_template_fields[i].fieldtype);
                                    frappe.model.set_value(child.doctype, child.name, "field_label", document_review_template_fields[i].field_label);
                                    if (document_review_template_fields[i].fieldtype == "Link") {
                                        frappe.model.set_value(child.doctype, child.name, "document_type", document_review_template_fields[i].options);
                                    }
                                    cur_frm.refresh_field('document_fields');
                                }
                            }
                        })
                    }
                } else if (document_review_template_fields[i].field_label == "Tax Field") {
                    for (var j = 0; j < taxes.length; j++) {
                        var values_d = taxes[j];
                        Object.keys(values_d).forEach(function(key) {
                            if (document_review_template_fields[i].fieldname == key) {
                                if (values_d[key] != null && values_d[key] != 0 && !tax_list.includes(key)) {
                                    tax_list.push(key);
                                    console.log("key===========" + key);
                                    var child = cur_frm.add_child("document_fields");
                                    frappe.model.set_value(child.doctype, child.name, "field_name", document_review_template_fields[i].label);

                                    frappe.model.set_value(child.doctype, child.name, "values", values_d[key]);
                                    frappe.model.set_value(child.doctype, child.name, "review_parameter", document_review_template_fields[i].review_parameters);
                                    //console.log("fieldtype========"+document_review_template_fields[i].fieldtype);
                                    frappe.model.set_value(child.doctype, child.name, "field_type", document_review_template_fields[i].fieldtype);
                                    frappe.model.set_value(child.doctype, child.name, "field_label", document_review_template_fields[i].field_label);
                                    if (document_review_template_fields[i].fieldtype == "Link") {
                                        frappe.model.set_value(child.doctype, child.name, "document_type", document_review_template_fields[i].options);
                                    }
                                    cur_frm.refresh_field('document_fields');
                                }
                            }
                        })
                    }
                }
            }

        }
    }
});

frappe.ui.form.on("Document Review Details", "refresh", function(frm, cdt, cdn) {
    var docName = "New Document Fields";
    var fields_details = function_doc_details(docName);
    for (var i = 0; i < fields_details.length; i++) {
        if (fields_details[i].fieldname == "field_name" || fields_details[i].fieldname == "values" || fields_details[i].fieldname == "review_parameter" || fields_details[i].fieldname == "field_label") {
            cur_frm.fields_dict.document_fields.grid.toggle_enable(fields_details[i].fieldname, false);
        }
    }
});

function get_fields_of_document_review(docName) {
    var docFields = "";
    frappe.call({
        method: "nhance.nhance.doctype.document_review_details.document_review_details.get_fields_details",
        args: {
            "docName": docName
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                docFields = r.message
            }
        } //end of call back
    }); // end of frappe call
    return docFields;

}

function get_sales_order_details(docIds, docName) {
    var docDetails = "";
    frappe.call({
        method: "nhance.nhance.doctype.document_review_details.document_review_details.get_sales_order_details",
        args: {
            "docIds": docIds,
            "docName": docName
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                docDetails = r.message
            }
        } //end of call back
    }); // end of frappe call
    return docDetails;

}

function get_expense_account(label) {
    //console.log("function label=========" + label);
    var expense_account = [];
    frappe.call({
        method: 'nhance.nhance.doctype.document_review_details.document_review_details.get_name',
        args: {
            "DocName": label
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                for (var i = 0; i < r.message.length; i++) {
                    var record = r.message[i]['name'];
                    // console.log("record ===========" + record);
                    expense_account.push(record);
                }
            } else {
                expense_account = null;
            }

        } //end of callback fun..
    }); //end of frappe call..
    return expense_account;
}

function function_doc_details(doctype) {
    var supplier_criticality = "";
    frappe.call({
        method: 'nhance.nhance.doctype.document_review_details.document_review_details.get_doc_fields',
        args: {
            "doctype": doctype

        },
        async: false,
        callback: function(r) {
            // console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}

function get_document_template_name(doctype_name) {
    var document_name = [];
    var expense_account = ""
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: "Document Review Templates",
            filters: {
                doc_type: ["=", doctype_name]
            },

            fieldname: ["name"]
        },
        async: false,

        callback: function(r) {
            if (r.message) {
                expense_account = r.message;
                for (var i = 0; i < expense_account.length; i++) {
                    document_name.push(expense_account[i]['name']);
                }
            } else {
                expense_account = null;
            }

        } //end of callback fun..
    }); //end of frappe call..
    return document_name;
}
