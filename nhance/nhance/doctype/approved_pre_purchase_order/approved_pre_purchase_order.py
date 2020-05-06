# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime
import time
class ApprovedPrePurchaseOrder(Document):
	pass
@frappe.whitelist()
def get_doc_details(doctype):
	doc_details = frappe.get_meta(doctype).get("fields")
	return doc_details

@frappe.whitelist()
def make_purchase_order(source_name):
	approved_pre_purcase = frappe.get_list("Approved Pre Purchase Item",filters={"parent":source_name, "docstatus":1}, fields=["*"])
	pre_purchase = frappe.get_list("Approved Pre Purchase Order", filters= {"name": source_name}, fields=["pre_purchase_orders"])
	project_being = frappe.get_list("Pre Purchase Orders", filters = {"name": pre_purchase[0]['pre_purchase_orders']}, fields=['project_being_ordered'])
	items_maps = []
	doc_project_list = project_list(project_being[0]['project_being_ordered'])
	for project in doc_project_list:
		swh = ""
		project_warehouse =  frappe.db.get_value('Project', project['project'], 'project_warehouse')
		reserve_warehouse =  frappe.db.get_value('Project', project['project'], 'reserve_warehouse')
		items_map = fetch_pending_sreqnos(project['project'],swh)
		items_maps.append(items_map)
	according_supplier = unified_supplier(approved_pre_purcase)
	creation_Date = datetime.datetime.now()
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	for sup in according_supplier:
		add_ress_data = ""
		supplier_address = ""
		supplier_gstin = ""
		tax_template = ""
		details = according_supplier[sup]
		prepared_details = get_prepared_details(details,items_maps)
		tax_details = ""
		supplier_address_details = frappe.db.sql("""select * from `tabAddress` a , `tabDynamic Link` dl where dl.link_name = %s and dl.parent = a.name""",sup,as_dict=1)
		tax_template_details = frappe.get_list("Supplier", filters={"name": sup}, fields=['pch_tax_template', 'pch_terms'])
		if tax_template_details:
			tax_template = tax_template_details[0]['pch_tax_template']
			
			tax_details = frappe.get_list("Purchase Taxes and Charges", filters={"parent": tax_template}, fields=["*"], order_by ="idx")
		#print "supplier_address_details-----------",supplier_address_details
		if supplier_address_details:
			for add in supplier_address_details:
				if add.address_type == "Billing":
					add_ress_data = str(add.address_line1)+'<br>'+str(add.address_line2)+'<br>'+str(add.city)+'<br>'+str(add.state)+'<br>'+str(add.pincode)+'<br>'+str(add.country)
					supplier_address = add.parent
					supplier_gstin = add.gstin
					
		outerJson_Transfer = {
			"doctype": "Purchase Order",
			"title": sup,
			"creation": creation_Date,
			"owner": "Administrator",
			"company": company,
			"due_date": creation_Date,
			"docstatus": 0,
			"supplier": sup,
			"terms": "",
			"address_display":add_ress_data,
			"supplier_address":supplier_address,
			"supplier_gstin":supplier_gstin,
			"approved_pre_purchase_order": source_name,
			"taxes_and_charges":tax_template,
			"items": [],
			"taxes": []
			}
		for items in prepared_details:
			project = items['project']
			#warehose_list = frappe.get_list("Project", filters = {"name": project}, fields=['reserve_warehouse'])
			#print "warehouse--------------",items['warehouse']
			innerJson_Transfer ={
				"creation": creation_Date,
				"qty": items['qty'],
				"item_code": items['item_code'],
				"doctype": "Purchase Order Item",
				"parenttype": "Purchase Order",
				"schedule_date": creation_Date,
				"parentfield": "items",
				"rate": items['rate'],
				"stock_uom":items['stock_uom'],
				"uom":items["puom"],
				"conversion_factor":items['conversion_factor'],
				"stock_requisition":items['sreq_no'],
				"warehouse": items['warehouse'],
				"project": project
				
			   	}
			outerJson_Transfer["items"].append(innerJson_Transfer)
		for tax in tax_details:
			inner_json_for_taxes = {
				"doctype": "Purchase Taxes and Charges",
				"parenttype": "Purchase Order",
				"parentfield": "taxes",
				"creation": creation_Date,
				"charge_type" : tax['charge_type'],
				"account_head":tax['account_head'],
				"rate":tax['rate'],
				"description" :tax['description'],
				"row_id" : tax['row_id'],
			}
			outerJson_Transfer["taxes"].append(inner_json_for_taxes)
			
			
		doc = frappe.new_doc("Purchase Order")
		doc.update(outerJson_Transfer)
		doc.save()
		if doc.name:
			frappe.msgprint("Purchase Order is created "+doc.name)

def unified_supplier(approved_pre_purcase):
	details = {}
	for app in approved_pre_purcase:
		supplier = app['approved_supplier']
		key = supplier
		if len(details) != 0:
			if key in details:
				approved_qty = app['approved_qty']
				if approved_qty != 0.0:
					details[key].append({"item_code":app['item_code'],"stock_uom":app['stock_uom'], "puom":app['puom'], "conversion_factor":app['conversion_factor'], "qty":approved_qty,"rate":app['approved_rate'],"total_stock_qty": app['total_stock_qty']})
			else:
				approved_qty =app['approved_qty']
				if app['approved_qty'] != 0.0:
					details.update({key:[{"item_code":app['item_code'],"stock_uom":app['stock_uom'], "puom":app['puom'], "conversion_factor":app['conversion_factor'], "qty":approved_qty,"rate":app['approved_rate'],"total_stock_qty": app['total_stock_qty']}]})
		else:
			approved_qty = app['approved_qty']
			if app['approved_qty'] != 0.0:
				details[key]= [{"item_code":app['item_code'],"stock_uom":app['stock_uom'], "puom":app['puom'], "conversion_factor":app['conversion_factor'], "qty":approved_qty,"rate":app['approved_rate'],"total_stock_qty": app['total_stock_qty']}]

	return details
			
