// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt

frappe.query_reports["Opportunity with Interactions"] = {
	"filters": [


	    {
                        "fieldname":"name",
                        "label": __("Opportunity"),
                        "fieldtype": "Link",
                        "options": "Opportunity",
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
                },
                
                {
                        "fieldname":"item_code",
                        "label": __("Item"),
                        "fieldtype": "Link",
                        "options": "Item"
                }
                                  
                
        ]
}

// $(function() {
//      $(wrapper).bind("show", function() {
//              frappe.query_report.load();
//      });
// });

