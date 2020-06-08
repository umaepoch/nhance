# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.utils import flt, getdate

def execute(filters=None):
	if not filters: filters = {}
	validate_filters(filters)
	columns = get_columns()
	item_map = get_item_details(filters)
	#print("item_map",item_map)
	iwb_map = get_item_warehouse_map(filters)
	print("iwb_map",iwb_map)
	no_warehouse_items_list = fetch_no_warehouse_items_list()
	#print("no_warehouse_items_list",no_warehouse_items_list)
	data = []
	summ_data = []
	item_prev = ""
	item_work = ""
	item_count = 1
	tot_bal_qty = 0
	loop_count = 1
	skip_row = 0
	total_stock = 0
	item_stock = 0
	stock_recon = 0
	items_entry_list = []

	for (company, item, warehouse) in sorted(iwb_map):
		if warehouse:
			#print("entered in sorted iwb_map if condition")
			item_stock, stock_recon = get_total_stock(item)
			total_stock = item_stock + stock_recon
			#print("total_stock",total_stock)
		else:
			#print("entered in sorted iwb_map else condition")
			total_stock = 0
			item_stock = 0
			stock_recon = 0

		qty_dict = iwb_map[(company, item, warehouse)]
		#print("qty_dict",qty_dict);
		data.append(
				[item,
				item_map[item]["item_group"],
				item_map[item]["item_name"],
				item_map[item]["detail"],
				item_map[item]["manufacturer"],
				item_map[item]["manufacturer_part_no"],
				item_map[item]["case"],
				warehouse,
				qty_dict.bal_qty, 
			total_stock, 
			item_stock, 
			stock_recon
			])
	for rows in data:
		#print ("item_code-----------------------", rows[0])
		#print ("rows----------------", rows)
		#print ("qty",rows[8])
		if loop_count == 1:
			#print("entered in  if loop_count==1 condition")
			item_prev = rows[0]
			if (rows[7] is None or rows[7] is "" and rows[8] == 0.0):
				#print("entered in  first if loop_count==1 if condition")
				skip_row = 1
			else:
				#print("entered in else loop_count==1 if condition")
				if rows[8] > 0:
					summ_data.append([item_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]])
					#print("summ_data inside else of loop_count==1",summ_data)
					items_entry_list.append(rows[0])
					#print("append rows[8] to items_entry_list")

			if (skip_row == 1 and (rows[9] is None or rows[9] == 0.0)):
				#print("entered in  second if loop_count==1 if condition")
				summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], "", rows[8]])
				items_entry_list.append(rows[0])
				skip_row = 0

			if (skip_row == 1 and rows[11] > 0 and (rows[10] is None or rows[10] <= 0.0)):
				#print("entered in  third if loop_count==1 if condition")
				summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], "", rows[8]])
				items_entry_list.append(rows[0])
				skip_row = 0

#			item_count = item_count + 1
		else:
			#print("entered in  else loop_count==1 condition")
			item_work = rows[0]

			if (rows[7] is None or rows[7] is "" and rows[8] == 0.0):
				skip_row = 1
				#print("entered in  else loop_count==1 if condition")

			else:
				#print("entered in  else loop_count==1 else condition")
				if rows[8] > 0:
					summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]])
					items_entry_list.append(rows[0])
			if item_prev == item_work:
				item_count = item_count + 1
				tot_bal_qty =float(tot_bal_qty + rows[8])
				skip_row = 0
			else:
				if (skip_row == 1 and (rows[9] is None or rows[9] == 0.0)):
					summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], "", rows[8]])
					items_entry_list.append(rows[0])

				if (skip_row == 1 and rows[11] > 0 and (rows[10] is None or rows[10] <= 0.0)):
					summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], "", rows[8]])
					items_entry_list.append(rows[0])
				skip_row = 0
				item_prev = item_work
				item_count = 0

		loop_count = loop_count + 1

	items_entry_list = list(set(items_entry_list))
	#print ("------length of-----items_entry_list---------------", len(items_entry_list))
	#print ("------no_warehouse_items_list--------------", no_warehouse_items_list)
	for no_warehouse_item in no_warehouse_items_list:
		if no_warehouse_item not in items_entry_list:
			#print ("------no_warehouse_item--------------", no_warehouse_item)
			no_whse_item_details = fetch_no_warehouse_item_details(no_warehouse_item)
			item_group = no_whse_item_details[0]['item_group']
			item_name = no_whse_item_details[0]['item_name']
			detail = no_whse_item_details[0]['detail']
			manufacturer = no_whse_item_details[0]['manufacturer']
			manufacturer_part_no = no_whse_item_details[0]['manufacturer_part_no']
			case = no_whse_item_details[0]['case']

			no_whse_item_details1 = fetch_no_warehouse_items_entry(filters)
			#print ("------no_whse_item_details--------------", no_whse_item_details)
			if no_whse_item_details1 is None:
				#print("entered in  if no_whse_item_details1 condition")
				summ_data.append([no_warehouse_item, item_group, item_name, detail, manufacturer, manufacturer_part_no, case, "", 0.0])
			else:
				#print("entered in  else no_whse_item_details1 condition")
				for no_whse_items in no_whse_item_details1:
					if no_warehouse_item == no_whse_items['item_code']:
						summ_data.append([no_warehouse_item, item_group, item_name, detail, manufacturer, manufacturer_part_no, case, "", 0.0])
				

	return columns, summ_data

