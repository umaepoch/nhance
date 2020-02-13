// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Label"] = {
	"filters": [
                    {
        "fieldname": "purchase_document_type",
        "label": __("Creation Document Type"),
        "fieldtype": "Link",
        "options": "DocType",
        "reqd": 1
	},
        {
        "fieldname": "purchase_document_no",
        "label": __("Creation Document No Stock Entry"),
        "fieldtype": "Link",
        "options": "Stock Entry",
        "reqd": 0,

         },
        {
        "fieldname": "purchase_document_no",
        "label": __("Creation Document No Purchase Receipt "),
        "fieldtype": "Link",
        "options": "Purchase Receipt",
        "reqd": 0,

         }
	]
}