def project_list(project):
	project = frappe.get_list("Project Childs", filters = {"parent":project}, fields=['project'], order_by = 'idx')
	return project

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
	##print "po_list-------", po_list
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
	max_price_of_last_10_purchase_transactions = frappe.db.sql("""select max(rate) as max_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate desc limit 1) t1""", (item_code,uom), as_dict=1)

	#print "max_price_of_last_10_purchase_transactions---------------------", max_price_of_last_10_purchase_transactions

	if max_price_of_last_10_purchase_transactions:
		return max_price_of_last_10_purchase_transactions[0]['max_price_rate']
	else:
		return 0

def fetch_min_price_of_last_10_purchase_transactions(item_code,uom):
	min_price_of_last_10_purchase_transactions = frappe.db.sql("""select min(rate) as min_price_rate from (select rate from `tabPurchase Order Item`  as tpoi where item_code = %s and uom = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate asc limit 1) t1""", (item_code,uom), as_dict=1)

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

def get_prepared_details(details,items_maps):
	items = []
	for d in details:
		key = d['item_code']
		total_qty = 0.0
		approved_qty = d['qty']
		for items_map in items_maps:
			for (sreq_no) in sorted(items_map):
				
				data = items_map[sreq_no]
				#print "data-----------",data
				for sreq_dict in data:
					if key == sreq_dict['item_code']:
						if approved_qty <= d['total_stock_qty']:
							if approved_qty > total_qty:
								total_qty += sreq_dict['sreq_qty']
								if total_qty <= approved_qty:
									warehose_list = frappe.get_list("Project", filters = {"name": sreq_dict['project']}, fields=['reserve_warehouse'])
									items.append({"item_code": sreq_dict['item_code'], "project": sreq_dict['project'], "qty":sreq_dict['sreq_qty'], "stock_uom":sreq_dict['stock_uom'], "conversion_factor":sreq_dict['conversion_factor'],"puom":sreq_dict['po_uom'],"rate":d['rate'],"sreq_no":sreq_dict['sreq_no'],"warehouse":warehose_list[0]['reserve_warehouse']  })
								else:
									warehose_list = frappe.get_list("Project", filters = {"name": sreq_dict['project']}, fields=['reserve_warehouse'])
									deff_qty = total_qty - approved_qty
									need_qty = sreq_dict['sreq_qty'] - deff_qty
									total_qty += need_qty
									items.append({"item_code": sreq_dict['item_code'], "project": sreq_dict['project'], "qty":need_qty, "stock_uom":sreq_dict['stock_uom'], "conversion_factor":sreq_dict['conversion_factor'],"puom":sreq_dict['po_uom'],"rate":d['rate'],"sreq_no":sreq_dict['sreq_no'],"warehouse":warehose_list[0]['reserve_warehouse']  })
									break
							elif approved_qty == total_qty:
								break
						else:
							warehose_list = frappe.get_list("Project", filters = {"name": sreq_dict['project']}, fields=['reserve_warehouse'])
							initial_qty = approved_qty - float(d['total_stock_qty'])
							approved_qty = float(d['total_stock_qty'])
							total_qty += sreq_dict['sreq_qty']

							#single_doc = frappe.get_single("Nhance Settings")
							single_doc = frappe.db.get_single_value("Nhance Settings", "default_warehouse")
							#print "single_doc----------",single_doc
							items.append({"item_code": sreq_dict['item_code'], "project": "", "qty":initial_qty, "stock_uom":sreq_dict['stock_uom'], "conversion_factor":sreq_dict['conversion_factor'],"puom":sreq_dict['po_uom'],"rate":d['rate'],"sreq_no":sreq_dict['sreq_no'], "warehouse":single_doc})

							if total_qty <= approved_qty:
								
								items.append({"item_code": sreq_dict['item_code'], "project": sreq_dict['project'], "qty":sreq_dict['sreq_qty'], "stock_uom":sreq_dict['stock_uom'], "conversion_factor":sreq_dict['conversion_factor'],"puom":sreq_dict['po_uom'],"rate":d['rate'],"sreq_no":sreq_dict['sreq_no'], "warehouse":warehose_list[0]['reserve_warehouse'] })
							else:
								deff_qty = total_qty - approved_qty
								need_qty = sreq_dict['sreq_qty'] - deff_qty
								total_qty += need_qty
								
								items.append({"item_code": sreq_dict['item_code'], "project": sreq_dict['project'], "qty":need_qty, "stock_uom":sreq_dict['stock_uom'], "conversion_factor":sreq_dict['conversion_factor'],"puom":sreq_dict['po_uom'],"rate":d['rate'],"sreq_no":sreq_dict['sreq_no'], "warehouse":warehose_list[0]['reserve_warehouse'] })
							
	return items
							
@frappe.whitelist()
def get_verification(source_name):
	get_verified = frappe.get_list("Purchase Order", filters={"approved_pre_purchase_order": source_name, 'docstatus':0}, fields=["name"])
	if get_verified:
		return get_verified
	else:
		return None				
