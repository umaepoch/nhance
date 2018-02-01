# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
import datetime
from collections import defaultdict
import operator
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
	global company_Name
	planning_warehouse = filters.get("planning_warehouse")
	company_Name = filters.get("company")
	if not filters: filters = {}
	validate_filters(filters)
	columns = get_columns()
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_map(filters)
	data = []
	summ_data = []
	for (item_code) in sorted(iwb_map):
		qty_dict = iwb_map[item_code]
		data.append([				
			        qty_dict.item_code,
				qty_dict.item_name,
				qty_dict.required_qty,
				qty_dict.qty_in_Stock,
				qty_dict.ef_planning_cycle,
				qty_dict.delta,
				qty_dict.reorder_Level,
				qty_dict.min_order_qty,
				qty_dict.wso,
				qty_dict.excess_Ordered,
				qty_dict.stock_uom,
				qty_dict.purchase_uom,
				qty_dict.conversion_factor,
				qty_dict.wso_puom,
				qty_dict.excess_ord_puom,
				qty_dict.supplier,
				qty_dict.rate,
				])
	for rows in data:
		summ_data.append([rows[0], rows[1], rows[2],
		rows[3], rows[4], rows[5], rows[6], rows[7], rows[8], rows[9], rows[10], rows[11], rows[12], rows[13], rows[14], rows[15], rows[16],])
	return columns, summ_data

