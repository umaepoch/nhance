# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast
from erpnext.stock.utils import update_included_uom_in_report

def execute(filters=None):
	include_uom = filters.get("include_uom")
	columns = get_columns()
	items = get_items(filters)
	sl_entries = get_stock_ledger_entries(filters, items)
	#print "sl_entries---------------",sl_entries
	item_details = get_item_details(items, sl_entries, include_uom)
	opening_row = get_opening_balance(filters, columns)
	data = []
	'''
	for sle in sl_entries:
		print "voucher type--------------",sle.voucher_type
		print "voucher no--------------",sle.voucher_no
		print "item code --------------",sle.item_code
	'''
	conversion_factors = []
	stock_qty = 0.0
	rarb_id = []
	s_rarb = ""
	t_rarb = ""
	
	if opening_row:
		data.append(opening_row)
	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		voucher_type = sle.voucher_type
		voucher_no = sle.voucher_no
		warehouse = sle.warehouse
		
		voucher_details = get_rarb_vouchers(voucher_type,voucher_no,sle.item_code, sle.voucher_detail_no)
		
		for voucher in voucher_details:
			item_code = voucher.item_code
			if voucher.pch_rarb_location_src is not None and voucher.s_warehouse == sle.warehouse:
				voucher_balance_qty = get_rarb_balance_src_qty(voucher_type,voucher_no,sle.item_code, sle.voucher_detail_no,warehouse,voucher.pch_rarb_location_src)
				
				available_qty = get_available_src_qty(voucher_balance_qty,stock_qty,rarb_id,voucher.pch_rarb_location_src,sle.item_code,sle.voucher_type)
				
				for qty in available_qty:
					if voucher.pch_rarb_location_src == qty['id'] and item_code == qty['item_code']:
						stock_qty = qty['stock_qty']

				data.append([sle.date, sle.item_code, item_detail.item_name, item_detail.item_group,
					voucher.pch_rarb_location_src,
					item_detail.brand, item_detail.description, sle.warehouse,
					item_detail.stock_uom, sle.actual_qty, stock_qty,
					(sle.incoming_rate if sle.actual_qty > 0 else 0.0),
					sle.valuation_rate, sle.stock_value, sle.voucher_type, sle.voucher_no,
					sle.batch_no, sle.serial_no, sle.project, sle.company])
			elif voucher.pch_rarb_location_trg is not None and voucher.t_warehouse == sle.warehouse:
				voucher_balance_qty = get_rarb_balance_qty(voucher_type,voucher_no,sle.item_code, sle.voucher_detail_no,warehouse,voucher.pch_rarb_location_trg)
				
				available_qty = get_available_qty(voucher_balance_qty,stock_qty,rarb_id,voucher.pch_rarb_location_trg,sle.item_code)
				
				
				for qty in available_qty:
					if voucher.pch_rarb_location_trg == qty['id'] and sle.item_code == qty['item_code']:
						stock_qty = qty['stock_qty']
						
				data.append([sle.date, sle.item_code, item_detail.item_name, item_detail.item_group,
					voucher.pch_rarb_location_trg,
					item_detail.brand, item_detail.description, sle.warehouse,
					item_detail.stock_uom, sle.actual_qty, stock_qty,
					(sle.incoming_rate if sle.actual_qty > 0 else 0.0),
					sle.valuation_rate, sle.stock_value, sle.voucher_type, sle.voucher_no,
					sle.batch_no, sle.serial_no, sle.project, sle.company])

		if include_uom:
			conversion_factors.append(item_detail.conversion_factor)
	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
	return columns, data

