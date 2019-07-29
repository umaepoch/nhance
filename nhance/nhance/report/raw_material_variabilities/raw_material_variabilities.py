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
	global prepare_report_data
	global company
	bom_type = ""
	new_bom_list=[]
	old_bom_list=[]
	new_bom_items = []
	old_bom_items = []
	company = filters.get("company")
	new_bom = filters.get("new_bom")
	old_bom = filters.get("old_bom")
	warehouse = filters.get("stock_warehouse")
	if new_bom:
		bom_type = "new"
		new_bom_items = get_exploded_bom_entries(filters, bom_type)
	if old_bom:
		bom_type = "old"
		old_bom_items = get_exploded_bom_entries(filters, bom_type)
		#print "old_bom_items--------------------", old_bom_items
	if len(new_bom_items) !=0:
		for items in new_bom_items:
			item_code = items['item_code']
			qty = items['bi_qty']
			old =0
			#print "item_code",item_code
			#print "item_code",qty
			details = {"item_code":item_code,"new_qty":qty,"old_qty":old}
			new_bom_list.append(details)
	if len(old_bom_items) !=0:
		old_bom_item_qty = 0
		for items in old_bom_items:
			item_code = items['item_code']
			qty = 0
			old_bom_item_qty =items['bi_qty']
			#print "item_code--",item_code
			#print "old_bom_item_qty--",old_bom_item_qty
			details = {"item_code":item_code,"new_qty":qty,"old_qty":old_bom_item_qty}
			old_bom_list.append(details)
			
	items_data = get_merge_bom_list(new_bom_list,old_bom_list)
	#print "items_data---------", items_data
	report_items_details = get_report_items(items_data,new_bom_items,old_bom_items,warehouse)
	prepare_report_data = []
	#print "ItemDetail",report_items_details
	for items in report_items_details:
		item_code = items['item_code']
		old_qty = items['old_qty']
		new_qty = items['new_qty']
		excees_qty = items['excees_qty']
		stock_qty = items['stock_qty']
		delta_qty=items['delta_qty']	
		prepare_report_data.append([ item_code, old_qty, new_qty, excees_qty, stock_qty, delta_qty])
	
	columns = get_columns()
	#print "DaTA----",prepare_report_data
	return columns, prepare_report_data

def get_columns():
		"""return columns"""
		columns = [
		_("Item")+":Link/Item:100",
		_("Old BOM Item Qty")+"::150",
		_("New BOM Item Qty")+"::140",
		_("Excess Qty")+"::100",
		_("Stock Qty")+"::100",
		_("Delta Qty")+"::100"
		 ]
		return columns

def get_merge_bom_list(new_bom_list,old_bom_list):
	after_merge=new_bom_list+old_bom_list
	item_data=[]
	for new in range(0,len(after_merge)):
		#print "new---", new
		for old in range(new,len(after_merge)):
			#print "new value ",after_merge[new]['item_code']
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
				new_qty=new_bom_items[new]['bi_qty']
		for old in range(0,len(old_bom_items)):
			old_item_code = old_bom_items[old]['item_code']
			if str(data) == str(old_item_code):
				old_qty = old_bom_items[old]['bi_qty']
				#print "old_qty---------", old_qty
		
		excees_qty = old_qty - new_qty
		item_code = data
		stock_qty = get_stock(item_code, warehouse)
		delta_qty = stock_qty - new_qty
		details = {"item_code":data,"new_qty":new_qty,"old_qty":old_qty,"excees_qty":excees_qty,"stock_qty":stock_qty,"delta_qty":delta_qty}
		data_for_report.append(details)
		new_qty=0
		old_qty=0
		excess_qty=0
		stock_qt=0
		delta_qty=0
	return data_for_report

def get_stock(item_code, warehouse):
	item_stock = get_balance_qty_from_sle(item_code, warehouse)
	return item_stock

