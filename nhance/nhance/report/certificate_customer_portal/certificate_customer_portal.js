// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Certificate-Customer Portal"] = {
	"filters": [
		{
        "fieldname": "customer_po",
        "label": __("Customer PO"),
        "fieldtype": "Data",
        "reqd": 0
	},
	{
        "fieldname": "item_code",
        "label": __("Item Code"),
        "fieldtype": "Link",
        "options": "Item",
        "reqd": 0,
	"get_query": function() {
		var item_code=[];
		var item_code=get_item_code_list();
		console.log("item_code",item_code);
	           return {
                    
		     "filters" : [
		 	['Item', 'name', 'in', item_code]
			]
              }
         }
	
	},
	{
        "fieldname": "item_serial_no",
        "label": __("Item Serial No"),
        "fieldtype": "Link",
        "options": "Serial No",
        "reqd": 0,
	"get_query": function() {
		var item_serial=[];
		var item_serial=get_item_serial_list();
		console.log("item_serial",item_serial);
	           return {
		     "filters" : [
			['Serial No', 'name', 'in', item_serial] 
			]
              }
         }
	},
	{
        "fieldname": "delivery_note",
        "label": __("Delivery Note"),
        "fieldtype": "Link",
        "options": "Delivery Note",
        "reqd": 0,
	"get_query": function() {
            var delivery_document_no = [];
            var delivery_document_no = get_delivery_document_no_name();
	    console.log("delivery_document_no",delivery_document_no);
		return{
		"filters": [
		["Delivery Note", "name", "in", delivery_document_no]
			]

		}
	}
	
	},
	{
        "fieldname": "sales_order_acknowleggement",
        "label": __("Sales Order Acknowledgement"),
        "fieldtype": "Link",
        "options": "Sales Order",
	"reqd": 0
	}

	]
}


function get_item_code_list(){
	var item_code_list = [];
	frappe.call({
	method: 'nhance.nhance.report.certificate_customer_portal.certificate_customer_portal.get_item_code',
	async: false,
	callback: function(r) {
	
		for (var i = 0; i < r.message.length; i++) {
				    
				    item_code_list.push(r.message[i].item_code);
				   
				    console.log("item_code_list",item_code_list);
				    
				}
		
	}
	
	});
	
	return item_code_list
	}

function get_item_serial_list(){
	var item_serial_list = [];
	frappe.call({
	method: 'nhance.nhance.report.certificate_customer_portal.certificate_customer_portal.get_item_serial_no',
	async: false,
	callback: function(r) {
	
		for (var i = 0; i < r.message.length; i++) {
				    
				    item_serial_list.push(r.message[i].name);
				   
				    console.log("item_serial_list",item_serial_list);
				    
				}
		
	}
	
	});
	
	return item_serial_list
	}

function get_delivery_document_no_name(){
	var delivery_document_list = [];
	frappe.call({
	method: 'nhance.nhance.report.certificate_customer_portal.certificate_customer_portal.get_delivery_document_no',
	async: false,
	callback: function(r) {
	
		for (var i = 0; i < r.message.length; i++) {
				    
				    delivery_document_list.push(r.message[i].delivery_document_no);
				   
				    console.log("delivery_document_list",delivery_document_list);
				    
				}
		
	}
	
	});
	
	return delivery_document_list
	}
