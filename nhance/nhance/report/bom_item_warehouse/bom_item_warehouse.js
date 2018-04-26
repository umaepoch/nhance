/**
 *
 */
// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
var warehouse = "";
var reference_no = "";
frappe.query_reports["BOM Item Warehouse"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
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
            "fieldname": "include_exploded_items",
            "label": __("Include Exploded Items"),
            "fieldtype": "Data",
            "default": "Y"

        },
        {
            "fieldname": "qty_to_make",
            "label": __("Quantity to Make"),
            "fieldtype": "Data",
            "default": "1",
	    "reqd": 1,
            "on_change": function(query_report) {
		var bomList = "";
		var bomNO = "";
		var check_for_whole_number_flag;
		var docName = frappe.query_report_filters_by_name.for.get_value();
                var qty = frappe.query_report_filters_by_name.qty_to_make.get_value();
                if (!jQuery.isNumeric(qty)){
                  frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                  frappe.throw("Quantity to Make value is not in proper format")
                }
                if (qty < 0){
                  frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                  frappe.throw("Quantity to Make cannot be nagative please input positive value")
                }
                if (qty < 1){
                  frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                  frappe.throw(" Quantity to Make should be greater than one")
                }
		if(docName=="Sales Order"){
		bomList = frappe.query_report_filters_by_name.hidden_bom.get_value();
		bomList = bomList.split(",");
		for(var i=0;i<bomList.length;i++){
		bomNO = bomList[i];
	        console.log("bomNO::"+bomNO);
		if(bomNO!="null"){
		check_for_whole_number_flag = check_for_whole_number(bomNO,qty,query_report);
		console.log("success.check_for_whole_number_flag."+check_for_whole_number_flag);
		}
		}
		}else if(docName=="BOM"){
		bomNO = frappe.query_report_filters_by_name.docIds.get_value();
		console.log("bomNO::"+bomNO);
		check_for_whole_number_flag = check_for_whole_number(bomNO,qty,query_report);
		}else if(docName=="Project"){
		bomNO = frappe.query_report_filters_by_name.master_bom_hidden.get_value();
		console.log("master_bom::"+bomNO);
		check_for_whole_number_flag = check_for_whole_number(bomNO,qty,query_report);
		}
		if(check_for_whole_number_flag){
		frappe.msgprint(__("Quantity to Make should be whole number"));
		}
            }
        },
	 {
            "fieldname":"for",
            "label": __("For"),
            "fieldtype": "Select",
            "options": ["Sales Order", "Project", "BOM"],
	    "on_change": function(query_report){
		var docName = frappe.query_report_filters_by_name.for.get_value();
		frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.fetch_Records",
			args: {
         	 		"docName":docName,
        	},
		async: false,
		callback: function(r) 
      		 { 
			console.log("docids options::"+r.message);
			var docIds_filter = frappe.query_report_filters_by_name.docIds;
			docIds_filter.df.options = r.message;
			docIds_filter.df.default = "";
			docIds_filter.refresh();
			docIds_filter.set_input(docIds_filter.df.default);
			
			query_report.refresh();

		}//end of call-back function..
		});//end of frappe call..
		}//end of on_change function..
        },
	{
	    "fieldname": "current_stock_balance",
            "label": __("Current Stock Balance to be considered?"),
            "fieldtype": "Check",
            "default": "0"
	},
	{
	   "fieldname":"docIds",
	   "label": __("Doc Ids"),
	   "fieldtype": "Select",
	   "on_change": function(query_report){		
		var docId = frappe.query_report_filters_by_name.docIds.get_value();
		var docName = frappe.query_report_filters_by_name.for.get_value();
		if(docName == "BOM"){
		console.log("docName....."+docName);
		query_report.refresh();
		}
		frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_sales_order_items",
			args: {
         	 		"docId":docId,
				"docName":docName
        	},
		async: false,
		callback: function(r) 
      		 { 
			//console.log("Response....."+r.message);
			if(docName == "Sales Order"){
			displayPopUpForSalesOrderItems(r.message,docId,query_report);
			}else if(docName == "Project"){
			  var masterBOM = r.message;
			  console.log("masterBOM....."+masterBOM);
			  if(masterBOM == "null"){
			  frappe.msgprint(__("Master BOM Not Found In The Project."));
			  var master_bom_hidden_filter = frappe.query_report_filters_by_name.master_bom_hidden;
			  master_bom_hidden_filter.df.options = masterBOM;
			  master_bom_hidden_filter.df.default = masterBOM;
			  master_bom_hidden_filter.refresh();
			  master_bom_hidden_filter.set_input(master_bom_hidden_filter.df.default);
			  query_report.refresh();
			  }else{
			  console.log("success.."+masterBOM[0].master_bom);
			  var master_bom = masterBOM[0].master_bom;
			  var master_bom_hidden_filter = frappe.query_report_filters_by_name.master_bom_hidden;
			  master_bom_hidden_filter.df.options = master_bom;
			  master_bom_hidden_filter.df.default = master_bom;
			  master_bom_hidden_filter.refresh();
			  master_bom_hidden_filter.set_input(master_bom_hidden_filter.df.default);
			  query_report.refresh();

			  var status = getBOMStatus(master_bom);
			  if(status.is_active==0){
			   frappe.msgprint(__("Master BOM Is Not Active "+master_bom));
			  } 
			  }
			}else if(docName == "BOM"){
			query_report.refresh();
			var status = getBOMStatus(docId);
			if(status.is_active==0){
			   frappe.msgprint(__("BOM Is Not Active "+docId));
			  } 
			}
			
			
		}//end of call-back function..
		});//end of frappe call..
		}//end of on_change function..
	},
	{
            "fieldname": "hidden_bom",
            "label": __("Hidden BOM"),
            "fieldtype": "Data",
	    "hidden": 1
        },
	{
            "fieldname": "master_bom_hidden",
            "label": __("Master BOM Hidden"),
            "fieldtype": "Data",
	    "hidden": 1
        }
    ],
    onload: function(report) {
	console.log("onload.............");
	console.log("Make Stock Requisition...");
	report.page.add_inner_button(__("Make Stock Requisition"),
                function() {
                  var reporter = frappe.query_reports["BOM Item Warehouse"];
                    reporter.makeStockRequisition(report,"");});

	report.page.add_inner_button(__("Make Stock Transfer"),
                function() {
		    var reporter = frappe.query_reports["BOM Item Warehouse"];
                    reporter.makeStockTransfer(report,"");});
	},
    isNumeric: function( obj ) {
    return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
  },
   makeStockRequisition: function(report, status) {
   var flag = "";
   makeStockOperations(report,status,flag);
 },
   makeStockTransfer(report, status){
   var flag = "True";
   makeStockOperations(report,status,flag);
 }
}

