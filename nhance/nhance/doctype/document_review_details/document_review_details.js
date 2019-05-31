// Copyright (c) 2019, Epoch and contributors
// For license information, please see license.txt
var doc_name_value = "";
var doc_id_value = "";
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
          //  fields.push(msg);
            fields.push(data);
            console.log("document type=========="+cur_frm.doc.doctype_name);
           if (cur_frm.doc.doctype_name != undefined && cur_frm.doc.doctype_name != "") {
            var dialog = new frappe.ui.Dialog({
                // msgprint("Please Select Document Template Want to Reveiew");
                 title: __("Please Select Document Template Want to Reveiew"),
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
          }else if(cur_frm.doc.doctype_name == undefined){
            //var fields1 = [];
            var selected_doc_name = "";
            /*
            var msg1 = {
                "label": "Please Select Document Template for Review",
                "fieldname": "tax_level_fields1",
                "fieldtype": "Section Break"
            }
            var data1 = [{
                "label": "Doc Name",
                "fieldname": "doc_name",
                "fieldtype": "Link",
                "options": DocType,
                "onchange": function(e) {
                    selected_doc_name = this.value;
                }
            },
            {
              "label": "Doc Id",
              "fieldname": "doc_id",
              "fieldtype":"Dynamic Link"
              "options": "doc_name"
            },
            {
              "label": "Templates Name",
              "fieldname": "templates_name",
              "fieldtype": "Link",
              "options": "Document Review Templates",
              "get_query": function() {
                  var docName = selected_doc_name;


                  return {
                      "doctype": "Document Review Templates",
                      "filters": {
                          "doc_type": docName
                      }
                  }
              }
            }
          ]
            fields1.push(msg1);
            fields1.push(data1);*/
            var dialogs = new frappe.ui.Dialog({
                 title: __("Select All Details For Document Review"),
              'fields' :[
                {
                  "label": "Doc Name",
                  "fieldname": "doc_name",
                  "fieldtype": "Link",
                  "options": "DocType",
                  "reqd":1,
                  "onchange": function(e) {
                      selected_doc_name = this.value;

                  }
              },
              {
                "label": "Doc Id",
                "fieldname": "doc_id",
                "fieldtype":"Dynamic Link",
                "options": "doc_name",
                "reqd":1,
                "get_query": function() {
                    return {
                        "doctype": selected_doc_name,
                        "filters": {
                            "docstatus": 0
                        }
                    }
                }

              },
              {
                "label": "Templates Name",
                "fieldname": "templates_name",
                "fieldtype": "Link",
                "reqd":1,
                "options": "Document Review Templates",
                "get_query": function() {
                    var docName = selected_doc_name;
                    return {
                        "doctype": "Document Review Templates",
                        "filters": {
                            "doc_type": docName
                        }
                    }
                }
              }
              ],
              primary_action: function() {
                    console.log(JSON.stringify(dialogs.get_values()));
                    var get_dialog_values = dialogs.get_values();
                     doc_name_value = get_dialog_values['doc_name'];
                     doc_id_value = get_dialog_values['doc_id'];
                     cur_frm.set_value("doc_name",doc_name_value);
                     cur_frm.set_value("doc_ids",doc_id_value);
                    var template_name_value = get_dialog_values['templates_name'];
                    var document_review_template_fields = get_fields_of_document_review(template_name_value);
                    var source_doctype_values = get_sales_order_details(doc_id_value,doc_name_value);
                    var order = source_doctype_values['order'];
                    var items_details = source_doctype_values['item'];
                    var taxes = source_doctype_values['taxes'];
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
                                           // console.log("key===========" + key);
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
                    dialogs.hide();
              }
            })
            dialogs.show();
          }
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
                                   // console.log("key===========" + key);
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
    },
    before_save:function(frm, cdt , cdn){
      var source_docIds = "";
      var source_docname = ""
      if(cur_frm.doc.doctype_name != undefined){
      if(cur_frm.doc.doctype_name == "Sales Order"){
        source_docIds = cur_frm.doc.sales_order;
        source_docname = cur_frm.doc.doctype_name;
        }
      else if(cur_frm.doc.doctype_name == "Purchase Order"){
        source_docIds = cur_frm.doc.purchase_order;
        source_docname = cur_frm.doc.doctype_name;
        }
      }else if(cur_frm.doc.doctype_name == undefined){
        source_docIds =  cur_frm.doc.doc_ids;
        source_docname = cur_frm.doc.doc_name;

      }
      console.log("source_docname==========="+source_docname);
      console.log("source_docIds==========="+source_docIds);
      under_review_check(source_docname,source_docIds);

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
frappe.ui.form.on("Document Review Details", "before_save", function(frm, cdt, cdn) {
  console.log("before save");
  /*
  var source_docIds = "";
  var source_docname = ""
  if(cur_frm.doc.doctype_name != undefined){
  if(cur_frm.doc.doctype_name == "Sales Order"){
    source_docIds = cur_frm.doc.sales_order;
    source_docname = cur_frm.doc.doctype_name;
    }
  else if(cur_frm.doc.doctype_name == "Purchase Order"){
    source_docIds = cur_frm.doc.purchase_order;
    source_docname = cur_frm.doc.doctype_name;
    }
  }else if(cur_frm.doc.doctype_name != undefined){
    source_docIds = doc_name_value;
    source_docname = doc_id_value;

  }
  console.log("source_docname==========="+source_docname);
  console.log("source_docIds==========="+source_docIds);
  under_review_check(source_docname,source_docIds);
*/
});
frappe.ui.form.on("Document Review Details", "on_submit", function(frm, cdt, cdn) {
	console.log("cur_frm.doc.doctype_name============="+cur_frm.doc.doctype_name);

	var source_docIds = "";
  var source_docname = ""
  if(cur_frm.doc.doctype_name != undefined){
	if(cur_frm.doc.doctype_name == "Sales Order"){
		source_docIds = cur_frm.doc.sales_order;
    source_docname = cur_frm.doc.doctype_name;
		}
	else if(cur_frm.doc.doctype_name == "Purchase Order"){
		source_docIds = cur_frm.doc.purchase_order;
    source_docname = cur_frm.doc.doctype_name;
		}
  }else if(cur_frm.doc.doctype_name == undefined){
    source_docIds = cur_frm.doc.doc_ids;
    source_docname = cur_frm.doc.doc_name;

  }
	console.log("source_docname==========="+source_docname);
	function_make_uncheck(source_docname,source_docIds);

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
function function_make_uncheck(doctype_name,source_docname){
	  frappe.call({
        method: 'nhance.nhance.doctype.document_review_details.document_review_details.get_uncheck_box_cheched',
        args: {
            "doctype": doctype_name,
	     "source_docname":source_docname

        },
        async: false,
        callback: function(r) {
            // console.log("supplier criticality..." + JSON.stringify(r.message));
           // supplier_criticality = r.message;
        }
    });
   // return supplier_criticality;
}
function under_review_check(doctype,name){
    frappe.call({
        method: 'nhance.nhance.doctype.document_review_details.document_review_details.get_check_box_cheched',
        args: {
	    "doctype":doctype,
            "name":name
        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
           // supplier_criticality = r.message;
        }
    });
   // return supplier_criticality;
}
