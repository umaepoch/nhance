// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Project Material Ordering Tool"] = {
    "filters": [{
        "fieldname": "project",
        "label": __("Project"),
        "fieldtype": "Link",
        "options": "Project",
        "reqd": 1,
        "on_change": function(query_report) {
            var project = frappe.query_report.get_filter_value("project");
            validate_project_details(project, query_report);
        }
    }, {
        "fieldname": "source_warehouse",
        "label": __("Source Warehouse"),
        "fieldtype": "Link",
        "options": "Warehouse"
    }],
    onload: function(report) {
        console.log("Make PO and Transfer Existing/Required Quantity..........");
        report.page.add_inner_button(__("Make PO and Transfer Existing/Required Quantity"),
            function() {
                var reporter = frappe.query_reports["Project Material Ordering Tool"];
                reporter.make_PO_and_transfer_qty(report);
            });
    },
    make_PO_and_transfer_qty: function(report) {
        make_PO_and_transfer_qty(report);
    }
}

function validate_project_details(project, query_report) {
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Project",
            filters: {
                name: ["=", project]
            },

            fieldname: ["reserve_warehouse", "master_bom", "project_warehouse"]
        },
        async: false,
        callback: function(r) {
            //console.log("validate_project_details..." + JSON.stringify(r.message));
            var master_bom = r.message.master_bom;
            var reserve_warehouse = r.message.reserve_warehouse;
            var project_warehouse = r.message.project_warehouse;

            if (master_bom == null || reserve_warehouse == null || project_warehouse == null) {
                frappe.query_report.refresh();
                frappe.msgprint(__("The Project Master for Project " + project + " is not updated with Master BOM/Reserve Warehouse/Project Warehouse. Please update these values in the Project Master and run this report again."));
            } else {
                frappe.query_report.refresh();
            }
        }
    });
}