function makeStockOperations(report,status,flag){
var filters = report.get_values();
var docIdVal = frappe.query_report_filters_by_name.docIds.get_value();
    var docName = frappe.query_report_filters_by_name.for.get_value();
    //var filters = report.get_values();
    if (docName == "Project") {
        reference_no = docIdVal;
        warehouse = getWarehouseName(docIdVal);
        //console.log("warehouse.............." + warehouse);
	masterBOMCalculations(filters,flag);
        //makeStockRequistion(filters,"");
    } else if (docName == "Sales Order") {
        warehouse = "";
        reference_no = docIdVal;
        //console.log(" SO reference_no.............." + reference_no);
        var bomList = filters.hidden_bom;
	bomList = bomList.split(",");
        console.log("bomList::" + bomList);
	var workflowStatus = "";
	var stockRequistionFlag = false;
	for(var i=0;i<bomList.length;i++){
	var bom = bomList[i].toString();
	if(bom!="null"){
        var bomDetails = getItemCode(bom);
	var bomItem = bomDetails[0];
	var bom_qty = bomDetails[1];
        var itemDetails = getSalesOrderItemDetails(reference_no);
	//var approval_required=0;
        console.log(" itemDetails.............." + itemDetails);
        if (itemDetails.has(bomItem)) {
            var quantityToMake = filters.qty_to_make;
            var itemQty = itemDetails.get(bomItem);
            var bomItemsList = getBomIitemsLlist();
            if (bomItemsList.length != 0) {
                var pendingQty = 0;
		var bomItemCode = "";
		var required_qty = 0;
		var bom_item_qty = 0;
		var sumOfItemQty = 0;
		var differnce = 0;
                for (var i = 0; i < bomItemsList.length; i++) { 
                    bomItemCode = bomItemsList[i].bom_item;
                    required_qty = bomItemsList[i].required_qty;
                    bom_item_qty = bomItemsList[i].bom_item_qty;
                    sumOfItemQty = getStockRequistionItemQty(reference_no, bomItemCode);
                    if (sumOfItemQty == null) {
                        sumOfItemQty = 0;
                    }
		    differnce = ((itemQty / bom_qty) * bom_item_qty) - (sumOfItemQty);
		    var factor = Math.pow(10,1);
		    differnce = Math.round(differnce * factor)/factor;
		    pendingQty = itemQty - [(sumOfItemQty / bom_item_qty) * bom_qty];
		    if (differnce > 0 && required_qty <= differnce) {
		      console.log("------------------Approval");
                      stockRequistionFlag = true;
		      workflowStatus = "Approved";
                    } else{
		      console.log("------------------Pending Approval");
		      stockRequistionFlag = true;
		      workflowStatus = "Pending Approval";
		    }
		    
		    console.log("bom_qty..." + bom_qty);
                    console.log("bomItemCode..." + bomItemCode);
                    console.log("required_qty..." + required_qty);
                    console.log("bom_item_qty..." + bom_item_qty);
                    console.log("sumOfItemQty..." + sumOfItemQty);
                    console.log(" BOM Item.............." + bomItem);
                    console.log(" BOM itemQty.............." + itemQty);
                    console.log(" QuantityToMake.............." + quantityToMake);
                    console.log(" differnce.............." + differnce);
                    console.log("pendingQty..." + pendingQty);
		    
                } //end of for loop..
            } //end of bomItemsList..
        } //end of inner if...
	}//end of if for bom checking..
	}// for loop....
	if (stockRequistionFlag) {
            makeStockRequistion(filters,workflowStatus,flag);
        }
    } //end of else if..
	else{
	console.log("docName::"+docName);
	bomItemsCalculation(filters,flag);
	}
}

