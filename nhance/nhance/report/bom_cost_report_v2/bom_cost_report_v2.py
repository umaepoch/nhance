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

#reload(sys)

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	global bom
	#print "report add total row-----------",report.add_total_row
	bom = ""
	bom = filters.get("bom")
	company = filters.get("company")
	#print ("company and filters=========",company)
	#print ("bom and filters=========",bom)
	bom_item = bom_details(company , bom)
	total_bom_qty = 0.0
	total_last_purchase_rate = 0.0
	total_item_cost_base_on_last_purchase = 0.0
	total_stock_valuation_price = 0.0
	total_item_cost_based_on_valuation_rate = 0.0
	total_max_purchase = 0.0
	total_avg_purchase = 0.0
	total_min_purchase = 0.0
	total_llp = 0.0
	total_item_amount_based_on_conversion = 0.0
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
			#print "valuation_prince===========",valuation_prince
			purchase_dict = ""
			#print "purchase_order_no=========",purchase_order_no
			stock_ledger_entry = get_stock_ledger_entry(item_code)
			#print "stock_ledger_entry===============",stock_ledger_entry
			#print "stock_valuation_price==============",stock_valuation_price
			stock_qty = bom_i.bi_qty
			total_bom_qty += stock_qty
			total_bom_qty = round(float(total_bom_qty),2)
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
			conversion_factor = 0.0
			item_cost_base_on_last_purchase = 0.0
			item_cost_based_on_valuation_rate = 0.0
			item_details = get_item_details(item_code)
			for code in item_details:
				purchase_uom = code.purchase_uom
				valuation_rate = code.valuation_rate
				item_group = code.item_group
				last_purchase = code.last_purchase_rate
				for stock in stock_ledger_entry:
					if stock.valuation_rate is not None:
						stock_valuation_price = stock.valuation_rate
				#print "item code --------------",item_code
				#print "stock_valuation_price=============",stock_valuation_price
				if last_purchase > 0:
					if code.last_purchase_rate is not None:
						last_purchase_rate = code.last_purchase_rate
						#print "last_purchase_rate-----------",last_purchase_rate
						check_last_purchase_rate = "Y"
						if stock_valuation_price == 0.0:
							stock_valuation_price = code.last_purchase_rate
							#print "stock_valuation_price====lpp=========",stock_valuation_price

				elif stock_valuation_price != 0.0:
					last_purchase_rate = stock_valuation_price
					check_last_purchase_rate = "N"
					#print "last_purchase_rate====svp=========",last_purchase_rate
				else:
					last_purchase_rate = valuation_rate
					#print "last_purchase_rate----vp-------",last_purchase_rate
					check_last_purchase_rate = "N"
					if stock_valuation_price == 0.0:
						stock_valuation_price = valuation_rate
						#print "stock_valuation_price====vp=========",stock_valuation_price
			
			if stock_valuation_price != 0.0:
				stock_valuation_price = round(stock_valuation_price ,2)
				total_stock_valuation_price += stock_valuation_price
				total_stock_valuation_price = round(float(total_stock_valuation_price),2)
			if purchase_uom is not None:
				items_conversion = get_conversion_factore(item_code, purchase_uom)
				
				if items_conversion is not None:
					for conversion in items_conversion:
						conversion_factor = conversion.conversion_factor
			else:
				items_conversion = get_conversion_factore(item_code, stock_uom)
				
				if items_conversion is not None:
					for conversion in items_conversion:
						conversion_factor = conversion.conversion_factor
						conversion_factor = round(float(conversion_factor),2)
			if last_purchase_rate is not None:
				last_purchase_rate = round(float(last_purchase_rate),2)
				total_last_purchase_rate +=  last_purchase_rate
				total_last_purchase_rate = round(float(total_last_purchase_rate),2)
			
			if conversion_factor is not None and stock_qty is not None and last_purchase_rate is not None:
				item_cost_base_on_last_purchase = stock_qty * last_purchase_rate
				item_cost_base_on_last_purchase = round(float(item_cost_base_on_last_purchase),2)
			total_item_cost_base_on_last_purchase += item_cost_base_on_last_purchase
			total_item_cost_base_on_last_purchase = round(float(total_item_cost_base_on_last_purchase),2)

			if stock_valuation_price is not None:
				item_cost_based_on_valuation_rate = stock_qty * stock_valuation_price
				item_cost_based_on_valuation_rate = round(float(item_cost_based_on_valuation_rate),2)
			total_item_cost_based_on_valuation_rate += item_cost_based_on_valuation_rate
			total_item_cost_based_on_valuation_rate = round(float(total_item_cost_based_on_valuation_rate),2)
			purchase_rate = get_purchase_order_no(item_code)

			max_purchase = purchase_rate[0]['highest_rate']
			min_purchase = purchase_rate[0]['lowest_rate']
			avg_purchase = purchase_rate[0]['avg_rate']
			number_of_purchase = purchase_rate[0]['purchase_name_count']
			'''
			number_of_purchase = get_number_of_purchase(item_code)
			for num in number_of_purchase:
				number_of_purchase = num.num_of_purchase
				if num.avg_purchase is not None:
					avg_purchase = num.avg_purchase
				if num.max_purchase is not None:
					max_purchase = num.max_purchase
				if num.min_purchase is not None:
					min_purchase = num.min_purchase

			
			required_qty = 1
			
			Amount_valuation_rate = (stock_valuation_price*stock_qty )/required_qty
			amount_last_purchase = 0.0
			if last_purchase_rate == 0:
				amount_last_purchase = (stock_valuation_price*stock_qty )/required_qty
			else :
				amount_last_purchase = (last_purchase_rate * stock_qty)/1
			
			amount_higher_purchase_rate = 0.0
			amount_lowest_purchase_rate = 0.0
			amount_avg_purchase_rate = 0.0
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_higher_purchase_rate = (stock_valuation_price*stock_qty )/required_qty
				else:
					amount_higher_purchase_rate = (last_purchase_rate * stock_qty)/1
			else :
				amount_higher_purchase_rate = (max_purchase * stock_qty)/1
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_lowest_purchase_rate = (stock_valuation_price*stock_qty )/required_qty
				else:
					amount_lowest_purchase_rate = (last_purchase_rate * stock_qty)/1
			else :
				amount_lowest_purchase_rate = (min_purchase * stock_qty)/1
			if number_of_purchase == 0:
				if last_purchase_rate == 0:
					amount_avg_purchase_rate = (stock_valuation_price*stock_qty )/required_qty
				else:
					amount_avg_purchase_rate = (last_purchase_rate * stock_qty)/1
			else :
				amount_avg_purchase_rate = (avg_purchase * stock_qty)/1
			
			llp = stock_qty * last_purchase_rate
			llp = round(float(llp), 2)
			total_llp += llp
			total_llp = round(float(total_llp),2)
			'''
			if conversion_factor != 0:
				'''
				max_purchase = max_purchase/conversion_factor
				min_purchase = min_purchase/conversion_factor
				avg_purchase = avg_purchase/conversion_factor

				avg_purchase = round(float(avg_purchase),2)
				max_purchase = round(float(max_purchase),2)
				min_purchase = round(float(min_purchase),2)
				'''
				total_avg_purchase += avg_purchase
				total_max_purchase += max_purchase
				total_min_purchase += min_purchase

				total_avg_purchase = round(float(total_avg_purchase),2)
				total_max_purchase = round(float(total_max_purchase),2)
				total_min_purchase = round(float(total_min_purchase),2)

				data.append([bom_name,item_group,item_code,stock_qty,stock_uom,conversion_factor,last_purchase_rate,
						item_cost_base_on_last_purchase ,stock_valuation_price,item_cost_based_on_valuation_rate
						,max_purchase , avg_purchase,min_purchase,number_of_purchase])
			else:
				frappe.throw("Please define Conversion Factor for purchase uom "+'"'+purchase_uom+'"'+ " of this "+'"'+item_code+'"'+" in Item Master and run this report again")
	get_total = get_report_total_row()
	#print "get_total------------",get_total
	if get_total[0].add_total_row == 0:
		#print "get_total------------",get_total[0].add_total_row
		data.append(["","","","","","","","","","","","","",""])
		data.append(["Total","","",total_bom_qty,"","",total_last_purchase_rate,total_item_cost_base_on_last_purchase
			,total_stock_valuation_price,total_item_cost_based_on_valuation_rate,total_max_purchase,
			total_avg_purchase,total_min_purchase,"",""])
	return columns, data

