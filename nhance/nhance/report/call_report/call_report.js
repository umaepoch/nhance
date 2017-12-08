// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Call Report"] = {
	"filters": [

	    {
                        "fieldname":"user",
                        "label": __("Sales Engineer"),
                        "fieldtype": "Link",
                        "options": "User",
                        "reqd": 0
                },
                
                {      "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "default": sys_defaults.year_start_date,
			
                },
                {
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "default": frappe.datetime.get_today()
                }
                
                             
                
        ]
}

