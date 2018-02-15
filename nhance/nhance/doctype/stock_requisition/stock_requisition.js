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
		var check_flag_for_whole_number_in_stock_transactions = false;
		var itemsArray = new Array();
		var whole_number_in_stock_transactions_flag = false;
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
					//console.log("result::"+JSON.stringify(r.message))
					itemsList = r.message.items;
					for(var arrayLength = 0; arrayLength < itemsList.length; arrayLength++){
						item_code = itemsList[arrayLength].item_code;
						qty = itemsList[arrayLength].qty;
						stock_qty = itemsList[arrayLength].stock_qty;
						purchase_uom = itemsList[arrayLength].uom;
						conversion_factor = itemsList[arrayLength].conversion_factor;
						//console.log("qty::"+qty);
						//console.log("stock_qty::"+stock_qty);
						check_flag = get_UOM_Details(purchase_uom);
        					//check_flag = itemsMap.get(item_code);
        					if(check_flag){
							console.log("check_flag::"+check_flag);
							var processedQty = processQuantity(check_args,qty);
							//console.log("processedQty is::"+processedQty);
							r.message.items[arrayLength].qty = processedQty;
						}
					}//end of for..
					r.message.supplier = "";
					r.message.supplier_name = "";
					frappe.get_doc(r.message.doctype, r.message.name).__run_link_triggers = true;
					frappe.set_route("Form", r.message.doctype, r.message.name);
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
var startTime = new Date().getTime();
var endTime = 0;
if (check_args.round_up_fractions == 1) {
    check_qty = Math.floor(qty);
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
endTime = new Date().getTime();
endTime = startTime + endTime;
//console.log("endTime::" + endTime);
return quantity;
}

function get_UOM_Details(purchase_uom) {
    var whole_number_in_stock_transactions_flag = false;
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "UOM",
            filters: {
                uom_name: ["=", purchase_uom]
            },

            fieldname: ["must_be_whole_number", "needs_to_be_whole_number_in_stock_transactions"]
        },
        async: false,
        callback: function(r) {
            whole_number_in_stock_transactions = r.message.needs_to_be_whole_number_in_stock_transactions;
            //console.log("whole_number_in_stock_transactions::" + whole_number_in_stock_transactions);
            if (whole_number_in_stock_transactions == 1) {
                whole_number_in_stock_transactions_flag = true;
                //itemsMap.set(item_code, whole_number_in_stock_transactions_flag);
            }
        }
    });
return whole_number_in_stock_transactions_flag;
}

