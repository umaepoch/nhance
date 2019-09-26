// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */
var flag = false;
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
        //console.log("Make PO and Transfer Existing/Required Quantity..........");
        report.page.add_inner_button(__("Make PO and Transfer Existing/Required Quantity"),
            function() {

                var reporter = frappe.query_reports["Project Material Ordering Tool"];
                reporter.make_PO_and_transfer_qty(report);
            });
    },
    make_PO_and_transfer_qty: function(report) {
	frappe.query_report.refresh();
	var doc_name1 = "Supplier";
	var supplier_fields = get_supplier_field(doc_name1);
	//console.log("address_fields-----------"+address_fields);
	//console.log("supplier flag========="+supplier_fields);
	if (supplier_fields == 1) {
        	make_PO_and_transfer_qty(report);
	}
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
    flag = false;
    var filters = report.get_values();
    var source_warehouse = filters.source_warehouse;
    var project = filters.project;
    var project_filter = frappe.query_report.get_filter_value("project");
    var swh_filter = frappe.query_report.get_filter_value("source_warehouse");
    var reportData = getReportData(project_filter,swh_filter);
    var materialTransferMap = new Map();
    var purchaseOrderMap = new Map();

    var reserve_whse = getReserveWarehouse(project);
/**
    console.log("...make_PO_and_transfer_qty..........");
    console.log("...source_warehouse.........." + source_warehouse);
    console.log("reportData-----length---" + reportData.length);
**/

    var checkPurchaseItemsList = [];
    var materialTransferList = [];

    for (var i = 0; i < reportData.length; i++) {
        var materialItems = {};
        var poItems = {};
        var materialList = [];
        var purchaseItemsList = [];
        var item_code = reportData[i]['item_code'];
        var stock_uom = reportData[i]['stock_uom'];
        var po_uom = reportData[i]['po_uom'];
        var sreq_no = reportData[i]['sreq_no'];
        var po_qty = reportData[i]['po_qty'];
        var mt_qty = reportData[i]['mt_qty'];
        var supplier = reportData[i]['supplier'];
        var bom = reportData[i]['bom'];
        var fulfilled_qty = reportData[i]['fulfilled_qty'];
        var conversion_factor = reportData[i]['conversion_factor'];
	var last_purchase_price = reportData[i]['last_purchase_price'];

        if (bom == null || bom == undefined) {
            bom = "";
        }
	
        if (mt_qty > 0) {
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
		materialTransferList.push(arrList);
            } else {
                materialList.push(materialItems);
                materialTransferMap.set(sreq_no, materialList);
		materialTransferList.push(materialList);
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
            poItems['stock_uom'] = stock_uom;
            poItems['supplier'] = supplier;
            poItems['qty'] = po_qty;
            poItems['bom'] = bom;
            poItems['warehouse'] = reserve_whse;
            poItems['price_list_rate'] = rate;
            poItems['bom'] = bom;
            poItems['project'] = project;
            poItems['conversion_factor'] = conversion_factor;
	    poItems['last_purchase_price']= last_purchase_price;

            if (purchaseOrderMap.has(sreq_no)) {
                var arrList = purchaseOrderMap.get(sreq_no);
                arrList.push(poItems);
                purchaseOrderMap.set(sreq_no, arrList);
                checkPurchaseItemsList.push(arrList);
            } else {
                purchaseItemsList.push(poItems);
                purchaseOrderMap.set(sreq_no, purchaseItemsList);
                checkPurchaseItemsList.push(purchaseItemsList);
            }
        }
    } //end of for loop...
    
    console.log("PurchaseItemsList-----length---" + checkPurchaseItemsList.length);
    console.log("MaterialTransferList-----length---" + materialTransferList.length);
    if(checkPurchaseItemsList.length == 0 && materialTransferList.length == 0){
		frappe.msgprint("All quantities of items related to this project have been ordered and/or transfered, Nothing to do!");
	}
    if (checkPurchaseItemsList.length != 0) {
        if (!flag) {
            var dialog = new frappe.ui.Dialog({
                title: __("Select Round Type"),
                fields: [
                    {
                      'fieldname': 'round_up_fractions',
                      'fieldtype': 'Check',
                      "label": __("Round Up Fractions")
                    },
                    {
                        'fieldname': 'round_fractions',
                        'fieldtype': 'Check',
                        "label": __("Round Fractions")
                    },

                    {
                        'fieldname': 'round_down_fractions',
                        'fieldtype': 'Check',
                        "label": __("Round Down Fractions")
                    },
                    {
                        'fieldname': 'do_nothing',
                        'fieldtype': 'Check',
                        "label": __("Do Nothing")
                    }
                ],
                primary_action: function() {
                    dialog.hide();
                    var check_args = dialog.get_values();
		console.log("logs are working fine");

                    //Creating PO's..
                    for (const entry of purchaseOrderMap.entries()) {
                        var supplier_map = new Map();
                        var sreq_no = entry[0];
                        var no_supplier_items = [];
                        var po_items_list = purchaseOrderMap.get(sreq_no); //key will be sreqno

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
                            for (var i = 0; i < no_supplier_items.length; i++) {
                                var stock_uom = no_supplier_items[i].stock_uom;
                                var qty = no_supplier_items[i].qty;
                                var check_flag = get_UOM_Details(stock_uom);
                                //console.log("no_supplier_items of qty------------" + no_supplier_items[i].qty);
                               // console.log("check_flag------------" + check_flag);
                                if (check_flag) {
                                      var processedQty = processQuantity(check_args, qty);
                                      //console.log("no_supplier_items of processedQty is--------------::" + processedQty);

                                      var purchase_uom = getPurchaseUom(no_supplier_items[i].item_code.toString());

                                      //******************
                                      if( purchase_uom == null){
                                          console.log("********no suppliers Purchase uom is null for item : "+no_supplier_items[i].item_code.toString() );
                                          no_supplier_items[i].qty = processedQty ;
                                          //no_supplier_items[i].qty = 20 ; //testing


                                      }
                                      else{
                                        var puom_qty = check_puom(purchase_uom,no_supplier_items[i].item_code, processedQty);
                                        console.log("no_supplier_items of puom_qty is-------------::" + puom_qty);
					var processedQty1 = processQuantity(check_args, puom_qty);
                                        no_supplier_items[i].qty = processedQty1;
                                      }

                                      //**********************


                                } //end of if..
                            } //end of for loop..

                            console.log("*************Suresh no_supplier_items--------" + JSON.stringify(no_supplier_items));
                            makePO(sreq_no, supplier, no_supplier_items);
                        }

                        for (const entry of supplier_map.entries()) {
                            var supplier = entry[0];
                            var supplier_items = supplier_map.get(supplier);
                            for (var i = 0; i < supplier_items.length; i++) {
                                var stock_uom = supplier_items[i].stock_uom;
                                var qty = supplier_items[i].qty;
                                var check_flag = get_UOM_Details(stock_uom);
                               // console.log("supplier_items of qty------------" + supplier_items[i].qty);
                               // console.log("check_flag------------" + check_flag);

                                if (check_flag) {
                                          //console.log("item code ------------"+supplier_items[i].item_code.toString());
                                          var processedQty = processQuantity(check_args, qty);
                                          //console.log("supplier_items of processedQty is---------------::" + processedQty);
                                          var purchase_uom = getPurchaseUom(supplier_items[i].item_code.toString());

                                        //*********
                                        if( purchase_uom == null){
                                          console.log("****supplier_items   Purchase uom is null for item : "+ supplier_items[i].item_code.toString() );

                                          supplier_items[i].qty = processedQty ;
                                         // supplier_items[i].qty = 20 ; //testing

                                        }
                                        else{
					  console.log("processedQty--------------"+processedQty);
                                          var puom_qty = check_puom(purchase_uom,supplier_items[i].item_code, processedQty);
					    var processedQty1 = processQuantity(check_args, puom_qty);
                                          console.log("supplier_items of puom_qty is-------------::" + processedQty1);
                                          supplier_items[i].qty = processedQty1
					

                                        }
                                        //********

                                          ;
                                } //end of if..

                            } //end of for loop..
                            console.log("supplier_items--------" + JSON.stringify(supplier_items));
                            makePO(sreq_no, supplier, supplier_items);
                        }

                    } //end of purchaseOrderMap
                }
            }); //end of dialog box...
            dialog.show();
            flag = true;
        }
    }

    //Creating Material Transfer of Stock Entry..
    for (const entry of materialTransferMap.entries()) {
        var sreq_no = entry[0];
        var mt_list = materialTransferMap.get(sreq_no);
        makeMaterialTransfer(sreq_no, mt_list);
    }
    //end of Material Transfer of Stock Entry..
} //end of make_PO_and_transfer_qty..



