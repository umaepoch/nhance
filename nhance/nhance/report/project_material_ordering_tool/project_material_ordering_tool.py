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

sum_data=[]
doc_name_created = []
def execute(filters=None):
	swh = ""
	global sum_data
	global doc_name_created
	doc_name_created = []
	columns = []
	sum_data = []
	columns = get_columns()
	if filters.get("source_warehouse"):
		swh = filters.get("source_warehouse")
	if filters.get("project"):
		project = filters.get("project")
		project_warehouse =  frappe.db.get_value('Project', project, 'project_warehouse')
    		reserve_warehouse =  frappe.db.get_value('Project', project, 'reserve_warehouse')
		#print "project_warehouse----------------",project_warehouse
		#print "reserve_warehouse----------------",reserve_warehouse
		items_map = fetch_pending_sreqnos(project,swh)
		if items_map:
			for (sreq_no) in sorted(items_map):
				data = items_map[sreq_no]
				print "final_debug data:",data
				for sreq_dict in data:
					#print "sreq_dict-----", sreq_dict['sreq_no']
					#print "bom-----", sreq_dict['bom']
					sreq_qty_in_stock_uom = sreq_dict['sreq_qty_in_stock_uom']
					excess_to_be_ordered = sreq_dict['excess_to_be_ordered']
					mt_qty = float(sreq_qty_in_stock_uom) - float(excess_to_be_ordered)
					qty_available_in_swh = sreq_dict['qty_available_in_swh']
					sreq_qty = sreq_dict['sreq_qty']
					
					item_code = sreq_dict['item_code']
					#jyoti
					fulfilled_qty = sreq_dict['fulFilledQty']
					print "fulfilled_qty---",fulfilled_qty

					warehouse_qty = get_warehouse_qty(project_warehouse,item_code)
					reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,item_code)
					qty_consumed_in_manufacture= get_stock_entry_quantities(project_warehouse,item_code)
					#rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture
					#jyoti added
					rw_pb_cons_qty = fulfilled_qty
					print "rw_pb_cons_qty--",rw_pb_cons_qty

					sreq_qty_in_stock_uom = sreq_dict['sreq_qty_in_stock_uom']
					qty_due_to_transfer = sreq_qty_in_stock_uom - rw_pb_cons_qty
					report_qty_due_to_transfer = 0
					quantities_are_covered = 0
					draft_poi_qty = 0
					submitted_poi_qty =0

					if qty_due_to_transfer > 0:
						report_qty_due_to_transfer = qty_due_to_transfer
					else:
						report_qty_due_to_transfer = 0
					
					purchase_order_with_zero_docstatus = get_purchase_order_with_zero_docstatus(project,item_code)
					purchase_order_with_one_docstatus = get_purchase_order_with_one_docstatus(project,item_code)
					
					
					if purchase_order_with_one_docstatus[0].submitted is not None:
						submitted_poi_qty = purchase_order_with_one_docstatus[0].submitted
						submitted_poi_qty=round(float(submitted_poi_qty),2)
					if purchase_order_with_zero_docstatus[0].draft is not None:
						draft_poi_qty = purchase_order_with_zero_docstatus[0].draft
						draft_poi_qty = round(float(draft_poi_qty),2)
					quantities_are_covered = submitted_poi_qty + draft_poi_qty + rw_pb_cons_qty
					report_qty_that_can_be_transfer = 0

					qty_that_can_be_transfer = report_qty_due_to_transfer - quantities_are_covered
					if qty_that_can_be_transfer < sreq_dict['qty_available_in_swh']:
						report_qty_that_can_be_transfer = qty_that_can_be_transfer
					elif qty_that_can_be_transfer >= sreq_dict['qty_available_in_swh']:
						report_qty_that_can_be_transfer = sreq_dict['qty_available_in_swh']
					if report_qty_that_can_be_transfer < 0:
						report_qty_that_can_be_transfer = 0

					to_be_order = float(sreq_qty_in_stock_uom) -float(quantities_are_covered) -  float(report_qty_that_can_be_transfer)
					print "Type of to_be_order",type(to_be_order)
					print "to_be_order",to_be_order

					need_to_be_order = 0.0
					if to_be_order > 0:
						need_to_be_order = to_be_order
						need_to_be_order = round(need_to_be_order , 2)
					else:
						need_to_be_order = 0
					print "item_code",sreq_dict['item_code']

					print "conversion_factor",sreq_dict['conversion_factor']
					print "Type of conversion_factor",type(sreq_dict['conversion_factor'])

					print "need_to_be_order",need_to_be_order
					print "Type of need_to_be_order", (type(need_to_be_order))
  
					conversion_fact = sreq_dict['conversion_factor']
					qty_in_poum = need_to_be_order / conversion_fact
					qty_in_poum = round(qty_in_poum , 4)
					print "qty_in_poum",qty_in_poum
					poum_qty = sreq_dict['qty_in_po_uom']
					poum_qty = round(poum_qty , 4)
					#print "report_qty_that_can_be_transfer------------",report_qty_that_can_be_transfer
					#print "mt_qty------------------",mt_qty
					print "final_debug inside for loop sum_data :",sum_data
					sum_data.append([
					sreq_dict['sreq_no'],
					project,
					sreq_dict['item_code'],
					sreq_dict['sreq_qty'],
					sreq_dict['sreq_uom'],
					sreq_dict['stock_uom'],
					sreq_dict['sreq_qty_in_stock_uom'],
					rw_pb_cons_qty,
					report_qty_due_to_transfer,
					sreq_dict['qty_available_in_swh'],
					draft_poi_qty,
					submitted_poi_qty,
					quantities_are_covered,
					report_qty_that_can_be_transfer,
					need_to_be_order,
					sreq_dict['po_uom'],
					sreq_dict['conversion_factor'],
					poum_qty,
					qty_in_poum,
					sreq_dict['default_supplier'],
					sreq_dict['last_purchase_price'],
					sreq_dict['no_of_purchase_transactions'],
					sreq_dict['max_price_of_last_10_purchase_transactions'],
					sreq_dict['min_price_of_last_10_purchase_transactions'],
					sreq_dict['avg_price_of_last_10_purchase_transactions'],
					sreq_dict['bom'],
					sreq_dict['fulFilledQty']
					])

	return columns, sum_data



