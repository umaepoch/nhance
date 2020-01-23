# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import datetime

class PickList(Document):
	pass

@frappe.whitelist()
def get_name(parent,item):
	name = frappe.db.sql("""select name from `tabPick List` where parent = '"""+parent+"""' and item = '"""+item+"""'""",as_dict=1)
	return name
@frappe.whitelist()
def get_batch_name(item_code):
	now = datetime.datetime.now()
	current_date =  now.strftime("%Y-%m-%d")
	get_item_expiry = frappe.db.sql("""select has_expiry_date from `tabItem` where name = %s""",item_code,as_dict=1)
	has_expiry = get_item_expiry[0].has_expiry_date
	batch_details = ""
	#print "has_expiry--------------",has_expiry
	if has_expiry == 1:
		batch_details = frappe.db.sql("""select name from `tabBatch` where item = '"""+item_code+"""' and expiry_date >= '"""+current_date+"""' order by expiry_date,creation asc limit 1""",as_dict=1)
	
	elif has_expiry == 0:
		batch_details = frappe.db.sql("""select name,expiry_date from `tabBatch` where item = %s  order by  creation desc limit 1""",item_code,as_dict=1)
	
	return batch_details
@frappe.whitelist()
def get_qty_available(item_code,warehouse):
	item_details = frappe.db.sql("""select actual_qty from `tabBin` where warehouse = '"""+warehouse+"""' and item_code = '"""+item_code+"""'""",as_dict=1)

	return item_details
@frappe.whitelist()
def get_serial_no(s_warehouse,batch,item_code,qty):
	qty = float(qty)
	#print "qty----------------",type(qty)
	qty = int(qty)
	#serial_no = frappe.db.sql("""select name from `tabSerial No` where warehouse = '"""+s_warehouse+"""' and item_code = '"""+item_code+"""' and batch = '"""+batch+"""' order by name asc limit %s""",qty,as_dict=1)4
	serial_no = frappe.db.sql("""select name from `tabSerial No` where warehouse =%s and item_code =%s and batch_no =%s order by creation asc limit %s""",(s_warehouse,item_code,batch,qty),as_dict=1)
	#print "serial_no---------------",serial_no
	return serial_no
@frappe.whitelist()
def get_rarb_warehouses(warehouse):
	rarb_warehouse = frappe.db.sql("""select warehouse from `tabRARB Warehouse` where warehouse = '"""+warehouse+"""' and is_active =1 and docstatus =1""", as_dict =1)
	#print "rarb_warehouse------------",rarb_warehouse
	if rarb_warehouse:
		return rarb_warehouse
	else:
		return None