function make_PO_and_transfer_qty(report) {
    var filters = report.get_values();
    var source_warehouse = filters.source_warehouse;
    var project = filters.project;
    var reportData = getReportData();
    var materialTransferMap = new Map();
    var purchaseOrderMap = new Map();

    var reserve_whse = getReserveWarehouse(project);

    console.log("...make_PO_and_transfer_qty..........");
    console.log("...source_warehouse.........." + source_warehouse);

    for (var i = 0; i < reportData.length; i++) {
        var materialItems = {};
        var poItems = {};
        var materialList = [];
        var purchaseItemsList = [];
        var item_code = reportData[i]['item_code'];
        var stock_uom = reportData[i]['stock_uom'];
        var po_uom = reportData[i]['po_uom'];
        var sreq_no = reportData[i]['sreq_no'];
        var tmp_po_qty = reportData[i]['po_qty'];
        var mt_qty = reportData[i]['mt_qty'];
        var supplier = reportData[i]['supplier'];
        var bom = reportData[i]['bom'];
	var fulfilled_qty = reportData[i]['fulfilled_qty'];
        var conversion_factor = reportData[i]['conversion_factor'];
	var po_qty = 0;

	var purchase_uom = getPurchaseUom(item_code);	
	var check_flag = get_UOM_Details(stock_uom);

	if(check_flag){
		var req_po_qty = 0;
		var check_qty = Math.floor(tmp_po_qty);
        	check_qty = tmp_po_qty - check_qty;

        	if (check_qty != 0.0) {
            		req_po_qty = Math.ceil(tmp_po_qty);
            		req_po_qty = parseInt(tmp_po_qty);
        	} else {
            		req_po_qty = parseInt(tmp_po_qty);
        	}

		if (purchase_uom != null && purchase_uom != undefined && purchase_uom != ""){
			var cf = fetch_conversion_factor(item_code,purchase_uom);
			if (cf != 0){
				po_qty = req_po_qty/conversion_factor;
			}else{
				frappe.throw(__("The Conversion Factor for UOM: "+ purchase_uom.toString()  +" for Item: "+ item_code.toString() +" is not defined. Please define the Conversion Factor or remove the Purchase UOM and try again."));
			}
		}else{
			po_qty = req_po_qty;
		}
		console.log("...tmp_po_qty....testing......" + tmp_po_qty);
        	console.log("...req_po_qty....testing......" + req_po_qty);
		console.log("...po_qty....testing......" + po_qty);
	}else{
		po_qty = tmp_po_qty;
	}

       
        if (bom == null || bom == undefined) {
            bom = "";
        }

        if (mt_qty > 0 && fulfilled_qty > 0) {
            materialItems['item_code'] = item_code;
            materialItems['sreq_no'] = sreq_no;
            materialItems['s_warehouse'] = source_warehouse;
            materialItems['t_warehouse'] = reserve_whse;
            materialItems['qty'] = mt_qty;
            materialItems['item_code'] = item_code;
            materialItems['stock_uom'] = stock_uom;
            materialItems['uom'] = po_uom;
            materialItems['bom'] = bom;
            materialItems['project'] = project;

            if (materialTransferMap.has(sreq_no)) {
                var arrList = materialTransferMap.get(sreq_no);
                arrList.push(materialItems);
                materialTransferMap.set(sreq_no, arrList);
            } else {
                materialList.push(materialItems);
                materialTransferMap.set(sreq_no, materialList);
            }
        }


        if (po_qty > 0) {
            var rate = 0;
            var itemPriceSettings = getItemPriceBasedOn();
            var itemRate = itemPriceSettings['item_rate'];
            var item_price_by = itemPriceSettings['item_price_by'];
            var price_list_by = itemPriceSettings['price_list_by'];

            if (item_price_by == "Valuation Rate (Item Master)") {
                rate = getItemValuationRate(item_code);
                if (rate == 0) {
                    price_list_by = "Standard Buying";
                    rate = getItemValuationRateFromPriceList(item_code, price_list_by);
                    if (rate == 0) {
                        rate = getItemLastPurchasePrice(item_code, po_uom);
                        if (rate == 0) {
                            rate = getItemValuationRateFromStockBalance(item_code);
                            if (rate == 0) {
                                rate = itemRate;
                            } //end of getItemValuationRateFromPriceList..
                        } //end of getItemValuationRateFromStockBalance..
                    } //end of getItemLastPurchasePrice..
                } //end of getItemValuationRate..
            } else if (item_price_by == "Last Purchase Price") {
                rate = getItemLastPurchasePrice(item_code, po_uom);
                if (rate == 0) {
                    rate = getItemValuationRateFromStockBalance(item_code);
                    if (rate == 0) {
                        rate = getItemValuationRate(item_code);
                        if (rate == 0) {
                            price_list_by = "Standard Buying";
                            rate = getItemValuationRateFromPriceList(item_code, price_list_by);
                            if (rate == 0) {
                                rate = itemRate;
                            } //end of getItemValuationRateFromPriceList..
                        }
                    }
                }
            } else if (item_price_by == "Valuation Rate (Stock Balance)") {
                rate = getItemValuationRateFromStockBalance(item_code);
                if (rate == 0) {
                    rate = getItemValuationRate(item_code);
                    if (rate == 0) {
                        price_list_by = "Standard Buying";
                        rate = getItemValuationRateFromPriceList(item_code, price_list_by);
                        if (rate == 0) {
                            rate = getItemLastPurchasePrice(item_code, po_uom);
                            if (rate == 0) {
                                rate = itemRate;
                            }
                        }
                    }
                }
            } else if (item_price_by == "Price List") {
                price_list_by = "Standard Buying";
                rate = getItemValuationRateFromPriceList(item_code, price_list_by);
                if (rate == 0) {
                    rate = getItemLastPurchasePrice(item_code, po_uom);
                    if (rate == 0) {
                        rate = getItemValuationRateFromStockBalance(item_code);
                        if (rate == 0) {
                            rate = getItemValuationRate(item_code);
                            if (rate == 0) {
                                rate = itemRate;
                            }
                        }
                    }
                }
            }

            poItems['item_code'] = item_code;
            poItems['sreq_no'] = sreq_no;
            poItems['supplier'] = supplier;
            poItems['qty'] = po_qty;
            poItems['bom'] = bom;
            poItems['warehouse'] = reserve_whse;
            poItems['price_list_rate'] = rate;
            poItems['bom'] = bom;
            poItems['project'] = project;
            poItems['conversion_factor'] = conversion_factor;

            if (purchaseOrderMap.has(sreq_no)) {
                var arrList = purchaseOrderMap.get(sreq_no);
                arrList.push(poItems);
                purchaseOrderMap.set(sreq_no, arrList);
            } else {
                purchaseItemsList.push(poItems);
                purchaseOrderMap.set(sreq_no, purchaseItemsList);
            }
        }
    } //end of for loop...

    //Creating PO's..
    for (const entry of purchaseOrderMap.entries()) {
        var supplier_map = new Map();
        var sreq_no = entry[0];
        var no_supplier_items = [];
        var po_items_list = purchaseOrderMap.get(sreq_no);

        for (var i = 0; i < po_items_list.length; i++) {
            var supplier = po_items_list[i].supplier;
            if (supplier == null || supplier == "" || supplier == undefined) {
                no_supplier_items.push(po_items_list[i]);
            } else {
                if (supplier_map.has(supplier)) {
                    var update_list = supplier_map.get(supplier);
                    update_list.push(po_items_list[i]);
                    supplier_map.set(supplier, update_list);
                } else {
                    var new_list = [];
                    new_list.push(po_items_list[i]);
                    supplier_map.set(supplier, new_list);
                }
            }
        }

        if (no_supplier_items.length != 0) {
            var supplier = "Generic Supplier";
            console.log("no_supplier_items--------" + JSON.stringify(no_supplier_items));
            makePO(sreq_no, supplier, no_supplier_items);
        }

        for (const entry of supplier_map.entries()) {
            var supplier = entry[0];
            var supplier_items = supplier_map.get(supplier);
            console.log("supplier_items--------" + JSON.stringify(supplier_items));
            makePO(sreq_no, supplier, supplier_items);
        }

    } //end of purchaseOrderMap

 //Creating Material Transfer of Stock Entry..
    for (const entry of materialTransferMap.entries()) {
        var sreq_no = entry[0];
        var mt_list = materialTransferMap.get(sreq_no);
        makeMaterialTransfer(sreq_no, mt_list);
    }
    //end of Material Transfer of Stock Entry..


} //end of make_PO_and_transfer_qty..


