# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, utils
from frappe.utils import flt, getdate, cint, formatdate
from datetime import datetime, timedelta

def execute(filters=None):

	global required_date
	global company
	global warehouse
	global data
	global ord_cs_qty
	global no_transfer
	global from_date
	global to_date

	if not filters: filters = {}
	required_date = filters.get("required_on")
	company = filters.get("company")
	warehouse = filters.get("warehouse")

	validate_filters(filters)

	columns = get_columns()
	item_map = get_item_details(filters)

	mat_req_map = get_material_request(filters)

	if filters.get("cutoff_date"):
		mat_sel_req_map = get_material_sel_request(filters)
	else:
		mat_sel_req_map = []

	pur_ord_map = get_purchase_orders(filters)

	if filters.get("cutoff_date"):
		pur_sel_ord_map = get_purchase_sel_orders(filters)
	else:		
		pur_sel_ord_map = []

	item_reorder_detail_map = get_item_reorder_details(filters)
	iwb_map = get_item_warehouse_map(filters)

	data = []
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]
		item_reorder_level = 0
		item_reorder_qty = 0
		mat_tot_pend_qty = 0
		mat_pend_qty = 0
		pur_pend_qty = 0
		pur_tot_pend_qty = 0
		ord_cs_qty = 0
		ord_ig_qty = 0

		if item + warehouse in item_reorder_detail_map:
			item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
			item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]
		
		if item in mat_req_map:
			mat_tot_pend_qty = mat_req_map[item]["sum(qty)"] - mat_req_map[item]["sum(ordered_qty)"]
			if mat_tot_pend_qty < 0:
				mat_tot_pend_qty = 0
	
		if item in mat_sel_req_map:
			mat_pend_qty = mat_sel_req_map[item]["sum(qty)"] - mat_sel_req_map[item]["sum(ordered_qty)"]
			if mat_pend_qty < 0:
				mat_pend_qty = 0
	
		if item in pur_ord_map:
			pur_tot_pend_qty = pur_ord_map[item]["sum(qty)"] - pur_ord_map[item]["sum(received_qty)"]
			if pur_tot_pend_qty < 0:
				pur_tot_pend_qty = 0

		if item in pur_sel_ord_map:
			pur_pend_qty = pur_sel_ord_map[item]["sum(qty)"] - pur_sel_ord_map[item]["sum(received_qty)"]
			if pur_pend_qty < 0:
				pur_pend_qty = 0

		if qty_dict.bal_qty > item_reorder_level:
			ord_cs_qty = 0
			ord_ig_qty = 0
	
		else:
			if (item_reorder_level - qty_dict.bal_qty - pur_pend_qty - mat_pend_qty) < 0:
				ord_cs_qty = 0
			else:
				ord_temp_cs_qty = item_reorder_level-qty_dict.bal_qty-pur_pend_qty-mat_pend_qty
				if ord_temp_cs_qty > item_reorder_qty:
					ord_cs_qty = ord_temp_cs_qty
				else:
					ord_cs_qty = item_reorder_qty
			
			if (item_reorder_level - qty_dict.bal_qty - pur_tot_pend_qty - mat_tot_pend_qty) < 0:
				ord_ig_qty = 0
			else:
				ord_temp_ig_qty = item_reorder_level-qty_dict.bal_qty-pur_tot_pend_qty-mat_tot_pend_qty

				if ord_temp_ig_qty > item_reorder_qty:
					ord_ig_qty = ord_temp_ig_qty
				else:
					ord_ig_qty = item_reorder_qty

		if item_reorder_level > 0:
			data.append([item, item_map[item]["item_name"],
				item_map[item]["item_group"],
				item_map[item]["brand"],
				item_map[item]["description"], warehouse,
				item_map[item]["stock_uom"], qty_dict.bal_qty,
				item_reorder_level,
				item_reorder_qty, mat_tot_pend_qty, mat_pend_qty, pur_tot_pend_qty, pur_pend_qty, ord_cs_qty, ord_ig_qty
			
			])

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Item")+":Link/Item:100",
		_("Item Name")+"::150",
		_("Item Group")+"::100",
		_("Brand")+"::90",
		_("Description")+"::140",
		_("Warehouse")+":Link/Warehouse:100",
		_("Stock UOM")+":Link/UOM:90",
		_("Balance Qty")+":Float:100",
		_("Reorder Level")+":Float:80",
		_("Reorder Qty")+":Float:80",
		_("Total Pending Material Requests")+":Float:80",
		_("Total Pending Material Request in the last selected days")+":Float:80",
		_("Total Pending Purchase Order Qty")+":Float:80",
		_("Total Pending Purchase Order in the last selected days")+":Float:80",
		_("Order Qty Considering Selected Days")+":Float:80",
		_("Order Qty Ignoring Selected Days")+":Float:80"

	]

	return columns

