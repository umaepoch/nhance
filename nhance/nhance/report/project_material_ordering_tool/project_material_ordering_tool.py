# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
import datetime
import time
import math
import json
import ast
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sum_data = []
def execute(filters=None):
	swh = ""
	global sum_data
	columns = []
	sum_data = []
	columns = get_columns()
	if filters.get("source_warehouse"):
		swh = filters.get("source_warehouse")
	if filters.get("project"):
		project = filters.get("project")
		items_map = fetch_pending_sreqnos(project,swh)	
		if items_map:
			for (sreq_no) in sorted(items_map):
				data = items_map[sreq_no]
				for sreq_dict in data:
					print "sreq_dict-----", sreq_dict['sreq_no']
					print "bom-----", sreq_dict['bom']
					sum_data.append([				
					sreq_dict['sreq_no'],
					project,
					sreq_dict['item_code'],
					sreq_dict['sreq_qty'],
					sreq_dict['sreq_uom'],
					sreq_dict['stock_uom'],
					sreq_dict['sreq_qty_in_stock_uom'],
					sreq_dict['qty_available_in_swh'],
					sreq_dict['excess_to_be_ordered'],
					sreq_dict['po_uom'],
					sreq_dict['conversion_factor'],
					sreq_dict['qty_in_po_uom'],
					sreq_dict['default_supplier'],
					sreq_dict['last_purchase_price'],
					sreq_dict['no_of_purchase_transactions'],
					sreq_dict['max_price_of_last_10_purchase_transactions'],
					sreq_dict['min_price_of_last_10_purchase_transactions'],
					sreq_dict['avg_price_of_last_10_purchase_transactions'],
					sreq_dict['bom']
					])	

	return columns, sum_data



