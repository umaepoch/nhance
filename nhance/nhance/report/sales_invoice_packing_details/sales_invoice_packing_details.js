// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Invoice Packing Details"] = {
	"filters": [
		{
        "fieldname": "si_name",
        "label": __("Sales Invoice"),
        "fieldtype": "Link",
        "options": "Sales Invoice",
        "reqd": 1
			}

	],
	onload: function(report) {
				console.log("onload.............");
				report.page.add_inner_button(__("Make Shipment"),
						function() {
								var reporter = frappe.query_reports["Sales Invoice Packing Details"];
								var filters = report.get_values();
								console.log("onload.............filters",filters.si_name);
								frappe.call({
										method: "nhance.nhance.report.sales_invoice_packing_details.sales_invoice_packing_details.make_shipment",
										async: false,
										args: {
										"si_name_filter":filters.si_name
										},
										callback: function(r)
										{
																	if(r.message){
	    													  frappe.msgprint("Delievery note has been successfully created Please check packing boxes and items doc for packing details")
																	}//end of if..
										}//end of call-back function..
								});//end of frappe call..
						});
	},//end of onload..
}