function getWarehouseName(project_name){
var wharehouse = "";
frappe.call({
    method: 'frappe.client.get_value',
    args: {
        doctype: "Project",
        filters: {
            name: ["=", project_name]
        },

        fieldname: ["warehouse"]
    },
    async: false,
    callback: function(r) {
        //console.log("warehouse..." + r.message.warehouse);
	wharehouse = r.message.warehouse;
    }
});
return wharehouse;
}

function getItemCode(bomName){
var bomDetails = [];
frappe.call({
    method: 'frappe.client.get_value',
    args: {
        doctype: "BOM",
        filters: {
            name: ["=", bomName]
        },

        fieldname: ["item","quantity"]
    },
    async: false,
    callback: function(r) {
        console.log("item_code..." + r.message.item);
	console.log("BOM QTY..." + r.message.quantity);
	bomDetails.push(r.message.item);
	bomDetails.push(r.message.quantity);
    }
});
return bomDetails;
}

function getSalesOrderItemDetails(so_Number){
var  salesOrderItemsMap= new Map();
frappe.call({
		method: 			    				    				"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_sales_order_item_details",
		args: {
         	 	"so_Number":so_Number,
        	},
		async: false,
		callback: function(r) 
      		 { 
		 	if(r.message)
	                 {
			    var itemDetails = r.message;
			    var itemCode = "";
			    var qty = 0;
			    var previousQty = 0;
			    console.log("length of item details..." + r.message.length);
			    for(var i=0;i<itemDetails.length;i++){
					itemCode = itemDetails[i].item_code;
					qty = itemDetails[i].qty;
					//console.log("item_code..." + itemDetails[i].item_code);
					//console.log("qty..." + itemDetails[i].qty);
					if(salesOrderItemsMap.has(itemCode)){
						previousQty = salesOrderItemsMap.get(itemCode);
						qty = qty + previousQty;
						salesOrderItemsMap.set(itemCode,qty);
					}else{
						salesOrderItemsMap.set(itemCode,qty);
					}
				}//enf of for loop..
			 }//end of if..
		}//end of callback fun...
		});//end of frappe call..
return salesOrderItemsMap;
}