def fetch_pending_sreqnos(project,swh):
	items_map = {}
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	sreq_nos_data = frappe.db.sql("""select distinct(sri.parent) as parent, sr.po_list as po_list from `tabStock Requisition Item` sri, `tabStock Requisition` sr where sri.project=%s and sr.name=sri.parent and sr.docstatus=1 and sr.status not in('Ordered') and sr.name=sri.parent""", project, as_dict=1)
	if sreq_nos_data:
		for sreq_data in sreq_nos_data:
			sreq_no = sreq_data['parent']
			po_list = sreq_data['po_list']
			
			if po_list:
				sreq_items = fetch_sreq_item_details(sreq_no)
				if sreq_items:
					sreq_qty = 0
					for items_data in sreq_items:
						item_code = items_data['item_code']
						bom_reference = items_data['pch_bom_reference']
						default_supplier = fetch_default_supplier(company,item_code)
						po_items = fetch_po_items_details(item_code,po_list)
						po_uom = fetch_item_purchase_uom(item_code)
						conversion_factor = fetch_conversion_factor(item_code,po_uom)

						last_purchase_price = fetch_last_purchase_price(str(item_code), str(items_data['uom']))
						max_price_of_last_10_purchase_transactions = fetch_max_price_of_last_10_purchase_transactions(item_code, items_data['uom'])
						min_price_of_last_10_purchase_transactions = fetch_min_price_of_last_10_purchase_transactions(item_code, items_data['uom'])
						avg_price_of_last_10_purchase_transactions = fetch_avg_price_of_last_10_purchase_transactions(item_code, items_data['uom'])
						no_of_purchase_transactions = fetch_no_of_purchase_transactions(item_code, items_data['uom'])

						key = items_data['parent']

						if swh:
							qty_available_in_swh = fetch_qty_available_in_swh(items_data['item_code'],swh)
						else:
							qty_available_in_swh = 0

						if qty_available_in_swh > float(items_data['stock_qty']):
							excess_to_be_ordered = 0
						else:
							excess_to_be_ordered = float(items_data['stock_qty']) - qty_available_in_swh

						if po_items:
							sreq_qty = float(items_data['qty']) - float(po_items['qty'])
							qty_in_po_uom = float(po_items['stock_qty'])

						if sreq_qty > 0:
							if key not in items_map:
								sreq_items_list = []
								sreq_items_list.append({
									"sreq_no": key,
									"item_code": items_data['item_code'],
									"sreq_qty": sreq_qty,
									"sreq_uom": (items_data['uom']),
									"stock_uom": (items_data['stock_uom']),
									"sreq_qty_in_stock_uom": float(items_data['stock_qty']),
									"qty_available_in_swh": float(qty_available_in_swh),
									"excess_to_be_ordered": excess_to_be_ordered,
									"po_uom": po_uom,
									"conversion_factor": conversion_factor,
									"qty_in_po_uom": qty_in_po_uom,
									"default_supplier": default_supplier,
									"last_purchase_price": last_purchase_price,
									"no_of_purchase_transactions": no_of_purchase_transactions,
									"max_price_of_last_10_purchase_transactions": max_price_of_last_10_purchase_transactions,
									"min_price_of_last_10_purchase_transactions": min_price_of_last_10_purchase_transactions,
									"avg_price_of_last_10_purchase_transactions": avg_price_of_last_10_purchase_transactions,
									"bom": bom_reference
									})
								items_map[key] = sreq_items_list
							else:
								prev_sreq_list = items_map[key]
								item_entry = {}
								item_entry["sreq_no"] = key
								item_entry["item_code"] = items_data['item_code'] 
								item_entry["sreq_qty"] = sreq_qty
								item_entry["sreq_uom"] = items_data['uom']  
								item_entry["stock_uom"] = items_data['stock_uom']
								item_entry["sreq_qty_in_stock_uom"] = float(items_data['stock_qty'])
								item_entry["qty_available_in_swh"] = float(qty_available_in_swh)
								item_entry["excess_to_be_ordered"] = excess_to_be_ordered 
								item_entry["po_uom"] = po_uom
								item_entry["conversion_factor"] = conversion_factor
								item_entry["qty_in_po_uom"] = qty_in_po_uom
								item_entry["default_supplier"] = default_supplier
								item_entry["last_purchase_price"] = last_purchase_price
								item_entry["no_of_purchase_transactions"] = no_of_purchase_transactions
								item_entry["max_price_of_last_10_purchase_transactions"] = max_price_of_last_10_purchase_transactions
								item_entry["min_price_of_last_10_purchase_transactions"] = min_price_of_last_10_purchase_transactions
								item_entry["avg_price_of_last_10_purchase_transactions"] = avg_price_of_last_10_purchase_transactions
								item_entry["bom"] =  bom_reference
								prev_sreq_list.append(item_entry)
								items_map[key] = prev_sreq_list
						
				
					
				
			else:
				sreq_items = fetch_sreq_item_details(sreq_no)
				if sreq_items:
					for items_data in sreq_items:
						item_code = items_data['item_code']
						bom_reference = items_data['pch_bom_reference']
						default_supplier = fetch_default_supplier(company,item_code)
						print "item_code---", item_code, items_data['uom']
						po_uom = fetch_item_purchase_uom(item_code)
						conversion_factor = fetch_conversion_factor(item_code,po_uom)

						last_purchase_price = fetch_last_purchase_price(str(item_code), str(items_data['uom']))
						max_price_of_last_10_purchase_transactions = fetch_max_price_of_last_10_purchase_transactions(item_code, items_data['uom'])
						min_price_of_last_10_purchase_transactions = fetch_min_price_of_last_10_purchase_transactions(item_code, items_data['uom'])
						avg_price_of_last_10_purchase_transactions = fetch_avg_price_of_last_10_purchase_transactions(item_code, items_data['uom'])
						no_of_purchase_transactions = fetch_no_of_purchase_transactions(item_code, items_data['uom'])

						key = items_data['parent']

						if swh:
							qty_available_in_swh = fetch_qty_available_in_swh(items_data['item_code'],swh)
						else:
							qty_available_in_swh = 0

						if qty_available_in_swh > float(items_data['stock_qty']):
							excess_to_be_ordered = 0
						else:
							excess_to_be_ordered = float(items_data['stock_qty']) - qty_available_in_swh
						print "key-----", key

						if key not in items_map:
							sreq_items_list = []
							sreq_items_list.append({
									"sreq_no": key,
									"item_code": items_data['item_code'],
									"sreq_qty": float(items_data['qty']),
									"sreq_uom": (items_data['uom']),
									"stock_uom": (items_data['stock_uom']),
									"sreq_qty_in_stock_uom": float(items_data['stock_qty']),
									"qty_available_in_swh": float(qty_available_in_swh),
									"excess_to_be_ordered": excess_to_be_ordered,
									"po_uom": po_uom,
									"conversion_factor": conversion_factor,
									"qty_in_po_uom": 0,
									"default_supplier": default_supplier,
									"last_purchase_price": last_purchase_price,
									"no_of_purchase_transactions": no_of_purchase_transactions,
									"max_price_of_last_10_purchase_transactions": max_price_of_last_10_purchase_transactions,
									"min_price_of_last_10_purchase_transactions": min_price_of_last_10_purchase_transactions,
									"avg_price_of_last_10_purchase_transactions": avg_price_of_last_10_purchase_transactions,
									"bom": bom_reference
									})
							items_map[key] = sreq_items_list
						else:
							prev_sreq_list = items_map[key]
							item_entry = {}
							item_entry["sreq_no"] = key
							item_entry["item_code"] = items_data['item_code'] 
							item_entry["sreq_qty"] = float(items_data['qty'])
							item_entry["sreq_uom"] = items_data['uom']  
							item_entry["stock_uom"] = items_data['stock_uom']
							item_entry["sreq_qty_in_stock_uom"] = float(items_data['stock_qty'])
							item_entry["qty_available_in_swh"] = float(qty_available_in_swh)
							item_entry["excess_to_be_ordered"] = excess_to_be_ordered 
							item_entry["po_uom"] = po_uom
							item_entry["conversion_factor"] = conversion_factor
							item_entry["qty_in_po_uom"] = 0
							item_entry["default_supplier"] = default_supplier
							item_entry["last_purchase_price"] = last_purchase_price
							item_entry["no_of_purchase_transactions"] = no_of_purchase_transactions
							item_entry["max_price_of_last_10_purchase_transactions"] = max_price_of_last_10_purchase_transactions
							item_entry["min_price_of_last_10_purchase_transactions"] = min_price_of_last_10_purchase_transactions
							item_entry["avg_price_of_last_10_purchase_transactions"] = avg_price_of_last_10_purchase_transactions
							item_entry["bom"] =  bom_reference
							prev_sreq_list.append(item_entry)
							items_map[key] = prev_sreq_list
		#print "items_map-----", items_map
						
		return items_map
	else:
		return None


