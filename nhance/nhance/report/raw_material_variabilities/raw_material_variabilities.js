// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Raw Material Variabilities"] = {
    "filters": [{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1

        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "old_bom",
            "label": __("Old BOM"),
            "fieldtype": "Link",
            "options": "BOM",
	    "get_query": function() {
		 return {
		    "doctype": "BOM",
		    "filters": {
				"docstatus": 1,
				}
	   	   }
	    }
        }, 
	{
            "fieldname": "new_bom",
            "label": __("New BOM"),
            "fieldtype": "Link",
            "options": "BOM",
	    "get_query": function() {
		 return {
		    "doctype": "BOM",
		    "filters": {
				"docstatus": 1,
				}
	   	   }
	    }
        },
	{
            "fieldname": "stock_warehouse",
            "label": __("Stock WareHouse"),
            "fieldtype": "Link",
            "options": "Warehouse"
        }

    ],
    onload: function(report) {
        console.log("onload.............");
        report.page.add_inner_button(__("Make Material Issue"),
            function() {

                var reporter = frappe.query_reports["Raw Material Variabilities"];
                reporter.makeMaterialIssue(report);
            });
    },
    isNumeric: function(obj) {
        return !jQuery.isArray(obj) && (obj - parseFloat(obj) + 1) >= 0;
    },
    makeMaterialIssue: function(report) {
        console.log("makeMaterialIssue.............");
        var materialIssueList = [];
        var dialog = new frappe.ui.Dialog({
            title: __("Select Target Warehouse"),
            fields: [{
                "fieldname": "target_warehouse",
                "label": __("Target Warehouse"),
                "fieldtype": "Link",
                "reqd": 1,
                "options": "Warehouse"
            }],
            primary_action: function() {
                dialog.hide();
                var target_warehouse = dialog.fields_dict.target_warehouse.get_value();
                console.log("target_warehouse............." + target_warehouse);
                var reportData = getReportData();
                var materialIssueList = [];
                console.log("reportData", reportData)
                if (reportData.length != 0) {
                    for (var i = 0; i < reportData.length; i++) {
                        var itemsArray = {};
                        var item_code = reportData[i]['item_code'];
                        var excees_qty = reportData[i]['excees_qty'];
                        var stock_qty = reportData[i]['stock_qty'];
                        var new_qty = reportData[i]['new_qty'];
                        console.log("item_code.............NNNNNNN" + item_code);
                        console.log("item_code............." + excees_qty);
                        if (excees_qty > 0 && stock_qty > new_qty) {
                            var qty = stock_qty - new_qty
                            itemsArray['item_code'] = item_code;
                            itemsArray['qty'] = qty;
                            itemsArray['warehouse'] = target_warehouse;
                            console.log("itemsArray............." + itemsArray);
                            materialIssueList.push(itemsArray);
                            console.log("materialIssueList............." + materialIssueList);
                        }
                    } //end of for loop..
                } //end of if..

                console.log("materialIssueList............." + JSON.stringify(materialIssueList));
                if (materialIssueList.length != 0) {
                    frappe.call({
                        method: "nhance.nhance.report.raw_material_variabilities.raw_material_variabilities.make_material_issue",
                        args: {
                            "material_items_list": materialIssueList
                        },
                        async: false,
                        callback: function(r) {
                            if (r.message) {
                                frappe.set_route('List', r.message);
                            }
                        } //end of callback fun..
                    }) //end of frappe call.
                } else {
                    frappe.msgprint("Make Material Issue Is Not Required.");
                }

            } //end of primary fun

        }); //end of dialog box..
        dialog.show();

    }

}

function getReportData() {
    var reportData = [];
    frappe.call({
        method: "nhance.nhance.report.raw_material_variabilities.raw_material_variabilities.get_report_data",
        async: false,
        callback: function(r) {
            console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}
