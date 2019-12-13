// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Requisition Items Not Ordered"] = {
	"filters": [
		{
		"fieldname":"company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1
		},
		{
		"fieldname":"bom",
		"label": __("BOM"),
		"fieldtype": "Link",
		"options": "BOM"
		},
		{
		"fieldname":"project",
		"label": __("Project"),
		"fieldtype": "Link",
		"options": "Project"
		}
	]
}
