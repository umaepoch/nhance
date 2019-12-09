# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from datetime import datetime
import datetime
from datetime import date, timedelta
import calendar
import time
import math
import json
import ast
import sys
reload(sys)

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	global bom
	bom = ""
	bom = filters.get("bom")
	bom_item = bom_details(filters)
	if bom is not None:
		for bom_i in bom_item:
			bom_name = bom_i.bom_name
			bom_item = bom_i.bo_item
			bo_qty = bom_i.bo_qty
			item_code = bom_i.bi_item
			item_name = bom_i.item_name
			description = bom_i.description
			stock_uom = bom_i.stock_uom
			stock_valuation_price = 0.0
			purchase_order_no = get_purchase_order_no(item_code)
			#print "valuation_prince===========",valuation_prince
			purchase_dict = []
		#	print "purchase_order_no=========",purchase_order_no
			for purchase in purchase_order_no:
				purchase_dict.append(purchase.parent)
			stock_ledger_entry = get_stock_ledger_entry(purchase_dict)
			for stock in stock_ledger_entry:
				if stock_uom == stock.stock_uom:
					stock_valuation_price = stock.valuation_rate
			#print "stock_valuation_price==============",stock_valuation_price
			stock_qty = bom_i.bi_qty
			purchase_uom = ""
			valuation_rate = 0.0
			item_group = ""
			last_purchase_rate = 0.0
			check_last_purchase_rate =""
			number_of_purchase = 0
			avg_purchase = 0.0
			max_purchase = 0.0
			min_purchase = 0.0
			last_purchase = 0.0
			item_details = get_item_details(item_code)
			for code in item_details:
				purchase_uom = code.purchase_uom
				valuation_rate = code.valuation_rate
				item_group = code.item_group
				last_purchase = code.last_purchase_rate
				if last_purchase > 0:
					last_purchase_rate = code.last_purchase_rate
					check_last_purchase_rate = "Y"
				else:
					last_purchase_rate = valuation_rate
					check_last_purchase_rate = "N"
			number_of_purchase = get_number_of_purchase(item_code)
			for num in number_of_purchase:
				number_of_purchase = num.num_of_purchase
				if last_purchase > 0:
					avg_purchase = round(num.avg_purchase , 2)
					max_purchase = round(num.max_purchase, 2)
					min_purchase = round(num.min_purchase,2)
				else:
					avg_purchase = valuation_rate
					max_purchase = valuation_rate
					min_purchase = valuation_rate
			required_qty = 1
			Amount_valuation_rate = (stock_valuation_price*bo_qty )/required_qty
			amount_last_purchase = 0.0
			if last_purchase_rate == 0:
				amount_last_purchase = (stock_valuation_price*bo_qty )/required_qty
			else :
				amount_last_purchase = (last_purchase_rate * bo_qty)/1
			amount_higher_purchase_rate = 0.0
			amount_lowest_purchase_rate = 0.0
			amount_avg_purchase_rate = 0.0
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_higher_purchase_rate = (stock_valuation_price*bo_qty )/required_qty
				else:
					amount_higher_purchase_rate = (last_purchase_rate * bo_qty)/1
			else :
				amount_higher_purchase_rate = (max_purchase * bo_qty)/1
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_lowest_purchase_rate = (stock_valuation_price*bo_qty )/required_qty
				else:
					amount_lowest_purchase_rate = (last_purchase_rate * bo_qty)/1
			else :
				amount_lowest_purchase_rate = (min_purchase * bo_qty)/1
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_avg_purchase_rate = (stock_valuation_price*bo_qty )/required_qty
				else:
					amount_avg_purchase_rate = (last_purchase_rate * bo_qty)/1
			else :
				amount_avg_purchase_rate = round((avg_purchase * bo_qty)/1,2)

			data.append([bom_name,bom_item,bo_qty,description,item_group,item_name,stock_uom,purchase_uom,item_code,stock_qty,required_qty,
			stock_valuation_price,last_purchase_rate,check_last_purchase_rate,number_of_purchase,max_purchase,avg_purchase,
			min_purchase,Amount_valuation_rate,amount_last_purchase,amount_higher_purchase_rate,amount_lowest_purchase_rate,amount_avg_purchase_rate])
	return columns, data

def bom_list():
	list = frappe.db.sql()
def get_columns():
	return [
		_("BOM") + "::110",
		_("Item ") + "::110",
		_("BOM Qty") + "::110",
		_("Description") + "::110",
		_("Item Group ") + "::110",
		_("Item Name") + "::110",
		_("Stock UOM") + "::110",
		_("Purchase UOM") + "::110",
		_("BOM Item") + "::110",
		_("BoM Item Qty") + "::110",
		_("Qty to calculat cost for ") + "::150",
		_("Current Valuation Rate") + "::130",
		_("Last Purchase Price") + "::130",
		_("Was there Last Purchase Price? ") + "::150",
		_("Number of Purchase Transactions that exist") + "::250",
		_("Last N Purchases - Highest") + "::160",
		_("Last N Purchases - Average") + "::160",
		_("Last N Purchases - Lowest") + "::160",
		_("Amount(Valuation Rate)")+"::150",
		_("Amount (Last Purchase Rate)")+"::160",
		_("Amount (Highest Purchase Rate)")+"::160",
		_("Amount (Lowest Purchase Rate)")+"::160",
		_("Amount (Average Purchase Rate)")+"::160"

	]
def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and bo.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)
	if filters.get("bom"):
		conditions += " and bi.parent = '%s'" % frappe.db.escape(filters.get("bom"), percent=False)
	return conditions

def bom_details(filters):
	conditions = get_conditions(filters)
	bom_detail = frappe.db.sql("""select
										bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project,bi.item_name,
										bi.item_code as bi_item,bi.description, bi.stock_qty as bi_qty,bi.stock_uom
								from
										`tabBOM` bo, `tabBOM Explosion Item` bi
								where
										bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1" %s order by bo.name,
										bi.item_code""" % conditions, as_dict=1)
	return bom_detail

def get_item_details(item_code):
	item_detail = frappe.db.sql("""select
											purchase_uom,valuation_rate,item_group,last_purchase_rate
									from
											`tabItem`
									where
											item_code = %s""",(item_code), as_dict =1)
	return item_detail

def get_number_of_purchase(item_code):
	purchase = frappe.db.sql("""select
										count(parent) as num_of_purchase,avg(rate) as avg_purchase,MAX(rate) as max_purchase,
										MIN(rate) as min_purchase
								from
										`tabPurchase Order Item`
								where
										item_code = %s and docstatus = 1""",(item_code), as_dict=1)
	return purchase
def get_purchase_order_no(item_code):
	purchase_order = frappe.db.sql("""select
													parent
											from
													`tabPurchase Order Item`
	 									where
													item_code = '"""+item_code+"""' and docstatus =1
										order by parent
									""", as_dict =1)
	return purchase_order
def get_stock_ledger_entry(purchase_dict):
	purchase_stock_valuation = []
	purchase_or = ""
	for purchase_o in purchase_dict:
		purchase_or = purchase_o
	#print "purchase_o------------------------",purchase_or
	stock_entry = frappe.db.sql("""select
											sl.stock_uom,sl.valuation_rate, pri.purchase_order
									from
											`tabStock Ledger Entry` sl, `tabPurchase Receipt Item` pri
									where
											pri.parent = sl.voucher_no and
											pri.purchase_order IN  ('"""+purchase_or+"""')
								    order by
											sl.name""",as_dict=1)
	return stock_entry
