// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const d = new Date();
var currentMonth = monthNames[d.getMonth()];
frappe.query_reports["India GSTR-1A"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"type_of_business",
			"label": __("Type of Business"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": ["B2B", "B2C Large", "B2C Small","CDNR", "EXPORT"],
			"default": "B2B"
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": ["January", "February", "March", "April", "May", "June",
 			 "July", "August", "September", "October", "November", "December"],
			"default": currentMonth
		}
	]
}
