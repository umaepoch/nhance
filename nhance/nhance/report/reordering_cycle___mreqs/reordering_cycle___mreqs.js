// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Reordering Cycle - MREQs"] = {
	"filters": [
		
		{
          		    "fieldname": "company",
		            "label": __("Company"),
		            "fieldtype": "Link",
		            "options": "Company",
		            "reqd": 1

	        },
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item"
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse",
			"reqd": 1,
		},

		{
	          "fieldname":"required_on",
        	  "label": __("Required Date"),
        	  "fieldtype": "Date",
        	  "default": frappe.datetime.get_today(),
        	  "on_change": function(query_report) {
        	    frappe.query_report.refresh();
		    var filters = query_report.get_values();
        	    var required_date = filters.required_on;
        	    if (required_date < frappe.datetime.get_today()){
        	      frappe.msgprint("Required Date cannot be an Earlier Date than today")
		      frappe.query_report.set_filter_value("required_on", frappe.datetime.get_today());
        	    }
        	  }
        	},
	
		{
			"fieldname": "cutoff_date",
			"label": __("Days to Consider"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
          		"on_change": function(query_report) {
        	    	frappe.query_report.refresh();
	    		var filters = query_report.get_values();
		        var cutoff_date = filters.cutoff_date;
            		if (cutoff_date > frappe.datetime.get_today()){
              			frappe.msgprint("Cutoff Date cannot be a later Date than today")
				frappe.query_report.set_filter_value("required_on", frappe.datetime.get_today());
            }
          }

		
			
		},
	],
    onload: function(report) {
        report.page.add_inner_button(__("As a draft"),
                function() {
                  var args = "as a draft"
                  var reporter = frappe.query_reports["Reordering Cycle - MREQs"];
                    reporter.makeStockRequisition(report,args);},'Make Stock Requisition'),
                    report.page.add_inner_button(__("As final"),
                        function() {
                          var args = "submit"
                          var reporter = frappe.query_reports["Reordering Cycle - MREQs"];
                          reporter.makeStockRequisition(report,args);},'Make Stock Requisition');
              },

    isNumeric: function( obj ) {
    return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
  },
   makeStockRequisition: function(report,status){
    var filters = report.get_values();
     if (filters.warehouse) {
         return frappe.call({
             method: "nhance.nhance.report.reordering_cycle___mreqs.reordering_cycle___mreqs.make_stock_requisition",
             args: {
                 "args": status
             },
             callback: function(r) {
               if(r.message) {
                 frappe.set_route('List',r.message );
             }
             }
         })
     } else {
         frappe.msgprint("Please select all filters For Stock Requisition")
     }

   }
}