def fetch_pending_sreqnos(project,swh):
	items_map = {}
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	sreq_nos_data = frappe.db.sql("""select distinct(sri.parent) as parent, sr.po_list as po_list from `tabStock Requisition Item` sri, `tabStock Requisition` sr where sri.project=%s and sr.name=sri.parent and sr.docstatus=1 and sr.status not in('Ordered')""", project, as_dict=1)

	if sreq_nos_data:
		for sreq_data in sreq_nos_data:
			sreq_no = sreq_data['parent']
			po_list = sreq_data['po_list']

			if po_list:
				sreq_items = fetch_sreq_item_details(sreq_no)
				if sreq_items:
					sreq_qty = 0
					fulFilledQty = 0
					for items_data in sreq_items:
						item_code = items_data['item_code']
						bom_reference = items_data['pch_bom_reference']
						fulFilledQty = items_data['fulfilled_quantity']
						default_supplier = fetch_default_supplier(company,item_code)
						po_items = fetch_po_items_details(item_code,po_list)
						po_uom = fetch_item_purchase_uom(item_code)
						conversion_factor = fetch_conversion_factor(item_code,po_uom)
						if conversion_factor == 0:
							conversion_factor = ""

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
							if sreq_qty < 0:
								sreq_qty = 0
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
									"bom": bom_reference,
									"fulFilledQty": fulFilledQty
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
								item_entry["fulFilledQty"] =  fulFilledQty
								prev_sreq_list.append(item_entry)
								items_map[key] = prev_sreq_list




			else:
				sreq_items = fetch_sreq_item_details(sreq_no)
				if sreq_items:
					fulFilledQty = 0
					for items_data in sreq_items:
						item_code = items_data['item_code']
						bom_reference = items_data['pch_bom_reference']
						fulFilledQty = items_data['fulfilled_quantity']
						default_supplier = fetch_default_supplier(company,item_code)
						#print "item_code---", item_code, items_data['uom']
						po_uom = fetch_item_purchase_uom(item_code)
						conversion_factor = fetch_conversion_factor(item_code,po_uom)
						if conversion_factor == 0:
							conversion_factor = ""

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
						#print "key-----", key

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
									"bom": bom_reference,
									"fulFilledQty": fulFilledQty
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
							item_entry["fulFilledQty"] =  fulFilledQty
							prev_sreq_list.append(item_entry)
							items_map[key] = prev_sreq_list
		#print "items_map-----", items_map

		return items_map
	else:
		return None