def fetch_no_warehouse_items_list():
	no_warehouse_items_list = []
	bin_items_list = frappe.db.sql(""" select item_code, sum(actual_qty) as qty  from `tabBin` group by item_code """, as_dict =1)
	for items_data in bin_items_list:
		qty = items_data['qty']
		item_code = items_data['item_code']
		if qty == 0.0:
			no_warehouse_items_list.append(item_code)
	return no_warehouse_items_list

def fetch_no_warehouse_item_details(no_warehouse_item):
	details = frappe.db.sql(""" select item_group,item_name,detail,manufacturer,manufacturer_part_no,`case` from `tabItem` where item_code=%s """, no_warehouse_item, as_dict =1)
	return details

def fetch_no_warehouse_items_entry(filters):
	conditions = get_conditions3(filters)
	#print "conditions------", conditions
	if conditions is not "":
		return frappe.db.sql(""" select item_code,item_name,item_group,detail,manufacturer,manufacturer_part_no,`case` from `tabItem` where item_code is not NULL%s""" % conditions, as_dict=1)
	else:
		return None

def get_columns():
	"""return columns"""

	columns = [
		_("Item")+":Link/Item:71",
		_("Item Group")+"::135",
		_("Item Name")+"::290",
		_("Detail")+"::80",
		_("MFR")+":Link/Manufacturer:110",
		_("MFR PN")+"::130",
		_("Case")+"::90",
		_("Warehouse")+":Link/Warehouse:100",
		_("Qty")+":Float:60"
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += ' and sle.posting_date <= %s' % frappe.db.escape(filters["to_date"])
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("item_code"):
		conditions += 'and sle.item_code = %s' % frappe.db.escape(filters.get("item_code"), percent=False)

	if filters.get("item_group"):
		conditions += ' and it.item_group = %s' % frappe.db.escape(filters.get("item_group"), percent=False)

	if filters.get("warehouse"):
		conditions += ' and sle.warehouse = %s' % frappe.db.escape(filters.get("warehouse"), percent=False)

	if filters.get("item_name"):
		conditions += 'and it.item_name =%s'  % frappe.db.escape(filters.get("item_name"), percent=False)

	if filters.get("cases"):
		conditions += ' and it.case =%s'  % frappe.db.escape(filters.get("cases"), percent=False)

	if filters.get("detail"):
		conditions += 'and it.detail = %s' % frappe.db.escape(filters.get("detail"), percent=False)

	if filters.get("mfr"):
		conditions += 'and it.manufacturer = %s'  % frappe.db.escape(filters.get("mfr"), percent=False)

	if filters.get("mfr_pn"):
		conditions += ' and it.manufacturer_part_no = %s'  % frappe.db.escape(filters.get("mfr_pn"), percent=False)

	return conditions

def get_conditions2(filters):
	conditions = ""
	if filters.get("item_code"):
		conditions += ' and it.item_code = %s'  % frappe.db.escape(filters.get("item_code"), percent=False)

	if filters.get("item_group"):
		conditions += ' and it.item_group = %s'  % frappe.db.escape(filters.get("item_group"), percent=False)

	if filters.get("item_name"):
		conditions += ' and it.item_name = %s' % frappe.db.escape(filters.get("item_name"), percent=False)

	if filters.get("cases"):
		conditions += ' and it.case = %s'  % frappe.db.escape(filters.get("cases"), percent=False)

	if filters.get("detail"):
		conditions += 'and it.detail = %s'  % frappe.db.escape(filters.get("detail"), percent=False)

	if filters.get("mfr"):
		conditions += ' and it.manufacturer = %s'  % frappe.db.escape(filters.get("mfr"), percent=False)

	if filters.get("mfr_pn"):
		conditions += ' and it.manufacturer_part_no = %s' % frappe.db.escape(filters.get("mfr_pn"), percent=False)

	return conditions

def get_conditions3(filters):
	conditions = ""
	if filters.get("item_code"):
		conditions += ' and item_code = %s'  % frappe.db.escape(filters.get("item_code"), percent=False)

	if filters.get("item_group"):
		conditions += ' and item_group =%s'  % frappe.db.escape(filters.get("item_group"), percent=False)

	if filters.get("item_name"):
		conditions += ' and item_name = %s' % frappe.db.escape(filters.get("item_name"), percent=False)

	if filters.get("cases"):
		conditions += ' and case =%s' % frappe.db.escape(filters.get("cases"), percent=False)

	if filters.get("detail"):
		conditions += ' and detail = %s' % frappe.db.escape(filters.get("detail"), percent=False)

	if filters.get("mfr"):
		conditions += ' and manufacturer = %s' % frappe.db.escape(filters.get("mfr"), percent=False)

	if filters.get("mfr_pn"):
		conditions += ' and manufacturer_part_no = %s' % frappe.db.escape(filters.get("mfr_pn"), percent=False)

	return conditions

def get_stock_ledger_entries(filters):
	conditions = get_conditions(filters)
	print("conditions",conditions)
	ledger_value=frappe.db.sql("""select sle.item_code,sle.warehouse, sle.posting_date, actual_qty, sle.valuation_rate,
		sle.company, voucher_type, qty_after_transaction, stock_value_difference
		from `tabStock Ledger Entry` sle, tabItem it
		where sle.docstatus < 2 and it.item_code = sle.item_code %s order by posting_date, posting_time, sle.name""" %
		conditions, as_dict=1)
	#print("ledger_value",ledger_value);
	return ledger_value

def get_stock_ledger_entries_wo_sl(filters):
	conditions = get_conditions2(filters)
	print("conditions2",conditions)
	stock_value=frappe.db.sql("""select it.item_code, "" as warehouse, "" as posting_date, 0 as actual_qty, 0 as valuation_rate,
			"" as company, "" as voucher_type, 0 as qty_after_transaction, 0 as stock_value_difference from tabItem it
			where not exists (select 1 from `tabStock Ledger Entry` sle where sle.docstatus < 2 and sle.item_code = it.item_code) %s""" % conditions, as_dict=1)
	#print("stock_value",stock_value)
	return stock_value

def get_item_warehouse_map(filters):
	iwb_map = {}
	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])
	kle = {}
	sle = get_stock_ledger_entries(filters)
	#print("sle",sle)
	kle = get_stock_ledger_entries_wo_sl(filters)
	#print("kle",kle)
	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0, "uom": None
			})

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]
		#print("qty_dict of sle",qty_dict)
		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		else:
			qty_diff = flt(d.actual_qty)
		value_diff = flt(d.stock_value_difference)
		#print("qty_diff",qty_diff)
		#print("value_diff",value_diff)
		

		if d.posting_date < from_date:
			#print("posting date less than from date")
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			print("posting date less than from date and posting date less than to date")
			if qty_diff > 0:
					qty_dict.in_qty += qty_diff
					qty_dict.in_val += value_diff
			else:
					qty_dict.out_qty += abs(qty_diff)
					qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff
		print("qty_dict.bal_qty in sle",qty_dict.bal_qty)

	if kle:    	
		for d in kle:
				key = (d.company, d.item_code, d.warehouse)
				if key not in iwb_map:
					iwb_map[key] = frappe._dict({
						"opening_qty": 0.0, "opening_val": 0.0,
						"in_qty": 0.0, "in_val": 0.0,
						"out_qty": 0.0, "out_val": 0.0,
						"bal_qty": 0.0, "bal_val": 0.0,
						"val_rate": 0.0, "uom": None
					})

				qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]
				#print("qty_dict of kle",qty_dict);
				if d.voucher_type == "Stock Reconciliation":
					qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
				else:
					print("entered in else of kle")
					qty_diff = flt(d.actual_qty)

					value_diff = flt(d.stock_value_difference)
		
					qty_dict.opening_qty = 0
					qty_dict.opening_val = 0

					qty_dict.in_qty = 0
					qty_dict.in_val = 0
					qty_dict.out_qty = 0
					qty_dict.out_val = 0

					qty_dict.val_rate = 0
					qty_dict.bal_qty = 0
					qty_dict.bal_val = 0
	#print("qty_dict.in_qty in kle",qty_dict.in_qty)
	#print("qty_dict.out_qty",qty_dict.out_qty)
	#print("qty_dict.bal_qty",qty_dict.bal_qty)
	
	return iwb_map

def get_item_details(filters):
	condition = ''
	value = ()
	if filters.get("item_code"):
		condition = "where item_code=%s"
		value = (filters["item_code"],)

	items = frappe.db.sql("""select name, item_name, stock_uom, item_group, brand, description,
							 default_supplier, manufacturer, `case`, manufacturer_part_no, detail
		from tabItem {condition}""".format(condition=condition), value, as_dict=1)

	return dict((d.name, d) for d in items)

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

def get_total_stock(item_code):

	item_stock = flt(frappe.db.sql("""select sum(actual_qty)
			from `tabStock Ledger Entry`
			where item_code=%s""",
			(item_code))[0][0])

	stock_recon = flt(frappe.db.sql("""select sum(qty_after_transaction)
			from `tabStock Ledger Entry`
			where item_code=%s and voucher_type = 'Stock Reconciliation'""",
			(item_code))[0][0])

	return item_stock, stock_recon

