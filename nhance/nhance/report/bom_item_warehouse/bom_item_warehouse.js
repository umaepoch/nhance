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
            "fieldname": "bom",
            "label": __("BOM"),
            "fieldtype": "Select",
            "width": "50",	
	    "options": getBOMList(),
	    "default": ""
        },
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
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item"
        },

        {
            "fieldname": "include_exploded_items",
            "label": __("Include Exploded Items"),
            "fieldtype": "Data",
            "default": "Y"

        },
	{
	    "fieldname": "current_stock_balance",
            "label": __("Current Stock Balance to be considered?"),
            "fieldtype": "Check",
            "default": "0"
	},
        {
            "fieldname": "qty_to_make",
            "label": __("Quantity to Make"),
            "fieldtype": "Data",
            "default": "1",
            "on_change": function(query_report) {

                var qty = frappe.query_report_filters_by_name.qty_to_make.get_value();
		var bomNO = frappe.query_report_filters_by_name.bom.get_value();
		if(bomNO == null){
		bomNO = frappe.query_report_filters_by_name.control_bom.get_value();
		}
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
                return frappe.call({
                    method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.check_for_whole_number",
                    args: {
                        "bomno": bomNO
                    },
                    callback: function(r) {
                        if (r.message && qty % 1 != 0) {
                            frappe.msgprint(__("Quantity to Make should be whole number"));
                            frappe.query_report_filters_by_name.qty_to_make.set_input("1");
			    query_report.trigger_refresh();

                        } else {
                            query_report.trigger_refresh();
                        }
                    }
                })
            }
        },
	 {
            "fieldname":"sales_and_project",
            "label": __("For"),
            "fieldtype": "Select",
            "options": ["Sales Order", "Project"]
        },
	{
	   "fieldname":"docIds",
	   "label": __("Doc Ids"),
	   "fieldtype": "Select"
	}
	,
	{
	   "fieldname":"so_items",
	   "label": __("Sales Order Items"),
	   "fieldtype": "Select"
	},
	{
	   "fieldname":"control_bom",
	   "label": __("Control BOM"),
	   "fieldtype": "Select"
	}
    ],
    onload: function(report) {
	//on changing of bom
	frappe.query_report_filters_by_name.bom.$input.on("change", function(){
	console.log("changing of bom.............");
	var sales_and_project_filter = frappe.query_report_filters_by_name.sales_and_project;
	sales_and_project_filter.df.read_only = 1;
	sales_and_project_filter.refresh();

	var docIds_filter = frappe.query_report_filters_by_name.docIds;
	docIds_filter.df.read_only = 1;
	docIds_filter.refresh();

	var so_items_filter = frappe.query_report_filters_by_name.so_items;
	so_items_filter.df.read_only = 1;
	so_items_filter.refresh();
	
	var control_bom_filter = frappe.query_report_filters_by_name.control_bom;
	control_bom_filter.df.read_only = 1;
	control_bom_filter.refresh();
	});//end of on_change bom..

	//on change function start..
	frappe.query_report_filters_by_name.sales_and_project.$input.on("change", function(){
	var docName = frappe.query_report_filters_by_name.sales_and_project.get_value();
	if(docName=="Sales Order" || docName=="Project"){
	var bom_filter = frappe.query_report_filters_by_name.bom;
	bom_filter.df.read_only = 1;
	bom_filter.refresh();
	}
	console.log("on change...."+docName);
	if(docName=="Project"){
	var so_items_filter = frappe.query_report_filters_by_name.so_items;
	so_items_filter.df.read_only = 1;
	so_items_filter.refresh();

	var control_bom_filter = frappe.query_report_filters_by_name.control_bom;
	control_bom_filter.df.read_only = 1;
	control_bom_filter.refresh();
	}

	frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.fetch_Records",
			args: {
         	 		"docName":docName,
        	},
		async: false,
		callback: function(r) 
      		 { 
			var docIds_filter = frappe.query_report_filters_by_name.docIds;
			docIds_filter.df.options = r.message;
			docIds_filter.df.default = "";
			docIds_filter.refresh();
			docIds_filter.set_input(docIds_filter.df.default);
		}
		});//end of frappe call..
	});//end of on_change function..

	//on change function start..
	frappe.query_report_filters_by_name.docIds.$input.on("change", function(){
	var soNumber = frappe.query_report_filters_by_name.docIds.get_value();
	console.log("on change..soNumber.."+soNumber);
	//......
	var control_bom_filter = frappe.query_report_filters_by_name.control_bom;
	control_bom_filter.df.options = [];
	control_bom_filter.df.default = "";
	control_bom_filter.refresh();
	control_bom_filter.set_input(control_bom_filter.df.default);
	frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_sales_order_items",
			args: {
         	 		"sales_order":soNumber,
        	},
		async: false,
		callback: function(r) 
      		 { 
			console.log("Response....."+r.message);
			var so_items_filter = frappe.query_report_filters_by_name.so_items;
			so_items_filter.df.options = r.message;
			so_items_filter.df.default = "";
			so_items_filter.refresh();
			so_items_filter.set_input(so_items_filter.df.default);
		}
		});//end of frappe call..
	});//end of on_change function..

	//on change function start..
	frappe.query_report_filters_by_name.so_items.$input.on("change", function(){
	var so_item = frappe.query_report_filters_by_name.so_items.get_value();
	var soNumber = frappe.query_report_filters_by_name.docIds.get_value();
	console.log("on change..so_item.."+so_item);
	frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_so_bom_list",
			args: {
				"sales_order":soNumber,
         	 		"item_code":so_item,
        	},
		async: false,
		callback: function(r) 
      		 { 
			console.log("control_bom Response....."+r.message.length);
			var bomList = [];
			if(r.message){
			for(var i=0;i<r.message.length;i++){
			console.log("for control_bom Response....."+r.message[i].name);
			bomList.push(r.message[i].name);
			}
			if(r.message.length>1){
			var control_bom_filter = frappe.query_report_filters_by_name.control_bom;
			control_bom_filter.df.options = bomList;
			control_bom_filter.df.default = "";
			control_bom_filter.refresh();
			control_bom_filter.set_input(control_bom_filter.df.default);
			}else{
			var control_bom_filter = frappe.query_report_filters_by_name.control_bom;
			control_bom_filter.df.options = r.message[0].name;
			control_bom_filter.df.default = r.message[0].name;
			control_bom_filter.refresh();
			control_bom_filter.set_input(control_bom_filter.df.default);
			}
			}
		}
		});//end of frappe call..
	});//end of on_change function..
	
	console.log("Make Stock Requisition...");
	report.page.add_inner_button(__("Make Stock Requisition"),
                function() {
                  var reporter = frappe.query_reports["BOM Item Warehouse"];
                    reporter.makeStockRequisition(report,"");});
	},
    isNumeric: function( obj ) {
    return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
  },
   makeStockRequisition: function(report, status) {
    var docIdVal = frappe.query_report_filters_by_name.docIds.get_value();
    var docName = frappe.query_report_filters_by_name.sales_and_project.get_value();
    var filters = report.get_values();
    if (docName == "Project") {
        reference_no = "";
        warehouse = getWarehouseName(docIdVal);
        console.log("warehouse.............." + warehouse);
        makeStockRequistion(filters,"");
    } else if (docName == "Sales Order") {
        warehouse = "";
        reference_no = docIdVal;
        console.log(" SO reference_no.............." + reference_no);
        var bom = filters.control_bom;
        console.log("bom::" + bom);
	var workflowStatus = "";
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
            var stockRequistionFlag = false;
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
                if (stockRequistionFlag) {
		    //approval_required = 0;
                    makeStockRequistion(filters,workflowStatus);
                } else if (pendingQty == 0) {
                    frappe.msgprint("Stock Requisition Is Already Done!!!");
                } else {
                    //frappe.msgprint("Stock Requisition Should Not Exceed More Than: " + pendingQty);
		    //frappe.msgprint("Repeated Stock Requisition, Needs Approval.");
		    /**approval_required = 1;
		    makeStockRequistion(filters,approval_required);**/
                }
            } //end of bomItemsList..
        } //end of inner if...
    } //end of else..
	else{
	var bom = filters.bom;
	console.log("bom::"+bom);
	bomItemsCalculation(filters);
	}
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
					console.log("item_code..." + itemDetails[i].item_code);
					console.log("qty..." + itemDetails[i].qty);
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
function getBOMList(){
var list=[];
frappe.call({
		method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.get_bom_list",			        		
		async: false,
		callback: function(r) 
      		 { 
			list = r.message;
		}
		});//end of frappe call..
return list;
}
function bomItemsCalculation(filters){
	    reference_no = filters.bom;
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
                    console.log("bomItemCode..." + bomItemCode);
		    console.log("bom_qty..." + bom_qty);
                    console.log("required_qty..." + required_qty);
                    console.log("bom_item_qty..." + bom_item_qty);
                    console.log("sumOfItemQty..." + sumOfItemQty);
		    console.log(" differnce.............." + differnce);
                    console.log("pendingQty..." + pendingQty);
                } //end of for loop..
                if (stockRequistionFlag) {
		    //approval_required = 0;
                    makeStockRequistion(filters,workflowStatus);
                } else if (pendingQty == 0) {
                    frappe.msgprint("Stock Requisition Is Already Done!!!");
                } else {
                    //frappe.msgprint("Stock Requisition Should Not Exceed More Than: " + pendingQty);
		    //frappe.msgprint("Repeated Stock Requisition, Needs Approval.");
		    /**approval_required = 1;
		    makeStockRequistion(filters,approval_required);**/
                }
            } //end of bomItemsList..
}
function makeStockRequistion(filters,workflowStatus) {
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
            //{"fieldtype": "Date", "label": __("Required Date"), "fieldname": "required_on", "reqd": 1},
            {
                "fieldname": "required_on",
                "label": __("Required Date"),
                "fieldtype": "Date",
                "default": get_today()
            },
            //{"fieldname": "reference_no", "label": __("Reference Number"), "fieldtype": "Data"}
        ],
        primary_action: function() {
            dialog.hide();
	    var projectFlag = false;
            show_alert(dialog.get_values());
	    var docName = filters.sales_and_project;
	    if(docName=="Project"){
	     projectFlag = true;
	    }
            //var filters = report.get_values();
            if (filters.company && filters.warehouse && filters.bom || filters.control_bom || projectFlag) {
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