@frappe.whitelist()
def fetch_conversion_factor(parent,uom):
	#print "parent -------------",parent
	records = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent=%s and uom=%s""", (parent, uom), as_dict=1)
	#print "records--------------",records
	if records:
		conversion_factor = records[0]['conversion_factor']
		return conversion_factor
	else:
		return 0

def fetch_po_items_details(item_code,po_list):
	#print "po_list-------", po_list
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
	#print "po_items-------", po_items
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
		qty = round(float(qty),2)
		stock_qty = qty / conversion_factor
		items_data = {"qty": qty,"stock_qty":stock_qty}
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
		return max_price_of_last_10_purchase_transactions[0]['max_price_rate']
	else:
		return 0

def fetch_min_price_of_last_10_purchase_transactions(item_code,uom):
	min_price_of_last_10_purchase_transactions = frappe.db.sql("""select min(rate) as min_price_rate from (select rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 10 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate asc limit 1) t1""", (item_code,uom), as_dict=1)

	#print "min_price_of_last_10_purchase_transactions---------------------", min_price_of_last_10_purchase_transactions

	if min_price_of_last_10_purchase_transactions:
		return min_price_of_last_10_purchase_transactions[0]['min_price_rate']
	else:
		return 0

def fetch_avg_price_of_last_10_purchase_transactions(item_code,uom):
	avg_price_of_last_10_purchase_transactions = frappe.db.sql("""select avg(rate) as avg_price from `tabPurchase Order Item` as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled'))""", (item_code,uom), as_dict=1)

	#print "avg_price_of_last_10_purchase_transactions---------------------", avg_price_of_last_10_purchase_transactions

	if avg_price_of_last_10_purchase_transactions:
		return avg_price_of_last_10_purchase_transactions[0]['avg_price']
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
				"pch_project_reference":items['project'],
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
	flag = ""
	tax_template = ""
	items_List = json.loads(po_items)
	#print "items_List-----------------", items_List
	creation_Date = datetime.datetime.now()
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	details = frappe.get_meta("Purchase Order").get("fields")
	#print "supplier-----------------", supplier
	#print "details----------------------",details

	if items_List:
		outerJson_Transfer = {
			"doctype": "Purchase Order",
			"title": supplier,
			"creation": creation_Date,
			"owner": "Administrator",
			"company": company,
			"due_date": creation_Date,
			"docstatus": 0,
			"supplier": supplier,
			"terms": "",
			"stock_requisition_id": sreq_no,
			"items": [],
			"taxes": []
			}

		for defaults in details:
			if defaults.fieldname == "supplier":
				#print "Default Supplier------------------------", defaults.default
				if defaults.default:
					supplier = defaults.default
					default_address = fetch_supplier_address(supplier)
					supplier_tax = frappe.get_all("Supplier", {"supplier_name":supplier}, "pch_tax_template")
					#print "supplier_tax------------",supplier_tax
					outerJson_Transfer['supplier'] = defaults.default
					for suppliers in supplier_tax:
						if suppliers.pch_tax_template:
							tax_template = suppliers.pch_tax_template
							outerJson_Transfer['taxes_and_charges'] = tax_template

					if default_address:
						outerJson_Transfer["supplier_address"] = default_address[0]['name']
						outerJson_Transfer["tc_name"] = default_address[0]['pch_terms']
						if default_address[0]['pch_terms']:
							terms_and_conditios = frappe.get_doc("Terms and Conditions", default_address[0]['pch_terms'])
							if terms_and_conditios.terms:
								outerJson_Transfer["terms"] = terms_and_conditios.terms
					else:
						outerJson_Transfer["supplier_address"] = ""
						outerJson_Transfer["tc_name"] = ""
					for suppliers in supplier_tax:
						if suppliers.pch_tax_template:
							tax_template = suppliers.pch_tax_template
							outerJson_Transfer['taxes_and_charges'] = tax_template
							purchase_taxes = frappe.get_doc("Purchase Taxes and Charges Template", tax_template)
							#print "purchase_taxes------", purchase_taxes.taxes, type(purchase_taxes.taxes)

							for data in purchase_taxes.taxes:
								charge_type = data.charge_type
								account_head = data.account_head
								rate = data.rate
								tax_amount = data.tax_amount
								description = data.description
								row_id = data.row_id
								inner_json_for_taxes = {
									"charge_type" : charge_type,
									"account_head":account_head,
									"rate":rate,
									"tax_amount": tax_amount,
									"description" :description,
									"row_id" : row_id,
								}
								outerJson_Transfer["taxes"].append(inner_json_for_taxes)
				else:
					address = fetch_supplier_address(supplier)
					#print "address-----------------", address
					#supplier_data = frappe.get_doc("Supplier", {"supplier_name":supplier}, "pch_tax_template")
					supplier_data = frappe.get_all("Supplier", {"supplier_name":supplier}, "pch_tax_template")
					#print "supplier_data-----------",supplier_data
					if address:
						outerJson_Transfer["supplier_address"] = address[0]['name']
						outerJson_Transfer["tc_name"] = address[0]['pch_terms']
						terms_and_conditios = ""
						if address[0]['pch_terms'] is not None:

							terms_and_conditios = frappe.get_doc("Terms and Conditions", address[0]['pch_terms'])

							if terms_and_conditios.terms:
								outerJson_Transfer["terms"] = terms_and_conditios.terms
					else:
						outerJson_Transfer["supplier_address"] = ""
						outerJson_Transfer["tc_name"] = ""
					for supplier_dt in supplier_data:
						if supplier_dt.pch_tax_template:
							tax_template = supplier_dt.pch_tax_template
							outerJson_Transfer['taxes_and_charges'] = tax_template
							purchase_taxes = frappe.get_doc("Purchase Taxes and Charges Template", tax_template)

							#print "purchase_taxes------", purchase_taxes.taxes, type(purchase_taxes.taxes)
							for data in purchase_taxes.taxes:
								charge_type = data.charge_type
								account_head = data.account_head
								rate = data.rate
								tax_amount = data.tax_amount
								description = data.description
								row_id = data.row_id
								inner_json_for_taxes = {
									"charge_type" : charge_type,
									"account_head":account_head,
									"rate":rate,
									"tax_amount": tax_amount,
									"description" :description,
									"row_id": row_id,
								}
								outerJson_Transfer["taxes"].append(inner_json_for_taxes)

			if defaults.fieldname == "customer":
				#print "customer Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['customer'] = defaults.default

			if defaults.fieldname == "auto_repeat":
				#print "auto_repeat Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['auto_repeat'] = defaults.default

			if defaults.fieldname == "select_print_heading":
				#print "select_print_heading Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['select_print_heading'] = defaults.default

			if defaults.fieldname == "party_account_currency":
				#print "party_account_currency Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['party_account_currency'] = defaults.default

			if defaults.fieldname == "payment_terms_template":
				#print "payment_terms_template Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['payment_terms_template'] = defaults.default

			if defaults.fieldname == "shipping_rule":
				#print "shipping_rule Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['shipping_rule'] = defaults.default

			if defaults.fieldname == "taxes_and_charges":
				#print "taxes_and_charges Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['taxes_and_charges'] = defaults.default

			if defaults.fieldname == "supplier_warehouse":
				#print "supplier_warehouse Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['supplier_warehouse'] = defaults.default

			if defaults.fieldname == "set_warehouse":
				#print "set_warehouse Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['set_warehouse'] = defaults.default

			if defaults.fieldname == "price_list_currency":
				#print "price_list_currency Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['price_list_currency'] = defaults.default

			if defaults.fieldname == "buying_price_list":
				#print "buying_price_list Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['buying_price_list'] = defaults.default

			if defaults.fieldname == "currency":
				#print "currency Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['currency'] = defaults.default

			if defaults.fieldname == "shipping_address":
				#print "shipping_address Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['shipping_address'] = defaults.default

			if defaults.fieldname == "contact_person":
				#print "contact_person Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['contact_person'] = defaults.default

			if defaults.fieldname == "supplier_address":
				#print "supplier_address Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['supplier_address'] = defaults.default

			if defaults.fieldname == "customer_contact_person":
				#print "customer_contact_person Default---", defaults.default
				if defaults.default:
					outerJson_Transfer['customer_contact_person'] = defaults.default

		for items in items_List:
			#print "item ----------------------",items['item_code']
			#print "item-----qty-----------",items['qty']
			stock_qty = items['qty'] * items['conversion_factor']
			stock_qty = round(stock_qty)
			#print "stock_qty-----qty-----------",stock_qty
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
				"warehouse": items['warehouse'],
				"rate": items['last_purchase_price']
			   	}
			#print "innerJson_Transfer ----------------------",innerJson_Transfer
			outerJson_Transfer["items"].append(innerJson_Transfer)
		#print "outerJson_Transfer--------------------",outerJson_Transfer
		doc = frappe.new_doc("Purchase Order")
		doc.update(outerJson_Transfer)
		doc.save()
		
		#print "doc.name 1------------",doc.name
		doc_name_created.append(doc.name)
		#msgDisplayAfterCreatePurchaseOrder(doc.name)
		
		#frappe.msgprint("Purchase Order is Created: "+doc.name)
		if doc.name:
			flag = doc.name
		ret = doc.doctype
		'''
		if ret:
			
			frappe.msgprint("Purchase Order is Created: "+doc.name)
		'''
	return flag

