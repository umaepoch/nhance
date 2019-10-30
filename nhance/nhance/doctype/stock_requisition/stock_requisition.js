// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

{% include 'erpnext/public/js/controllers/buying.js' %};

frappe.ui.form.on('Stock Requisition', {
	setup: function(frm) {
		frm.custom_make_buttons = {
		}
	},
	onload: function(frm) {
		// add item, if previous view was item
		erpnext.utils.add_item(frm);

		//set schedule_date
		set_schedule_date(frm);

		// formatter for material request item
		frm.set_indicator_formatter('item_code',
			function(doc) { return (doc.qty<=doc.ordered_qty) ? "green" : "orange" }),

		frm.fields_dict["items"].grid.get_field("warehouse").get_query = function(doc, cdt, cdn){
			return{
				filters: {'company': doc.company}
			}
		}
	}
});

//update qty to be order on submit of sreq
frappe.ui.form.on('Stock Requisition', {

	refresh: function(frm, cdt, cdn) {
		console.log("sreq refreshed");
		if(cur_frm.doc.workflow_state == "Approved"){
		console.log("SREQ approved **************");
		var d = frappe.get_doc(cdt, cdn);
		console.log("d  :::" + d );
		var stockRequisitionID = d.name;
		console.log("stockRequisitionID  :::" + stockRequisitionID );

		if (stockRequisitionID != null && stockRequisitionID != "") {
			if (cur_frm.doc.pch_is_submitted_sreq_updated == "No") {
				var updated_sreq_items_data = [];

				var sreq_items_data = get_sreq_items_data(stockRequisitionID);  //sreq_items_data[{"item_code":"Test Item1","qty":1}]
				console.log("from submit,before update :::: sreq_items_data ::::::: ",JSON.stringify(sreq_items_data));

				for (var i = 0; i < sreq_items_data.length; i++) {
					var sreq_item_code = sreq_items_data[i]['item_code'];
					var sreq_qty = sreq_items_data[i]['qty'];
					var sreq_fulfilled_qty = sreq_items_data[i]['fulfilled_quantity'];//jyoti added this
					//var quantity_to_be_order = sreq_qty ;
					var quantity_to_be_order = sreq_qty - sreq_fulfilled_qty;//jyoti changed the formula

					updated_sreq_items_data.push(
						{
							"sreq_item_code":sreq_item_code,
							"quantity_to_be_order":quantity_to_be_order
						}
					);
					} //end of for

				console.log("from approvel,calculated for updation, sreq_items_data ",JSON.stringify(updated_sreq_items_data));
				update_sreq_items_data_on_sreq_approvel(updated_sreq_items_data,stockRequisitionID);
				update_submitted_sreq( stockRequisitionID);
				refresh_field("quantity_to_be_order");
				refresh_field(frm.doc.items);

				sreq_items_data = get_sreq_items_data(stockRequisitionID);
				console.log("from submit,after update :::: sreq_items_data ::::::: ",JSON.stringify(sreq_items_data));

			}// end if pch_is_cancelled_po_updated checking

		} //if stockRequisitionID check

	} // end of if check approved
	} //end of refresh
});
//End update qty to be order on submit of sreq

//raghu code
/**
frappe.ui.form.on('Stock Requisition', {
   refresh: function(frm, cdt, cdn) {
      cur_frm.set_query("item_code", "items", function(frm, cdt, cdn) {
         var item_list = [];
         var d = locals[cdt][cdn];
         var item_group = d.item_group;
         console.log("Stock Requisition refresh****inside**********");
         if (item_group != undefined && item_group != null) {
            item_list = fetch_items(item_group);
            return {
               "filters": [
                  ["Item", "name", "in", item_list]
               ]
            }
            refresh_field("item_code");
            refresh_field("items");
         }
      });
   }
});
**/
//raghu end

