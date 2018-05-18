# Copyright (c) 2013, Epoch and contributors
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
	global data
	global company
	new_bom_list=[]
	old_bom_list=[]
	company = filters.get("company")
	new_bom = filters.get("new_bom")
	old_bom = filters.get("old_bom")
	warehouse = filters.get("stock_warehouse")
	new_bom_items=get_new_bom_value(new_bom);
	old_bom_items=get_old_bom_value(old_bom);

	if len(new_bom_items) !=0:
		for items in new_bom_items:
			item_code = items['item_code']
			qty = items['qty']
			old =0
			print "item_code",item_code
			print "item_code",qty
			details = {"item_code":item_code,"new_qty":qty,"old_qty":old}
			new_bom_list.append(details)
	if len(old_bom_items) !=0:
		for items in old_bom_items:
			item_code = items['item_code']
			qty = 0
			old =items['qty']
			print "item_code",item_code
			print "item_code",qty
			details = {"item_code":item_code,"new_qty":qty,"old_qty":old}
			old_bom_list.append(details)
			
	items_data=get_merge_bom_list(new_bom_list,old_bom_list);
	report_items_details=get_report_items(items_data,new_bom_items,old_bom_items,warehouse)
	data = []
	print "ItemDetail",report_items_details
	for items in report_items_details:
		item_code = items['item_code']
		old_qty = items['old_qty']
		new_qty = items['new_qty']
		excees_qty = items['excees_qty']
		stock_qty = items['stock_qty']
		delta_qty=items['delta_qty']	
		data.append([				
			    	item_code,
				old_qty,
				new_qty,
				excees_qty,
				stock_qty,
				delta_qty
				])
	
	
	columns = get_columns()
	print "DaTA----",data
	return columns, data

def get_columns():
		"""return columns"""
		columns = [
		_("Item")+":Link/Item:100",
		_("Old Qty")+"::150",
		_("New Qty")+"::140",
		_("Excess Qty")+"::100",
		_("Stock Qty")+"::100",
		_("Delta Qty")+"::100"
		 ]
		return columns


def get_new_bom_value(new_bom):
	new_bom_value = frappe.db.sql("""select item_code,qty from `tabBOM Item` where parent=%s and docstatus=1""",(new_bom),as_dict=1)
	print "new_bom_value----------------",new_bom_value
	return new_bom_value


def get_old_bom_value(old_bom):
	old_bom_value = frappe.db.sql("""select item_code,qty from `tabBOM Item` where parent=%s and docstatus=1""",(old_bom),as_dict=1)
	print "old_bom_value----------------",old_bom_value
	return old_bom_value

def get_merge_bom_list(new_bom_list,old_bom_list):
	after_merge=new_bom_list+old_bom_list
	item_data=[]
	for new in range(0,len(after_merge)):
		print "new---",new
		for old in range(new,len(after_merge)):
			print "new value ",after_merge[new]['item_code']
			new_item_code=after_merge[new]['item_code']
			old_item_code=after_merge[old]['item_code']
			new_qty=after_merge[new]['new_qty']
			old_qty=after_merge[old]['old_qty']
			new_old_qty=after_merge[new]['old_qty']
			if new_item_code  not in item_data:
				item_data.append(new_item_code)
				break;	
				
	return item_data		
		
def get_report_items(items_data,new_bom_items,old_bom_items,warehouse):
	new_qty=0
	old_qty=0
	excess_qty=0
	stock_qty=0
	data_for_report=[]	
	for data in items_data:
		for new in range(0,len(new_bom_items)):
			new_item_code=new_bom_items[new]['item_code']
			if data==new_item_code:
				new_qty=new_bom_items[new]['qty']
		for old in range(0,len(old_bom_items)):
			old_item_code=old_bom_items[old]['item_code']
			if data==old_item_code:
				old_qty=old_bom_items[old]['qty']
		
		excees_qty=old_qty-new_qty
		#query for quantity accordind to warehouse value
		stock_qty= frappe.db.sql("""select qty  from `tabStock Entry Detail` where item_code=%s and t_warehouse=%s""", 					(data,warehouse), as_dict=1)
		if len(stock_qty) !=0:
			stock_qty = stock_qty[0]['qty']
		else:
			stock_qty=0
		delta_qty=stock_qty-new_qty

		details = {"item_code":data,"new_qty":new_qty,"old_qty":old_qty,"excees_qty":excees_qty,"stock_qty":stock_qty,"delta_qty":delta_qty}
		data_for_report.append(details)
		new_qty=0
		old_qty=0
		excess_qty=0
		stock_qt=0
		delta_qty=0
	return data_for_report

@frappe.whitelist()
def get_report_data():
	report_data = []
	details = {}
	for rows in data:
		item_code = rows[0]
		old_qty = rows[1]
		new_qty = rows[2]
		excees_qty = rows[3]
		stock_qty=rows[4];
		details = {"item_code":item_code,"old_qty":old_qty,"new_qty":new_qty,"excees_qty":excees_qty,"stock_qty":stock_qty}
		report_data.append(details)
	return report_data

		
@frappe.whitelist()
def make_material_issue(material_items_list):
	raw_material_list = json.loads(material_items_list)
	items_List = json.dumps(raw_material_list)
	items_List = ast.literal_eval(items_List)
	required_date = datetime.datetime.now()
	return_doc = ""
	innerJson_transfer = " "
	OuterJson_Transfer = {
	"company": company,
	"doctype": "Stock Requisition",
	"title": "Material Issue",
	"material_request_type": "Material Issue",
	"items": [
	]
	}

	for data in items_List:
		item_code = data['item_code']
		qty = data['qty']
		target_warehouse = data['warehouse']
		innerJson_transfer = {
			"doctype": "Stock Requisition Item",
			"item_code": item_code,
			"qty": qty,
			"schedule_date": required_date,
			"warehouse":target_warehouse,
		}
		OuterJson_Transfer["items"].append(innerJson_transfer)
	doc = frappe.new_doc("Stock Requisition")
	doc.update(OuterJson_Transfer)
	doc.save()
	return_doc = doc.doctype
	if return_doc:
		return return_doc