def fetch_supplier_address(supplier):
	address = frappe.db.sql("""select name,pch_terms from `tabSupplier` where name=%s""", supplier, as_dict=1)

	if address:
		return address
	else:
		return None
def msgDisplayAfterCreatePurchaseOrder(docname):
	frappe.msgprint("Purchase Order is Created: "+docname)
	return 1
@frappe.whitelist()
def get_report_data(project_filter,swh_filter):
	report_data = []
	qty_in_poum = 0.0
	details = {}
	sum_datas =[]
	if project_filter:
		#project = filters.get("project")
		items_map = fetch_pending_sreqnos(project_filter,swh_filter)
		#project_warehouse =  frappe.db.get_value('Project', project_filter, 'project_warehouse')
    		#reserve_warehouse =  frappe.db.get_value('Project', project_filter, 'reserve_warehouse')
		if items_map:
			for (sreq_no) in sorted(items_map):
				data = items_map[sreq_no]
				for sreq_dict in data:
					#print "sreq_dict-----", sreq_dict['sreq_no']
					#print "bom-----", sreq_dict['bom']
					sum_datas.append([
					sreq_dict['sreq_no'],
					project_filter,
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
					sreq_dict['bom'],
					sreq_dict['fulFilledQty']
					])
	for rows in sum_datas:
		if project_filter:
			project_warehouse =  frappe.db.get_value('Project', project_filter, 'project_warehouse')
	    		reserve_warehouse =  frappe.db.get_value('Project', project_filter, 'reserve_warehouse')
			warehouse_qty = get_warehouse_qty(project_warehouse,rows[2])
			reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,rows[2])
			qty_consumed_in_manufacture= get_stock_entry_quantities(project_warehouse,rows[2])
			#rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture
			#jyoti
			fulfilled_qty = sreq_dict['fulFilledQty']
			#print "fulfilled_qty---",fulfilled_qty
			#jyoti added
			rw_pb_cons_qty = fulfilled_qty
			#print "rw_pb_cons_qty--",rw_pb_cons_qty
			purchase_order_with_zero_docstatus = get_purchase_order_with_zero_docstatus(project_filter,rows[2])
			purchase_order_with_one_docstatus = get_purchase_order_with_one_docstatus(project_filter,rows[2])
			
			submitted_poi_qty = 0
			draft_poi_qty = 0	
			if purchase_order_with_one_docstatus[0].submitted is not None:
				submitted_poi_qty = purchase_order_with_one_docstatus[0].submitted
			if purchase_order_with_zero_docstatus[0].draft is not None:
				draft_poi_qty = purchase_order_with_zero_docstatus[0].draft
			quantities_are_covered = submitted_poi_qty + draft_poi_qty + rw_pb_cons_qty

			#print "quantities_are_covered ------------",quantities_are_covered
			qty_due_to_transfer = rows[6] - rw_pb_cons_qty
			#print "qty_due_to_transfer------------",qty_due_to_transfer
			qty_can_be_transfered = qty_due_to_transfer - quantities_are_covered

			#print "qty_can_be_transfered------------------",qty_can_be_transfered
			mt_qty = 0
			if qty_can_be_transfered < rows[7]:
				mt_qty = qty_can_be_transfered
			elif qty_can_be_transfered >= rows[7]:
				mt_qty = rows[7]
		
			if mt_qty < 0:
				mt_qty = 0
			
			to_be_order = rows[6] -float(quantities_are_covered) -  float(mt_qty)
			need_to_be_order = 0
			if to_be_order > 0:
				need_to_be_order = to_be_order
			else:
				need_to_be_order = 0
			qty_in_poum = need_to_be_order / rows[10]
			qty_in_poum = round(qty_in_poum , 4)
			#print "qty_in_poum-------------------",qty_in_poum
			
		#print "row-----", rows
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
		fulfilled_qty = rows[19]
		last_purchase_price = rows[13]
		sreq_qty = rows[3]
		#mt_qty = float(sreq_qty_in_stock_uom) - float(excess_to_be_ordered)
		details = {"sreq_no":sreq_no,
			   "project":project,
			   "item_code":item_code,
			   "stock_uom":stock_uom,
			   "mt_qty":mt_qty,
			   "po_qty":need_to_be_order,
			   "conversion_factor":conversion_factor,
			   "po_uom":po_uom,
			   "supplier":supplier,
			   "bom":bom_reference,
			   "fulfilled_qty":fulfilled_qty,
			   "last_purchase_price":last_purchase_price,
			   "sreq_qty":sreq_qty
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
		_("Quantity Transfered")+"::100",
		_("Quantity due to be transferred")+"::120",
		_("Quantity Available in Source Warehouse (Stock UOM)")+"::150",
		_("Draft PO.s that are in the system for the Project")+"::150",
		_("Ordered PO.s that are in the System for the Project")+"::150",
		_("Quantities that are covered")+"::130",
		_("Quantities that can be Transferred")+"::130",
		_("Quantities that need to be ordered (Stock Uom)")+"::130",
		_("PO UOM")+":Link/UOM:100",
		_("Conversion Factor")+"::",
		_("Qty in PO UOM")+"::100",
		_("Qty in PUOM")+"::100",
		_("Default Supplier")+"::140",
		_("Last Purchase Price (Stock UOM)")+"::100",
		_("Number of Purchase Transactions")+"::150",
		_("Highest Price of Last 10 Purchase Transactions (Stock UOM)")+"::90",
		_("Lowest Price of Last 10 Purchase Transactions (Stock UOM)")+"::100",
		_("Average of Last 10 Purchase Transactions")+"::150"
		 ]
	return columns