frappe.ui.form.on("Stock Requisition Item", {
	qty: function (frm, doctype, name) {
		var d = locals[doctype][name];
		if (flt(d.qty) < flt(d.min_order_qty)) {
			frappe.msgprint(__("Warning: Material Requested Qty is less than Minimum Order Qty"));
		}
	},

	item_code: function(frm, doctype, name) {
		set_schedule_date(frm);
	},

	schedule_date: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.schedule_date) {
			if(!frm.doc.schedule_date) {
				//erpnext.utils.copy_value_in_all_row(frm.doc, cdt, cdn, "items", "schedule_date");
				$.each(frm.doc.items, function(i, d) {
				    d.schedule_date = frm.doc.schedule_date;
				    refresh_field("schedule_date");
				    }); //end of each...
				    refresh_field(frm.doc.items);
			} else {
				set_schedule_date(frm);
			}
		}
	}
});

erpnext.buying.MaterialRequestController = erpnext.buying.BuyingController.extend({
	onload: function(doc) {
		this._super();
		this.frm.set_query("item_code", "items", function() {
			return {
				query: "erpnext.controllers.queries.item_query"
			}
		});
	},

	refresh: function(doc) {
		var me = this;
		this._super();


		if(doc.docstatus == 1 && doc.status != 'Stopped') {
			if(flt(doc.per_ordered, 2) < 100) {
				// make
				if(doc.material_request_type === "Material Transfer")
					cur_frm.add_custom_button(__("Transfer Material"),
					this.make_stock_entry, __("Make"));

				if(doc.material_request_type === "Material Issue")
					cur_frm.add_custom_button(__("Issue Material"),
					this.make_stock_entry, __("Make"));

				if(doc.material_request_type === "Purchase")
					cur_frm.add_custom_button(__('Purchase Order'),
						this.make_purchase_order, __("Make"));

				if(doc.material_request_type === "Purchase")
					cur_frm.add_custom_button(__("Request for Quotation"),
						this.make_request_for_quotation, __("Make"));

				if(doc.material_request_type === "Purchase")
					cur_frm.add_custom_button(__("Supplier Quotation"),
					this.make_supplier_quotation, __("Make"));

				if(doc.material_request_type === "Manufacture")
					cur_frm.add_custom_button(__("Work Order"),
					this.raise_work_orders, __("Make"));

				cur_frm.page.set_inner_btn_group_as_primary(__("Make"));

				// stop
				cur_frm.add_custom_button(__('Stop'),
					cur_frm.cscript['Stop Material Request']);
			}
		}

		if (this.frm.doc.docstatus===0) {
			this.frm.add_custom_button(__('Sales Order'),
				function() {
					erpnext.utils.map_current_doc({
						method: "erpnext.selling.doctype.sales_order.sales_order.make_material_request",
						source_doctype: "Sales Order",
						target: me.frm,
						setters: {
							company: me.frm.doc.company
						},
						get_query_filters: {
							docstatus: 1,
							status: ["!=", "Closed"],
							per_delivered: ["<", 99.99],
						}
					})
				}, __("Get items from"));
		}

		if(doc.docstatus == 1 && doc.status == 'Stopped')
			cur_frm.add_custom_button(__('Re-open'),
				cur_frm.cscript['Unstop Material Request']);

	},

	get_items_from_bom: function() {
		var d = new frappe.ui.Dialog({
			title: __("Get Items from BOM"),
			fields: [
				{"fieldname":"bom", "fieldtype":"Link", "label":__("BOM"),
					options:"BOM", reqd: 1, get_query: function(){
						return {filters: { docstatus:1 }}
					}},
				{"fieldname":"warehouse", "fieldtype":"Link", "label":__("Warehouse"),
					options:"Warehouse", reqd: 1},
				{"fieldname":"fetch_exploded", "fieldtype":"Check",
					"label":__("Fetch exploded BOM (including sub-assemblies)"), "default":1},
				{fieldname:"fetch", "label":__("Get Items from BOM"), "fieldtype":"Button"}
			]
		});
		d.get_input("fetch").on("click", function() {
			var values = d.get_values();
			if(!values) return;
			values["company"] = cur_frm.doc.company;
			frappe.call({
				method: "erpnext.manufacturing.doctype.bom.bom.get_bom_items",
				args: values,
				callback: function(r) {
					if(!r.message) {
						frappe.throw(__("BOM does not contain any stock item"))
					} else {
						erpnext.utils.remove_empty_first_row(cur_frm, "items");
						$.each(r.message, function(i, item) {
							var d = frappe.model.add_child(cur_frm.doc, "Stock Requisition Item", "items");
							d.item_code = item.item_code;
							d.item_name = item.item_name;
							d.description = item.description;
							d.warehouse = values.warehouse;
							d.uom = item.stock_uom;
							d.stock_uom = item.stock_uom;
							d.conversion_factor = 1;
							d.qty = item.qty;
						});
					}
					d.hide();
					refresh_field("items");
				}
			});
		});
		d.show();
	},

	tc_name: function() {
		this.get_terms();
	},

	validate_company_and_party: function(party_field) {
		return true;
	},

	calculate_taxes_and_totals: function() {
		return;
	},
	make_purchase_order: function( ) {
		var whole_number = 0;
		var whole_number_in_stock_transactions = 0;
		var dialog_box_flag = false;
		var dialog_displayed = false;
		var itemsList = "";
		var company = "";
		var supplierList = [];
		var defaultSupplierItemsMap = new Map();
		var check_flag_for_whole_number_in_stock_transactions = false;
		var itemsArray = new Array();
		var whole_number_in_stock_transactions_flag = false;
		var check_args = "";
		console.log("make_purchase_order --------------SREQ ID::"+cur_frm.doc.name);

		//validating purchase uom and  conversion_factor
        	var sreq_items_data = cur_frm.doc.items;
        	for(var i = 0; i < sreq_items_data.length; i++){
            		var item_code = sreq_items_data[i].item_code ;
            		var purchase_uom = getPurchaseUom(item_code);
            		//console.log("purchase_uom--------------::"+purchase_uom);
            		if(purchase_uom!=null){
                		var conversion_factor = getConversionFactor(purchase_uom,item_code);
                		//console.log("conversion_factor--------------::"+conversion_factor);
                		if (conversion_factor == 0 || conversion_factor == undefined){
                    			frappe.throw(__("The Conversion Factor for UOM: "+ purchase_uom.toString()  +" for Item: "+ item_code.toString() +" is not defined. Please define the Conversion Factor or remove the Purchase UOM and try again."));
                		}
            		}

        	}//end of for
        	//End validating purchase uom and conversion conversion_factor

		if(!dialog_displayed){
			var dialog = new frappe.ui.Dialog({
			title: __("Select Round Type:"),
			fields: [
				{"fieldtype": "Check", "label": __("Round Up Fractions"), "fieldname": "round_up_fractions"},
				{"fieldtype": "Check", "label": __("Round Down Fractions"), "fieldname": "round_down_fractions"},
				{"fieldtype": "Check", "label": __("Round Fractions"), "fieldname": "round_fractions"},
				{"fieldtype": "Check", "label": __("Do Nothing"), "fieldname": "do_nothing"}
				],
				primary_action: function(){
				check_args = dialog.get_values();
				frappe.call({
					type: "POST",
					method: 'frappe.model.mapper.make_mapped_doc',
					args: {
					method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_purchase_order",
					source_name: cur_frm.doc.name,
					selected_children: cur_frm.get_selected()
						},
					freeze: true,
					async: false,
					callback: function(r) {
						if(!r.exc) {
					frappe.model.sync(r.message);
					itemsList = r.message.items;
					var index = 0;
					var no_Supplier_Items = new Array();
					company = r.message.company;
					console.log("###################cur_frm.doc.name::"+cur_frm.doc.name);
					for(var arrayLength = 0; arrayLength < itemsList.length; arrayLength++){
						var arr = {};
    						var arrList = [];
						var default_supplier = "";
						var cost_center = "";
						var expense_account = "";
						var price_list = "";
						var item_code = itemsList[arrayLength].item_code;
						var qty = itemsList[arrayLength].qty;
						var uom = itemsList[arrayLength].uom;
						var stock_uom = itemsList[arrayLength].stock_uom;
						var stock_qty = itemsList[arrayLength].stock_qty;
						var cost_center1 = itemsList[arrayLength].cost_center;
						var expense_account1 = itemsList[arrayLength].expense_account;
						var purchase_uom = getPurchaseUom(item_code);
						var check_flag = get_UOM_Details(stock_uom);
						var pch_bom_reference = "" ;
						var project = "" ;
						if( itemsList[arrayLength].pch_bom_reference != null && itemsList[arrayLength].pch_bom_reference != undefined){
							pch_bom_reference= itemsList[arrayLength].pch_bom_reference;
						}
						if( itemsList[arrayLength].project != null && itemsList[arrayLength].project != undefined){
							project= itemsList[arrayLength].project;
						}
						console.log("purchase_uom::"+purchase_uom);

						/**
						console.log("purchase_uom::"+purchase_uom);
						console.log("qty::"+qty);
						console.log("cost_center::"+cost_center1);
						console.log("expense_account-------------::"+expense_account1);
						console.log("check_flag::"+check_flag);
						**/
        					if(check_flag){
							var processedQty = processQuantity(check_args,stock_qty);
							//console.log("processedQty is::"+processedQty);
							qty = processedQty;
							itemsList[arrayLength].qty = qty;
							itemsList[arrayLength].stock_qty = qty;
						}//end of check_flag..
						else{
						itemsList[arrayLength].qty = stock_qty;
						itemsList[arrayLength].stock_qty = stock_qty;
						qty = stock_qty;
						}
						if(purchase_uom!=null){
						var conversion_factor = getConversionFactor(purchase_uom,item_code);
						//console.log("conversion_factor::"+conversion_factor);
						qty = qty/conversion_factor;
						itemsList[arrayLength].qty = qty;
						itemsList[arrayLength].uom = purchase_uom;
						itemsList[arrayLength].conversion_factor = conversion_factor;
						}else{
						purchase_uom = uom;
						}
						//console.log("stock_qty is::"+stock_qty);
   						var stock_uom = itemsList[arrayLength].stock_uom;
    						var warehouse = itemsList[arrayLength].warehouse;

						var item_default_details = getItemDetails(item_code,company);

						if (item_default_details.length != 0){
							default_supplier = item_default_details[0]['default_supplier'];
							cost_center = item_default_details[0]['buying_cost_center'];
							expense_account = item_default_details[0]['expense_account'];
							//var warehouse = item_default_details[0]['default_warehouse'];
							price_list = item_default_details[0]['default_price_list'];
						}

						if (price_list != null && price_list != ""){
							var item_price = fetch_item_price(item_code,price_list);
							arr['price_list_rate'] = item_price;
							itemsList[arrayLength].price_list_rate = item_price;
						}else{
							arr['price_list_rate'] = 0.0;
							itemsList[arrayLength].price_list_rate = 0.0;
						}

						/**
						if (warehouse != null){
							arr['warehouse'] = warehouse;
							itemsList[arrayLength].warehouse = warehouse;
						}else{
							arr['warehouse'] = warehouse;
						}**/

						if (cost_center != null && cost_center != ""){
							arr['cost_center'] = cost_center;
							itemsList[arrayLength].cost_center = cost_center;
						}else{
							arr['cost_center'] = cost_center1;
						}

						if (expense_account != null && expense_account != ""){
							arr['expense_account'] = expense_account;
							itemsList[arrayLength].expense_account = expense_account;
						}else{
							arr['expense_account'] = expense_account1;
						}


						arr['item_code'] = item_code;
   						arr['supplier'] = default_supplier;
    						arr['qty'] = qty;
    						arr['stock_qty'] = stock_qty;
    						arr['stock_uom'] = stock_uom;
    						arr['purchase_uom'] = purchase_uom;
								arr['warehouse'] = warehouse;
								arr['pch_bom_reference'] = pch_bom_reference;
								arr['project'] = project;
    						//arr['price'] = standard_rate;

    						arr['conversion_factor'] = conversion_factor;

						if(default_supplier == null || default_supplier == ""){
							//itemsList[arrayLength].rate = standard_rate;
							no_Supplier_Items.push(itemsList[arrayLength]);
						}else{
							if(!supplierList.includes(default_supplier)){
    								supplierList.push(default_supplier);
   							 }
							if (defaultSupplierItemsMap.has(default_supplier)) {
        							arrList = defaultSupplierItemsMap.get(default_supplier);
        							arrList.push(arr);
       								defaultSupplierItemsMap.set(default_supplier, arrList);
   							 } else {
       								arrList.push(arr);
        							defaultSupplierItemsMap.set(default_supplier, arrList);
    							 }
						}//end of else...
					}//end of for..
					console.log("no_Supplier_Items::"+no_Supplier_Items);
					r.message.items = no_Supplier_Items;
					var msg = r.message;
					making_PurchaseOrder_For_SupplierItems(supplierList,defaultSupplierItemsMap,company,no_Supplier_Items,msg,cur_frm);
					}
					}//end of callback fun..
				});//end of frappe call..
        			dialog.hide();
    				}
				});//end of frappe ui dialog...
				dialog.show();
				dialog_displayed = true;
		}
	},

	make_request_for_quotation: function(){
		frappe.model.open_mapped_doc({
			method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_request_for_quotation",
			frm: cur_frm,
			run_link_triggers: true
		});
	},

	make_supplier_quotation: function() {
		frappe.model.open_mapped_doc({
			method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_supplier_quotation",
			frm: cur_frm
		});
	},

	make_stock_entry: function() {
		console.log("--------material_request_type--------"+cur_frm.doc.material_request_type);
		var me = this;
		var stock_requisition_id = cur_frm.doc.name;
		console.log("stock_requisition_id--------"+stock_requisition_id);
		if (cur_frm.doc.material_request_type == "Material Issue"){
		var issueFlag = getStockRequisitionIssueFlag(stock_requisition_id);
		if (issueFlag == "true"){
		frappe.call({
			type: "POST",
			method: 'frappe.model.mapper.make_mapped_doc',
			args: {
				method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_stock_entry",
				source_name: cur_frm.doc.name,
				selected_children: cur_frm.get_selected()
				},
			freeze: true,
			async: false,
			callback: function(r) {
				/**
				console.log("se--------"+JSON.stringify(r.message));
				console.log("se--------"+r.message.items);
				console.log("se--------"+r.message.name);
				**/
				var items = r.message.items;
				var stockEntryList = r.message;
				makeStockEntry(stockEntryList,items,stock_requisition_id,cur_frm);
			}
			});
		}else{
			frappe.msgprint(__("Material Issue is already done for "+stock_requisition_id));
		}
		}else if(cur_frm.doc.material_request_type == "Material Transfer"){
			frappe.model.open_mapped_doc({
			method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_stock_entry",
			frm: cur_frm
			});
		}

	},

	raise_work_orders: function() {
		var me = this;
		console.log("Docname--------"+cur_frm.doc.name);
		frappe.call({
			method:"nhance.nhance.doctype.stock_requisition.stock_requisition.raise_work_orders",
			args: {
				"stock_requisition": cur_frm.doc.name
			},
			callback: function(r) {
				if(r.message.length) {
					cur_frm.reload_doc();
				}
			}
		});
	},

	validate: function() {
		set_schedule_date(this.frm);
	},

	items_add: function(doc, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if(doc.schedule_date) {
			row.schedule_date = doc.schedule_date;
			refresh_field("schedule_date", cdn, "items");
		} else {
			this.frm.script_manager.copy_from_first_row("items", row, ["schedule_date"]);
		}
	},

	items_on_form_rendered: function() {
		set_schedule_date(this.frm);
	},

	schedule_date: function() {
		set_schedule_date(this.frm);
	}
});

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new erpnext.buying.MaterialRequestController({frm: cur_frm}));

