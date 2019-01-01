// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM Tree Illustration"] = {
	"filters": [
		{
            "fieldname": "bom",
            "label": __("BOM"),
            "fieldtype": "Link",
            "options": "BOM",
            "reqd": 1
        }
	]
}
