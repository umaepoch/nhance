# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now
from erpnext.stock.utils import update_included_uom_in_report
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition

from six import iteritems

def execute(filters=None):
	if not filters: filters = {}

	validate_filters(filters)

	include_uom = filters.get("include_uom")
	columns = get_columns()
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)
	#print "sle------------------",sle
	# if no stock ledger entry found return
	if not sle:
		return columns, []
	#rarb_voucher = get_rarb_vouchers(sle)
	iwb_map = get_item_warehouse_map(filters, sle)
	
	item_map = get_item_details(items, sle, filters)
	
	item_reorder_detail_map = get_item_reorder_details(item_map.keys())
	data = []
	conversion_factors = []
	
	for (company,item, warehouse,rarb_location) in sorted(iwb_map):
		if item_map.get(item):
			qty_dict = iwb_map[(company,item, warehouse,rarb_location)]
			item_reorder_level = 0
			item_reorder_qty = 0
			if item + warehouse in item_reorder_detail_map:
				item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
				item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]
			'''
			target_qty = get_target_qty(rarb_location,warehouse,item,sle)
			source_qty = get_source_qty(rarb_location,warehouse,item,sle)
			in_trg_qty = 0.0
			out_src_qty = 0.0
			bal_qty = 0.0
			for target in target_qty:
				for qty in target:
					if qty.rarb_id == rarb_location:
						in_trg_qty += qty.t_qty
			
			for source in source_qty:
				for qty in source:
					if qty.rarb_id == rarb_location:
						out_src_qty += qty.s_qty
			stock_qty = get_stock_qty(rarb_location,warehouse,item,sle)
			if stock_qty:
				for stock in stock_qty:
					for qty in stock:
						if qty.rarb_id == rarb_location:
							in_trg_qty += qty.s_qty
			bal_qty = in_trg_qty - out_src_qty
			'''
			report_data = [rarb_location,item, item_map[item]["item_name"],
				item_map[item]["item_group"],
				item_map[item]["brand"],
				item_map[item]["description"], warehouse,
				item_map[item]["stock_uom"], qty_dict.opening_qty,
				qty_dict.opening_val, qty_dict.in_qty,
				qty_dict.in_val, qty_dict.out_qty,
				qty_dict.out_val, qty_dict.bal_qty,
				qty_dict.bal_val, qty_dict.val_rate,
				item_reorder_level,
				item_reorder_qty,
				company
			]

			if filters.get('show_variant_attributes', 0) == 1:
				variants_attributes = get_variants_attributes()
				report_data += [item_map[item].get(i) for i in variants_attributes]

			if include_uom:
				conversion_factors.append(item_map[item].conversion_factor)

			data.append(report_data)

	if filters.get('show_variant_attributes', 0) == 1:
		columns += ["{}:Data:100".format(i) for i in get_variants_attributes()]

	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		{"label": _("RARB Location"), "fieldname": "rarb_location", "fieldtype": "Data", "width": 100},
		{"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		{"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 90},
		{"label": _("Description"), "fieldname": "description", "width": 140},
		{"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 100},
		{"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
		{"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Opening Value"), "fieldname": "opening_val", "fieldtype": "Float", "width": 110},
		{"label": _("In Qty"), "fieldname": "in_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("In Value"), "fieldname": "in_val", "fieldtype": "Float", "width": 80},
		{"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Out Value"), "fieldname": "out_val", "fieldtype": "Float", "width": 80},
		{"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Balance Value"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 100},
		{"label": _("Valuation Rate"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 90, "convertible": "rate"},
		{"label": _("Reorder Level"), "fieldname": "reorder_level", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Reorder Qty"), "fieldname": "reorder_qty", "fieldtype": "Float", "width": 80, "convertible": "qty"},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 100}
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters.get("to_date"))
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("warehouse"):
		warehouse_details = frappe.db.get_value("Warehouse",
			filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
		if warehouse_details:
			conditions += " and exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)"%(warehouse_details.lft,
				warehouse_details.rgt)

	return conditions

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = ' and sle.item_code in ({})'\
			.format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items]))

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,sle.voucher_no,sle.voucher_detail_no, sle.rarb_location
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index)
		where sle.docstatus < 2 %s %s
		order by sle.posting_date, sle.posting_time, sle.name""" %
		(item_conditions_sql, conditions), as_dict=1)

def get_item_warehouse_map(filters, sle):
	iwb_map = {}
	#print "sle---------------------",sle
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))
	#print "rarb_voucher---------------------",rarb_voucher
	for d in sle:
		rarb_location = ""
		if d.rarb_location:
			rarb_location = d.rarb_location
		item_code = d.item_code
		key = (d.company,d.item_code, d.warehouse, rarb_location)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0
			})
		keys = iwb_map.keys()
		qty_dict = iwb_map[(d.company,d.item_code, d.warehouse ,rarb_location)]
		if rarb_location:
			if d.voucher_type == "Stock Reconciliation":
		
				qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
			else:
				qty_diff = flt(d.actual_qty)

			value_diff = flt(d.stock_value_difference)

			if d.posting_date < from_date:
				qty_dict.opening_qty += qty_diff
				qty_dict.opening_val += value_diff

			elif d.posting_date >= from_date and d.posting_date <= to_date:
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
	for (company,item, warehouse,rarb_location) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item,warehouse,rarb_location)]

		no_transactions = True
		float_precision = cint(frappe.db.get_default("float_precision")) or 3
		for key, val in iteritems(qty_dict):
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			iwb_map.pop((company,item, warehouse,rarb_location))

	return iwb_map

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

def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sle]))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if filters.get("include_uom"):
		cf_field = ", ucd.conversion_factor"
		cf_join = "left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom='%s'" \
			% frappe.db.escape(filters.get("include_uom"))

	item_codes = ', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])
	res = frappe.db.sql("""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom {cf_field}
		from
			`tabItem` item 
			{cf_join}
		where
			item.name in ({item_codes}) and ifnull(item.disabled, 0) = 0
	""".format(cf_field=cf_field, cf_join=cf_join, item_codes=item_codes), as_dict=1)

	for item in res:
		item_details.setdefault(item.name, item)

	if filters.get('show_variant_attributes', 0) == 1:
		variant_values = get_variant_values_for(list(item_details))
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in iteritems(item_details)}

	return item_details

def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.db.sql("""
			select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
			from `tabItem Reorder`
			where parent in ({0})
		""".format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])), as_dict=1)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

def get_variants_attributes():
	'''Return all item variant attributes.'''
	return [i.name for i in frappe.get_all('Item Attribute')]

def get_variant_values_for(items):
	'''Returns variant values for items.'''
	attribute_map = {}
	for attr in frappe.db.sql('''select parent, attribute, attribute_value
		from `tabItem Variant Attribute` where parent in (%s)
		''' % ", ".join(["%s"] * len(items)), tuple(items), as_dict=1):
			attribute_map.setdefault(attr['parent'], {})
			attribute_map[attr['parent']].update({attr['attribute']: attr['attribute_value']})

	return attribute_map
'''
def get_rarb_vouchers(sle):
	#print "voucher_no-------------",voucher_no
	rarb_locations_data = []
	for d in sle:
		voucher_no = d.voucher_no
		voucher_type = d.voucher_type
		item_code = d.item_code
		if voucher_type == "Stock Entry":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.pch_rarb_location_src,sti.pch_rarb_location_trg,sti.item_code
							from 
								`tabStock Entry` st ,`tabStock Entry Detail` sti 
							where 
								st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
			rarb_locations_data.append(rarb_locations)
		elif voucher_type == "Purchase Invoice":
		
			rarb_locations = frappe.db.sql("""
							select
								 sti.pch_rarb_location_trg,sti.item_code
							from 
								`tabPurchase Invoice` st ,`tabPurchase Invoice Item` sti 
							where 
								st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
			rarb_locations_data.append(rarb_locations)
		elif voucher_type == "Purchase Receipt":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.pch_rarb_location_trg, sti.item_code 
							from 
								`tabPurchase Receipt` st ,`tabPurchase Receipt Item` sti 
							where 
								st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
			rarb_locations_data.append(rarb_locations)
		elif voucher_type == "Sales Invoice":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.pch_rarb_location_src, sti.item_code 
							from 
								`tabSales Invoice` st ,`tabSales Invoice Item` sti 
							where 
								st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
			rarb_locations_data.append(rarb_locations)
		elif voucher_type == "Stock Reconciliation":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.pch_rarb_location_src, sti.item_code 
							from 
								`tabStock Reconciliation` st ,`tabStock Reconciliation Item` sti 
							where 
								st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
			rarb_locations_data.append(rarb_locations)
		elif voucher_type == "Delivery Note":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.pch_rarb_location_src, sti.item_code 
							from 
								`tabDelivery Note` st ,`tabDelivery Note Item` sti 
							where 
								st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
			rarb_locations_data.append(rarb_locations)
	sorted_data = get_unique_id(rarb_locations_data)
	return sorted_data

