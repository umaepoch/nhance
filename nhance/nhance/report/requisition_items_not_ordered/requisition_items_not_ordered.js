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
            
        }
	],
"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
        value = default_formatter(row, cell, value, columnDef, dataContext);
       
	if (columnDef.id != "company"> 1) {
            value = "<span style='color:#000000!important;font-weight:none'>" + value + "</span>";
       }

       return value;
    }
}