def get_exploded_bom_entries(filters, bom_type):
	if bom_type == "old":
		conditions = get_conditions_for_old_bom(filters)
	if bom_type == "new":
		conditions = get_conditions_for_new_bom(filters)
	#print "---------conditions::", conditions
	return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as qty, bo.project, bi.item_code, bi.stock_qty as bi_qty from `tabBOM` bo, `tabBOM Explosion Item` bi where bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1" %s order by bo.name, bi.item_code""" % conditions, as_dict=1)

def get_conditions_for_old_bom(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and bo.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)

	if filters.get("old_bom"):
		conditions += " and bi.parent = '%s'" % frappe.db.escape(filters.get("old_bom"), percent=False)
	return conditions

def get_conditions_for_new_bom(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and bo.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)

	if filters.get("new_bom"):
		conditions += " and bi.parent = '%s'" % frappe.db.escape(filters.get("new_bom"), percent=False)
	return conditions

@frappe.whitelist()
def get_sreq_items_list(requested_by,item_code):
	total_qty = 0
	items_data = {}
	items_list = []
	sreqID = frappe.db.sql("""select name from `tabStock Requisition` where requested_by = %s """, (requested_by), as_dict=1)
	if len(sreqID)!=0:
		for stockReqID in sreqID:
			if stockReqID['name'] is not None:
				parent = stockReqID['name']
				#print "parent-------", parent
				details = frappe.db.sql("""select item_code,qty from `tabStock Requisition Item` where parent = %s and 								item_code=%s""", (parent,item_code), as_dict=1)
				#print "length of details------", len(details)
				for rows in details:
					item_code = rows['item_code']
					qty = rows['qty']
					total_qty = float(total_qty) + float(qty)
	return total_qty

@frappe.whitelist()
def get_report_data():
	report_data = []
	details = {}
	for rows in prepare_report_data:
		item_code = rows[0]
		old_qty = rows[1]
		new_qty = rows[2]
		excees_qty = rows[3]
		stock_qty=rows[4];
		details = {"item_code":item_code,"old_qty":old_qty,"new_qty":new_qty,"excees_qty":excees_qty,"stock_qty":stock_qty}
		report_data.append(details)
	return report_data

@frappe.whitelist()
def make_stock_requisition(stockRequisitionItemsList, materialRequestType, workflow_status, reference_no):
	raw_material_list = json.loads(stockRequisitionItemsList)
	items_List = json.dumps(raw_material_list)
	items_List = ast.literal_eval(items_List)
	required_date = datetime.datetime.now()
	return_doc = ""
	innerJson_transfer = " "
	OuterJson_Transfer = {
	"company": company,
	"doctype": "Stock Requisition",
	"items": [
	]
	}

	if materialRequestType == "Purchase":
		OuterJson_Transfer["title"] = "Purchase"
		OuterJson_Transfer["requested_by"] = reference_no
		OuterJson_Transfer["workflow_state"] = workflow_status
		OuterJson_Transfer["material_request_type"] = "Purchase"
	elif materialRequestType == "Issue":
		OuterJson_Transfer["title"] = "Material Issue"
		OuterJson_Transfer["requested_by"] = reference_no
		OuterJson_Transfer["material_request_type"] = "Material Issue"

	for data in items_List:
		item_code = data['item_code']
		qty = data['qty']
		target_warehouse = data['warehouse']
		innerJson_transfer = {
			"doctype": "Stock Requisition Item",
			"item_code": item_code,
			"qty": qty,
			"schedule_date": required_date,
			"warehouse":target_warehouse
		}
		OuterJson_Transfer["items"].append(innerJson_transfer)
	doc = frappe.new_doc("Stock Requisition")
	doc.update(OuterJson_Transfer)
	if materialRequestType == "Purchase":
		if workflow_status == "Approved":
			doc.submit()
		else:
			doc.save()
	else:
		if workflow_status == "Approved":
			doc.submit()
		else:
			doc.save()
	return_doc = doc.doctype
	if return_doc:
		return return_doc