function getStockRequistionItemQty(so_number,item_code){
var stockRequistionItemQty = "";
frappe.call({
	      method: 			    				    				"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_stock_requistion_item_qty",
	      args: {
         	 	"so_Number":so_number,
			"item_code":item_code,
        	},
	      async: false,
	      callback: function(r) 
      	      { 
	   	if(r.message) {
			console.log("StockRequistionItemQty..." + r.message);
			stockRequistionItemQty = r.message;
		}//end of if..
	      }//end of callback fun...
	});//end of frappe call..
return stockRequistionItemQty;
}
function getStockRequistionBOMItemQty(bom,item_code){
var stockRequistionBOMItemQty = "";
frappe.call({
	      method: 			    				    				"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_stock_requistion_bom_item_qty",
	      args: {
         	 	"bom":bom,
			"item_code":item_code,
        	},
	      async: false,
	      callback: function(r) 
      	      { 
	   	if(r.message) {
			console.log("stockRequistionBOMItemQty..." + r.message);
			stockRequistionBOMItemQty = r.message;
		}//end of if..
	      }//end of callback fun...
	});//end of frappe call..
return stockRequistionBOMItemQty;
}
function getBomIitemsLlist(){
var bomItemsData = "";
frappe.call({
	      method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_bom_items_list",
	      async: false,
	      callback: function(r) 
      	      { 
	   	if(r.message) {
			console.log("#############BOM Item..." + r.message.length);
			bomItemsData = r.message;
		}//end of if..
	      }//end of callback fun...
	});//end of frappe call..
return bomItemsData;
}

function getStockRequistionBOMItemQtyForProject(projectID, item_code){
var stockRequistionBOMItemQty = "";
frappe.call({
	      method: 			    				    				"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_stock_requistion_bom_item_qty_for_project",
	      args: {
         	 	"project":projectID,
			"item_code":item_code,
        	},
	      async: false,
	      callback: function(r) 
      	      { 
	   	if(r.message) {
			console.log("stockRequistionBOMItemQty..." + r.message);
			stockRequistionBOMItemQty = r.message;
		}//end of if..
	      }//end of callback fun...
	});//end of frappe call..
return stockRequistionBOMItemQty;
}
function bomItemsCalculation(filters,flag){
	    reference_no = filters.docIds;
	    warehouse = "";
	    var workflowStatus = "";
            var bomDetails = getItemCode(reference_no);
	    var bomItem = bomDetails[0];
	    var bom_qty = bomDetails[1];
	    var bomItemsList = getBomIitemsLlist();
            var stockRequistionFlag = false;
            if (bomItemsList.length != 0) {
                var pendingQty = 0;
		var bomItemCode = "";
		var required_qty = 0;
		var bom_item_qty = 0;
		var sumOfItemQty = 0;
		var differnce = 0;
		var quantityToMake = filters.qty_to_make;
                for (var i = 0; i < bomItemsList.length; i++) { 
                    bomItemCode = bomItemsList[i].bom_item;
                    required_qty = bomItemsList[i].required_qty;
                    bom_item_qty = bomItemsList[i].bom_item_qty;
                    sumOfItemQty = getStockRequistionBOMItemQty(reference_no, bomItemCode);
                    if (sumOfItemQty == null) {
                        sumOfItemQty = 0;
                    }
		    differnce = ((bom_qty * bom_item_qty)/bom_qty) - (sumOfItemQty);
		    var factor = Math.pow(10,1);
		    differnce = Math.round(differnce * factor)/factor;
		    //pendingQty = bom_qty - [(sumOfItemQty / bom_item_qty)];
		    if (differnce > 0 && required_qty <= differnce) {
		      console.log("------------------Approval");
                      stockRequistionFlag = true;
		      workflowStatus = "Approved";
                    } else{
		      console.log("------------------Pending Approval");
		      stockRequistionFlag = true;
		      workflowStatus = "Pending Approval";
		    }
		    /**
                    console.log("bomItemCode..." + bomItemCode);
		    console.log("bom_qty..." + bom_qty);
                    console.log("required_qty..." + required_qty);
                    console.log("bom_item_qty..." + bom_item_qty);
                    console.log("sumOfItemQty..." + sumOfItemQty);
		    console.log(" differnce.............." + differnce);
                    console.log("pendingQty..." + pendingQty);
		    **/
                } //end of for loop..
                if (stockRequistionFlag) {
		    //approval_required = 0;
                    makeStockRequistion(filters,workflowStatus,flag);
                } 
            } //end of bomItemsList..
}


