# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	unique_po_items_list = []

	global company
	company = filters.get("company")
	sreq_data=get_po_list()
	print "sreq_data ::", sreq_data
	columns = get_columns()
	sreq_items_data = []
	pos_list = ""
	for name in sreq_data:
		sreq_id = name['name']
		pos_list_tmp = name['po_list']
		if pos_list_tmp is not None and pos_list_tmp is not "" and pos_list_tmp != 'NULL':
			if pos_list == "":
				pos_list = pos_list_tmp
			else:
				pos_list = pos_list + "," + pos_list_tmp
		sreq_list = get_requisitioned_items(sreq_id)
		if len(sreq_list)!=0:
			for sreq_items in  sreq_list:
				item_code = sreq_items['item_code']
				qty = sreq_items['qty']
				data = {
				"sreq_id": sreq_id,
				"item_code": item_code,
				"qty": qty
				}
				sreq_items_data.append(data)

	items_list = sreq_items_data
	unique_stock_requisition_list = get_unique_items_list(items_list)
	print "----------unique_stock_requisition_list-----------::", unique_stock_requisition_list
	if len(pos_list)!=0:
		items_list = get_po_items_data(pos_list)
		unique_po_items_list = get_unique_items_list(items_list)
		print "----------unique_po_items_list-----------::", unique_po_items_list

	if len(unique_stock_requisition_list)!=0:
		data = []
		for item_code in unique_stock_requisition_list:
			details = unique_stock_requisition_list[item_code]
			item = details.item_code
			sreq_qty = details.qty
			sreq_qty=float("{0:.2f}".format(sreq_qty))
			ordered_qty = check_item_code_in_po_list(unique_po_items_list,item)
			ordered_qty=float("{0:.2f}".format(ordered_qty))
			pending_qty = float(sreq_qty) - float(ordered_qty)
			pending_qty=float("{0:.2f}".format(pending_qty))
			print "sreq_qty-------",sreq_qty
			data.append([
			item,
			sreq_qty,
			ordered_qty,
			pending_qty
			])
		return columns, data
	else:
		pass
		
def get_columns():
		"""return columns"""
		columns = [
		_("Item")+":Link/Item:100",
		_("Total Qty")+"::100",
		_("Ordered Qty")+"::140",
		_("Pending Qty")+"::100"
		 ]
		return columns
def get_po_list():
	#po_list = frappe.db.sql("""select name,po_list,material_request_type from `tabStock Requisition` where name="SREQ-00022" """, as_dict=1)
	po_list = frappe.db.sql("""select name,po_list,material_request_type from `tabStock Requisition` where docstatus=1 and 			    material_request_type='Purchase' """, as_dict=1)
	return po_list

def get_requisitioned_items(sreq_id):
	sreq_list = frappe.db.sql("""select item_code,qty from `tabStock Requisition Item` where parent=%s""",(sreq_id),as_dict=1)
	return sreq_list

def get_unique_items_list(items_list):
	if len(items_list)!=0:
		items_map = {}
		for data in items_list:
			item_code = data['item_code']
			qty = data['qty']
			key = item_code
			if key in items_map:
				item_entry = items_map[key]
				qty_temp = item_entry["qty"]
				item_entry["qty"] = (qty_temp) + (qty)

			else:
				items_map[key] = frappe._dict({
						"item_code": item_code, 
						"qty": qty, 
						})
		print "-------items_map--------::", items_map
		return items_map

def get_po_items_data(pos_list):
	items_details = []
	splitted_pos_list = pos_list.split(",")
	if len(splitted_pos_list)!=0:
		for po in splitted_pos_list:
			po_items = get_po_items(po)
			for item in po_items:
				data = get_items_list(item)
				items_details.append(data)
	return items_details

def get_po_items(po):
	po_items = frappe.db.sql("""select item_code,qty from `tabPurchase Order Item` where parent=%s and docstatus=1""", (po), as_dict=1)
	return po_items

def get_items_list(item):
	item_code = item['item_code']
	qty = item['qty']
	data = {"item_code":item_code,
		"qty":qty
		}
	#print "-----------------data is::", data
	return data

def check_item_code_in_po_list(unique_po_items_list,item):
	if item in unique_po_items_list:
		item_entry = unique_po_items_list[item]
		qty = item_entry['qty']
	else:
		qty = 0
	return qty