function check_puom(purchase_uom, item_code,req_po_qty) {
    if (purchase_uom != null && purchase_uom != undefined && purchase_uom != "") {
        var cf = fetch_conversion_factor(item_code, purchase_uom);
	//console.log("item-code-----------------"+item_code);
	//console.log("cf-----------------------"+cf);
        if (cf != 0) {
            po_qty = req_po_qty / cf;
	    return po_qty;
        } else {
            frappe.throw(__("The Conversion Factor for UOM: " + purchase_uom.toString() + " for Item: " + item_code.toString() + " is not defined. Please define the Conversion Factor or remove the Purchase UOM and try again."));
        }
    }
}

function processQuantity(check_args, qty) {
    var quantity = 0;
    if (check_args.round_up_fractions == 1) {
	console.log("round up ");
        var check_qty = Math.floor(qty);
	console.log("check_qty----------"+check_qty);
        check_qty = qty - check_qty;
	console.log("check_qty after subtract with qty--------------"+check_qty);
        if (check_qty != 0.0) {
            quantity = Math.ceil(qty);
            quantity = parseInt(quantity);
        } else {
            quantity = parseInt(qty);
        }

    } else if (check_args.round_down_fractions == 1) {
	console.log("round_down_fractions");
        quantity = parseInt(qty);
    } else if (check_args.round_fractions == 1) {
	console.log("round_fractions");
        quantity = Math.round(qty);
    }
    if (quantity == 0) {
        quantity = qty;
    }
    console.log("quantity::" + quantity);
    return quantity;
}

function fetch_conversion_factor(item_code, purchase_uom) {
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

    //console.log("supplier----" + supplier);
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

function getReportData(project_filter,swh_filter) {
    var reportData = [];
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.get_report_data",
	 args: {
            "project_filter":project_filter,
	    "swh_filter":swh_filter
        },
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


function getPurchaseUom(item_code) {
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
            if (r.message) {
                purchase_uom = r.message.purchase_uom;
            } else {
                purchase_uom = null;
            }
        }
    });

    return purchase_uom;
}
function get_supplier_field(doc_name){
    var reportData = 0;
    frappe.call({
        method: "nhance.nhance.report.project_material_ordering_tool.project_material_ordering_tool.fields",
	 args: {
            "doc_name":doc_name
        },
        async: false,
        callback: function(r) {
            //console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;
	    //console.log("reportData==========="+reportData);
        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}
