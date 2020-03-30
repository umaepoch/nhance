// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Po due for delivery"] = {
	"filters": [
		
		{
			"fieldname":"Status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["Draft","To Receive and Bill","To Bill","To Receive","Completed","Cancelled"],
                        "default":"To Receive and Bill"
			
		}, 
		{
			"fieldname":"Percent",
			"label": __("Percent"),
			"fieldtype": "Select",
			"options": [0,90,100],
			"default":"0"
			
			
		},
		{
			"fieldname":"supplier",
			"label": __("supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"reqd": 1,
			
			


			
			
		}			
				
		
		]
}