def get_conditions(filters):
	conditions = ""
	to_date = utils.today()
	from_date = getdate(to_date) - timedelta(days=300)
	conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(to_date)

	if not filters.get("cutoff_date"):
		frappe.throw(_("Cutoff date is required"))

	if filters.get("item_group"):		
		ig_details = frappe.db.get_value("Item Group", filters.get("item_group"), 
			["lft", "rgt"], as_dict=1)
			
		if ig_details:
			conditions += """ 
				and exists (select name from `tabItem Group` ig 
				where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)
			""" % (ig_details.lft, ig_details.rgt)
		
	if filters.get("item_code"):
		conditions += " and sle.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

	if filters.get("warehouse"):
		warehouse_details = frappe.db.get_value("Warehouse", filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
		if warehouse_details:
			conditions += " and exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)"%(warehouse_details.lft,
				warehouse_details.rgt)

	return conditions

def get_stock_ledger_entries(filters):
	conditions = get_conditions(filters)
	
	join_table_query = ""
	if filters.get("item_group"):
		join_table_query = "inner join `tabItem` item on item.name = sle.item_code"
	
	return frappe.db.sql("""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index) %s
		where sle.docstatus < 2 %s 
		order by sle.posting_date, sle.posting_time, sle.name""" %
		(join_table_query, conditions), as_dict=1)

def get_item_warehouse_map(filters):
	iwb_map = {}
#	from_date = getdate(filters.get("from_date"))
#	to_date = getdate(filters.get("to_date"))
	to_date = utils.today()
	from_date = getdate(to_date) - timedelta(days=300)

	sle = get_stock_ledger_entries(filters)

	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
	#	mat_req_qty = get_material_request(d.item_code)
	#	pen_po_qty = get_purchase_order(d.item_code)
				
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0
			})

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date:
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= getdate(from_date) and d.posting_date <= getdate(to_date):
			if qty_diff > 0:
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff
		
	iwb_map = filter_items_with_no_transactions(iwb_map)

	return iwb_map
	
def filter_items_with_no_transactions(iwb_map):
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]
		
		no_transactions = True
		float_precision = cint(frappe.db.get_default("float_precision")) or 3
		for key, val in qty_dict.items():
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False
		
		if no_transactions:
			iwb_map.pop((company, item, warehouse))

	return iwb_map

def get_item_details(filters):
	condition = ''
	value = ()

	if filters.get("item_code"):
		condition = "where item_code=%s"
		value = (filters.get("item_code"),)

	items = frappe.db.sql("""select name, item_name, stock_uom, item_group, brand, description
		from tabItem {condition}""".format(condition=condition), value, as_dict=1)

		
	return dict((d.name , d) for d in items)

def get_item_reorder_details(filters):
	condition = ''
	value = ()
	if filters.get("item_code"):
		condition = "where parent=%s"
		value = (filters.get("item_code"),)

	item_reorder_details = frappe.db.sql("""select parent,warehouse,warehouse_reorder_qty,warehouse_reorder_level
		from `tabItem Reorder` {condition}""".format(condition=condition), value, as_dict=1)
	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)

