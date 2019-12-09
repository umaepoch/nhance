// Copyright (c) 2019, Epoch and contributors
// For license information, please see license.txt
frappe.ui.form.on('Document Review Templates', {
	refresh: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var doctype = "";
	console.log("stutas ==========="+cur_frm.doc.status);
	if (d.doc_type != "" && d.doc_type != undefined) {
            doctype = d.doc_type;
	    
        }
        var child_doctype = doctype.toString() + " Item";
	if(cur_frm.doc.__islocal){
       // if (cur_frm.docstatus != 1 && cur_frm.status != "Draft") {
            //cur_frm.set_df_property("items_section", "hidden", true);
            //cur_frm.set_df_property("taxes_section", "hidden", true);
            console.log("doctyep------------" + cur_frm.doc.doctype);
            var cur_doctype = cur_frm.doc.doctype;
            var current_doc = function_doc_details(cur_doctype);
	     
            var child_fields = "";
            var child_doc = "";
            var child_doc1 = "";
	
            for (var i = 0; i < current_doc.length; i++) {
                if (current_doc[i].fieldname != "pull" && current_doc[i].fieldname != "doc_type") {
                    
                        cur_frm.set_df_property(current_doc[i].fieldname, "hidden", true);
                    }
            }
        }
	},
	pull: function(frm, cdt, cdn) {

        console.log("clicked----");
        var d = locals[cdt][cdn];
        var doctype = d.doc_type;
        var child_doc_fields = "";
        var child_doc_fields1 = "";
        var child_taxes_fields = "";
        var child_taxes_fields1 = "";
        var cur_doctype = cur_frm.doc.doctype;
	var cur_name = cur_frm.doc.name;
	console.log("current docname ========"+cur_name);
	var current_doc_detials = "";
	if(cur_name != undefined){
	 	current_doc_detials = get_current_doc_details(cur_name);
	}
        var current_doc = function_doc_details(cur_doctype);
	
            for (var i = 0; i < current_doc.length; i++) {
              
                    if (current_doc[i].fieldname == "fields_descriptions" || current_doc[i].fieldname == "fields_details_section") {
			console.log(current_doc[i].fieldname);
                        cur_frm.set_df_property(current_doc[i].fieldname, "hidden", false);
                    }
              
		 
            }
        var doc_details = function_doc_details(doctype);
	for(var doc =0; doc < doc_details.length; doc++){
	  if (doc_details[doc].fieldname == "items") {
                    var child_doc = doc_details[doc].options;
                    child_doc_fields = function_doc_details(child_doc);
	}else if(doc_details[doc].fieldname == "taxes") {
                    var child_doc = doc_details[doc].options;
                    child_taxes_fields = function_doc_details(child_doc);
		}
	}
        var fields = [];
        var items = "";
        var taxes = "";
        var field_index = 42;
	var select_all = {
		"fieldtype": "Check",
                "label": "Select All",
                "fieldname": "select_all"
		}
	 fields.push(select_all);
	 var section = {
            "label": "Parent Doc Fields",
            "fieldname": "parent_level_fields",
            "fieldtype": "Section Break",
            "collapsible": "1",
            "bold": 1
        }
        fields.push(section);
        for (var i = 0; i < doc_details.length; i++) {
            if (doc_details[i].label == "Items") {
                items = get_doc_items_details(doc_details[i].options);

            }
		
            if (doc_details[i].fieldname == "taxes") {
                taxes = get_doc_items_details(doc_details[i].options);
                //console.log("taxes---------------"+taxes);
            }
            var fieldtype = (doc_details[i].fieldtype || "");
            if (doc_details[i].label != "" && doc_details[i].label != undefined) {
                if (fieldtype != "Column Break" && fieldtype != "Section Break" && fieldtype != "Button" && fieldtype != "Code" && fieldtype != "Table"  && fieldtype != "Text") {
                    if (i != field_index) {
                        //console.log("fieldtype --=----------"+doc_details[i].fieldtype);
                        var data = {
                            "fieldtype": "Check",
                            "label": doc_details[i].label,
                            "fieldname": doc_details[i].fieldname
                        }
                        fields.push(data);
                    } else if (i == field_index) {
                        field_index += field_index;
                        var data = {
                            "fieldtype": "Check",
                            "label": doc_details[i].label,
                            "fieldname": doc_details[i].fieldname
                        }
                        var column = {
                            "fieldtype": "Column Break",
                            "fieldname": "column_break" + i + ""
                        }
                        //data.append(column);
                        fields.push(data);
                        fields.push(column);
                    }


                }
            }
        }
	
        var section = {
            "label": "Doc Item Fields",
            "fieldname": "item_level_fields",
            "fieldtype": "Section Break",
            "collapsible": "1",
            "bold": 1
        }
        fields.push(section);
	
        var item_index = 15;
        for (var i = 0; i < items.length; i++) {
            var item_fieldtype = (items[i].fieldtype || "");
            if (items[i].label != "" && items[i].label != undefined) {
                if (item_fieldtype != "Column Break" && item_fieldtype != "Small Text" && item_fieldtype != "Section Break" && item_fieldtype != "Section Break" && item_fieldtype != "Button" && item_fieldtype != "Code" && item_fieldtype != "Table" && item_fieldtype != "Text Editor" && fieldtype != "Text") {
                    if (i != item_index) {
                        var data = {
                            "fieldtype": "Check",
                            "label": items[i].label,
                            "fieldname": items[i].fieldname

                        }
                        fields.push(data);
                    } else if (i == item_index) {
                        item_index += item_index;
                        var data = {
                            "fieldtype": "Check",
                            "label": items[i].label,
                            "fieldname": items[i].fieldname

                        }
                        fields.push(data);
                        var column = {
                            "fieldtype": "Column Break",
                            "fieldname": "column_break" + i + ""
                        }
                        fields.push(column);
                    }
                }
            }
        }
        var section1 = {
            "label": "Doc Taxes Fields",
            "fieldname": "tax_level_fields1",
            "fieldtype": "Section Break",
            "collapsible": "1",
            "bold": 1
        }
        fields.push(section1);
        var tax_index = 6;
        for (var i = 0; i < taxes.length; i++) {
            var item_fieldtype = (taxes[i].fieldtype || "");
            if (taxes[i].label != "" && taxes[i].label != undefined) {
                if (item_fieldtype != "Column Break" && item_fieldtype != "Small Text" && item_fieldtype != "Section Break" && item_fieldtype != "Section Break" && item_fieldtype != "Button" && item_fieldtype != "Code" && item_fieldtype != "Table" && item_fieldtype != "Text Editor" && fieldtype != "Text") {
                    if (i != tax_index) {
                        var data = {
                            "fieldtype": "Check",
                            "label": taxes[i].label,
                            "fieldname": taxes[i].fieldname

                        }
                        fields.push(data);
                    } else if (i == tax_index) {
                        tax_index += tax_index;
                        var data = {
                            "fieldtype": "Check",
                            "label": taxes[i].label,
                            "fieldname": taxes[i].fieldname

                        }
                        fields.push(data);
                        var column = {
                            "fieldtype": "Column Break",
                            "fieldname": "column_break" + i + ""
                        }
                       fields.push(column);
                        //fields.push(data);

                    }
                }
            }
        }
        var d = new frappe.ui.Dialog({

            'fields': fields,
            primary_action: function() {

                d.hide();
		var fields_details = "";
		
               var dialog_json = d.get_values();
               // console.log(JSON.stringify(dialog_json));
                Object.keys(dialog_json).forEach(function(key) {
                    // console.table("in dialog box==="+JSON.stringify(doc_details));
                    if (dialog_json[key] == 1) {
			
                        //key = key.charAt(0).toUpperCase() + key.slice(1);
                        // console.log(key);
			if(cur_frm.doc.__islocal){
			for(var doc_d =0; doc_d < doc_details.length; doc_d++){
			    if(doc_details[doc_d].fieldname == key){
				var child = cur_frm.add_child("fields_descriptions");
				frappe.model.set_value(child.doctype, child.name, "label", doc_details[doc_d].label);
				frappe.model.set_value(child.doctype, child.name, "field_label", "Parent Field");
				frappe.model.set_value(child.doctype, child.name, "fieldtype", doc_details[doc_d].fieldtype);
				frappe.model.set_value(child.doctype, child.name, "fieldname", doc_details[doc_d].fieldname);
				frappe.model.set_value(child.doctype, child.name, "options", doc_details[doc_d].options);
				cur_frm.refresh_field('fields_descriptions');
				}
					
			}
			for(var child_d = 0; child_d < child_doc_fields.length; child_d++){
				if(child_doc_fields[child_d].fieldname == key){
				var child = cur_frm.add_child("fields_descriptions");
				frappe.model.set_value(child.doctype, child.name, "label", child_doc_fields[child_d].label);
				frappe.model.set_value(child.doctype, child.name, "field_label", "Item Field");
				frappe.model.set_value(child.doctype, child.name, "fieldtype", child_doc_fields[child_d].fieldtype);
				frappe.model.set_value(child.doctype, child.name, "fieldname", child_doc_fields[child_d].fieldname);
				frappe.model.set_value(child.doctype, child.name, "options", child_doc_fields[child_d].options);
				cur_frm.refresh_field('fields_descriptions');
				
					}
			
				}
			for(var tax_d = 0; tax_d < child_taxes_fields.length; tax_d++){
				if(child_taxes_fields[tax_d].fieldname == key){
				var child = cur_frm.add_child("fields_descriptions");
				frappe.model.set_value(child.doctype, child.name, "label", child_taxes_fields[tax_d].label);
				frappe.model.set_value(child.doctype, child.name, "field_label", "Tax Field");
				frappe.model.set_value(child.doctype, child.name, "fieldtype", child_taxes_fields[tax_d].fieldtype);
				frappe.model.set_value(child.doctype, child.name, "fieldname", child_taxes_fields[tax_d].fieldname);
				frappe.model.set_value(child.doctype, child.name, "options", child_taxes_fields[tax_d].options);
				cur_frm.refresh_field('fields_descriptions');
				
					}
				}
		}
		if(!cur_frm.doc.__islocal){
			var current_fields_list = [];
			for(var cr_doc = 0; cr_doc < current_doc_detials.length; cr_doc++){
				current_fields_list.push(current_doc_detials[cr_doc].fieldname);
			}
			for(var doc_d =0; doc_d < doc_details.length; doc_d++){
		 		if(key == doc_details[doc_d].fieldname){
				if(!current_fields_list.includes(key)){
					//console.log("current field name========="+current_doc_detials[cr_doc].fieldname);
					
					//console.log("parent fields =========="+key);
					var child = cur_frm.add_child("fields_descriptions");
					frappe.model.set_value(child.doctype, child.name, "label", doc_details[doc_d].label);
					frappe.model.set_value(child.doctype, child.name, "field_label", "Parent Field");
					frappe.model.set_value(child.doctype, child.name, "fieldtype", doc_details[doc_d].fieldtype);
					frappe.model.set_value(child.doctype, child.name, "fieldname", doc_details[doc_d].fieldname);
					frappe.model.set_value(child.doctype, child.name, "options", doc_details[doc_d].options);
					cur_frm.refresh_field('fields_descriptions');
					//break;
				}
				}
			}
			
			for(var child_d = 0; child_d < child_doc_fields.length; child_d++){
				if(child_doc_fields[child_d].fieldname == key){
					if(!current_fields_list.includes(key)){
					console.log("item fields =========="+key);
					var child = cur_frm.add_child("fields_descriptions");
					frappe.model.set_value(child.doctype, child.name, "label", child_doc_fields[child_d].label);
					frappe.model.set_value(child.doctype, child.name, "field_label", "Item Field");
					frappe.model.set_value(child.doctype, child.name, "fieldtype", child_doc_fields[child_d].fieldtype);
					frappe.model.set_value(child.doctype, child.name, "fieldname", child_doc_fields[child_d].fieldname);
					frappe.model.set_value(child.doctype, child.name, "options", child_doc_fields[child_d].options);
					cur_frm.refresh_field('fields_descriptions');
				
					}
			}
				}
			for(var tax_d = 0; tax_d < child_taxes_fields.length; tax_d++){
				 if(child_taxes_fields[tax_d].fieldname == key){
					if(!current_fields_list.includes(key)){
					console.log("tax fields =========="+key);
					var child = cur_frm.add_child("fields_descriptions");
					frappe.model.set_value(child.doctype, child.name, "label", child_taxes_fields[tax_d].label);
					frappe.model.set_value(child.doctype, child.name, "field_label", "Tax Field");
					frappe.model.set_value(child.doctype, child.name, "fieldtype", child_taxes_fields[tax_d].fieldtype);
					frappe.model.set_value(child.doctype, child.name, "fieldname", child_taxes_fields[tax_d].fieldname);
					frappe.model.set_value(child.doctype, child.name, "options", child_taxes_fields[tax_d].options);
					cur_frm.refresh_field('fields_descriptions');
				
					}
				}
				}
			
			}
			}
                })
            }
        });
	 d.fields_dict.select_all.input.onclick = function() {
			
			var ckb_status = $("input[data-fieldname='select_all']").prop('checked');
			console.log("ckb_status============="+ckb_status);
			if(ckb_status == true){
				for(var doc_d =0; doc_d < doc_details.length; doc_d++){
				 var dialog_fieldtype = (doc_details[doc_d].fieldtype || "");
				  if (doc_details[doc_d].label != "" && doc_details[doc_d].label != undefined) {
                if (dialog_fieldtype != "Column Break"  && dialog_fieldtype != "Section Break" && dialog_fieldtype != "Button" && dialog_fieldtype != "Code" && dialog_fieldtype != "Table"  && dialog_fieldtype != "Text") {
				   var fieldname = doc_details[doc_d].fieldname;
				   $("input[data-fieldname = "+fieldname+"]").prop('checked', true);
				}
			}
		}
		for(var child_d = 0; child_d < child_doc_fields.length; child_d++){
		  $("input[data-fieldname = "+child_doc_fields[child_d].fieldname+"]").prop('checked', true);
		}
		for(var tax_d = 0; tax_d < child_taxes_fields.length; tax_d++){
			$("input[data-fieldname = "+child_taxes_fields[tax_d].fieldname+"]").prop('checked', true);
		}
		}else if(ckb_status == false){
			for(var doc_d =0; doc_d < doc_details.length; doc_d++){
				 var dialog_fieldtype = (doc_details[doc_d].fieldtype || "");
				  if (doc_details[doc_d].label != "" && doc_details[doc_d].label != undefined) {
                if (dialog_fieldtype != "Column Break"  && dialog_fieldtype != "Section Break" && dialog_fieldtype != "Button" && dialog_fieldtype != "Code" && dialog_fieldtype != "Table"  && dialog_fieldtype != "Text") {
				   var fieldname = doc_details[doc_d].fieldname;
				   $("input[data-fieldname = "+fieldname+"]").prop('checked', false);
				}
			}
		}for(var child_d = 0; child_d < child_doc_fields.length; child_d++){
		  $("input[data-fieldname = "+child_doc_fields[child_d].fieldname+"]").prop('checked', false);
		}
		for(var tax_d = 0; tax_d < child_taxes_fields.length; tax_d++){
			$("input[data-fieldname = "+child_taxes_fields[tax_d].fieldname+"]").prop('checked', false);
		}
		}
		
                        //show_alert(date);
			/*
                        //selectStudentIdFromStudentDocType(batch_name);
                        function_doctype_cancell_amended(doctype, docIdss, date);
			*/
                    }

        d.show();
    }
});
function function_doc_details(doctype) {
    var supplier_criticality = "";
    console.log("doc type----------" + doctype);

    frappe.call({
        method: 'nhance.nhance.doctype.document_review_templates.document_review_templates.get_doc_details',
        args: {
            "doctype": doctype

        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}

function get_doc_items_details(doctype) {
    var supplier_criticality = "";
    console.log("doc type----------" + doctype);

    frappe.call({
        method: 'nhance.nhance.doctype.document_review_templates.document_review_templates.get_doc_details_itmes',
        args: {
            "doctype": doctype

        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}

function function_get_item_details(item_code) {
    var supplier_criticality = "";
    frappe.call({
        method: 'nhance.nhance.doctype.document_review_templates.document_review_templates.get_details_itme',
        args: {
            "item_code": item_code

        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}

function function_item_price(item_code) {
    var supplier_criticality = "";

    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Item Price",
            filters: {
                item_code: ["=", item_code]
            },
            fieldname: ["price_list_rate"]
        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}

function function_taxes_details(taxes_doc, taxes_and_charges) {
    var supplier_criticality = "";

    frappe.call({
        method: 'nhance.nhance.doctype.document_review_templates.document_review_templates.get_taxes_details',
        args: {
            "taxes_doc": taxes_doc,
            "taxes_and_charges": taxes_and_charges
        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}
function get_current_doc_details(cur_name){
    var supplier_criticality = "";
	 frappe.call({
        method: 'nhance.nhance.doctype.document_review_templates.document_review_templates.get_current_doc_details',
        args: {
            "cur_name": cur_name,
        },
        async: false,
        callback: function(r) {
            //  console.log("supplier criticality..." + JSON.stringify(r.message));
            supplier_criticality = r.message;
        }
    });
    return supplier_criticality;
}
