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
sum_data=[]
doc_name_created = []
def execute(filters=None):
	columns, data = [], []
	swh = ""
	
	project = filters.get("project")
	#project_details = get_project_details(project)
	if filters.get("source_warehouse"):
		swh = filters.get("source_warehouse")
	prepare_data = []
	if filters.get("project"):
		project = filters.get("project")
		doc_project_list = project_list(project)
		columns = get_columns(doc_project_list)
		total_qty = 0.0
		recommended_order = 0.0
		approved_order = 0.0
		recommended_qty = 0.0
		draft_qty = 0.0
		submit_qty = 0.0
		
		
		for project in doc_project_list:
			#print "lenth of project ---------",len(doc_project_list)
			project_warehouse =  frappe.db.get_value('Project', project['project'], 'project_warehouse')
			reserve_warehouse =  frappe.db.get_value('Project', project['project'], 'reserve_warehouse')
			##print "project_warehouse----------------",project_warehouse
			##print "reserve_warehouse----------------",reserve_warehouse
			items_map = fetch_pending_sreqnos(project['project'],swh)
			if items_map:
				
				for (sreq_no) in sorted(items_map):
					data = items_map[sreq_no]
					
					##print "data-------",data
					prepare_data.append(data)
					for sreq_dict in data:
						#unique_qty = item_wise_qty(sreq_dict)
						##print "sreq_dict-----", sreq_dict['sreq_no']
						##print "bom-----", sreq_dict['bom']
						sreq_qty_in_stock_uom = sreq_dict['sreq_qty_in_stock_uom']
						excess_to_be_ordered = sreq_dict['excess_to_be_ordered']
						mt_qty = float(sreq_qty_in_stock_uom) - float(excess_to_be_ordered)
						qty_available_in_swh = sreq_dict['qty_available_in_swh']
						sreq_qty = sreq_dict['sreq_qty']

						item_code = sreq_dict['item_code']

						#jyoti
						fulfilled_qty = sreq_dict['fulFilledQty']
						##print "fulfilled_qty---",fulfilled_qty#



						warehouse_qty = get_warehouse_qty(project_warehouse,item_code)
						reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,item_code)
						qty_consumed_in_manufacture= get_stock_entry_quantities(project_warehouse,item_code)
						#rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture


						#jyoti added
						rw_pb_cons_qty = fulfilled_qty
						##print "rw_pb_cons_qty--",rw_pb_cons_qty#

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

						purchase_order_with_zero_docstatus = get_purchase_order_with_zero_docstatus(project['project'],item_code)
						purchase_order_with_one_docstatus = get_purchase_order_with_one_docstatus(project['project'],item_code)


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

						need_to_be_order = 0.0
						if to_be_order > 0:
							need_to_be_order = to_be_order
							need_to_be_order = round(need_to_be_order , 2)
						else:
							need_to_be_order = 0
						conversion_fact = 0.0
						if sreq_dict['conversion_factor'] != '':
							conversion_fact = sreq_dict['conversion_factor']
						qty_in_poum = 0.0
						if conversion_fact != 0.0:
							qty_in_poum = need_to_be_order / conversion_fact
						else:
							qty_in_poum = need_to_be_order
						qty_in_poum = round(qty_in_poum , 4)
						poum_qty = sreq_dict['qty_in_po_uom']
						poum_qty = round(poum_qty , 4)

						##print "report_qty_that_can_be_transfer------------",report_qty_that_can_be_transfer
						##print "mt_qty------------------",mt_qty
						total_qty += + sreq_dict['sreq_qty']
						recommended_order = total_qty
						approved_order = total_qty
						conversion_total = float(total_qty) / float(sreq_dict['conversion_factor'])
						conversion_total = round(conversion_total , 4)
						if len(doc_project_list) > project['idx']:
							sum_data.append([
							sreq_dict['item_code'],
							project['project'],
							sreq_dict['sreq_qty'],
							"",
							"",
							"",
							sreq_dict['po_uom'],
							sreq_dict['conversion_factor'],
							"",
							sreq_dict['default_supplier']
							])
						elif len(doc_project_list) == project['idx']:
							sum_data.append([
							sreq_dict['item_code'],
							project['project'],
							sreq_dict['sreq_qty'],
							total_qty,
							recommended_order,
							approved_order,
							sreq_dict['po_uom'],
							sreq_dict['conversion_factor'],
							conversion_total,
							sreq_dict['default_supplier']
							])
	prepare_datas = unique_prepare_data(prepare_data,doc_project_list)
	
	final_data = []
	i =0
	
	project = filters.get("project")
	for dt in prepare_datas:
		total_qtys = 0.0
		recommended_qty = 0.0
		approved_qty = 0.0
		sums_data = []
		item_code = dt['item_code']
		sums_data.append(dt['item_code'])
		recommended_qty = frappe.get_list("Pre Purchase Orders", filters = {"project_being_ordered":project , "docstatus":1}, fields=["name"])
		if recommended_qty:
			for rec in recommended_qty:
				rec_name = rec['name']
				rec_qty = frappe.get_list("Pre Purchase Item", filters = {"parent":rec_name, "item":dt['item_code']}, fields=["recommended_qty"])
				#print "rec_qty---------------",rec_qty
				recommended_qty = rec_qty[0]['recommended_qty']
				app_name = frappe.get_list("Approved Pre Purchase Order", filters = {"pre_purchase_orders": rec_name, "docstatus": 1}, fields=["name"])
				if app_name:
					#print "app_name----------------",app_name
					for app in app_name:
						apr_name = app['name']
						app_qty = frappe.get_list("Approved Pre Purchase Item", filters={"parent": apr_name, "item_code":dt['item_code']}, fields=["approved_qty"])
						if app_qty:
							approved_qty = app_qty[0]['approved_qty']
			
		for pro in doc_project_list:
			
			project_item = 'item-'+str(pro['project'])
			
			if pro['project'] == dt[project_item]:
				projects = pro['project']
				total_qtys += float(dt[str(projects)])
				sums_data.append(dt[projects])
		qty_with_poum = float(total_qtys) / float(dt['conversion_factor'])
		pre_purchase_details_draft = get_pre_purchase_details_draft(project,item_code)
		pre_purchase_details_submit = get_pre_purchase_details_submit(project,item_code)
		for draft in pre_purchase_details_draft:
			if draft.recommended_qty != 0.0:
				draft_qty += float(draft.recommended_qty)
			else:
				draft_qty += float(draft.total_stock_qty)
		qty_with_poum = round(qty_with_poum,4)
		sums_data.append(draft_qty)
		sums_data.append(total_qtys)
		sums_data.append(recommended_qty)
		sums_data.append(approved_qty)
		sums_data.append(dt['po_uom'])
		sums_data.append(dt['conversion_factor'])
		sums_data.append(qty_with_poum)
		sums_data.append(dt['default_supplier'])
		#print "sums_data---------------",sums_data
		final_data.append(sums_data)
	#print "final_data---------------",final_data
				
	return columns, final_data



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
									"fulFilledQty": fulFilledQty,
									"project":project
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
								item_entry["project"] =  project
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
						##print "item_code---", item_code, items_data['uom']
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
						##print "key-----", key

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
									"fulFilledQty": fulFilledQty,
									"project":project
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
							item_entry["project"] =  project
							prev_sreq_list.append(item_entry)
							items_map[key] = prev_sreq_list
		##print "items_map-----", items_map

		return items_map
	else:
		return None

