# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
#from frappe.utils.jinja import get_jenv, get_template, render_template
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime,comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from datetime import datetime
#import flask
#from flask import Flask
from collections import defaultdict
import frappe
import json
import time
import math
import ast


def execute(filters=None):

	global item_map
	global whs_flag
	global whse
	global iwb_map
	global company
	global planning_warehouse
	global summ_data

	planning_warehouse = filters.get("planning_warehouse")


	if not filters: filters = {}
	validate_filters(filters)

	columns = get_columns()
	print "#####warehouse:", type(columns[12])

	item_map = get_item_details(filters)
	#print "##item-Details", item_map
	
	iwb_map = get_item_warehouse_map(filters)
	print "iwb_map==>>", iwb_map

	data = []
	summ_data = []

	#for (item_code, ordered_qty, qty_in_Stock, ef_planning_cycle, delta, reorder_Level, 		         min_order_qty, wso, excess_Ordered, whse) in sorted(iwb_map):
	for (item_code) in sorted(iwb_map):
		qty_dict = iwb_map[item_code]
		data.append([				
			        qty_dict.item_code,
				qty_dict.required_qty,
				qty_dict.qty_in_Stock,
				qty_dict.ef_planning_cycle,
				qty_dict.delta,
				qty_dict.reorder_Level,
				qty_dict.min_order_qty,
				qty_dict.wso,
				qty_dict.excess_Ordered,
				])

	for rows in data:
		#print "row-1", rows[4]
		summ_data.append([rows[0], rows[1], rows[2],
		rows[3], rows[4], rows[5], rows[6], rows[7], rows[8]])
	return columns, summ_data

def get_columns():           
		"""return columns"""
		columns = [	
		_("Item_Code")+"::100",
		_("MR Recd.")+"::100",
		_("Qty in Stock")+"::100",
		_("Excess from Planning Cycle")+"::100",
		_("Delta")+"::100",
		_("Reorder Level")+"::100",
		_("MOQ")+"::100",
		_("What Should be ordered")+"::100",
		_("Excess Ordered")+"::100",
		_("Supplier")+":Select/Supplier:100",
		_("Rate")+":Text:100",	
		_("Tax Template")+"::100",
		_("Are You Ordering this?")+":Text:100",
		 ]
		return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("item_code"):
		conditions += " and item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)

	return conditions


def validate_filters(filters):
		print "##validating filters..."
		if not (filters.get("item_code") or filters.get("warehouse")):
				sle_count = flt(frappe.db.sql("""select count(name) from          
				`tabStock Ledger Entry`""")[0][0])	


def get_item_details(filters):
		condition = ''
		value = ()
		if filters.get("item_code"):
				condition = "where item_code=%s"
				value = (filters["item_code"],)

		items = frappe.db.sql("""select item_group, item_name, name, brand, description
				from `tabMaterial Request Item` {condition}""".format(condition=condition), 				value, as_dict=1)

		return dict((d.name, d) for d in items)

def get_Reorder_Level(item_code):
	reord_List = frappe.db.sql("""select warehouse, warehouse_reorder_level  from `tabItem Reorder` 	where 	parent = %s""", item_code, as_dict=1)
	return reord_List
	