@frappe.whitelist()
def fields(doc_name):
	fieldname = []
	flag = 0
	field_details = frappe.get_meta(doc_name).get("fields")
	if doc_name == "Supplier":
		fieldname = []
		for field in field_details:
			fieldname.append(field.fieldname)
		if "pch_terms" not in fieldname:
			frappe.msgprint("Terms and Condition field is not created in: "+doc_name+" doctype")
			flag = 0
		elif "pch_tax_template" not in fieldname:
			frappe.msgprint("Tax Template field is not created in: "+doc_name)
			flag = 0
		else:
			flag =1

	return flag
def get_warehouse_qty(warehouse,item_code):
 whse_qty = 0
 details = frappe.db.sql("""select actual_qty from `tabBin` where warehouse=%s and item_code=%s and actual_qty > 0 """, (warehouse,item_code), as_dict=1)
 if len(details)!=0:
   if details[0]['actual_qty'] is not None:
     whse_qty = details[0]['actual_qty']
 return whse_qty

def get_stock_entry_quantities(warehouse,item_code):
    total_qty = 0
    po_details = {}
    qty_consumed_in_manufacture = 0

    details = frappe.db.sql("""select sed.item_code,sed.qty,se.purpose from `tabStock Entry Detail` sed,
        `tabStock Entry` se where sed.item_code=%s and sed.s_warehouse=%s and se.purpose='Manufacture' and
        sed.parent=se.name and se.docstatus=1""", (item_code,warehouse), as_dict=1)

    if len(details)!=0:
      for entries in details:
        if entries['qty'] is None:
          qty = 0
        else:
          qty = float(entries['qty'])
        total_qty = total_qty + qty

    return total_qty
