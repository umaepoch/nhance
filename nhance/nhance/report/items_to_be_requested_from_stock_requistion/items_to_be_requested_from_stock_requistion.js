// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Items To Be Requested From Stock Requistion"] = {
	"filters": [
	  {
            "fieldname": "company",
            "label": __("company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },
	 {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "default": "All"
        },
	{
            "fieldname": "planning_warehouse",
            "label": __("Planning Warehouse"),
            "fieldtype": "Link",
            "reqd": 1,
            "options": "Warehouse",
            "get_query": function() {	
                return {
                    'filters': [
                        ['Warehouse', 'is_group', '=', '0']
                    ]
                }	
            }
        }
	],
 onload: function(report) {
        report.page.add_inner_button(__("As a draft"),
                function() {
                  var args = "as a draft"
                  var reporter = frappe.query_reports["Items To Be Requested From Stock Requistion"];
                    reporter.makePurchaseOrder(report,args);},'Make Purchase Order'),
                    report.page.add_inner_button(__("As final"),
                        function() {
                          var args = "as final"
			 var filters = report.get_values();
                          var reporter = frappe.query_reports["Items To Be Requested From Stock Requistion"];
                          reporter.makePurchaseOrder(report,args);},'Make Purchase Order');

              },
    isNumeric: function( obj ) {
    return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
  },
   makePurchaseOrder: function(report,status){
    var filters = report.get_values();
	//alert("### makePurchaseOrder::");
     if (filters.warehouse) {
         return frappe.call({
             method: "nhance.nhance.report.items_to_be_requested_from_stock_requistion.items_to_be_requested_from_stock_requistion.make_Purchase_Items",
             args: {
                 "args": status
             },
             callback: function(r) {
               if(r.message) {
		 frappe.set_route("Form", "Pre Purchase Order", r.message);
             }
             }
         })
     } 
   }
}