def fetch_conversion_factor(parent,uom):
	records = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent=%s and uom=%s""", (parent, uom), as_dict=1)
	if records:
		conversion_factor = records[0]['conversion_factor']
		return conversion_factor

def fetch_po_items_details(item_code,po_list):
	print "po_list-------", po_list
	qty = 0
	stock_qty = 0
	po_items = {}
	splitted_po = po_list.split(",")
	for po in splitted_po:
		po_data = fetch_po_data(item_code,po)
		if po_data:
			qty = qty + float(po_data['qty'])
			stock_qty = stock_qty + float(po_data['stock_qty'])
	po_items['qty'] = qty
	po_items['stock_qty'] = stock_qty
	print "po_items-------", po_items
	return po_items

def fetch_item_purchase_uom(item_code):
	purchase_uom = ""
	details = frappe.db.sql(""" select purchase_uom,stock_uom from `tabItem` where item_code=%s""", item_code, as_dict=1)
	if details:
		if details[0]['purchase_uom']:
			purchase_uom = details[0]['purchase_uom']
		else:
			purchase_uom = details[0]['stock_uom']
	return purchase_uom
	

def fetch_po_data(item_code,po):
	po_data = frappe.db.sql(""" select item_code,qty,conversion_factor,uom,stock_qty from `tabPurchase Order Item` where item_code=%s and parent=%s""", (item_code,po), as_dict=1)

	if po_data:
		conversion_factor = po_data[0]['conversion_factor']
		qty = po_data[0]['stock_qty']
		stock_qty = qty / conversion_factor
		items_data = {"qty": po_data[0]['qty'],"stock_qty":stock_qty}
		return items_data
	else:
		return 

def fetch_no_of_purchase_transactions(item_code,uom):
	po_count = frappe.db.sql("""select count(po.name) as po_count from `tabPurchase Order` po , `tabPurchase Order Item` poi where po.docstatus=1 and poi.item_code=%s and poi.uom=%s and po.name=poi.parent""", (item_code,uom), as_dict=1)
	#print "po_count---------------------", po_count

	if po_count:
		return po_count[0]['po_count']
	else:
		return 0

@frappe.whitelist()
def fetch_last_purchase_price(item_code,uom):
	last_purchase_price = frappe.db.sql(""" select tpoi.rate as last_purchase_price from `tabPurchase Order` po, `tabPurchase Order Item` tpoi where  tpoi.item_code=%s and tpoi.uom=%s and po.name=tpoi.parent and po.docstatus=1 order by tpoi.rate desc limit 1""", (item_code,uom), as_dict=1)

	#print "last_purchase_price---------------------", last_purchase_price
	if last_purchase_price:
		return last_purchase_price[0]['last_purchase_price']
	else:
		return 0


def fetch_max_price_of_last_10_purchase_transactions(item_code,uom):
	max_price_of_last_10_purchase_transactions = frappe.db.sql("""select max(rate) as max_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 10 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate desc limit 1) t1""", (item_code,uom), as_dict=1)

	#print "max_price_of_last_10_purchase_transactions---------------------", max_price_of_last_10_purchase_transactions

	if max_price_of_last_10_purchase_transactions:
		max_price_of_last_10_purchase_transactions[0]['max_price_rate']
	else:
		return 0

def fetch_min_price_of_last_10_purchase_transactions(item_code,uom):
	min_price_of_last_10_purchase_transactions = frappe.db.sql("""select min(rate) as min_price_rate from (select rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 10 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate asc limit 1) t1""", (item_code,uom), as_dict=1)

	#print "min_price_of_last_10_purchase_transactions---------------------", min_price_of_last_10_purchase_transactions

	if min_price_of_last_10_purchase_transactions:
		min_price_of_last_10_purchase_transactions[0]['min_price_rate']
	else:
		return 0

def fetch_avg_price_of_last_10_purchase_transactions(item_code,uom):
	avg_price_of_last_10_purchase_transactions = frappe.db.sql("""select avg(rate) as avg_price from `tabPurchase Order Item` as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled'))""", (item_code,uom), as_dict=1)

	#print "avg_price_of_last_10_purchase_transactions---------------------", avg_price_of_last_10_purchase_transactions

	if avg_price_of_last_10_purchase_transactions:
		avg_price_of_last_10_purchase_transactions[0]['avg_price']
	else:
		return 0