def get_columns():
	columns = [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Datetime", "width": 95},
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 130},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 100},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		{"label": _("RARB Location"), "fieldname": "source_location", "fieldtype": "Data", "width": 100},
		{"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 100},
		{"label": _("Description"), "fieldname": "description", "width": 200},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 100},
		{"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 100},
		{"label": _("Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 50, "convertible": "qty"},
		{"label": _("Balance Qty"), "fieldname": "qty_after_transaction", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Incoming Rate"), "fieldname": "incoming_rate", "fieldtype": "Currency", "width": 110,
			"options": "Company:company:default_currency", "convertible": "rate"},
		{"label": _("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 110,
			"options": "Company:company:default_currency", "convertible": "rate"},
		{"label": _("Balance Value"), "fieldname": "stock_value", "fieldtype": "Currency", "width": 110,
			"options": "Company:company:default_currency"},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 110},
		{"label": _("Voucher #"), "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 100},
		{"label": _("Batch"), "fieldname": "batch_no", "fieldtype": "Link", "options": "Batch", "width": 100},
		{"label": _("Serial #"), "fieldname": "serial_no", "fieldtype": "Link", "options": "Serial No", "width": 100},
		{"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 100},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 110}
	]

	return columns

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = 'and sle.item_code in ({})'\
			.format(', '.join(['"' + frappe.db.escape(i) + '"' for i in items]))

	return frappe.db.sql("""select concat_ws(" ", posting_date, posting_time) as date,
			item_code, warehouse, actual_qty, qty_after_transaction, incoming_rate, valuation_rate,
			stock_value, voucher_type, voucher_no, batch_no, serial_no, company, project,voucher_detail_no
		from `tabStock Ledger Entry` sle 
		where company = %(company)s and
			posting_date between %(from_date)s and %(to_date)s
			{sle_conditions}
			{item_conditions_sql}
			order by posting_date asc, posting_time asc, name asc"""\
		.format(
			sle_conditions=get_sle_conditions(filters),
			item_conditions_sql = item_conditions_sql
		), filters, as_dict=1)

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def get_item_details(items, sl_entries, include_uom):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sl_entries]))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if include_uom:
		cf_field = ", ucd.conversion_factor"
		cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom='%s'" \
			% frappe.db.escape(include_uom)

	item_codes = ', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])
	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom {cf_field}
		from
			`tabItem` item
			{cf_join}
		where
			item.name in ({item_codes})
	""".format(cf_field=cf_field, cf_join=cf_join, item_codes=item_codes), as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	return item_details

def get_sle_conditions(filters):
	conditions = []
	if filters.get("warehouse"):
		warehouse_condition = get_warehouse_condition(filters.get("warehouse"))
		if warehouse_condition:
			conditions.append(warehouse_condition)
	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")
	if filters.get("batch_no"):
		conditions.append("batch_no=%(batch_no)s")
	if filters.get("project"):
		conditions.append("project=%(project)s")

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_opening_balance(filters, columns):
	if not (filters.item_code and filters.warehouse and filters.from_date):
		return

	from erpnext.stock.stock_ledger import get_previous_sle
	last_entry = get_previous_sle({
		"item_code": filters.item_code,
		"warehouse_condition": get_warehouse_condition(filters.warehouse),
		"posting_date": filters.from_date,
		"posting_time": "00:00:00"
	})
	row = [""]*len(columns)
	row[1] = _("'Opening'")
	for i, v in ((9, 'qty_after_transaction'), (11, 'valuation_rate'), (12, 'stock_value')):
			row[i] = last_entry.get(v, 0)

	return row

def get_warehouse_condition(warehouse):
	warehouse_details = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"], as_dict=1)
	if warehouse_details:
		return " exists (select name from `tabWarehouse` wh \
			where wh.lft >= %s and wh.rgt <= %s and warehouse = wh.name)"%(warehouse_details.lft,
			warehouse_details.rgt)

	return ''

def get_item_group_condition(item_group):
	item_group_details = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=1)
	if item_group_details:
		return "item.item_group in (select ig.name from `tabItem Group` ig \
			where ig.lft >= %s and ig.rgt <= %s and item.item_group = ig.name)"%(item_group_details.lft,
			item_group_details.rgt)

	return ''
def get_rarb_vouchers(voucher_type,voucher_no,item_code,voucher_detail_no):
	rarb_locations = ""
	if voucher_type == "Stock Entry":
		
		rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src,sti.pch_rarb_location_trg ,
							sti.t_warehouse as t_warehouse, sti.s_warehouse as s_warehouse
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""'""", as_dict =1)
	elif voucher_type == "Purchase Invoice":
		
		rarb_locations = frappe.db.sql("""
						select
							 sti.pch_rarb_location_trg,sti.item_code,sti.warehouse as t_warehouse
						from 
							`tabPurchase Invoice` st ,`tabPurchase Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""'""", as_dict =1)
	elif voucher_type == "Purchase Receipt":
		
		rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_trg, sti.item_code, sti.warehouse as t_warehouse
						from 
							`tabPurchase Receipt` st ,`tabPurchase Receipt Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""'""", as_dict =1)
	elif voucher_type == "Sales Invoice":
		
		rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src, sti.item_code, sti.warehouse as s_warehouse
						from 
							`tabSales Invoice` st ,`tabSales Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""'""", as_dict =1)
	elif voucher_type == "Stock Reconciliation":
		
		rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src, sti.item_code,sti.warehouse as s_warehouse
						from 
							`tabStock Reconciliation` st ,`tabStock Reconciliation Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							""", as_dict =1)
	elif voucher_type == "Delivery Note":
		
		rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src, sti.item_code,sti.warehouse as s_warehouse
						from 
							`tabDelivery Note` st ,`tabDelivery Note Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name = '"""+voucher_detail_no+"""'""", as_dict =1)
	return rarb_locations
def get_rarb_balance_qty(voucher_type,voucher_no,item_code,voucher_detail_no,warehouse,rarb_location):
	stock_qty = 0.0
	rarb_s_warehouse_qty = ""
	rarb_t_warehouse_qty = ""
	if voucher_type == "Stock Entry":
		
		rarb_t_warehouse_qty = frappe.db.sql("""
						select 
							 sti.qty as t_qty
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""' and sti.t_warehouse = %s and
							sti.pch_rarb_location_trg = %s""",(warehouse,rarb_location), as_dict =1)
	elif voucher_type == "Purchase Invoice":
		
		rarb_t_warehouse_qty = frappe.db.sql("""
						select
							sti.qty as t_qty
						from 
							`tabPurchase Invoice`  st, `tabPurchase Invoice Item`  sti
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""' and sti.warehouse = %s and
							sti.pch_rarb_location_trg = %s""",(warehouse,rarb_location), as_dict =1)
	elif voucher_type == "Purchase Receipt":
		
		rarb_t_warehouse_qty = frappe.db.sql("""
						select 
							sti.qty as t_qty
						from 
							`tabPurchase Receipt` st, `tabPurchase Receipt Item` sti
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""' and sti.warehouse = %s and
							sti.pch_rarb_location_trg = %s""",(warehouse,rarb_location), as_dict =1)
	'''
	elif voucher_type == "Stock Reconciliation":
		
		rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src, sti.item_code,sti.warehouse as s_warehouse
						from 
							`tabStock Reconciliation` st ,`tabStock Reconciliation Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							""", as_dict =1)
	'''
	target_qty = 0.0
	if rarb_t_warehouse_qty:
		target_qty = rarb_t_warehouse_qty[0].t_qty
	return target_qty
def get_rarb_balance_src_qty(voucher_type,voucher_no,item_code,voucher_detail_no,warehouse,rarb_location):
	stock_qty = 0.0
	rarb_s_warehouse_qty = ""
	rarb_t_warehouse_qty = ""
	if voucher_type == "Stock Entry":
		
		rarb_s_warehouse_qty = frappe.db.sql("""
						select 
							sti.qty as s_qty
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""' and sti.s_warehouse = %s and
							sti.pch_rarb_location_src = %s""",(warehouse,rarb_location), as_dict =1)
	elif voucher_type == "Sales Invoice":
		
		rarb_s_warehouse_qty = frappe.db.sql("""
						select 
							sti.qty as s_qty
						from 
							`tabSales Invoice`  st ,`tabSales Invoice Item`  sti
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""' and sti.warehouse = %s and
							sti.pch_rarb_location_src = %s""",(warehouse,rarb_location), as_dict =1)
	elif voucher_type == "Delivery Note":
		
		rarb_s_warehouse_qty = frappe.db.sql("""
						select 
							sti.qty as s_qty
						from 
							`tabDelivery Note` st, `tabDelivery Note Item`  sti
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.name ='"""+voucher_detail_no+"""' and sti.warehouse = %s and
							sti.pch_rarb_location_src = %s""",(warehouse,rarb_location), as_dict =1)
	
	elif voucher_type == "Stock Reconciliation":
		
		rarb_s_warehouse_qty = frappe.db.sql("""
						select 
							sti.qty as s_qty
						from 
							`tabStock Reconciliation` st ,`tabStock Reconciliation Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.warehouse = %s and
							sti.pch_rarb_location_src = %s""",(warehouse,rarb_location), as_dict =1)
	
	source_qty = 0.0
	if rarb_s_warehouse_qty:
		source_qty = rarb_s_warehouse_qty[0].s_qty
	return source_qty

def get_available_qty(voucher_balance_qty,stock_qty,rarb_id,rarb_location, item_code):
	if rarb_id:
		if rarb_location in [d['id'] for d in rarb_id 
					if d['item_code'] == item_code]:
			print "item_code--------------------",item_code
			print "rarb_location-----------------",rarb_location
			for rarb in rarb_id:
				if rarb_location == rarb['id'] and rarb['item_code']== item_code:
					
					total_qty = rarb['stock_qty']
					total_qty += voucher_balance_qty
					rarb['stock_qty'] = total_qty
		else:
			rarb_id.append({
				"id": rarb_location,
				"item_code":item_code, 
				"stock_qty": voucher_balance_qty
				})
	else:
		rarb_id.append({
			"id": rarb_location,
			"item_code":item_code, 
			"stock_qty": voucher_balance_qty
		})
	
	print "rarb_id--------------------",rarb_id
	
	return rarb_id
def get_available_src_qty(voucher_balance_qty,stock_qty,rarb_id,rarb_location,item_code,voucher_type):
	if voucher_type != "Stock Reconciliation":
		if rarb_id:
			if rarb_location in [d['id'] for d in rarb_id] and item_code in [d['item_code'] for d in rarb_id]:
				for rarb in rarb_id:
					if rarb_location == rarb['id'] and rarb['item_code']== item_code:
						total_qty = rarb['stock_qty']
						total_qty -= voucher_balance_qty
						#rarb_id = []
						rarb['stock_qty'] = total_qty

			else:
				rarb_id.append({
					"id": rarb_location,
					"item_code":item_code,
					"stock_qty": voucher_balance_qty
					})
		else:
			rarb_id.append({
				"id": rarb_location,
				"item_code":item_code, 
				"stock_qty": voucher_balance_qty
			})
	else:
		if rarb_id:
			if rarb_location in [d['id'] for d in rarb_id] and item_code in [d['item_code'] for d in rarb_id]:
				for rarb in rarb_id:
					if rarb_location == rarb['id'] and rarb['item_code']== item_code:
						
						
						rarb['stock_qty'] = voucher_balance_qty
			else:
				rarb_id.append({
					"id": rarb_location,
					"item_code":item_code,
					"stock_qty": voucher_balance_qty
					})
		else:
			rarb_id.append({
				"id": rarb_location,
				"item_code":item_code, 
				"stock_qty": voucher_balance_qty
			})
	return rarb_id