cur_frm.cscript['Stop Material Request'] = function() {
    var doc = cur_frm.doc;
    console.log("from cancel:" + doc.name);
    var stock_requisition_id=doc.name
    frappe.call({
        method: "nhance.nhance.doctype.stock_requisition.stock_requisition.cancel_stock_requisition",
	 args: {
               "stock_requisition_id": stock_requisition_id
               },
        async: false,
	callback: function(r) {
		if(r.message) {
			cur_frm.reload_doc();
		}
		}
         });
    /**
    $c('runserverobj', args={'method':'update_status', 'arg': 'Stopped', 'docs': doc}, function(r,rt) {
    	cur_frm.refresh();
    });
   **/
};

cur_frm.cscript['Unstop Material Request'] = function(){
	var doc = cur_frm.doc;
	$c('runserverobj', args={'method':'update_status', 'arg': 'Submitted','docs': doc}, function(r,rt) {
		cur_frm.refresh();
	});
};

function set_schedule_date(frm) {
	if(frm.doc.schedule_date){
		//erpnext.utils.copy_value_in_all_row(frm.doc, frm.doc.doctype, frm.doc.name, "items", "schedule_date");
		$.each(frm.doc.items, function(i, d) {
			d.schedule_date = frm.doc.schedule_date;
			refresh_field("schedule_date");
			}); //end of each...
			refresh_field(frm.doc.items);
	}
}