def get_material_sel_request(filters):
	condition = ''
	value = ()
	curr_date = utils.today()

	if filters.get("cutoff_date"):
		cutoff_date = filters.get("cutoff_date")
#		diff_date = getdate(curr_date) - timedelta(days=ignore_days)

		condition = " and mr.transaction_date >= '%s'" % frappe.db.escape(filters.get("cutoff_date"))


	if filters.get("warehouse"):
		condition += " and mri.warehouse='%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)

	if filters.get("item_code"):
		condition += "and mri.item_code='%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

		pending_sel_materials = frappe.db.sql("""select mri.item_code, sum(qty), sum(ordered_qty) from `tabMaterial Request Item` mri, `tabMaterial Request` mr where mri.parent = mr.name and mr.status = "Submitted" and mr.docstatus not in ("2", "0") %s""" % condition,  as_dict=1)

	else:
		pending_sel_materials = frappe.db.sql("""select mri.item_code, sum(qty), sum(ordered_qty) from `tabMaterial Request Item` mri, `tabMaterial Request` mr where mri.parent = mr.name and mr.status = "Submitted" and mr.docstatus not in ("2", "0") %s group by mri.item_code""" % condition, as_dict=1)

#	pending_mat_com_qty = flt(frappe.db.sql("""select sum(ordered_qty) from `tabMaterial Request Item` mri, `tabMaterial Request` mr where mri.parent = mr.name and mr.status not in ("Stopped", "Cancelled") and mri.item_code = %s""", (item_code))[0][0])
#	pending_mat_req_qty = pending_mat_tot_qty - pending_mat_com_qty

	return dict((d.item_code , d) for d in pending_sel_materials)

def get_material_request(filters):
	condition = ''
	value = ()

	if filters.get("warehouse"):
		condition = " and mri.warehouse='%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)

	if filters.get("item_code"):
		condition += "and mri.item_code='%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

		pending_materials = frappe.db.sql("""select mri.item_code, sum(qty), sum(ordered_qty) from `tabMaterial Request Item` mri, `tabMaterial Request` mr where mri.parent = mr.name and mr.status= "Submitted" and mr.docstatus = "1" %s""" % condition,  as_dict=1)

	else:
		pending_materials = frappe.db.sql("""select mri.item_code, sum(qty), sum(ordered_qty) from `tabMaterial Request Item` mri, `tabMaterial Request` mr where mri.parent = mr.name and mr.status = "Submitted" and mr.docstatus = "1" %s group by mri.item_code""" % condition, as_dict=1)

	return dict((d.item_code , d) for d in pending_materials)


def get_purchase_sel_orders(filters):
	condition = ''
	value = ()
	curr_date = utils.today()

	if filters.get("cutoff_date"):
		cutoff_date = filters.get("cutoff_date")
#		diff_date = getdate(curr_date) - timedelta(days=ignore_days)

		condition = " and po.transaction_date >= '%s'" % frappe.db.escape(filters.get("cutoff_date"))


	if filters.get("warehouse"):
		condition += " and poi.warehouse='%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)


	if filters.get("item_code"):
		condition += " and poi.item_code='%s'" % frappe.db.escape(filters.get("item_code"), percent=False)


		pending_purchase_sel_orders = frappe.db.sql("""select poi.item_code, sum(qty), sum(received_qty) from `tabPurchase Order Item` poi, `tabPurchase Order` po where poi.parent = po.name and po.status not in ("Closed", "Delivered" "Cancelled") and po.docstatus = "1"  %s""" % condition, as_dict=1)

	else:
		pending_purchase_sel_orders = frappe.db.sql("""select poi.item_code, sum(qty), sum(received_qty) from `tabPurchase Order Item` poi, `tabPurchase Order` po where poi.parent = po.name and po.status not in ("Closed", "Delivered" "Cancelled") and po.docstatus = "1" %s group by poi.item_code"""  % condition, as_dict=1)

	
	return dict((d.item_code , d) for d in pending_purchase_sel_orders)