def fetch_default_supplier(company,item_code):
	ds = frappe.db.sql(""" select default_supplier from `tabItem Default` where company=%s and parent=%s""", (company,item_code), as_dict=1)
	if ds:
		return ds[0]['default_supplier']
	else:
		return ""
	
def fetch_sreq_item_details(sreq_no):
	details = frappe.db.sql(""" select * from `tabStock Requisition Item` where parent=%s""", sreq_no, as_dict=1)
	return details

def fetch_qty_available_in_swh(item_code,swh):
	details = frappe.db.sql("""select actual_qty from `tabBin` where item_code=%s and warehouse=%s""", (item_code,swh), as_dict=1)
	if details:
		return details[0]['actual_qty']
	else:
		return 0

@frappe.whitelist()
def fetch_stock_balance_valuation_rate(item_code):
	details = frappe.db.sql("""select distinct(valuation_rate) as rate from `tabStock Ledger Entry` where item_code=%s""", item_code, as_dict=1)
	if details:
		return details[0]['rate']
	else:
		return 0

def fetch_valuation_rate_from_item_price(item_code,price_list):
	details = frappe.db.sql("""select price_list_rate as rate from `tabItem Price` where item_code=%s and price_list=%s""", 				(item_code,price_list), as_dict=1)
	if details:
		return details[0]['rate']
	else:
		return 0

@frappe.whitelist()
def fetch_item_price_settings_details():
	details = frappe.get_doc("Item Price Settings")
	return details

@frappe.whitelist()
def make_stock_entry(sreq_no,mt_list):
	mt_items_map = {}
	sreq_items_list = []
	materialTransferItems = eval(mt_list)
	company = frappe.db.get_single_value("Global Defaults", "default_company")

	if materialTransferItems:
		outerJson_Transfer = {
			"naming_series": "STE-",
			"doctype": "Stock Entry",
			"title": "Material Transfer",
			"docstatus": 1,
			"purpose": "Material Transfer",
			"company": company,
			"stock_requisition_id": sreq_no,
			"items": []
			}

		for items in materialTransferItems:
			key = items['item_code']
			qty = items['qty']

			if key not in mt_items_map:
				mt_items_map[key] = float(qty)

			innerJson_Transfer ={
				"item_code":items['item_code'],
				"s_warehouse":items['s_warehouse'],
				"t_warehouse":items['t_warehouse'],
				"qty":items['qty'],
				"pch_bom_reference":items['bom'],
				"pch_project":items['project'],
				"doctype": "Stock Entry Detail"
				}
			outerJson_Transfer["items"].append(innerJson_Transfer)

		doc = frappe.new_doc("Stock Entry")
		doc.update(outerJson_Transfer)
		doc.save()
		ret = doc.doctype

		if mt_items_map:
			updat_sreq_items_fulfilled_qty(mt_items_map,sreq_no)

		if ret:
			frappe.msgprint("Stock Entry is created: "+doc.name)

