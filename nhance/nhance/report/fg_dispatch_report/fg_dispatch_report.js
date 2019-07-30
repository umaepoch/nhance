// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["FG Dispatch Report"] = {
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
        "reqd": 1,
        "get_query": function() {
	           return {
                    "doctype": "Sales Order",
		     "filters" : [
			['Sales Order', 'docstatus', '!=', '2'] 
			]
              }
         }
}
]
}


