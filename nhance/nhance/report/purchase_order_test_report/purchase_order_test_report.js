// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Test Report"] = {
	"filters": [{
        "fieldname": "company",
        "label": __("Company"),
        "fieldtype": "Link",
        "options": "Company",
        "reqd": 1
	}],
    onload: function(report) {
        console.log("Purchase Order Test Report..........");
        report.page.add_inner_button(__("Make PR for Pending Qty's"),
            function() {
                var reporter = frappe.query_reports["Purchase Order Test Report"];
                reporter.make_po_for_pending_qtys(report);
            });
    },
    make_po_for_pending_qtys: function(report) {
        makePO(report);
    }
}


function makePO(report){
	console.log("makePO....entered......");
	var reportData = getReportData();
	console.log("reportData::" + JSON.stringify(reportData));

}


function getReportData() {
    var reportData = [];
    frappe.call({
        method: "nhance.nhance.report.purchase_order_test_report.purchase_order_test_report.get_report_data",
        async: false,
        callback: function(r) {
            //console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}

