// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM-Cost-Report v2"] = {
	"filters": [{
		"fieldname":"company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1,
		"default": frappe.defaults.get_user_default("Company")
	},
	{
		"fieldname": "bom",
		"label": __("BOM"),
		"fieldtype": "Link",
		"options": "BOM",
		"reqd": 1,
		"get_query": function() {
			return {
			"doctype": "BOM",
			"filters": {
			"docstatus": 1,
			}
			}
			}
	}

	]
}