def get_purchase_orders(filters):
	condition = ''
	value = ()

	if filters.get("warehouse"):
		condition += " and poi.warehouse='%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)


	if filters.get("item_code"):
		condition += " and poi.item_code='%s'" % frappe.db.escape(filters.get("item_code"), percent=False)


		pending_purchase_orders = frappe.db.sql("""select poi.item_code, sum(qty), sum(received_qty) from `tabPurchase Order Item` poi, `tabPurchase Order` po where poi.parent = po.name and po.status not in ("Closed", "Delivered" "Cancelled") and po.docstatus = "1"  %s""" % condition, as_dict=1)

	else:
		pending_purchase_orders = frappe.db.sql("""select poi.item_code, sum(qty), sum(received_qty) from `tabPurchase Order Item` poi, `tabPurchase Order` po where poi.parent = po.name and po.status not in ("Closed", "Delivered" "Cancelled") and po.docstatus = "1" %s group by poi.item_code"""  % condition, as_dict=1)

	
	return dict((d.item_code , d) for d in pending_purchase_orders)


def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

#@frappe.whitelist()
#def check_for_whole_number(bomno):
#	return (frappe.db.sql("""select must_be_whole_number from `tabUOM` where name IN (select uom from `tabBOM`where name = %s) """, (bomno))[0][0])

#def check_for_whole_number_itemwise(item):
#	return (frappe.db.sql("""select must_be_whole_number from `tabUOM` where name IN (select stock_uom from `tabItem`where name = %s) """, (item))[0][0])



@frappe.whitelist()
def make_stock_requisition(args):
	global required_date_count
#	if getdate(required_date) == getdate(datetime.now().strftime('%Y-%m-%d')):
#		if required_date_count == False:
#			required_date_count = True
#			frappe.throw(_("Required Date is set to today's date, if you still want to proceed click on 'Stock Requisition' again"))

#	test_whole_number = check_for_whole_number(bom_for_validation)
#	if test_whole_number and float(qty_to_make) % 1 != 0:
#		frappe.throw("Quantity to Make should be whole number")

	innerJson_requisition = " "
	innerJson_transfer = " "
	ret = ""
	newJson_transfer = {
	"company": company,
	"doctype": "Stock Requisition",
	"title": "Material Transfer",
	"material_request_type": "Material Transfer",
	"quantity_to_make": 1,


	"items": [
]
}

	newJson_requisition = {
	"company": company,
	"doctype": "Stock Requisition",
	"title": "Purchase",
	"material_request_type": "Purchase",
	"quantity_to_make": 1,


	"items": [
]
}

	no_transfer = 0	
	required = ""
	whse_map = {}
	empty_desc = []
	empty_uom = []

	for rows in data:
		required = str(rows[14]).strip()

		if (required and float(required) != 0.0):
			
			if rows[4] == "":
				empty_desc.append(rows[0])
			if rows[6] == "":
				empty_uom.append(rows[0])
			no_transfer = no_transfer + 1
				
			innerJson_transfer =	{
			"doctype": "Stock Requisition Item",
			"item_code": rows[0],
			"qty": rows[14],
			"schedule_date": required_date,
			"warehouse": warehouse,
			"uom": rows[6],
			"description": rows[4]
			   }

			newJson_transfer["items"].append(innerJson_transfer)

	if float(no_transfer) == 0:
		frappe.msgprint("Planning Warehouse has all the item !! Stock transfer is not required")
	else:
		if empty_uom:
			frappe.throw(_("UOM for  {0} is empty,Please add UOM in Item Master Doctype.").format(frappe.bold(comma_and(empty_uom))))
		if empty_desc:
			frappe.throw(_("Description for  {0} is empty,Please add description in Item Master Doctype.").format(frappe.bold(comma_and(empty_desc))))
		doc = frappe.new_doc("Stock Requisition")
		doc.update(newJson_transfer)
		if args == "as a draft":
			doc.save()
		else:
			doc.submit()
		ret = doc.doctype

	
	del data[:]
	del required
	if ret:
		return ret