def bom_list():
	list = frappe.db.sql()
def get_columns():
	return [
		_("BOM") + "::110",
		_("Item Group ") + "::110",
		_("Bom Item ") + ":Link/Item:110",
		_("Bom Item Qty") + "::110",
		_("Stock UOM") + "::110",
		_("Conversion Factor") + "::110",
		_("Last Purchase Price") + "::130",
		_("Total Bom Item Cost Based on Last Purchase Price") + "::180",
		_("Current Valuation Rate") + "::130",
		_("Total Bom Item Cost Based on Current Valuation Rate")+"::180",
		_("Last N Purchases - Highest") + "::160",
		_("Last N Purchases - Average") + "::160",
		_("Last N Purchases - Lowest") + "::160",
		_("Number of Purchase Transactions that exist") + "::250"

	]
'''
def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and bo.company = %s" % frappe.db.escape(filters.get("company"), percent=False)
	if filters.get("bom"):
		conditions += " and bi.parent = %s" % frappe.db.escape(filters.get("bom"), percent=False)
	return conditions
'''
def bom_details(company , bom):
	#conditions = get_conditions(company , bom)
	#print ("conditions-------------",conditions)
	bom_detail = frappe.db.sql("""select
						bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty,
						 bo.project,bi.item_name,bi.item_code as bi_item,bi.description, 
							bi.stock_qty as bi_qty,bi.stock_uom
					from
						`tabBOM` bo, `tabBOM Explosion Item` bi
					where
						bo.name = bi.parent and bo.is_active=1 and bo.docstatus = 1 and 
						bo.company = '"""+company+"""' and bi.parent = '"""+bom+"""'

					order by
						bi.item_code""", as_dict=1)
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
	#print "item code-------------------",item_code
	purchase_name_count = 0
	total_rate = 0.0
	lowest_rate = 0.0
	highest_rate = 0.0
	avg_rate = 0.0
	purchase_order_lha = []
	purchase_order = frappe.db.sql("""select 
						poi.item_code,poi.conversion_factor,poi.rate,poi.parent
					from 
						`tabPurchase Order Item` poi 
					where 
						poi.item_code = %s  and docstatus = 1
						""",item_code, as_dict =1)

	lowest_purchase_item_rate = frappe.db.sql("""SELECT tbl.parent,tbl.rate,tbl.conversion_factor,tbl.item_code 
						 FROM `tabPurchase Order Item` tbl   INNER JOIN   
						(SELECT parent, min(rate) as min_rate     FROM `tabPurchase Order Item`     
						GROUP BY parent   ) tbl1   ON tbl1.parent = tbl.parent
				 WHERE tbl1.min_rate = tbl.rate and tbl.item_code = %s and tbl.docstatus =1""",item_code, as_dict =1)

	highest_purchase_item_rate = frappe.db.sql("""SELECT parent, rate, conversion_factor , item_code  FROM  `tabPurchase Order Item`  
					WHERE  rate  = ( SELECT MAX(rate) FROM `tabPurchase Order Item` where item_code = %s) 					and docstatus =1 and conversion_factor = (select min(conversion_factor) from `tabPurchase Order Item` where 					item_code = %s) 
					and item_code = %s""",(item_code,item_code,item_code), as_dict =1)
	if highest_purchase_item_rate:
		for highest in highest_purchase_item_rate:
			highest_rate = highest.rate / highest.conversion_factor
	#print "highest rate -------------",highest_rate
	
	if lowest_purchase_item_rate:
		for lowest in lowest_purchase_item_rate:
			lowest_rate = lowest.rate / lowest.conversion_factor
	#print "lowest_rate--------------",lowest_rate
	if purchase_order:
		for purchase in purchase_order:
			purchase_name_count = purchase_name_count + 1
			conversion_factor = purchase.conversion_factor
			rate = purchase.rate
			rate_with_conversion = rate / conversion_factor
			total_rate += rate_with_conversion
			
			#purchase_name_count += purchase_name_count + 1
			
			#print "conversion_factor------------",conversion_factor
			#print "rate------------",rate
			#print "rate_with_conversion------------",rate_with_conversion
	if purchase_name_count > 0.0:
		avg_rate = total_rate/purchase_name_count
	#print "purchase_name_count------------",purchase_name_count
	#print "total_rate------------",total_rate 
	#print "avg_rate------------",avg_rate 
	#print "--------------------------------------end item calculation--------------------------"
	highest_rate = round(float(highest_rate),2)
	lowest_rate = round(float(lowest_rate),2)
	avg_rate = round(float(avg_rate),2)
	purchase_name_count = round(float(purchase_name_count),2)
	purchase_order_lha.append(
				{
				"highest_rate":highest_rate,
				"lowest_rate":lowest_rate,
				"avg_rate":avg_rate,
				"purchase_name_count":purchase_name_count
				})
	#print "purchase_order_lha------------",purchase_order_lha
	return purchase_order_lha
def get_stock_ledger_entry(item_code):
	stock_entry = ""
	stock_entry = frappe.db.sql(""" select  
						name,valuation_rate, item_code  
					from  
						`tabStock Ledger Entry` 
					where 
						name = (select max(name) from `tabStock Ledger Entry` where item_code =%s)
						 """,item_code,as_dict=1)
	#print "stock_entry===========",stock_entry
	return stock_entry

def get_conversion_factore(item_code,purchase_uom):
	
	#print "item_code==============",item_code
	conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = %s and uom = %s """,(item_code,purchase_uom), as_dict=1)
	'''
	conversion = frappe.get_all('UOM Conversion Detail', filters={"parent": item_code}, fields=["conversion_factor"])
	
	print "item_code==============",item_code
	print "conversion---------------",conversion
	'''
	#print "item_code==============",item_code
	#print "item_code==============",purchase_uom
	#print "conversion---------------",conversion
	return conversion
def get_report_total_row():
	total_row_checking = frappe.db.sql("""select add_total_row from `tabReport` where report_name = 'BOM-Cost-Report v2'""",as_dict =1)

	return total_row_checking