function fetch_item_price(item_code,price_list){
var rate = 0.0;
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Item Price",
            filters: {
                item_code: ["=", item_code],
		price_list: ["=", price_list],
            },
            fieldname: ["price_list_rate"]
        },
        async: false,
        callback: function(r) {
		if (r.message){
        		rate = r.message.price_list_rate;
		}
        }
    });
return rate;
}

function processQuantity(check_args,qty) {
var quantity = 0;
if (check_args.round_up_fractions == 1) {
    var check_qty = Math.floor(qty);
    check_qty = qty - check_qty;
    if (check_qty != 0.0) {
        quantity = Math.ceil(qty);
        quantity = parseInt(quantity);
    } else {
        quantity = parseInt(qty);
    }

} else if (check_args.round_down_fractions == 1) {
    quantity = parseInt(qty);
} else if (check_args.round_fractions == 1) {
    quantity = Math.round(qty);
}
if (quantity == 0) {
    quantity = qty;
}
console.log("quantity::"+quantity);
return quantity;
}

function getItemDetails(item_code,company){
var details = [];
frappe.call({
           method: "nhance.nhance.doctype.stock_requisition.stock_requisition.fetch_item_defaults",
           args: {
                   "company": company,
		   "item_code": item_code
           },
	   async: false,
           callback: function(r) {
           if (r.message) {
		console.log("ItemDetails::"+ JSON.stringify(r.message));
		details = r.message;
            }
            }//end of callback fun..
           })//end of frappe call..
return details;
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

function getConversionFactor(purchase_uom,item_code){
var conversion_factor;
frappe.call({
           method: "nhance.nhance.doctype.stock_requisition.stock_requisition.fetch_conversion_factor",
           args: {
                   "purchase_uom": purchase_uom,
		   "item_code": item_code
           },
	   async: false,
           callback: function(r) {
           if (r.message) {
		console.log("conversion_factor::"+r.message);
		conversion_factor = r.message;
            }
            }//end of callback fun..
           })//end of frappe call..
return conversion_factor;
}//end of getConversionFactor..

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
//					making_PurchaseOrder_For_SupplierItems(supplierList,defaultSupplierItemsMap,company,no_Supplier_Items,msg,cur_frm);
function making_PurchaseOrder_For_SupplierItems(supplierList,myMap,company,items,message,cur_frm){

var srID = cur_frm.doc.name;

/**
** Preparing JsonArray Data To Display Dialog box with Suppliers and Tax Template..
**/

var dialog_fields = new Array();
var dialog_array = [];
var supplier = "";
var column_break_json ={
"fieldtype":"Column Break",
"fieldname":"column_break"
}
var column_break_data = JSON.stringify(column_break_json);
for(var i=0;i<supplierList.length;i++){
	supplier = supplierList[i];
	var supplier_json ={
		"fieldtype":"Data",
		"fieldname":"supplier"+ "_" + i,
		"default": supplier,
		"bold":1,
		"read_only":1
		}
	var tax_template_json ={
		"fieldtype":"Link",
		"fieldname":"tax_template" + "_" + i,
		"options": "Purchase Taxes and Charges Template",
		"reqd":1
		}
	var tax_template_data = JSON.stringify(tax_template_json);
	var supplier_data = JSON.stringify(supplier_json);
	dialog_fields.push(supplier_data);
	//dialog_fields.push(column_break_data);
	dialog_fields.push(tax_template_data);
}//end of for loop..

var dialogArray = [];
for(var i=0;i<dialog_fields.length;i++){
dialogArray.push(JSON.parse(dialog_fields[i]));
}
/**
** End of Preparing JsonArray Data..
**/

console.log("message-----------------");
if(supplierList.length!=0){
cur_frm.save("Update");
var dialog = new frappe.ui.Dialog({
title: __("Select Tax Template For Suppilers"),
fields: dialogArray,
	primary_action: function(){
	dialog.hide();
	var check_args = dialog.get_values();
	var args_length = Object.keys(check_args).length;
	var supplier_and_tax_array = [];
	/**
	** Fetching values from check_args...
	*/
	for(var i=0;i<args_length/2;i++){
	var supplier = "supplier_"+i;
	var tax_template = "tax_template_"+i;
	var supplier_val = check_args[supplier];
	var tax_template_val = check_args[tax_template];
	/**console.log("supplier_val::" + supplier_val);
	console.log("tax_template_val::" + tax_template_val);**/
	var supplier_and_tax_json={
		"supplier": supplier_val,
		"tax_template": tax_template_val
	}
	var supplier_and_tax_data = JSON.stringify(supplier_and_tax_json);
	supplier_and_tax_array.push(supplier_and_tax_data);
	}//end of for loop..
	//end of Fetching values from check_args...

	/**
	** Making Purchase Order For Default Supplier Items..
	**/
	var tax_template = "";
	for (const entry of myMap.entries()) {
    		var map_supplier = entry[0];
    		var list = myMap.get(map_supplier);
		for(var i = 0;i<supplier_and_tax_array.length;i++){
			var details = JSON.parse(supplier_and_tax_array[i]);
			var supplier = details.supplier;
			var tax_template_for_supplier = details.tax_template;
			if(map_supplier == supplier){
				tax_template = tax_template_for_supplier;
			}
		}//end of inner for-loop..
    		console.log("###list", list.length);
    		console.log("###list", list);
    		frappe.call({
       			 method: "nhance.nhance.doctype.stock_requisition.stock_requisition.making_PurchaseOrder_For_SupplierItems",
        		 args: {
          			  "args": list,
           			  "company": company,
				  "tax_template": tax_template,
				  "srID": srID,
       				},
			async: false,
        		callback: function(r) {
				console.log("########-PO::"+r.message);
        		}
   		 }); //end of frappe call.
	}//end of outer for-loop..
	if(items.length!=0){
	makePUrchaseOrderForNoSupplierItems(message,items,cur_frm,srID);
	}
	}
	});//end of dialog box...
	dialog.show();
}else{
	if(items.length!=0){
	console.log("-----------------items::"+items.length);
	makePUrchaseOrderForNoSupplierItems(message,items,cur_frm,srID);

	}
}
}//end of function..

function makePUrchaseOrderForNoSupplierItems(message,items,cur_frm,srID){
	message.items = items;
	message.stock_requisition_id  = srID;


	//getting default values
	var defualt_list=["supplier","company","customer","customer_contact_person",
	"supplier_address","contact_person","shipping_address","currency","buying_price_list",
	"price_list_currency","set_warehouse","supplier_warehouse","taxes_and_charges","shipping_rule",
	"payment_terms_template","party_account_currency","select_print_heading",
	"auto_repeat"]
	var po_default_values=get_po_default_values();
	console.log("from no supplier default values"+JSON.stringify(po_default_values));


	for (var i = 0; i < defualt_list.length; i++) {

	 var default_field = defualt_list[i] ;
	 var key_default_value = "defualt_" + defualt_list[i] ;
	 if  ( po_default_values[key_default_value] != null )
	 {
		 var append_default_val = po_default_values[key_default_value] ;
		 message.default_field  = append_default_val ;
		 console.log("appended_default_field ---"+ default_field+  ":" + append_default_val);
	 }

	}




	//getting default values end

	frappe.get_doc(message.doctype, message.name).__run_link_triggers = true;
	frappe.set_route("Form", message.doctype, message.name);
}//end of makePUrchaseOrderForNoSupplierItems..

function updatePOList(srID,poList){
frappe.call({
	method: "nhance.nhance.doctype.stock_requisition.stock_requisition.update_po_list",
	args: {
         	 "srID":srID,
		 "po_list":poList
        },
	async: false,
	callback: function(r)
      	{
	//console.log("");
	}
	});//end of frappe call..
}//end of updatePOList..

function getStockRequisitionIssueFlag(stock_requisition_id){
var checkFlag = false;
console.log("SreqID-----"+stock_requisition_id);
frappe.call({
	method: "nhance.nhance.doctype.stock_requisition.stock_requisition.check_stock_entry_for_stock_requisition",
        args: {
		"stock_requisition_id": stock_requisition_id
       		},
	async: false,
        callback: function(r) {
		console.log("Result-----callback----");
		console.log("Result---------"+r.message);
		checkFlag = r.message;
        }//end of call-back fun..
    }); //end of frappe call.

return checkFlag;
}

function makeStockEntry(stockEntryList,items,stock_requisition_id,cur_frm){
var company = stockEntryList.company;
frappe.call({
	method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_material_issue",
        args: {
                 "items": items,
		 "company": company,
		 "stock_requisition_id": stock_requisition_id
                },
        async: false,
        callback: function(r) {
        	if (r.message) {
                	cur_frm.reload_doc();
			frappe.msgprint(__("Material Issue is created for: "+stock_requisition_id));
                 }
        } //end of callback fun..
       }) //end of frappe call.
}


/**

frappe.ui.form.on("Stock Requisition", "refresh", function(frm) {
   cur_frm.set_query("item_code", "items", function(frm, cdt, cdn) {
      var d = locals[cdt][cdn];
      var item_group = d.item_group;
      var item_list = fetch_items(item_group);
      console.log("checking----------------");
      if (item_list != null) {
         return {
            "filters": [
               ["Item", "name", "in", item_list]
            ]
         }
         refresh_field("item_code");
         refresh_field("items");
      }
   });
});

function fetch_items(item_group) {
   var itemList = [];
   frappe.call({
      method: 'nhance.nhance.doctype.stock_requisition.stock_requisition.fetch_items',
      args: {
         "item_group": item_group,
      },
      async: false,
      callback: function(r) {
         if (r.message) {
		console.log("Result-----fetch_items----"+ JSON.stringify(r.message));
		for(var i=0;i<r.message.length;i++){
			var item = r.message[i].name;
			itemList.push(item);
		}
            //expense_account = r.message.item_code;
         }
      } //end of callback fun..
   }); //end of frappe call..
return itemList;
}
**/

//qty to be order start SREQ refresh functions //PMRT start (Update "qty to be order" field on approving sreq )
function update_sreq_items_data_on_sreq_approvel( updated_sreq_items_data,stockRequisitionID ) {
	console.log(" This data is going to be updated" + JSON.stringify(updated_sreq_items_data));
	frappe.call({
        method: "nhance.api.update_sreq_items_data_on_sreq_approvel",
        args: {
            "updated_sreq_items_data": updated_sreq_items_data,
						"stockRequisitionID" :stockRequisitionID
        },
        async: false,
        callback: function(r) {
					if (r.message) {
						console.log("updatd sreq item succesfully");
					} else {
						console.log("failed to update sreq data");
					}
				}  //end of call back
    }); // end of frappe call
} //  end of update_sreq_items_data

function get_sreq_items_data( stockRequisitionID ) {

	var sreq_items_data;

	frappe.call({
        method: "nhance.api.get_sreq_items_data",
        args: {
            "stockRequisitionID": stockRequisitionID
        },
        async: false,
        callback: function(r) {
					if (r.message) {
						sreq_items_data = r.message;
            } else {
							console.log("no get_sreq_items_data data");
            }

				}  //end of call back
    }); // end of frappe call

		return sreq_items_data;
}  //end of  get_sreq_items_data


function update_submitted_sreq(stockRequisitionID) {
    frappe.call({
        method: "nhance.api.update_submitted_sreq",
        args: {
            "stockRequisitionID": stockRequisitionID
        },
        async: false,
        callback: function(r) {}
    });
}
//qty to be order functions end

//making po from sreq get_po_default_values
function get_po_default_values(){
	var po_default_values_local;

	frappe.call({
				method: "nhance.nhance.doctype.stock_requisition.stock_requisition.get_po_default_values",
				args: {
				},
				async: false,
				callback: function(r) {
					if (r.message) {
						po_default_values_local = r.message;
						}

				}  //end of call back
		}); // end of frappe call
		return po_default_values_local

}
//making po from sreq get_po_default_values