def get_target_qty(rarb_location,warehouse,item,sle):
	target_qty = 0.0
	target_rarb_location = []
	for d in sle:
		docids = d.voucher_no
		if d.voucher_type == "Stock Entry":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.qty as t_qty,sti.pch_rarb_location_trg as rarb_id
							from 
								`tabStock Entry` st ,`tabStock Entry Detail` sti 
							where 
								st.name = '"""+d.voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item+"""' and  st.docstatus = 1
								and sti.t_warehouse = %s and sti.pch_rarb_location_trg = %s
								and sti.name = '"""+d.voucher_detail_no+"""'
								""",(warehouse,rarb_location), as_dict =1)
			target_rarb_location.append(rarb_locations)
		elif d.voucher_type == "Purchase Invoice":
		
			rarb_locations = frappe.db.sql("""
							select
								sti.qty as t_qty,sti.pch_rarb_location_trg as rarb_id
							from 
								`tabPurchase Invoice` st ,`tabPurchase Invoice Item` sti 
							where 
								st.name = '"""+d.voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item+"""' and  st.docstatus = 1 and 
								sti.warehouse = %s and sti.pch_rarb_location_trg = %s and 
								sti.name = '"""+d.voucher_detail_no+"""'
								""",(warehouse,rarb_location), as_dict =1)
			target_rarb_location.append(rarb_locations)
		elif d.voucher_type == "Purchase Receipt":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.qty as t_qty,sti.pch_rarb_location_trg as rarb_id
							from 
								`tabPurchase Receipt` st ,`tabPurchase Receipt Item` sti 
							where 
								st.name = '"""+d.voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item+"""' and  st.docstatus = 1 and 
								sti.warehouse = %s and sti.pch_rarb_location_trg = %s
								and sti.name = '"""+d.voucher_detail_no+"""'
								""",(warehouse,rarb_location), as_dict =1)
			target_rarb_location.append(rarb_locations)
	
	return target_rarb_location

