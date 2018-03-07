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
				erpnext.utils.copy_value_in_all_row(frm.doc, cdt, cdn, "items", "schedule_date");
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
					cur_frm.add_custom_button(__("Production Order"),
					function() { me.raise_production_orders() }, __("Make"));

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
	make_purchase_order: function() {
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
				console.log("primary_action-----------------");
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
					//console.log("result::"+JSON.stringify(r.message))
					itemsList = r.message.items;
					//r.message.items = [{}];
					var index = 0;
					var no_Supplier_Items = new Array();
					company = r.message.company;
					console.log("primary_action------callback-----------");
					for(var arrayLength = 0; arrayLength < itemsList.length; arrayLength++){
						var arr = {};
    						var arrList = [];
						var item_code = itemsList[arrayLength].item_code;
						var qty = itemsList[arrayLength].qty;
						var uom = itemsList[arrayLength].uom;
						var stock_uom = itemsList[arrayLength].stock_uom;
						var stock_qty = itemsList[arrayLength].stock_qty;
						//var conversion_factor = itemsList[arrayLength].conversion_factor;
						var purchase_uom = getPurchaseUom(item_code);
						console.log("purchase_uom::"+purchase_uom);
						console.log("qty::"+qty);
						//console.log("stock_qty::"+stock_qty);
						var check_flag = get_UOM_Details(stock_uom);
						console.log("check_flag::"+check_flag);
        					if(check_flag){
							var processedQty = processQuantity(check_args,stock_qty);
							console.log("processedQty is::"+processedQty);
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
						console.log("conversion_factor::"+conversion_factor);
						qty = qty/conversion_factor;
						itemsList[arrayLength].qty = qty;
						itemsList[arrayLength].uom = purchase_uom;
						itemsList[arrayLength].conversion_factor = conversion_factor;
						}else{
						purchase_uom = uom;
						}
						console.log("stock_qty is::"+stock_qty);
   						var stock_uom = itemsList[arrayLength].stock_uom;
    						var warehouse = itemsList[arrayLength].warehouse;
						var supplier = getItemDetails(item_code);

						arr['item_code'] = item_code;
   						arr['supplier'] = supplier;
    						arr['qty'] = qty;
    						arr['stock_qty'] = stock_qty;
    						arr['stock_uom'] = stock_uom;
    						arr['purchase_uom'] = purchase_uom;
    						//arr['price'] = standard_rate;
    						arr['warehouse'] = warehouse;
    						arr['conversion_factor'] = conversion_factor;

						if(supplier == null){
							//itemsList[arrayLength].rate = standard_rate;
							no_Supplier_Items.push(itemsList[arrayLength]);
						}else{
							if(!supplierList.includes(supplier)){
    								supplierList.push(supplier);
   							 }
							if (defaultSupplierItemsMap.has(supplier)) {
        							arrList = defaultSupplierItemsMap.get(supplier);
        							arrList.push(arr);
       								defaultSupplierItemsMap.set(supplier, arrList);
   							 } else {
       								arrList.push(arr);
        							defaultSupplierItemsMap.set(supplier, arrList);
    							 }
						}//end of else...
					}//end of for..
					console.log("no_Supplier_Items::"+no_Supplier_Items);
					r.message.items = no_Supplier_Items;
					var msg = r.message;
					making_PurchaseOrder_For_SupplierItems(supplierList,defaultSupplierItemsMap,company,no_Supplier_Items,msg);
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
		frappe.model.open_mapped_doc({
			method: "nhance.nhance.doctype.stock_requisition.stock_requisition.make_stock_entry",
			frm: cur_frm
		});
	},

	raise_production_orders: function() {
		var me = this;
		frappe.call({
			method:"nhance.nhance.doctype.stock_requisition.stock_requisition.raise_production_orders",
			args: {
				"material_request": me.frm.doc.name
			},
			callback: function(r) {
				if(r.message.length) {
					me.frm.reload_doc();
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
	$c('runserverobj', args={'method':'update_status', 'arg': 'Stopped', 'docs': doc}, function(r,rt) {
		cur_frm.refresh();
	});
};

cur_frm.cscript['Unstop Material Request'] = function(){
	var doc = cur_frm.doc;
	$c('runserverobj', args={'method':'update_status', 'arg': 'Submitted','docs': doc}, function(r,rt) {
		cur_frm.refresh();
	});
};

function set_schedule_date(frm) {
	if(frm.doc.schedule_date){
		erpnext.utils.copy_value_in_all_row(frm.doc, frm.doc.doctype, frm.doc.name, "items", "schedule_date");
	}
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

function getItemDetails(item_code){
var supplier = "";
frappe.call({
    method: 'frappe.client.get_value',
    args: {
        doctype: "Item",
        filters: {
            item_code: ["=", item_code]
        },

        fieldname: ["default_supplier"]
    },
    async: false,
    callback: function(r) {
        console.log("default_supplier..." + r.message.default_supplier);
        supplier = r.message.default_supplier;

    }
});
return supplier;
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
var conversion_factor = 0;
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "UOM Conversion Detail",
            filters: {
                uom: ["=", purchase_uom],
		parent: ["=", item_code]
		
            },

            fieldname: ["conversion_factor"]
        },
        async: false,
        callback: function(r) {
		if(r.message){
            	conversion_factor = r.message.conversion_factor;
		}else{
		conversion_factor =null;
		}
        }
    });
return conversion_factor;
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

function making_PurchaseOrder_For_SupplierItems(supplierList,myMap,company,items,message){
console.log("making_PurchaseOrder_For_SupplierItems-----------------");
/**
** Preparing JsonArray Data To Display Dialog box with Suppliers and Tax Template..
**/
console.log("#####-supplierList::"+supplierList);
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
       				},
        		callback: function(r) {
        		}
   		 }); //end of frappe call.
	}//end of outer for-loop..

	if(items.length!=0){
	message.items = items;
	message.supplier = "";
	message.supplier_name = "";
	frappe.get_doc(message.doctype, message.name).__run_link_triggers = true;
	frappe.set_route("Form", message.doctype, message.name);
	}
	}
	});//end of dialog box...
	dialog.show();
}else{
	if(items.length!=0){
	message.items = items;
	message.supplier = "";
	message.supplier_name = "";
	frappe.get_doc(message.doctype, message.name).__run_link_triggers = true;
	frappe.set_route("Form", message.doctype, message.name);
	}
}
}//end of function..
