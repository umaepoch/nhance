# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from datetime import datetime, timedelta
import datetime
class RARBWarehouse(Document):
	def on_cancel(self):
		frappe.db.set(self, "is_active", 0)

@frappe.whitelist()
def make_rarb_warehouse(source_name, target_doc=None, ignore_permissions=False):
	#print "source_name ------------",source_name
	def set_missing_values(source, target):
		target.is_pos = 0
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
#		set company address
#		target.update(get_company_address(target.company))
#		if target.company_address:
#			target.update(get_fetch_values("Documents Review Details", 'company_address', target.company_address))
#		 set the redeem loyalty points if provided via shopping cart
#		if source.loyalty_points and source.order_type == "Shopping Cart":
#			target.redeem_loyalty_points = 1
	def postprocess(source, target):
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Sales Invoice Advance
		#target.set_advances()
	doc = get_mapped_doc("Warehouse", source_name,	{
		"Warehouse": {
			"doctype": "RARB Warehouse",
			"field_map": {
				"warehouse": source_name
			},
			"validation": {
				"docstatus": ["=", 0],
			}
		}
	},  target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doc
@frappe.whitelist()
def get_higher_date(warehouse,start_date,name):
	end_date = ""
	start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
	#print "start_date----------------",start_date
	dates = frappe.db.sql("""select name,start_date from `tabRARB Warehouse` where warehouse = %s and start_date > %s and docstatus =1 order by start_date asc limit 1 """,(warehouse,start_date), as_dict = 1)
	#print "dates----------------",dates
	dates_lower = frappe.db.sql("""select name,start_date from `tabRARB Warehouse` where warehouse = %s and start_date < %s and docstatus = 1 order by start_date desc limit 1 """,(warehouse,start_date), as_dict = 1)
	#print "dates_lower---------------",dates_lower
	if dates_lower:
		for date in dates:
			end_date = start_date - timedelta(days=1)
			names = date.name
			#get_update_doc_value(names,end_date)
			frappe.db.sql("""update `tabRARB Warehouse` set end_date = '"""+ str(end_date)+"""'where name='"""+str(names)+"""'""")
	if dates:
		#end_date = []
		for date in dates:
			
			end_date = date.start_date - timedelta(days=1)
			#get_update_doc_value(name,end_date)
			frappe.db.sql("""update `tabRARB Warehouse` set end_date = '"""+ str(end_date)+"""'where name='"""+str(name)+"""'""")
			#print "end_date--------------",end_date
		#print "nearest_date------------",nearest_date
		return end_date
	else:
		
		frappe.db.sql("""update `tabRARB Warehouse` set end_date = Null where name='"""+str(name)+"""' and docstatus =1""")
		return None

@frappe.whitelist()
def get_end_foramte_date(end_date,start_date, warehouse):
	flag = False
	now = datetime.datetime.now()
	current_date =  now.strftime("%Y-%m-%d")
	
	#higher_date = get_higher_date(warehouse,start_date)
	if current_date <= end_date and current_date >= start_date:
		#print "i am coming here"
		is_active = 1
		flag = True
		#frappe.db.sql("""update `tabRARB Warehouse` set is_active = '"""+ str(is_active)+"""'where warehouse='"""+str(warehouse)+"""'""")
	else:
		#print "or i am coming here"
		is_active = 0
		flag = False
		#frappe.db.sql("""update `tabRARB Warehouse` set is_active = '"""+ str(is_active)+"""'where warehouse='"""+str(warehouse)+"""'""")
	return flag
@frappe.whitelist()
def get_next_start_date(warehouse,start_date,name):
	flag = False
	get_higher_date = ""
	now = datetime.datetime.now()
	current_date =  now.strftime("%Y-%m-%d")
	#print "current_date------------",type(current_date)
	get_higher_date = dates = frappe.db.sql("""select name,start_date from `tabRARB Warehouse` where warehouse = %s and start_date > %s and docstatus =1 order by start_date asc limit 1 """,(warehouse,start_date), as_dict = 1)
	if start_date <= current_date:
		#print "yeah date is greater then"
		is_active = 1
		flag = True
		#frappe.db.sql("""update `tabRARB Warehouse` set is_active = '"""+ str(is_active)+"""' where warehouse='"""+str(warehouse)+"""' and name = '"""+name+"""'""")
	elif start_date <= current_date and get_higher_date is None:
		flag = True
	elif start_date > current_date:
		is_active = 0
		flag = False
		#frappe.db.sql("""update `tabRARB Warehouse` set is_active = '"""+ str(is_active)+"""' where warehouse='"""+str(warehouse)+"""' and name = '"""+name+"""'""")
	#return current_date
	return flag

@frappe.whitelist()
def get_update_pre_doc(warehouse,start_date,name):
	get_is_active_update(warehouse,start_date,name)
	start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
	dates = frappe.db.sql("""select name,start_date from `tabRARB Warehouse` where warehouse = %s and start_date < %s and docstatus =1 order by start_date desc limit 1 """,(warehouse,start_date), as_dict = 1)
	dates_higher = frappe.db.sql("""select name,start_date from `tabRARB Warehouse` where warehouse = %s and start_date > %s and docstatus =1 order by start_date asc limit 1 """,(warehouse,start_date), as_dict = 1)
	#print "dates----------------",dates
	if dates_higher:
		for date in dates_higher:
			end_date = date.start_date - timedelta(days=1)
			get_update_doc_value(name,end_date)
			frappe.db.sql("""update `tabRARB Warehouse` set end_date = '"""+ str(end_date)+"""' where name='"""+str(name)+"""' and docstatus =1""")
	if dates:
		for date in dates:
			end_date = start_date - timedelta(days=1)
			names = date.name
			#get_update_doc_value(names,end_date)
			frappe.db.sql("""update `tabRARB Warehouse` set end_date = '"""+ str(end_date)+"""' where name='"""+str(names)+"""'""")
	get_is_active_update(warehouse,start_date,name)
	return dates

def get_is_active_update(warehouse,start_date,name):

	dates = frappe.db.sql("""select name,start_date,end_date from `tabRARB Warehouse` where warehouse = %s and start_date < %s and docstatus =1 order by start_date desc limit 1 """,(warehouse,start_date), as_dict = 1)
	
	now = datetime.datetime.now()
	current_date =  now.strftime("%Y-%m-%d")
	#current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d')
	for date in dates:
		names = date.name
		previous_start_date = date.start_date
		previous_end_date = date.end_date
		
		if str(previous_start_date) <= current_date and str(previous_end_date) >= current_date:
			#print "yeah date is greater then"
			is_active = 1
			#flag = True
			#print "is_active===============",is_active
			frappe.db.sql("""update `tabRARB Warehouse` set is_active = '"""+ str(is_active)+"""' where warehouse='"""+str(warehouse)+"""' and name = '"""+names+"""'""")
		else :
			is_active = 0
			#print "is_active===============",is_active
			#flag = False
			frappe.db.sql("""update `tabRARB Warehouse` set is_active = '"""+ str(is_active)+"""' where warehouse='"""+str(warehouse)+"""' and name = '"""+names+"""'""")
	return True
@frappe.whitelist()
def get_update_doc(name,end_date):
	doc = frappe.get_doc("RARB Warehouse" , name)
	modified = doc.modified
	doc.update({
		"modified":modified,
		"end_date":end_date	
		})
	doc.save()
	return True
@frappe.whitelist()
def get_update_is_active(name,is_active):
	doc = frappe.get_doc("RARB Warehouse" , name)
	modified = doc.modified
	doc.update({
		   "modified":modified,
		   "is_active":is_active
		})
	doc.save()
	return True
@frappe.whitelist()
def get_update_doc_value(name,end_date):
	doc = frappe.get_doc("RARB Warehouse" , name)
	modified = doc.modified
	doc.update({
		"modified":modified,
		"end_date":end_date	
		})
	frappe.db.commit()
	return True

# //For Stock Entry Detail's custom field RARB Location (Source Warehouse) and RARB Location (Target Warehouse) .....
@frappe.whitelist()
def get_rarb_warehouse(warehouse):
	rarb_warehouse = frappe.db.sql("""select warehouse from `tabRARB Warehouse` where warehouse = '"""+warehouse+"""' and is_active =1 and docstatus =1""", as_dict =1)
	#print "rarb_warehouse------------",rarb_warehouse
	if rarb_warehouse:
		return rarb_warehouse
	else:
		return None
@frappe.whitelist()
def get_rarb_warehouse_item_name(warehouse):
	rarb_id = frappe.db.sql("""select ri.rarb_id,ri.name from `tabRARB Warehouse Item` ri , `tabRARB Warehouse` r where r.warehouse = '"""+warehouse+"""' and ri.rarb_active = "Yes" and r.name = ri.parent and r.docstatus =1 and r.is_active =1 order by ri.rarb_id asc""", as_dict=1)
	
	return rarb_id
@frappe.whitelist()
def get_rarb_items_detail(warehouse,pch_rarb_location_src):
	rarb_items = frappe.db.sql("""select ri.rarb_item  from `tabRARB Warehouse Item` ri, `tabRARB Warehouse` r where r.warehouse = '"""+warehouse+"""' and r.name = ri.parent and r.is_active =1 and ri.rarb_id = '"""+pch_rarb_location_src+"""'""", as_dict =1)
	return rarb_items