function masterBOMCalculations(filters,flag){
console.log("Master BOM.............." + filters.master_bom_hidden);
var masterBOM = filters.master_bom_hidden;
var bomDetails = getItemCode(masterBOM);
var bomItem = bomDetails[0];
var bom_qty = bomDetails[1];
var bomItemsList = getBomIitemsLlist();
if (bomItemsList.length != 0) {
    var pendingQty = 0;
    var bomItemCode = "";
    var required_qty = 0;
    var bom_item_qty = 0;
    var sumOfItemQty = 0;
    var differnce = 0;
    for (var i = 0; i < bomItemsList.length; i++) { 
    	bomItemCode = bomItemsList[i].bom_item;
    	required_qty = bomItemsList[i].required_qty;
   	bom_item_qty = bomItemsList[i].bom_item_qty;
   	sumOfItemQty = getStockRequistionBOMItemQtyForProject(reference_no, bomItemCode);
    	if (sumOfItemQty == null) {
    	    sumOfItemQty = 0;
    	}
    	differnce = ((bom_qty * bom_item_qty)/bom_qty) - (sumOfItemQty);
	var factor = Math.pow(10,1);
	differnce = Math.round(differnce * factor)/factor;

	if (differnce > 0 && required_qty <= differnce) {
	    console.log("------------------Approval");
            stockRequistionFlag = true;
	    workflowStatus = "Approved";
        } else{
	    console.log("------------------Pending Approval");
	    stockRequistionFlag = true;
	    workflowStatus = "Pending Approval";
	}

    	console.log("ProjectID..." + reference_no);
   	console.log("bomItemCode..." + bomItemCode);
    	console.log("bom_qty..." + bom_qty);
   	console.log("required_qty..." + required_qty);
    	console.log("bom_item_qty..." + bom_item_qty);
    	console.log("sumOfItemQty..." + sumOfItemQty);
}//end of for loop..
if (stockRequistionFlag) {
       makeStockRequistion(filters,workflowStatus,flag);
} 
}//end of if..
}//end of function..

function makeStockRequistion(filters,workflowStatus,flag) {
    var dialog = new frappe.ui.Dialog({
        title: __("Enter Information For Stock Requisition"),
        fields: [{
                "fieldname": "planning_warehouse",
                "label": __("Planning Warehouse"),
                "fieldtype": "Link",
                "reqd": 1,
                "options": "Warehouse",
                "default": warehouse,
                "get_query": function() {
                    return {
                        'filters': [
                            ['Warehouse', 'is_group', '=', '0']
                        ]
                    }
                }
            },
            {
                "fieldname": "required_on",
                "label": __("Required Date"),
                "fieldtype": "Date",
                "default": get_today()
            }
        ],
        primary_action: function() {
            dialog.hide();
	    var projectFlag = false;
            show_alert(dialog.get_values());
	    var docName = filters.for;
	    if(docName=="Project"){
	     projectFlag = true;
	    }
            //var filters = report.get_values();
            if (filters.company && filters.warehouse && filters.docIds || projectFlag) {
		if(workflowStatus=="Pending Approval"){
			    console.log("workflowStatus::"+workflowStatus);
		     	    frappe.msgprint("Repeated Stock Requisition, needs approval.");
		        }
                var planning_warehouse = dialog.fields_dict.planning_warehouse.get_value();
                var required_on = dialog.fields_dict.required_on.get_value();
                //var reference_no = dialog.fields_dict.reference_no.get_value();
                return frappe.call({
                    method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.make_stock_requisition",
                    args: {
                        "planning_warehouse": planning_warehouse,
                        "required_date": required_on,
                        "reference_no": reference_no,
			"workflowStatus": workflowStatus,
			"check_flag": flag
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route('List', r.message);
                        }
                    } //end of callback fun..
                }) //end of frappe call.
            } else {
                frappe.msgprint("Please select all three filters For Stock Requisition")
            }
        }
    }); //end of dialog box..
    dialog.show();
}

function check_SOItem_Status(item_code){
var status = "";
frappe.call({
	      method: 			    				    				"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_so_item_status",
	      args: {
			"item_code":item_code
        	},
	      async: false,
	      callback: function(r) 
      	      { 
	   	if(r.message) {
			console.log("status..." + r.message.status);
			status = r.message.status;
		}//end of if..
	      }//end of callback fun...
	});//end of frappe call..
return status;
}