@frappe.whitelist()
def fetch_conversion_factor(parent,uom):
	##print "parent -------------",parent
	records = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent=%s and uom=%s""", (parent, uom), as_dict=1)
	##print "records--------------",records
	if records:
		conversion_factor = records[0]['conversion_factor']
		return conversion_factor
	else:
		return 0

def fetch_po_items_details(item_code,po_list):
	###print "po_list-------", po_list
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
	##print "po_items-------", po_items
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
	##print "po_count---------------------", po_count
	
	if po_count:
		return po_count[0]['po_count']
	else:
		return 0

@frappe.whitelist()
def fetch_last_purchase_price(item_code,uom):
	last_purchase_price = frappe.db.sql(""" select tpoi.rate as last_purchase_price from `tabPurchase Order` po, `tabPurchase Order Item` tpoi where  tpoi.item_code=%s and tpoi.uom=%s and po.name=tpoi.parent and po.docstatus=1 order by tpoi.rate desc limit 1""", (item_code,uom), as_dict=1)

	##print "last_purchase_price---------------------", last_purchase_price
	if last_purchase_price:
		return last_purchase_price[0]['last_purchase_price']
	else:
		return 0


def fetch_max_price_of_last_10_purchase_transactions(item_code,uom):
	max_price_of_last_10_purchase_transactions = frappe.db.sql("""select max(rate) as max_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate desc limit 1) t1""", (item_code,uom), as_dict=1)

	

	if max_price_of_last_10_purchase_transactions:
		return max_price_of_last_10_purchase_transactions[0]['max_price_rate']
	else:
		return 0

def fetch_min_price_of_last_10_purchase_transactions(item_code,uom):
	min_price_of_last_10_purchase_transactions = frappe.db.sql("""select min(rate) as min_price_rate from (select rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate asc limit 1) t1""", (item_code,uom), as_dict=1)

	##print "min_price_of_last_10_purchase_transactions---------------------", min_price_of_last_10_purchase_transactions

	if min_price_of_last_10_purchase_transactions:
		return min_price_of_last_10_purchase_transactions[0]['min_price_rate']
	else:
		return 0

def fetch_avg_price_of_last_10_purchase_transactions(item_code,uom):
	avg_price_of_last_10_purchase_transactions = frappe.db.sql("""select avg(rate) as avg_price from `tabPurchase Order Item` as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled'))""", (item_code,uom), as_dict=1)

	##print "avg_price_of_last_10_purchase_transactions---------------------", avg_price_of_last_10_purchase_transactions

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
def make_purchase_orders(po_items,project_filter,doc_project_list):
	flag = ""
	tax_template = ""
	
	#supplier_address_details = frappe.db.sql("""select * from `tabAddress` a , `tabDynamic Link` dl where dl.link_name = %s and dl.parent = a.name""",supplier,as_dict=1)

	#print "supplier_address_details------------",po_items
	creation_Date = datetime.datetime.now()
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	details = frappe.get_meta("Purchase Order").get("fields")
	##print "supplier-----------------", supplier
	##print "details----------------------",details
	
	
				
		
	if po_items:
		outerJson_Transfer = {
			"doctype": "Pre Purchase Orders",
			"creation": creation_Date,
			"owner": "Administrator",
			"docstatus": 0,
			"date":creation_Date,
			"items": [],
			"project_being_ordered":project_filter
			}


		for items in po_items:
			approved_qty = 0.0
			recommended_qty = 0.0
			pre_purchase_order = frappe.get_list("Pre Purchase Orders", filters={"project_being_ordered":project_filter,"docstatus":1}, fields=["name"])
			for pre in pre_purchase_order:
				name = pre['name']
				pre_purchase_items = frappe.get_list("Pre Purchase Item", filters={"parent":name, 'item':items['item_code']}, fields=["recommended_qty"])
				approved_pre_purchase = frappe.get_list("Approved Pre Purchase Order", filters={"pre_purchase_orders":name,"docstatus":1}, fields=["name"])
				if approved_pre_purchase:
					for app in approved_pre_purchase:
						name = app['name']
						approved_item = frappe.get_list("Approved Pre Purchase Item", filters={"parent":name,'item_code':items['item_code']}, fields=["*"])
						qty = approved_item[0]['approved_qty']
						approved_qty += float(qty)
				
				rec_qty = pre_purchase_items[0]['recommended_qty']
				recommended_qty +=  float(rec_qty)
			
			need_to_be_qty = 0.0
			pre_purchase_details_draft = get_pre_purchase_details_draft(project_filter,items['item_code'])
			#pre_purchase_details_submit = get_pre_purchase_details_submit(project_filter,items['item_code'])
			submit_qty = 0.0
			draft_qty = 0.0
			for draft in pre_purchase_details_draft:
				if draft.recommended_qty != 0.0:
					draft_qty += float(draft.recommended_qty)
				else:
					draft_qty += float(draft.total_stock_qty)
			
				
			total_qty = 0.0
			
			for pro in doc_project_list:
				projects = "item-"+pro['project']
				if pro['project'] == items[str(projects)]:
					projectss = pro['project']
					total_qty += items[str(projectss)]
			
			conversion_factor = items['conversion_factor']
			stock_qty = total_qty
			available_qty = stock_qty - draft_qty
			if available_qty > 0.0:
				if approved_qty == recommended_qty:
					need_to_be_qty = float(available_qty) - float(approved_qty)
				elif approved_qty > recommended_qty:
					qty_re = float(recommended_qty) - float(approved_qty) 
					total_approved = float(recommended_qty) + float(qty_re)
					need_to_be_qty = float(available_qty) - float(total_approved)
			elif approved_qty < recommended_qty:
				qty_re = float(approved_qty) - float(recommended_qty)
				total_approved = float(approved_qty) + float(qty_re)
				need_to_be_qty = float(available_qty) - float(total_approved)
			qty_in_puom = float(need_to_be_qty)/float(conversion_factor)
			if need_to_be_qty > 0.0:
				innerJson_Transfer ={
					"creation": creation_Date,
					"total_stock_qty": need_to_be_qty,
					"item": items['item_code'],
					"default_supplier":items['default_supplier'],
					"stock_uom":items['stock_uom'],
					"conversion_factor":items['conversion_factor'],
					"puom":items['po_uom'],
					"last_n_highest":items['last_n_highest'],
					"last_n_lowest":items['last_n_lowest'],
					"last_n_average":items['last_n_average'],
					"number_of_transactions":items['no_of_transaction'],
					"qty_in_puom":qty_in_puom
				   	}
				outerJson_Transfer["items"].append(innerJson_Transfer)
		#print "outerJson_Transfer--------------------",outerJson_Transfer["items"]
		if len(outerJson_Transfer["items"]) != 0:
			doc = frappe.new_doc("Pre Purchase Orders")
			doc.update(outerJson_Transfer)
			doc.save()

			##print "doc.name 1------------",doc.name
			doc_name_created.append(doc.name)
			#msgDisplayAfterCreatePurchaseOrder(doc.name)

			#frappe.msg#print("Purchase Order is Created: "+doc.name)
			if doc.name:
				flag = doc.name
			ret = doc.doctype
		
			if ret:

				return ret 
		else:
			frappe.msgprint("There is no Item to create Pre Purchase Order ")

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
def get_report_data(project_filter):
	swh_filter = ""
	doc_project_list = project_list(project_filter)
	report_data = []
	qty_in_poum = 0.0
	details = {}
	sum_datas =[]
	prepared_data = []
	if project_filter:
		for pro in doc_project_list:
			#project = filters.get("project")
			items_map = fetch_pending_sreqnos(pro['project'],swh_filter)
			#project_warehouse =  frappe.db.get_value('Project', project_filter, 'project_warehouse')
	    		#reserve_warehouse =  frappe.db.get_value('Project', project_filter, 'reserve_warehouse')
			if items_map:
				for (sreq_no) in sorted(items_map):
					data = items_map[sreq_no]
					prepared_data.append(data)
					for sreq_dict in data:
						##print "sreq_dict-----", sreq_dict['sreq_no']
						##print "bom-----", sreq_dict['bom']
						sum_datas.append([
							sreq_dict['sreq_no'],
							sreq_dict['project'],
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


	
		
	prepare_datas = unique_prepare_data(prepared_data,doc_project_list)
	doctype = make_purchase_orders(prepare_datas,project_filter,doc_project_list)
	return doctype
	data.append(["00","00"])
	return columns, data
def get_columns(doc_project_list):
	
	columns = [
		_("Item")+"::100",
		]
	for pro in doc_project_list:
		columns.append(_(pro['project'])+"::100",)
	columns.append(_("Draft Pre Purchase")+"::120")
	columns.append(	
		_("Total Result")+"::100")
	columns.append(	_("Recommended Order")+"::100")
	columns.append(_("Approved Order")+"::100")
	columns.append(	_("Pur UOM")+"::100")
	columns.append(	_("Conversion Factor")+"::100")
	columns.append(	_("Qty Pur UOM")+"::100")
	columns.append(	_("Default Supplier")+"::100")
	return columns


def project_list(project):
	project = frappe.get_list("Project Childs", filters = {"parent":project}, fields=['project','idx'], order_by = 'idx')
	return project

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
def unique_prepare_data(sum_data,doc_project_list):
	#print "sum_data-----------",sum_data
	sum_datas = sum_data[0]
	
	if len(sum_datas)!=0:
		i = 0
		composite_tax = []
		for data in sum_data:
			#print "data-------------------------",data
			for d in data:
				i += 1
				item_name = d['item_code']
				#print "project------------",d['project']
				#print "item--------------",item_name
				tax_amount = d['project']
				#print "project -------------",tax_amount
				key = item_name
				#print "composite_tax-------------",composite_tax
				if len(composite_tax) != 0:
					if key in [ds['item_code'] for ds in composite_tax]:
						for dp in composite_tax:
							if key == dp['item_code']:
								
								projects = 'item-'+str(d['project'])
									
								dp.update({d['project']:d['sreq_qty'], projects:d['project']})

					else:
						i = 1
						projects = 'item-'+str(d['project'])
						composite_tax.append({"item_code":d['item_code'],d['project']:d['sreq_qty'],projects:d['project'],"po_uom":d['po_uom'],"conversion_factor":d['conversion_factor'],"default_supplier":d['default_supplier'],"stock_uom":d['stock_uom'],"last_n_highest":d['max_price_of_last_10_purchase_transactions'],"last_n_lowest":d['min_price_of_last_10_purchase_transactions'],"last_n_average":d['avg_price_of_last_10_purchase_transactions'],"no_of_transaction":d['no_of_purchase_transactions']})
					
				else:
					i = 1
					projects = 'item-'+str(d['project'])
					composite_tax.append({"item_code":d['item_code'], d['project']:d['sreq_qty'],projects:d['project'],"po_uom":d['po_uom'],"conversion_factor":d['conversion_factor'],"default_supplier":d['default_supplier'],"stock_uom":d['stock_uom'],"last_n_highest":d['max_price_of_last_10_purchase_transactions'],"last_n_lowest":d['min_price_of_last_10_purchase_transactions'],"last_n_average":d['avg_price_of_last_10_purchase_transactions'],"no_of_transaction":d['no_of_purchase_transactions']})
		#print "composite_tax-------------",composite_tax
		#print "doc_project_list-------------",doc_project_list
		projects_details = []
		j =0
		'''
		for db in composite_tax:
			for pro in doc_project_list:
				j += 1
				projects = "project_"+str(j)
				if projects in db:
					#pass
					#print "db--------------------------",db
					#print "helo-----------------------",projects
				else:
					dp.update({pro['project']:"", projects:pro['project']})
			j = 0
		'''
		
		for pro in doc_project_list:
			j += 1
			projectss = pro['project']
			projects = "project_"+str(j)
			
			for db in composite_tax:
				#print "project ------------",projectss
				project_item = 'item-'+str(pro['project'])
				if project_item not in db:
					#pass
					#print "db--------------------------",db
					#print "helo-----------------------",projects
					db.update({pro['project']:0.0, project_item:pro['project']})
				
					
		return composite_tax
	
def get_pre_purchase_details_draft(project,item_code):
	purchase = frappe.db.sql("""select pri.recommended_qty, pri.total_stock_qty,pri.item,pr.project_being_ordered from `tabPre Purchase Orders` pr, `tabPre Purchase Item` pri where pr.project_being_ordered = %s and pr.docstatus= 0 and pri.item = %s""",(project,item_code), as_dict=1)
	return purchase
def get_pre_purchase_details_submit(project,item_code):
	purchase = frappe.db.sql("""select pri.recommended_qty, pri.total_stock_qty,pri.item,pr.project_being_ordered from `tabPre Purchase Orders` pr, `tabPre Purchase Item` pri where pr.project_being_ordered = %s and pri.docstatus= 1 and pri.item = %s""",(project,item_code), as_dict=1)
	return purchase