function fetch_conversion_factor(item_code,purchase_uom){
var cf = 0.0;
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.fetch_conversion_factor",
        args: {
            "parent": item_code,
            "uom": purchase_uom
        },
        async: false,
        callback: function(r) {
            console.log("conversion_factor..." + r.message);
            cf = r.message;

        }
    });
    return cf;
}

function makePO(sreq_no, supplier, po_items) {
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.make_purchase_orders",
        args: {
            "sreq_no": sreq_no,
            "supplier": supplier,
            "po_items": po_items
        },
        async: false,
        callback: function(r) {} //end of call-back function..
    }); //end of frappe call..
}


function makeMaterialTransfer(sreq_no, mt_list) {
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.make_stock_entry",
        args: {
            "sreq_no": sreq_no,
            "mt_list": mt_list
        },
        async: false,
        callback: function(r) {} //end of call-back function..
    }); //end of frappe call..
}




function getItemValuationRate(item_code) {
    var valuation_rate = 0.0;
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Item",
            filters: {
                item_code: ["=", item_code]
            },

            fieldname: ["valuation_rate"]
        },
        async: false,
        callback: function(r) {
            //console.log("valuation_rate..." + r.message.valuation_rate);
            valuation_rate = r.message.valuation_rate;

        }
    });
    return valuation_rate;
}


function getItemLastPurchasePrice(item_code, po_uom) {
    var lastPurchasePrice = 0.0;
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.fetch_last_purchase_price",
        args: {
            "item_code": item_code,
            "uom": po_uom
        },
        async: false,
        callback: function(r) {
            //console.log("LastPurchaserice::" + JSON.stringify(r.message));
            lastPurchasePrice = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return lastPurchasePrice;
}

function getItemValuationRateFromStockBalance(item_code) {
    var rate = 0.0;
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.fetch_stock_balance_valuation_rate",
        args: {
            "item_code": item_code
        },
        async: false,
        callback: function(r) {
            //console.log("ItemValuationRateFromStockBalance::" + JSON.stringify(r.message));
            rate = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return rate;
}


function getItemValuationRateFromPriceList(item_code, price_list_by) {
    var rate = 0.0;
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.fetch_valuation_rate_from_item_price",
        args: {
            "item_code": item_code,
            "price_list": price_list_by
        },
        async: false,
        callback: function(r) {
            //console.log("ItemValuationRateFromPriceList::" + JSON.stringify(r.message));
            rate = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return rate;
}

function getItemPriceBasedOn() {
    var price_details = {};
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.fetch_item_price_settings_details",
        async: false,
        callback: function(r) {
            //console.log("fetch_item_price_settings_details::" + JSON.stringify(r.message));
            //console.log("item_price_by::" + r.message.item_price_by);
            price_details['item_price_by'] = r.message.item_price_by;
            price_details['item_rate'] = r.message.item_rate;
        } //end of call-back function..
    }); //end of frappe call..

    return price_details;
}

function getReserveWarehouse(project) {
    var r_warehouse = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Project",
            filters: {
                name: ["=", project]
            },
            fieldname: ["reserve_warehouse"]
        },
        async: false,
        callback: function(r) {
            //console.log("reserve_warehouse..." + r.message.reserve_warehouse);
            r_warehouse = r.message.reserve_warehouse;

        }
    });
    return r_warehouse;

}

function getReportData() {
    var reportData = [];
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.get_report_data",
        async: false,
        callback: function(r) {
            //console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}


function get_UOM_Details(stock_uom) {
    var whole_number_in_stock_transactions_flag = false;
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "UOM",
            filters: {
                uom_name: ["=", stock_uom]
            },
            fieldname: ["must_be_whole_number", "needs_to_be_whole_number_in_stock_transactions"]
        },
        async: false,
        callback: function(r) {
            var whole_number_in_stock_transactions = r.message.needs_to_be_whole_number_in_stock_transactions;
            if (whole_number_in_stock_transactions == 1) {
                whole_number_in_stock_transactions_flag = true;
            }
        }
    });
return whole_number_in_stock_transactions_flag;
}


function getPurchaseUom(item_code){
var purchase_uom = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Item",
            filters: {
		item_code: ["=", item_code]
            },

            fieldname: ["purchase_uom"]
        },
        async: false,
        callback: function(r) {
		if(r.message){
            	purchase_uom = r.message.purchase_uom;
		}else{
		purchase_uom =null;
		}
        }
    });

return purchase_uom;
}