function displayPopUpForSalesOrderItems(items,soNumber,query_report){
var dialog_fields = new Array();
var dialogArray = [];
var sortedItems = [];
var status = "";
var sortingItemsFronItemsGroup = [];
for(var i=0;i<items.length;i++){
var item = items[i];
status = check_SOItem_Status(item.toString());
if(status==1){
sortingItemsFronItemsGroup.push(item);
}
}
for(var i=0;i<sortingItemsFronItemsGroup.length;i++){
	var item = sortingItemsFronItemsGroup[i];
	var item_json ={
		"fieldtype":"Check",
		"label": item,
		"fieldname":"item"+ "_" + i,	
		"default": 0,
		"bold":1
		}
	var items_data = JSON.stringify(item_json);
	dialog_fields.push(items_data);
	sortedItems.push(item.toString());
}//end of for loop..
var all_check_json ={
		"fieldtype":"Check",
		"label": "All",
		"fieldname": "all",	
		"default": 0,
		"bold":1
		}
	var all_check_data = JSON.stringify(all_check_json);
	dialog_fields.push(all_check_data);
for(var i=0;i<dialog_fields.length;i++){
dialogArray.push(JSON.parse(dialog_fields[i]));
}
var dialog = new frappe.ui.Dialog({																																																																																																																																																																						
title: __("Select BOM Item"),
fields: dialogArray,
	primary_action: function(){
	dialog.hide();
	var check_args = dialog.get_values();
	var args_length = Object.keys(check_args).length;
	console.log(":check_args json:"+JSON.stringify(check_args));
	console.log(":args_length:"+args_length);
	console.log(":sortedItems_length:"+sortedItems.length);
	var hidden_bom_list = "";
	for(var i=0;i<sortedItems.length;i++){
	var selected_item = "item_"+i;
	var check_val = check_args[selected_item];
	var check_val_for_all = check_args["all"];
	var item_name = sortedItems[i].toString();
	console.log(":item_name:"+item_name);
	console.log(":check_val:"+check_val);
	if(check_val==1 || check_val_for_all == 1){
	 frappe.call({
	 method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_bom_list",
	 args: {
         	 "soNumber":soNumber,
		 "item_code":item_name
        	},
	 async: false,
	 callback: function(r) 
      	  { 
	   if(r.message) {
		console.log("#############BOM Item..." + r.message);
		var bom_status = r.message;
		var bom = bom_status.control_bom;
		console.log("#############BOM ..." + bom);
		if(bom!="null"){
			var status = getBOMStatus(bom);
			if(bom_status.is_default == "so"){
				if(status.docstatus == 2 || status.is_active==0){
					frappe.msgprint(__("ControlBOM Is Not Active "+bom+ "\n"+". Please submit an active BOM and run this report again."));
				}
			}else if(bom_status.is_default == "default"){
					frappe.msgprint(__("ControlBOM For "+item_name+" Is Not Found. Considering Default BOM."));
			}else if(bom_status.is_default == "null"){
					frappe.msgprint(__("There is no active BOM for "+item_name+ "\n"+". Please submit an active BOM and run this report again."));
			}
		}else if(bom == "null"){
		frappe.msgprint(__("There is no active BOM for "+item_name+ "\n"+". Please submit an active BOM and run this report again."));
	        }
		if(hidden_bom_list == ""){
		hidden_bom_list = bom;
		}else{
		hidden_bom_list = hidden_bom_list + "," + bom;
		}
	     }//end of if..
	   }//end of callback fun...
	});//end of frappe call..
	}//end of check_val..
	}//end of for loop..
	console.log("#############hidden_bom_list..." + hidden_bom_list);
	var hidden_bom_filter = frappe.query_report_filters_by_name.hidden_bom;
	hidden_bom_filter.df.options = hidden_bom_list;
	hidden_bom_filter.df.default = hidden_bom_list;
	hidden_bom_filter.refresh();
	hidden_bom_filter.set_input(hidden_bom_filter.df.default);
	query_report.refresh();
	}//end of primary_action
	});//end of dialog box...
	dialog.show();
}


function check_for_whole_number(bomNO,qty,query_report){
var check_for_whole_number = false;
frappe.call({
           method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.check_for_whole_number",
           args: {
                   "bomno": bomNO
           },
	   async: false,
           callback: function(r) {
           if (r.message && qty % 1 != 0) {
	    //console.log("Quantity to Make should be whole number..");
            //frappe.msgprint(__("Quantity to Make should be whole number"));
	    check_for_whole_number = true;
            frappe.query_report_filters_by_name.qty_to_make.set_input("1");
	    query_report.refresh();
            } else {
	    check_for_whole_number = false;
            query_report.refresh();
            }
            }//end of callback fun..
           })//end of frappe call..
return check_for_whole_number;
}

function getBOMStatus(bom){
var status = "";
frappe.call({
    method: 'frappe.client.get_value',
    args: {
        doctype: "BOM",
        filters: {
            name: ["=", bom]
        },
        fieldname: ["docstatus","is_active"]
    },
    async: false,
    callback: function(r) {
        //console.log("status..." + r.message.docstatus);
        status = r.message;
    }
});
return status;
}

	