def get_item_warehouse_map(filters):

		iwb_map = {}
		sle = get_sales_order_entries()
		total_stock = 0
		efpc = 0.0
		wso = 0.0
		temp_whse = []
		item_flag = {}
		whs_flag = 0
		if filters.get("planning_warehouse"):
			planning_warehouse = filters.get("planning_warehouse")
			

		if filters.get("warehouse"):
			temp_whse = filters.get("warehouse")

			if temp_whse == 'All':
				whse, whs_flag = get_warehouses()
				#print "####All-whs:", whse, whs_flag
			else:
				whse, whs_flag = get_whs_branch(temp_whse, filters)
				#print "####whs:", whse, whs_flag
		else:

			whse = get_warehouses()
			#print "@@@@@whs::", whse

		print "####sle->", sle

		#print "####data-type of sle", type(sle)
		
		for d in sle:
			wh_stock = 0
			for w in whse:
				whse_stock = get_stock(d.item_code, w)
				#print "##whse_stock::", whse_stock
				wh_stock = wh_stock + whse_stock

			#print "#############total_stock", wh_stock
			min_Order_Quantity = get_MOQ(d.item_code)
			moq = list(min_Order_Quantity)
			moq1 = list(sum(moq, ()))
			#print "#############min_Order_Quantity", moq1[0]
			purchase_Order_Item = getPurchase_OrderItem_Details(d.item_code)
			print "purchase_Order_Item::", purchase_Order_Item

			reOrder_Level_List = get_Reorder_Level(d.item_code)
			item_Reord_Level = 0
			print "##-reOrder_Level_List::", reOrder_Level_List
			if len(reOrder_Level_List) != 0:	
				warehouse = reOrder_Level_List[0]['warehouse']
				if planning_warehouse == warehouse:
					item_Reord_Level = reOrder_Level_List[0]['warehouse_reorder_level']

				
			qty = 0
			rec_qty = 0
			excess_ord = 0
			excess_prev = 0
			excess_from_planning_cycle = 0

			for items in purchase_Order_Item:
				if items.warehouse in whse:
					quantity = items.qty
					received_qty = items.received_qty
					excess_Ordered = items.excess_order

					qty = qty + quantity
					rec_qty = rec_qty + received_qty
					excess_prev = excess_prev + excess_Ordered
			#print "##qty::", qty
			pending_Qty = qty - rec_qty
			#excess_ord = 10
			print "###-excess_prev:", excess_prev
			print "###-pending_Qty:", pending_Qty
			if pending_Qty > 0:
				
				if excess_prev > pending_Qty:
					excess_from_planning_cycle = excess_prev - pending_Qty
				else:
					excess_from_planning_cycle = excess_prev
			print "###-excess_from_planning_cycle:", excess_from_planning_cycle

			key = d.item_code
			req_Qty = 0
			wso = 0
			delta = 0

			if key in iwb_map:
				
				print "#### item already exists", key
				item_entry = iwb_map[key]
				qty_temp = item_entry["required_qty"]
				item_entry["required_qty"] = item_entry["required_qty"] + d.req_qty
				req_Qty = item_entry["required_qty"]

				#print "###-req_Qty", req_Qty
				#print "###-wh_stock", wh_stock

				delta = item_entry["required_qty"] - wh_stock - excess_from_planning_cycle
				print "###-delta::", delta
				print "###-min_Order_Quantity::", min_Order_Quantity
				print "###-item_code::", item_entry["item_code"]

				if delta > 0:			
					if delta >= float(moq1[0]):
						wso = delta
					else:
						wso = float(moq1[0])
						print "#######-wso::", wso
 						excess_ord = wso - delta
				else:
					excess_ord = 0

				#print "#######-delta::", delta
				print "#######-wso::", wso
				#print "########-excess_ord::", excess_ord
				item_entry["delta"] = delta
				item_entry["wso"] = wso
				item_entry["excess_Ordered"] = excess_ord
				item_entry["min_order_qty"] = min_Order_Quantity
				item_entry["reorder_Level"] = item_Reord_Level	

			else:

				delta = d.req_qty - wh_stock - excess_from_planning_cycle
				if delta > 0:			
					if delta >= float(moq1[0]):
						wso = delta
					else:
						wso = float(moq1[0])
 						excess_ord = wso - delta
				#print "#### item does not exist", key
				iwb_map[key] = frappe._dict({
								 "item_code": d.item_code, 
							         "required_qty": d.req_qty,
							         "qty_in_Stock": wh_stock,
								 "ef_planning_cycle": 								         excess_from_planning_cycle,
								 "delta": delta,
							         "reorder_Level": item_Reord_Level,
								 "min_order_qty": min_Order_Quantity, 
								 "wso": wso,
								 "excess_Ordered": excess_ord,
							})
			
		return iwb_map
									

def get_total_stock(item_code):

	item_stock = flt(frappe.db.sql("""select sum(actual_qty)
			from `tabStock Ledger Entry`
			where item_code=%s""",
			(item_code))[0][0])

	stock_recon = flt(frappe.db.sql("""select sum(qty_after_transaction)
			from `tabStock Ledger Entry`
			where item_code=%s and voucher_type = 'Stock Reconciliation'""",
			(item_code))[0][0])
	#print "item_stock && stock_recon", item_stock, stock_recon

	tot_stock = item_stock + stock_recon
	return tot_stock


def get_stock(item_code, warehouse):		

	item_stock = get_balance_qty_from_sle(item_code, warehouse)
	#print "#####item_stock::", item_stock
	return item_stock

def getPurchase_OrderItem_Details(item_code):

	return frappe.db.sql("""select qty, received_qty, excess_order, warehouse from 				`tabPurchase Order Item` where item_code = %s""", item_code, as_dict=1)




def get_MOQ(item_code):

	moq_List = frappe.db.sql("""select min_order_qty from `tabItem` where item_code = %s""", item_code)
	return moq_List
	


def get_warehouses():

		whse = frappe.db.sql("""select name from `tabWarehouse`""")
		whse_list = [row[0] for row in whse]


		whs_flag = 1
		return whse_list, whs_flag

