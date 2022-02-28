// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["SO Cost Report"] = {
	"filters": [{
		"fieldname":"company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1,
		"default": frappe.defaults.get_user_default("Company")
	},
	{
		"fieldname": "sales_order",
		"label": __("Sales Order"),
		"fieldtype": "Link",
		"options": "Sales Order",
		"reqd": 1
	}
		

	]
}