def get_purchase_order_with_zero_docstatus(project,item_code):
	number_of_purchase_with_zero_docstatus = frappe.db.sql("""select sum(stock_qty) as draft from `tabPurchase Order Item` where project = %s and item_code = %s and docstatus =0""",(project,item_code), as_dict =1)
	
	return number_of_purchase_with_zero_docstatus

def get_purchase_order_with_one_docstatus(project,item_code):
	number_of_purchase_with_one_docstatus = frappe.db.sql("""select sum(stock_qty) as submitted from `tabPurchase Order Item` where project = %s and item_code = %s and docstatus =1""",(project,item_code), as_dict =1)
	return number_of_purchase_with_one_docstatus

@frappe.whitelist()
def check_and_update(data,sreq_no):
	
	#print "sreq_no------------------",sreq_no
	#print "supplier_items-----------------",supplier_items
	#print "data---------------",data
	items_List = json.loads(data)
	for items in items_List:
		item_code = items['item_code']
		round_qty = items['round_qty']
		frappe.db.sql("""update `tabStock Requisition Item`  set qty_allowed_to_be_order = %s  where item_code = %s and parent = %s""", (round_qty, item_code, sreq_no))
		
	return 1

@frappe.whitelist()
def getQtyAllowed(stockRequisitionID):
	allowed_qty = frappe.db.sql("""select item_code,qty_allowed_to_be_order from `tabStock Requisition Item` where parent = %s """,stockRequisitionID, as_dict =1)
	return allowed_qty
