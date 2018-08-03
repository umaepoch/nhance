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
                reporter.makeMaterialIssue(report, "Issue");
            });
        report.page.add_inner_button(__("Make Stock Requisition"),
            function() {
                var reporter = frappe.query_reports["Raw Material Variabilities"];
                reporter.makeMaterialIssue(report, "Purchase");
		//reporter.bom_Calculations(report);
            });
    },
    isNumeric: function(obj) {
        return !jQuery.isArray(obj) && (obj - parseFloat(obj) + 1) >= 0;
    },
    makeMaterialIssue: function(report, checkMaterialRequestType) {
        console.log("makeMaterialIssue.............");
	var MESSAGE = "";
	var flag = false;
	var issueFlag = false;
	var purchaseFlag = false;
	var filters = report.get_values();
	var old_bom = filters.old_bom;
    	var new_bom = filters.new_bom;
        var materialIssueList = [];
	var reportData = getReportData();
	for (var i = 0; i < reportData.length; i++) {
		var excees_qty = reportData[i]['excees_qty'];
                var stock_qty = reportData[i]['stock_qty'];
                var new_qty = reportData[i]['new_qty'];
		if (excees_qty > 0 && stock_qty > new_qty){
			issueFlag = true;
			break;
		}
	}
	for (var i = 0; i < reportData.length; i++) {
		var excees_qty = reportData[i]['excees_qty'];
                var stock_qty = reportData[i]['stock_qty'];
                var new_qty = reportData[i]['new_qty'];
		if(excees_qty < 0){
			purchaseFlag = true;
			break;
		}
	}

	if (checkMaterialRequestType == "Issue"){
		MESSAGE = "No Items to be issued..";
		flag = issueFlag;
	}else if (checkMaterialRequestType == "Purchase"){
		MESSAGE = "Stock Requisition is not required..";
		flag = purchaseFlag;
	}

	if(flag){
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
                var materialIssueList = [];
                var materialPurchaseList = [];
		var stockRequisitionItemsList = [];
                console.log("reportData", reportData);
		var workflow_status = "";
                if (reportData.length != 0) {
                    for (var i = 0; i < reportData.length; i++) {
                        var itemsArray = {};
                        var purchaseItemsJson = {};
                        var item_code = reportData[i]['item_code'];
                        var excees_qty = reportData[i]['excees_qty'];
                        var stock_qty = reportData[i]['stock_qty'];
                        var new_qty = reportData[i]['new_qty'];
                        if (excees_qty > 0 && stock_qty > new_qty) {
                            var qty = stock_qty - new_qty
                            itemsArray['item_code'] = item_code;
                            itemsArray['qty'] = qty;
                            itemsArray['warehouse'] = target_warehouse;
                            console.log("itemsArray............." + itemsArray);
                            materialIssueList.push(itemsArray);
                            console.log("materialIssueList............." + materialIssueList);
                        }
                        if (excees_qty < 0) {
			    var old_bom_qty = checkStockRequistionForBOM(old_bom,item_code);
    			    var new_bom_qty = checkStockRequistionForBOM(new_bom,item_code);
			    var final_qty = [parseFloat(new_qty) - (parseFloat(old_bom_qty) + parseFloat(new_bom_qty))];
			    excees_qty = parseFloat(excees_qty) * (-1);
			    
			    console.log("old_bom_qty................."+old_bom_qty);
			    console.log("new_bom_qty................."+new_bom_qty);
			    console.log("final_qty................."+final_qty);
			    console.log("excees_qty................."+excees_qty);

			    if(excees_qty <= final_qty){
				workflow_status = "Approved";
			    }else if(excees_qty > final_qty){
				workflow_status = "Pending Approval";
			    }
                            purchaseItemsJson['item_code'] = item_code;
                            purchaseItemsJson['qty'] = parseFloat(excees_qty);
                            purchaseItemsJson['warehouse'] = target_warehouse;
                            materialPurchaseList.push(purchaseItemsJson);
                        }
                    } //end of for loop..
                } //end of if..
                if (checkMaterialRequestType == "Issue") {
                    if (materialIssueList.length != 0) {
			console.log("materialIssueList............." + JSON.stringify(materialIssueList));
			stockRequisitionItemsList = materialIssueList;
                        makeStockRequistion(stockRequisitionItemsList,checkMaterialRequestType,"","");
                    } 
                } else if (checkMaterialRequestType == "Purchase") {
                    if (materialPurchaseList.length != 0) {
			console.log("materialPurchaseList............." + JSON.stringify(materialPurchaseList));
                        stockRequisitionItemsList = materialPurchaseList;
                        makeStockRequistion(stockRequisitionItemsList,checkMaterialRequestType,workflow_status,new_bom);
                    } 
                }
            } //end of primary fun
        }); //end of dialog box..
        dialog.show();
	}else{
	frappe.msgprint(MESSAGE);
	}
    }
}

function checkStockRequistionForBOM(bom,item_code) {
var total_qty_for_item = 0;
frappe.call({
        method: "nhance.nhance.report.raw_material_variabilities.raw_material_variabilities.get_sreq_items_list",
        args: {
            "requested_by": bom,
	    "item_code": item_code
        },
        async: false,
        callback: function(r) {
            if (r.message) {
		total_qty_for_item = r.message;
		console.log("total_qty_for_item----------"+r.message);
            }
        } //end of callback fun..
    }) //end of frappe call.
return total_qty_for_item;
}//end of function..

function makeStockRequistion(stockRequisitionItemsList,checkMaterialRequestType,workflow_status,new_bom) {
    frappe.call({
        method: "nhance.nhance.report.raw_material_variabilities.raw_material_variabilities.make_stock_requisition",
        args: {
            "stockRequisitionItemsList": stockRequisitionItemsList,
	    "materialRequestType": checkMaterialRequestType,
	    "workflow_status": workflow_status,
	    "reference_no": new_bom
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                frappe.set_route('List', r.message);
            }
        } //end of callback fun..
    }) //end of frappe call.
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
