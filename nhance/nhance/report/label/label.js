// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Label"] = {
	"filters": [
                    {
        "fieldname": "document_type",
        "label": __("Creation Document Type"),
        "fieldtype": "Link",
        "options": "DocType",
        "reqd": 1
	},
        {
        "fieldname": "document_no_value",
        "label": __("Creation Document No "),
        "fieldtype": "Dynamic Link",
        "options": "document_type",
        "reqd": 0,
         }
       
	]
}