def get_whs_branch(temp_whs, filters):
	whse = frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse = %s""", temp_whs)
	whse_list = [row[0] for row in whse]
	if whse_list:
		whs_flag = 1
		return whse_list, whs_flag
	else:
		whs_flag = 0
		whse = filters.get("warehouse")
		return whse, whs_flag

def get_sales_order_entries():
	
	#print "####get_sales_order_entries:"
	#conditions = get_conditions(filters)
	#print "##conditions:", conditions

	#return frappe.db.sql("""select item_name, item_group, item_code, ordered_qty, min_order_qty from  `tabMaterial Request Item` where docstatus = "1" %s  order by item_code """ % conditions, as_dict=1)

	return frappe.db.sql("""select item_name, item_group, item_code, qty-ordered_qty as req_qty, min_order_qty from  `tabMaterial Request Item` where docstatus = "1"  and qty > ordered_qty order by item_code """, as_dict=1)	


def get_SupplierList():

	return frappe.db.sql("""select supplier_name  from `tabSupplier`""", as_dict=1)

def get_TaxList():

	return frappe.db.sql("""select name  from `tabSales Taxes and Charges Template`""", as_dict=1)

	
@frappe.whitelist()
def make_Purchase_Items(args):

	supplier_List = get_SupplierList()
	print "######-supplier_List::", supplier_List

	tax_List = get_TaxList()
	print "######-tax_List::", tax_List

	creation_Date = getdate(datetime.now().strftime('%Y-%m-%d'))

	ret = ""
	innerJson_Transfer = " "

	outerJson_Transfer = {"item": [
	]}
	
	print "######-summ_data::", summ_data
	for rows in summ_data:	
		
		print "######-item_code::", rows[0]
		innerJson_Transfer = {
					"item_code": rows[0],
					"qty": rows[7],
					"excess_ordered": rows[8],
					"doctype": "Pre Purchase Order Item",
					"parentfield": "Item"
				  	}
		outerJson_Transfer["item"].append(innerJson_Transfer)


	doc = frappe.new_doc("Pre Purchase Order")
	print "outerJson_Transfer::", outerJson_Transfer
	doc.update(outerJson_Transfer)

	if args == "as a draft":
		doc.save()
		
		print "###-Document is saved."

	#doc.submit()
	print "###-Document is submitted."
	ret = doc.doctype
	docid = doc.name
	print "## Docid:", doc.name

	if ret:

		return docid
	
@frappe.whitelist()
def get_Sales_Taxes_and_Charges(account_head):
	tax_List = frappe.db.sql("""select rate, charge_type, description  from `tabSales Taxes and Charges` 		where 	account_head = %s""", account_head, as_dict=1)
	return tax_List

@frappe.whitelist()
def get_AccountHead():
	account_head_List = frappe.db.sql("""select name  from `tabAccount` where account_type = 'Tax' 		""", as_dict=1)
	return account_head_List
	

@frappe.whitelist()
def make_PurchaseOrder(args,tax_template):

	ret = ""
	print "###########- under make_PurchaseOrder", args
	#print "###########- tax_template", tax_template
	#account_head = tax_template + " " + "-" + " MSPL"
	#account_head = tax_template.replace(tax_template[:3], '')
	acc, account_head = tax_template.split(" ", 1)
	print "###########- account_head", account_head
	order_List = json.loads(args)
	items_List = json.dumps(order_List)
	items_List = ast.literal_eval(items_List)
	creation_Date = getdate(datetime.now().strftime('%Y-%m-%d'))
	#print "creation_Date", creation_Date

	account_head_List = get_AccountHead()
	#print "account_head_List::", account_head_List
	for acc_head in account_head_List:
		#print "===>", account_head, acc_head.name
		if account_head in acc_head.name:
			print "##acc_head::", acc_head.name
			print "##tax_template ", tax_template, acc_head.name
			account_head = acc_head.name

	tax_Rate_List = get_Sales_Taxes_and_Charges(account_head)
	#print "tax_Rate_List::", tax_Rate_List
	#print "tax_Rate_List::", tax_Rate_List[0]['charge_type']
	charge_type = tax_Rate_List[0]['charge_type']
	rate = tax_Rate_List[0]['rate']
	description = tax_Rate_List[0]['description']

	outerJson_Transfer = {
					"doctype": "Purchase Order",
					"title": "Purchase Order",
					"creation": creation_Date,
					"owner": "Administrator",
					"taxes_and_charges": tax_template,
					"company": "Merit Systems Pvt Ltd",
					"docstatus": 0,
					"items": [
					],
					"taxes": [{			 
        				"owner": "Administrator",
        				"charge_type": charge_type,
        				"account_head": account_head,
        				"rate": rate,
        				"parenttype": "Purchase Order",
        				"description": description,
        				"parentfield": "taxes"
					}],
					}

	i = 0
	print "items_List::", items_List

	for items in items_List:

		#print "#######-item_code",  items_List[i]['item_code']
		#print "########-qty",  items_List[i]['qty']
		outerJson_Transfer['supplier'] = items_List[i]['supplier']
		innerJson_Transfer =	{
					"creation": creation_Date,
					"qty": items_List[i]['qty'],
					"item_code": items_List[i]['item_code'],
					"amount": items_List[i]['price'],
					"excess_order": items_List[i]['excess_ordered'],
					"doctype": "Purchase Order Item",
					"parenttype": "Purchase Order",
					"schedule_date": creation_Date,
					"parentfield": "items"
				   	}
		i = i + 1
		#outerJson_Transfer['taxes_and_charges'] = items_List['tax_template']
		outerJson_Transfer["items"].append(innerJson_Transfer)
		#print "####-outerJson_Transfer::", outerJson_Transfer
	doc = frappe.new_doc("Purchase Order")
	doc.update(outerJson_Transfer)
	doc.save()
	ret = doc.doctype
	ret = "Purchase Order is Done!!!"
	if ret:
		return ret
		



	





