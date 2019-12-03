// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["shark report"] = {
	"filters": [{
        "fieldname": "company",
        "label": __("Company"),
        "fieldtype": "Link",
        "options": "Company",
        "reqd": 1
	},
{
        "fieldname": "sales_order",
        "label": __("Sales Order"),
        "fieldtype": "Link",
        "options": "Sales Order",
        "reqd": 1
	},
],
}





