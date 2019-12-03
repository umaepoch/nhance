// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balance - RARB Location"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse",
			"reqd":1,
			"get_query": function() {
				 var rarb_warehouse = []
				
				 rarb_warehouse = get_rarb_warehouse_item_name();
				console.log("rarb_warehouse---------------"+rarb_warehouse);
				return{
				"filters": [
					["Warehouse", "name", "in", rarb_warehouse]
				    ]
				
				}
			}
		},
		{
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
		{
			"fieldname": "show_variant_attributes",
			"label": __("Show Variant Attributes"),
			"fieldtype": "Check"
		},
	]
}
function get_rarb_warehouse_item_name(){
	var supplier_criticality = [];
	frappe.call({
		method: 'nhance.nhance.report.stock_balance___rarb_location.stock_balance___rarb_location.get_rarb_warehouse_item_name',
		args: {
		},
		async: false,
		callback: function(r) {
		    console.log("supplier criticality..." + JSON.stringify(r.message));
			 for (var i = 0; i < r.message.length; i++) {
				    supplier_criticality.push(r.message[i].warehouse);
				    
				}
			console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
    return supplier_criticality;
}
