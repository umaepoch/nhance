// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Workflow Action"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.month_start(), -1),
            "width": "80"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.month_end(), -1)
        },
	{
	    "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Link",
            "options": "Workflow State"
	}
		
	],
	
	 onload: function(report) {
        //console.log("Make PO and Transfer Existing/Required Quantity..........");
        report.page.add_inner_button(__("Workflow Action"),
            function() {
             
               
            });
  
    },
 
}



function get_sales_order(start_date,end_date){
	 var sales = "";
    frappe.call({
        method: "nhance.nhance.report.sales_order_workflow_actions.sales_order_workflow_actions.sales_order_detials",
        args: {
            "start_date": start_date,
           "end_date": end_date
        },
        async: false,
        callback: function(r) {
            //console.log("ItemValuationRateFromStockBalance::" + JSON.stringify(r.message));
            sales = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return sales;

}