def updat_sreq_items_fulfilled_qty(mt_items_map,sreq_no):
	sreq_item_list = []
	sreq_items = frappe.db.sql(""" select sri.item_code as item_code,sri.fulfilled_quantity as fulfilled_quantity from `tabStock Requisition` sr,`tabStock Requisition Item` sri where sr.name= %s and sri.parent=sr.name """,(sreq_no), as_dict=1)

	if sreq_items:
		for items_data in sreq_items:
			original_fulfilled_qty = 0
			item_code = items_data['item_code']
			fulfilled_quantity = items_data['fulfilled_quantity']
			
			if item_code in mt_items_map:
				transfered_qty = mt_items_map[item_code]
				original_fulfilled_qty = float(fulfilled_quantity) + float(transfered_qty)

			sreq_item_list.append({"item_code": item_code, "fulfilled_qty": original_fulfilled_qty})

	if sreq_item_list:
		for sreq_data in sreq_item_list:
			item_code = sreq_data['item_code']
			fulfilled_quantity = sreq_data['fulfilled_qty']

			frappe.db.sql("""update `tabStock Requisition Item` sri set fulfilled_quantity=%s where sri.parent = %s and sri.item_code = %s """, (fulfilled_quantity,sreq_no,item_code))
				

@frappe.whitelist()
def make_purchase_orders(sreq_no,supplier,po_items):
	
	items_List = json.loads(po_items)
	print "type of po_items_list---------", type(items_List), items_List
	creation_Date = datetime.datetime.now()
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if items_List:
		outerJson_Transfer = {
			"doctype": "Purchase Order",
			"title": "Purchase Order",
			"creation": creation_Date,
			"owner": "Administrator",
			"company": company,
			"due_date": creation_Date,
			"docstatus": 0,
			"supplier": supplier,
			"stock_requisition_id": sreq_no,
			"items": [],
			"taxes": []
			}

		for items in items_List:
			innerJson_Transfer ={
				"creation": creation_Date,
				"qty": items['qty'],
				"item_code": items['item_code'],
				"pch_bom_reference":items['bom'],
				"project":items['project'],
				"price_list_rate": items['price_list_rate'],
				"doctype": "Purchase Order Item",
				"parenttype": "Purchase Order",
				"schedule_date": creation_Date,
				"parentfield": "items",
				"warehouse": items['warehouse']
			   	}
			outerJson_Transfer["items"].append(innerJson_Transfer)
			

		doc = frappe.new_doc("Purchase Order")
		doc.update(outerJson_Transfer)
		doc.save()
		ret = doc.doctype
		if ret:
			frappe.msgprint("Purchase Order is Created:"+doc.name)
	

@frappe.whitelist()
def get_report_data():
	report_data = []
	details = {}
	for rows in sum_data:
		print "row-----", rows
		sreq_no = rows[0]
		project = rows[1]
		item_code = rows[2]
		stock_uom = rows[5]
		sreq_qty_in_stock_uom = rows[6]
		excess_to_be_ordered = rows[8]
		po_uom = rows[9]
		conversion_factor = rows[10]
		supplier = rows[12]
		bom_reference = rows[18]
		mt_qty = float(sreq_qty_in_stock_uom) - float(excess_to_be_ordered)
		details = {"sreq_no":sreq_no,
			   "project":project,
			   "item_code":item_code,
			   "stock_uom":stock_uom,
			   "mt_qty":mt_qty,
			   "po_qty":excess_to_be_ordered,
			   "conversion_factor":conversion_factor,
			   "po_uom":po_uom,
			   "supplier":supplier,
			   "bom":bom_reference
			}
		report_data.append(details)
	return report_data

def get_columns():
	"""return columns"""
	columns = [
		_("SREQ No")+":Link/Stock Requisition:100",
		_("Project")+":Link/Project:100",
		_("SREQ Item")+":Link/Item:100",
		_("SREQ Quantity")+"::100",
		_("SREQ UOM")+"::140",
		_("Stock UOM")+"::100",
		_("SREQ Quantity in Stock UOM")+"::150",
		_("Quantity Available in Source Warehouse (Stock UOM)")+"::150",
		_("Excess to be Ordered")+"::90",
		_("PO UOM")+"::100",
		_("Conversion Factor")+"::",
		_("Qty in PO UOM")+"::100",
		_("Default Supplier")+"::140",
		_("Last Purchase Price (Stock UOM)")+"::100",
		_("Number of Purchase Transactions")+"::150",
		_("Highest Price of Last 10 Purchase Transactions (Stock UOM)")+"::90",
		_("Lowest Price of Last 10 Purchase Transactions (Stock UOM)")+"::100",
		_("Average of Last 10 Purchase Transactions")+"::150"
		 ]
	return columns

