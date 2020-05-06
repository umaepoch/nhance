// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pre Purchase Orders Report"] = {
	"filters": [
		{
        "fieldname": "project",
        "label": __("Project"),
        "fieldtype": "Link",
        "options": "Project Being Ordered",
        "reqd": 1,
        "on_change": function(query_report) {
            var project = frappe.query_report.get_filter_value("project");
            //validate_project_details(project, query_report);
        }
    }, {
        "fieldname": "source_warehouse",
        "label": __("Source Warehouse"),
        "fieldtype": "Link",
        "options": "Warehouse",
	"hidden":1
    }
	],
	onload: function(report) {
		//console.log("Make PO and Transfer Existing/Required Quantity..........");
		report.page.add_inner_button(__("Make Pre Purchase Order"),
		    function() {

		        var reporter = frappe.query_reports["Pre Purchase Orders Report"];
		        reporter.make_PO_and_transfer_qty(report);
		    });
	},
	 make_PO_and_transfer_qty: function(report) {
       // frappe.query_report.refresh();
        
            make_PO_and_transfer_qty(report);
      
    }
}
function make_PO_and_transfer_qty(report) {
    flag = false;
    var filters = report.get_values();
    var source_warehouse = filters.source_warehouse;
    var project = filters.project;
    var project_filter = frappe.query_report.get_filter_value("project");
    var swh_filter = frappe.query_report.get_filter_value("source_warehouse");
   // var dont_transfer_order = frappe.query_report.get_filter_value("dont_order_qty");
    var reportData = getReportData(project_filter);
}

function getReportData(project_filter) {
    var reportData = [];
    frappe.call({
        method: "nhance.nhance.report.pre_purchase_orders_report.pre_purchase_orders_report.get_report_data",
        args: {
            "project_filter": project_filter
        },
        async: false,
        callback: function(r) {
            //console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;
	    if(reportData != undefined){
	   	 frappe.set_route("List", reportData);
		}
        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}