def get_source_qty(rarb_location,warehouse,item,sle):
	source_qty = 0.0
	souce_rarb_location = []
	for d in sle:
		
		docids = d.voucher_no
		if d.voucher_type == "Stock Entry":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.qty as s_qty,sti.pch_rarb_location_src as rarb_id
							from 
								`tabStock Entry` st ,`tabStock Entry Detail` sti 
							where 
								st.name = '"""+d.voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item+"""' and  st.docstatus = 1
								and sti.s_warehouse = %s and sti.pch_rarb_location_src = %s
								and sti.name = '"""+d.voucher_detail_no+"""'
								""",(warehouse,rarb_location), as_dict =1)
			souce_rarb_location.append(rarb_locations)
		elif d.voucher_type == "Sales Invoice":
		
			rarb_locations = frappe.db.sql("""
							select
								sti.qty as s_qty,sti.pch_rarb_location_src as rarb_id
							from 
								`tabSales Invoice` st ,`tabSales Invoice Item` sti 
							where 
								st.name = '"""+d.voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item+"""' and  st.docstatus = 1 and 
								sti.warehouse = %s and sti.pch_rarb_location_src = %s
								and sti.name = '"""+d.voucher_detail_no+"""'
								""",(warehouse,rarb_location), as_dict =1)
			souce_rarb_location.append(rarb_locations)
		elif d.voucher_type == "Delivery Note":
		
			rarb_locations = frappe.db.sql("""
							select 
								sti.qty as s_qty, sti.pch_rarb_location_src as rarb_id
							from 
								`tabDelivery Note` st ,`tabDelivery Note Item` sti 
							where 
								st.name = '"""+d.voucher_no+"""' and st.name = sti.parent and 
								sti.item_code = '"""+item+"""' and  st.docstatus = 1 and 
								sti.warehouse = %s and sti.pch_rarb_location_src = %s
								and sti.name = '"""+d.voucher_detail_no+"""'
								""",(warehouse,rarb_location), as_dict =1)
			souce_rarb_location.append(rarb_locations)
	
	return souce_rarb_location
def get_stock_qty(rarb_location,warehouse,item,sle):
	source_qty = 0.0
	souce_rarb_location = []
	
	rarb_locations = frappe.db.sql("""
					select 
						qty as s_qty, pch_rarb_location_src as rarb_id,item_code
					from 
						`tabStock Reconciliation Item`  
					where 
						item_code = '"""+item+"""' and 
						warehouse = %s and pch_rarb_location_src = %s
						""",(warehouse,rarb_location), as_dict =1)

	souce_rarb_location.append(rarb_locations)
	return souce_rarb_location	
'''
@frappe.whitelist()
def get_rarb_warehouse_item_name():
	rarb_id = frappe.db.sql("""select warehouse from `tabRARB Warehouse`  where  docstatus =1 and is_active =1 """, as_dict=1)
	return rarb_id
'''
def get_unique_id(items_list):
	if len(items_list)!=0:
		items_state = {}
		for data in items_list:
			for d in data:
				if d.pch_rarb_location_src is not None:
					item_code = d.item_code
					rarb_location = d.pch_rarb_location_src
					rarb_items = str(rarb_location)+"-"+str(item_code)
					key = rarb_items
					if key in items_state:
						item_entry = items_state[key]
						qty_temp = item_entry["rarb_location"]

					else:
						items_state[key] = frappe._dict({
								"rarb_location": rarb_location, 
								"rarb_items": rarb_items,
								"item_code":item_code
								})
				elif d.pch_rarb_location_trg is not None:
					rarb_location = d.pch_rarb_location_trg
					item_code = d.item_code
					rarb_items = str(rarb_location)+"-"+str(item_code)
					key = rarb_items
					if key in items_state:
						item_entry = items_state[key]
						qty_temp = item_entry["rarb_location"]

					else:
						items_state[key] = frappe._dict({
								"rarb_location": rarb_location, 
								"rarb_items": rarb_items,
								"item_code":item_code
								})
				
		return items_state
'''
@frappe.whitelist()
def get_rarb_warehouse(warehouse):
	rarb_warehouse = frappe.db.sql("""select warehouse, start_date , end_date from `tabRARB Warehouse` where warehouse = %s and docstatus =1""",warehouse, as_dict=1)
	return rarb_warehouse
'''
@frappe.whitelist()
def set_rarb_location(stock,data):
	voucher_no = stock.voucher_no
	voucher_type = stock.voucher_type
	voucher_detail_no = stock.voucher_detail_no
	item_code = stock.item_code
	warehouse = stock.warehouse
	trg_rarb_locations = ""
	src_rarb_locations = ""
	if voucher_type == "Stock Entry":
		
		trg_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_trg as rarb_id_trg
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.t_warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Purchase Invoice":
	
		trg_rarb_locations = frappe.db.sql("""
						select
							sti.pch_rarb_location_trg as rarb_id_trg
						from 
							`tabPurchase Invoice` st ,`tabPurchase Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s  and 
							sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Purchase Receipt":
	
		trg_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_trg as rarb_id_trg
						from 
							`tabPurchase Receipt` st ,`tabPurchase Receipt Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Stock Entry":
		
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.s_warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Sales Invoice":
	
		src_rarb_locations = frappe.db.sql("""
						select
							sti.pch_rarb_location_src as rarb_id_src
						from 
							`tabSales Invoice` st ,`tabSales Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Delivery Note":
	
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src
						from 
							`tabDelivery Note` st ,`tabDelivery Note Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Stock Reconciliation":
		
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src 
						from 
							`tabStock Reconciliation` st ,`tabStock Reconciliation Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
	if src_rarb_locations:
		#print "src_rarb_locations-------------",src_rarb_locations[0].rarb_id_src
		frappe.db.set_value("Stock Ledger Entry", stock.name, "rarb_location", src_rarb_locations[0].rarb_id_src)
	if trg_rarb_locations:
		frappe.db.set_value("Stock Ledger Entry", stock.name, "rarb_location", trg_rarb_locations[0].rarb_id_trg)
'''