def get_columns():           
		"""return columns"""
		columns = [	
		_("Item Code")+"::100",
		_("Item Name")+"::100",
		_("MR Recd.")+"::100",
		_("Qty In Stock")+"::100",
		_("Excess From Planning Cycle")+"::100",
		_("Delta")+"::100",
		_("Reorder Level")+"::100",
		_("MOQ")+"::100",
		_("What Should Be ordered")+"::100",
		_("Excess Ordered")+"::100",
		_("Stock Uom")+"::100",
		_("Purchase Uom")+"::100",
		_("Conversion Factor")+"::100",
		_("What Should Be ordered(Purchase Uom)")+"::100",
		_("Excess Ordered(Purchase Uom)")+"::100",
		_("Supplier")+"::100",
		_("Rate")+"::100",
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
		items = frappe.db.sql("""select item_group, item_name, name, brand, uom as purchase_uom, description
				from `tabStock Requisition Item` {condition}""".format(condition=condition), value, as_dict=1)
		return dict((d.name, d) for d in items)

def get_Reorder_Level(item_code):
	reord_List = frappe.db.sql("""select warehouse, warehouse_reorder_level  from `tabItem Reorder` 	where 	parent = %s""", item_code, as_dict=1)
	return reord_List

def get_ItemName(item_code):
	item_names_list = frappe.db.sql("""select item_name  from `tabItem` 	where 	item_code = %s""", item_code, as_dict=1)
	return item_names_list

def get_Uom_Data(item_code):
	uom_Data = frappe.db.sql("""select stock_uom, purchase_uom  from `tabItem` where item_code = %s """, (item_code), as_dict=1)
	if len(uom_Data)!=0:
		stock_uom = uom_Data[0]['stock_uom']
		purchase_uom = uom_Data[0]['purchase_uom']
		if purchase_uom is None or purchase_uom is "":
			purchase_uom = stock_uom
	must_be_whole_number = frappe.db.sql("""select must_be_whole_number  from `tabUOM` where uom_name = %s """, (purchase_uom), as_dict=1)
	uom_Data.extend(must_be_whole_number)
	return uom_Data
	

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
			else:
				whse, whs_flag = get_whs_branch(temp_whse, filters)
		else:
			whse = get_warehouses()
		conversion_factor = 0
		for d in sle:
			wh_stock = 0
			for w in whse:
				whse_stock = get_stock(d.item_code, w)
				wh_stock = wh_stock + whse_stock
			min_Order_Quantity = get_MOQ(d.item_code)
			moq = list(min_Order_Quantity)
			moq1 = list(sum(moq, ()))
			#print "#############min_Order_Quantity", moq1[0]
			purchase_Order_Item = getPurchase_OrderItem_Details(d.item_code)
			#print "purchase_Order_Item::", purchase_Order_Item

			item_names_list = get_ItemName(d.item_code)
			item_name = ""
			#print "##-item_names_list::", item_names_list
			if len(item_names_list) != 0:	
				item_name = item_names_list[0]['item_name']

			reOrder_Level_List = get_Reorder_Level(d.item_code)
			item_Reord_Level = 0
			#print "##-reOrder_Level_List::", reOrder_Level_List
			if len(reOrder_Level_List) != 0:	
				warehouse = reOrder_Level_List[0]['warehouse']
				if planning_warehouse == warehouse:
					item_Reord_Level = reOrder_Level_List[0]['warehouse_reorder_level']

			uom_details = get_Uom_Data(d.item_code)
			if len(uom_details)!=0:
				stock_uom = uom_details[0]['stock_uom']
				purchase_uom = uom_details[0]['purchase_uom']
				if purchase_uom is None or purchase_uom is "":
					purchase_uom = stock_uom
					conversion_factor = 1
				else:
					convert_factor = frappe.db.sql("""select conversion_factor as conversion_factor from `tabUOM Conversion Detail` t2 where t2.parent = %s and uom = %s""", (d.item_code, purchase_uom))

					if convert_factor:
						conversion_factor = convert_factor[0][0]
					else:
						conversion_factor = 1	
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
			pending_Qty = qty - rec_qty
			if pending_Qty > 0:
				
				if excess_prev > pending_Qty:
					excess_from_planning_cycle = excess_prev - pending_Qty
				else:
					excess_from_planning_cycle = excess_prev
			key = d.item_code
			req_Qty = 0
			wso = 0
			delta = 0
			min_order_quantity = 0
			if key in iwb_map:
				item_entry = iwb_map[key]
				qty_temp = item_entry["required_qty"]
				item_entry["required_qty"] = item_entry["required_qty"] + d.req_qty
				req_Qty = item_entry["required_qty"]
				delta = item_entry["required_qty"] - wh_stock - excess_from_planning_cycle
				min_order_quantity = map(operator.itemgetter(0), min_Order_Quantity)
				min_order_quantity = min_order_quantity[0]
				if delta > 0:			
					if delta >= float(moq1[0]):
						wso = delta
					else:
						wso = float(moq1[0])
						print "#######-wso::", wso
 						excess_ord = wso - delta
				else:
					excess_ord = 0
				wso_puom = wso/conversion_factor
				excess_ord_puom = excess_ord/conversion_factor

				item_entry["delta"] = delta
				item_entry["wso"] = wso
				item_entry["excess_Ordered"] = excess_ord
				item_entry["min_order_qty"] = min_order_quantity
				item_entry["reorder_Level"] = item_Reord_Level	
				item_entry["wso_puom"] = wso_puom
				item_entry["excess_ord_puom"] = excess_ord_puom	
			else:
				delta = d.req_qty - wh_stock - excess_from_planning_cycle
				if delta > 0:			
					if delta >= float(moq1[0]):
						wso = delta
					else:
						wso = float(moq1[0])
 						excess_ord = wso - delta

				wso_puom = wso/conversion_factor
				excess_ord_puom = excess_ord/conversion_factor

				iwb_map[key] = frappe._dict({
								 "item_code": d.item_code, 
								 "item_name": item_name, 
							         "required_qty": d.req_qty,
							         "qty_in_Stock": wh_stock,
								 "ef_planning_cycle": 								         excess_from_planning_cycle,
								 "delta": delta,
							         "reorder_Level": item_Reord_Level,
								 "min_order_qty": min_order_quantity, 
								 "wso": wso,
								 "excess_Ordered": excess_ord,
								 "stock_uom": stock_uom,
								 "purchase_uom": purchase_uom,
								 "conversion_factor": conversion_factor,
								 "wso_puom": wso_puom,
								 "excess_ord_puom": excess_ord_puom,
								 "supplier": "",
								 "rate": "",
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
	tot_stock = item_stock + stock_recon
	return tot_stock

def get_stock(item_code, warehouse):		
	item_stock = get_balance_qty_from_sle(item_code, warehouse)
	return item_stock

def getPurchase_OrderItem_Details(item_code):
	return frappe.db.sql("""select qty, received_qty, excess_order, warehouse from `tabPurchase Order Item` where item_code = %s""", item_code, as_dict=1)

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
	return frappe.db.sql("""select item_name, item_group, parent, item_code, qty-ordered_qty as req_qty, min_order_qty from  `tabStock Requisition Item` where docstatus = "1"  and qty > ordered_qty order by item_code """, as_dict=1)	

def get_SupplierList():
	return frappe.db.sql("""select supplier_name  from `tabSupplier`""", as_dict=1)

def get_TaxList():
	return frappe.db.sql("""select name  from `tabSales Taxes and Charges Template`""", as_dict=1)

def get_item_price_details(item_code):
	item_price_details = frappe.db.sql("""select parent,max(rate) as max_price_rate, min(rate) as min_price_rate from `tabPurchase Order Item` where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY)""", (item_code), as_dict=1)
	po_Number = item_price_details[0]['parent']
	last_purchase_price = frappe.db.sql("""select rate as last_purchase_price from `tabPurchase Order Item` where item_code = %s order by creation desc limit 1""", item_code, as_dict=1)
	supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s""", po_Number, as_dict=1)
	item_price_details.extend(last_purchase_price)
	item_price_details.extend(supplier)
	return item_price_details

@frappe.whitelist()
def make_Purchase_Items(args):
	supplier_List = get_SupplierList()
	tax_List = get_TaxList()
	creation_Date = datetime.datetime.now()
	ret = ""
	innerJson_Transfer = " "
        outerJson_Transfer = {"item": [
	]}
	for reportData in summ_data:
		if args == "as final":
			supplier = reportData[15]
			if reportData[0] is None or reportData[0] is "":
				frappe.msgprint("Select Item Code...")
			if supplier is None or supplier is "":
				frappe.msgprint("Select Supplier")
			if reportData[16] is None or reportData[16] is "":
				frappe.msgprint("Set Price For Item...")
		break
	for rows in summ_data:	
		item_code = rows[0]
		item_price_details = get_item_price_details(item_code)
		if item_price_details is not None and len(item_price_details)!=0:
			if len(item_price_details) == 3:
				last_purchase_rate = item_price_details[1]['last_purchase_price']
				if item_price_details[0]['max_price_rate'] is not None:
					max_price_rate = item_price_details[0]['max_price_rate']
				else:
					max_price_rate = 0
				if item_price_details[0]['min_price_rate'] is not None:
					min_price_rate = item_price_details[0]['min_price_rate']
				else:
					min_price_rate = 0
				if item_price_details[0]['parent'] is not None:
					po_Number = item_price_details[0]['parent']
				if item_price_details[2]['supplier'] is not None:
					supplier = item_price_details[2]['supplier']
			else:
				min_price_rate = 0
				last_purchase_rate = 0
				max_price_rate = 0
		uom_details = get_Uom_Data(item_code)
		round_up_down = 0
		round_off = "up"
		if len(uom_details)!=0:
			must_be_whole_number = uom_details[1]['must_be_whole_number']
			if must_be_whole_number == 1:
				item_qty = float(rows[13])
 				check_qty = math.floor(item_qty) 
				check_qty = item_qty - check_qty
				if check_qty != 0.0:
					if round_off == "up":
						quantity = math.ceil(item_qty)
						quantity = int(quantity)
					else:
						quantity = int(item_qty)
				else:
					quantity = int(item_qty)
				print "#################-quantity::", quantity
			else:
				quantity = rows[13]
		if quantity > 0:
			innerJson_Transfer = {
			"item_code": rows[0],
			"qty": quantity,
      			"last_purchase_price": last_purchase_rate,
			"max_purchaseprice_in_last_180days": max_price_rate,
			"min_purchaseprice_in_last_180days": min_price_rate,
			"excess_ordered": rows[14],
			"doctype": "Pre Purchase Order Item",
			"parentfield": "Item"
			}
			outerJson_Transfer["item"].append(innerJson_Transfer)
			doc = frappe.new_doc("Pre Purchase Order")
			print "outerJson_Transfer::", outerJson_Transfer
			doc.update(outerJson_Transfer)
			if args == "as a draft":
				doc.save()
			else:
	  			doc.save()
			ret = doc.doctype
			docid = doc.name
	print "## Docid:", docid
	if ret:
		return docid
def get_Purchase_Taxes_and_Charges(account_head, tax_name):
	tax_List = frappe.db.sql("""select rate, charge_type, description  from `tabPurchase Taxes and Charges` where account_head = %s and parent = %s""", (account_head, tax_name), as_dict=1)
	return tax_List

@frappe.whitelist()
def make_PurchaseOrder(args,tax_template):
	ret = ""
	global tax_Rate_List 
	tax_Rate_List = {}
	order_List = json.loads(args)
	items_List = json.dumps(order_List)
	items_List = ast.literal_eval(items_List)
	creation_Date = datetime.datetime.now()
	outerJson_Transfer = {
					"doctype": "Purchase Order",
					"title": "Purchase Order",
					"creation": creation_Date,
					"owner": "Administrator",
					"taxes_and_charges": tax_template,
					"company": company_Name,
					"due_date": creation_Date,
					"docstatus": 0,
					"supplier":"",
					"items": [
					],
					"taxes": [			 
        				],
					}

	i = 0
	if tax_template is not None and tax_template is not "":
		tax_Name = frappe.get_doc("Purchase Taxes and Charges Template", tax_template)
		for taxes in tax_Name.taxes:
			account_Name = taxes.account_head
			if account_Name:
				tax_Rate_List = get_Purchase_Taxes_and_Charges(account_Name, tax_Name.name)
				if tax_Rate_List is not None and len(tax_Rate_List) != 0:
					charge_type = tax_Rate_List[0]['charge_type']
					rate = tax_Rate_List[0]['rate']
					description = tax_Rate_List[0]['description']
					taxes_Json_Transfer = {"owner": "Administrator",
        						       "charge_type": charge_type,
        				                       "account_head": account_Name,
        						       "rate": rate,
        						       "parenttype": "Purchase Order",
        						       "description": description,
        						       "parentfield": "taxes"
								}
					outerJson_Transfer["taxes"].append(taxes_Json_Transfer)
	print "items_List::", items_List
	for items in items_List:
		outerJson_Transfer['supplier'] = items_List[i]['supplier']
		innerJson_Transfer =	{
					"creation": creation_Date,
					"qty": items_List[i]['qty'],
					"item_code": items_List[i]['item_code'],
					"price_list_rate": items_List[i]['price'],
					"excess_order": items_List[i]['excess_ordered'],
					"doctype": "Purchase Order Item",
					"parenttype": "Purchase Order",
					"schedule_date": creation_Date,
					"parentfield": "items",
					"warehouse": planning_warehouse
				   	}
		i = i + 1
		outerJson_Transfer["items"].append(innerJson_Transfer)
	print "########-Final Purchase Order Json::", outerJson_Transfer
	doc = frappe.new_doc("Purchase Order")
	doc.update(outerJson_Transfer)
	doc.save()
	ret = doc.doctype
	if ret:
		frappe.msgprint("Purchase Order is Created:"+doc.name)
		
