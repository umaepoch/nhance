// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt

frappe.query_reports["BOM Item Warehouse with Sales Orders and PO"] = {
	"filters": [

	
		{
                        "fieldname":"sales_order",
                        "label": __("Sales Order"),
                        "fieldtype": "Link",
                        "options": "Sales Order",
			"reqd": 1
			                        
                },
	        {
                        "fieldname":"bom",
                        "label": __("BOM"),
                        "fieldtype": "Link",
                        "options": "BOM",
			                        
                },
                
		{
                        "fieldname":"company",
                        "label": __("Company"),
                        "fieldtype": "Link",
                        "options": "Company",
			"reqd": 1
                        
                },
                
                {
                        "fieldname":"warehouse",
                        "label": __("Warehouse"),
                        "fieldtype": "Link",
                        "options": "Warehouse",
		},
                {
                        "fieldname":"item_code",
                        "label": __("Item"),
                        "fieldtype": "Link",
                        "options": "Item"
                },
                       
		{
			"fieldname":"include_exploded_items",
			"label": __("Include Exploded Items"),
			"fieldtype": "Data",
                        "default": "Y"
			
		}          
                
        ]
}

// $(function() {
//      $(wrapper).bind("show", function() {
//              frappe.query_report.load();
//      });
// });

