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
	company = filters.get("company")
	sales_order = ""
	sales_order = filters.get("sales_order")
	sales_item = sales_item_details(company ,sales_order)
	print("sales_item",sales_item)
	for items in sales_item:
	  sales_item_code=items.item_code
	  print("=========",sales_item_code)
	  bom=frappe.db.get_value("BOM",{"item":sales_item_code,"is_default":1},"name")
	  print("item_default_bom",bom)
	  if bom is None:
	    frappe.msgprint(" Item "+sales_item_code+" does not have default BOM")
	  if bom is not None:
	    bom_item = bom_details(company ,bom)
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
	        purchase_dict = ""
	        stock_ledger_entry = get_stock_ledger_entry(item_code)
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
	          if last_purchase > 0:
	            if code.last_purchase_rate is not None:
	              last_purchase_rate = code.last_purchase_rate
	              check_last_purchase_rate = "Y"
	            if stock_valuation_price == 0.0:
	              stock_valuation_price = code.last_purchase_rate
	          elif stock_valuation_price != 0.0:
	            last_purchase_rate = stock_valuation_price
	            check_last_purchase_rate = "N" 
	          else:
	            last_purchase_rate = valuation_rate
	            check_last_purchase_rate = "N"
	            if stock_valuation_price == 0.0:
	              stock_valuation_price = valuation_rate
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
	        purchase_rate = get_sales_order_no(item_code)
	        max_purchase = purchase_rate[0]['highest_rate']
	        min_purchase = purchase_rate[0]['lowest_rate']
	        avg_purchase = purchase_rate[0]['avg_rate']
	        number_of_purchase = purchase_rate[0]['purchase_name_count']
	        if conversion_factor != 0:
	          total_avg_purchase += avg_purchase
	          total_max_purchase += max_purchase
	          total_min_purchase += min_purchase
	          total_avg_purchase = round(float(total_avg_purchase),2)
	          total_max_purchase = round(float(total_max_purchase),2)
	          total_min_purchase = round(float(total_min_purchase),2)
	          data.append([bom_name,item_group,item_code,stock_qty,stock_uom,last_purchase_rate,
						item_cost_base_on_last_purchase ,round(stock_valuation_price),round(item_cost_based_on_valuation_rate)
						])
	          
	        else:
	          frappe.throw("Please define Conversion Factor for purchase uom "+'"'+purchase_uom+'"'+ " of this "+'"'+item_code+'"'+" in Item Master and run this report again")
	          
	    get_total = get_report_total_row()
	    if get_total[0].add_total_row == 0:
	      data.append(["","","","","","","","","","","","","",""])
	      data.append(["Total","","",total_bom_qty,"",total_last_purchase_rate,total_item_cost_base_on_last_purchase
			,round(float(total_stock_valuation_price),2),round(float(total_item_cost_based_on_valuation_rate),2),"",""])
		 
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
		_("Purchase Rate Last") + "::130",
		_("RM Cost - Purchase Rate") + "::180",
		_("Current Valuation Rate") + "::130",
		_("RM Cost - Valuation Rate")+"::180"
		

	]
	
def sales_item_details(company,sales_order):
	sales_item_details = frappe.db.sql("""select si.item_code
		from `tabSales Order` so, `tabSales Order Item` si 
					where so.name = si.parent and so.docstatus = 1 and 
					so.company = '"""+company+"""' and si.parent = '"""+sales_order+"""'
					order by
						si.item_code""", as_dict=1)
	return sales_item_details

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
										`tabSales Order Item`
								where
										item_code = %s and docstatus = 1""",(item_code), as_dict=1)
	return purchase
def get_sales_order_no(item_code):
	#print "item code-------------------",item_code
	purchase_name_count = 0
	total_rate = 0.0
	lowest_rate = 0.0
	highest_rate = 0.0
	avg_rate = 0.0
	sales_order_lha = []
	sales_order = frappe.db.sql("""select 
						poi.item_code,poi.conversion_factor,poi.rate,poi.parent
					from 
						`tabSales Order Item` poi 
					where 
						poi.item_code = %s  and docstatus = 1
						""",item_code, as_dict =1)

	lowest_purchase_item_rate = frappe.db.sql("""SELECT parent,rate,item_code,conversion_factor from `tabSales Order Item`  where rate = (select min(rate) from `tabSales Order Item` where item_code = %s and docstatus =1) and item_code = %s and conversion_factor = (select max(conversion_factor) from `tabSales Order Item` where item_code = %s and docstatus =1) and docstatus =1""",(item_code,item_code,item_code), as_dict =1)

	highest_purchase_item_rate = frappe.db.sql("""SELECT parent,rate,item_code,min(conversion_factor) as conversion_factor
	from `tabSales Order Item`  
	where rate = (select max(rate) from `tabSales Order Item` where item_code = %s and docstatus =1) 
		and item_code = %s and docstatus =1""",(item_code,item_code), as_dict =1)
	if highest_purchase_item_rate:
		for highest in highest_purchase_item_rate:
			if highest.rate is not None and highest.conversion_factor is not None:
				highest_rate = highest.rate / highest.conversion_factor
	#print "highest rate -------------",highest_rate
	
	if lowest_purchase_item_rate:
		for lowest in lowest_purchase_item_rate:
			if lowest.rate is not None and lowest.conversion_factor is not None:
				lowest_rate = lowest.rate / lowest.conversion_factor
	#print "lowest_rate--------------",lowest_rate
	if sales_order:
		for purchase in sales_order:
			purchase_name_count = purchase_name_count + 1
			conversion_factor = purchase.conversion_factor
			rate = purchase.rate
			rate_with_conversion = rate / conversion_factor
			total_rate += rate_with_conversion
	if purchase_name_count > 0.0:
		avg_rate = total_rate/purchase_name_count
	highest_rate = round(float(highest_rate),2)
	lowest_rate = round(float(lowest_rate),2)
	avg_rate = round(float(avg_rate),2)
	purchase_name_count = round(float(purchase_name_count),2)
	sales_order_lha.append(
				{
				"highest_rate":highest_rate,
				"lowest_rate":lowest_rate,
				"avg_rate":avg_rate,
				"purchase_name_count":purchase_name_count
				})
	
	return sales_order_lha
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
	
	return conversion
def get_report_total_row():
	total_row_checking = frappe.db.sql("""select add_total_row from `tabReport` where report_name = 'SO Cost Report'""",as_dict =1)

	return total_row_checking

