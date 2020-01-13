# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from datetime import datetime, timedelta
import datetime
import json
from frappe import _
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

@frappe.whitelist()
def create_rarb_id(name, warehouse,rarbs):
	rarbs = json.loads(rarbs)
	outerJson_Transfer = []
	'''
	rarb_id = frappe.db.sql("""select warehouse,rarb_id from `tabRARB ID` where warehouse =%s""",warehouse, as_dict=1)
	if rarb_id:
		for rarb in rarb_id:
			for ids in rarbs:
				if rarb.rarb_id == ids['rarb_id']:
					frappe.db.set_value("RARB ID", rarb['rarb_id'], "is_active", 1)
				else:
					frappe.db.set_value("RARB ID", rarb['rarb_id'], "is_active", 0)
	else:
		for rarb in rarbs:
			rarb_id = rarb['rarb_id']
			outerJson_Transfer = {
				"doctype": "RARB ID",
				"owner": "Administrator",
				"docstatus": 0,
				"rarb_id":rarb['rarb_id'],
				"warehouse":warehouse,
				"is_active": 1
			}
			doc = frappe.new_doc("RARB ID")
			doc.update(outerJson_Transfer)
			doc.save()
			doc.submit()
			frappe.msgprint("RARB ID has been created for "+doc.name)
	'''
	for rarb in rarbs:
		rarb_id = frappe.db.sql("""select rarb_id from `tabRARB ID` where rarb_id =%s""",rarb['rarb_id'], as_dict=1)
		if rarb_id:
			pass
		else:
			rarb_id = rarb['rarb_id']
			outerJson_Transfer = {
				"doctype": "RARB ID",
				"owner": "Administrator",
				"docstatus": 0,
				"rarb_id":rarb['rarb_id']
			}
			doc = frappe.new_doc("RARB ID")
			doc.update(outerJson_Transfer)
			doc.save()
			frappe.msgprint("RARB ID has been created for "+doc.name)
@frappe.whitelist()
def set_rarb_location(stock,data):
	voucher_no = stock.voucher_no
	voucher_type = stock.voucher_type
	voucher_detail_no = stock.voucher_detail_no
	item_code = stock.item_code
	warehouse = stock.warehouse
	trg_rarb_locations = ""
	src_rarb_locations = ""
	if voucher_type == "Stock Entry":
		
		trg_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_trg as rarb_id_trg, sti.qty as t_qty
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.t_warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src, sti.qty as s_qty
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.s_warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Purchase Invoice":
	
		trg_rarb_locations = frappe.db.sql("""
						select
							sti.pch_rarb_location_trg as rarb_id_trg, sti.qty as t_qty
						from 
							`tabPurchase Invoice` st ,`tabPurchase Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s  and 
							sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Purchase Receipt":
	
		trg_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_trg as rarb_id_trg, sti.qty as t_qty
						from 
							`tabPurchase Receipt` st ,`tabPurchase Receipt Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
		
		
	elif voucher_type == "Sales Invoice":
	
		src_rarb_locations = frappe.db.sql("""
						select
							sti.pch_rarb_location_src as rarb_id_src, sti.qty as s_qty
						from 
							`tabSales Invoice` st ,`tabSales Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Delivery Note":
	
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src, sti.qty as s_qty
						from 
							`tabDelivery Note` st ,`tabDelivery Note Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Stock Reconciliation":
		
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src, sti.qty as s_qty
						from 
							`tabStock Reconciliation` st ,`tabStock Reconciliation Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1""", as_dict =1)
	total = 0.0
	if src_rarb_locations:
		
		frappe.db.set_value("Stock Ledger Entry", stock.name, "rarb_location", src_rarb_locations[0].rarb_id_src)
		
	if trg_rarb_locations:
		frappe.db.set_value("Stock Ledger Entry", stock.name, "rarb_location", trg_rarb_locations[0].rarb_id_trg)
		
def check_available_qty(stock,data):
	voucher_no = stock.voucher_no
	voucher_type = stock.voucher_type
	voucher_detail_no = stock.voucher_detail_no
	item_code = stock.item_code
	warehouse = stock.warehouse
	src_rarb_locations = ""
	if voucher_type == "Stock Entry":
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src, sti.transfer_qty as s_qty
						from 
							`tabStock Entry` st ,`tabStock Entry Detail` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1
							and sti.s_warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Sales Invoice":
	
		src_rarb_locations = frappe.db.sql("""
						select
							sti.pch_rarb_location_src as rarb_id_src, sti.stock_qty as s_qty
						from 
							`tabSales Invoice` st ,`tabSales Invoice Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	elif voucher_type == "Delivery Note":
	
		src_rarb_locations = frappe.db.sql("""
						select 
							sti.pch_rarb_location_src as rarb_id_src, sti.stock_qty as s_qty
						from 
							`tabDelivery Note` st ,`tabDelivery Note Item` sti 
						where 
							st.name = '"""+voucher_no+"""' and st.name = sti.parent and 
							sti.item_code = '"""+item_code+"""' and  st.docstatus = 1 and 
							sti.warehouse = %s 
							and sti.name = '"""+voucher_detail_no+"""'
							""",(warehouse), as_dict =1)
	if src_rarb_locations:
		creation = str(stock.posting_date)+" "+str(stock.posting_time)
		stock_ledger = frappe.db.sql("""select 
							* 
						from 
							`tabStock Ledger Entry` 
						where 
							warehouse = %s and item_code = %s and rarb_location = %s and docstatus = 1 
							and creation <= %s""",
							(warehouse,item_code,src_rarb_locations[0].rarb_id_src,creation), as_dict=1)
		target_qty = 0.0
		source_qty = 0.0
		bal_qty = 0.0
		for led in stock_ledger:
			if led.voucher_type == "Purchase Invoice":
				target_qty += led.actual_qty
				bal_qty = target_qty - source_qty
			elif led.voucher_type == "Purchase Receipt":
				target_qty += led.actual_qty
				bal_qty = target_qty - source_qty
			elif led.voucher_type == "Stock Entry":
				stock_entry_datails = frappe.get_list("Stock Entry Detail", filters={'parent': led.voucher_no,'t_warehouse': led.warehouse, 'item_code': led.item_code, 'pch_rarb_location_trg': src_rarb_locations[0].rarb_id_src }, fields=['transfer_qty'])
				if stock_entry_datails:
					target_qty += stock_entry_datails[0].transfer_qty
					bal_qty = target_qty - source_qty

				stock_entry_datails = frappe.get_list("Stock Entry Detail", filters={'parent': led.voucher_no,'s_warehouse': led.warehouse, 'item_code': led.item_code, 'pch_rarb_location_src': src_rarb_locations[0].rarb_id_src }, fields=['transfer_qty'])
				if stock_entry_datails:
					source_qty += stock_entry_datails[0].transfer_qty
					bal_qty = target_qty - source_qty
			elif led.voucher_type == "Sales Invoice":
				source_qty -= led.actual_qty
				bal_qty = target_qty - source_qty
			elif led.voucher_type == "Delivery Note":
				source_qty -= led.actual_qty
				bal_qty = target_qty - source_qty
			elif led.voucher_type == "Stock Reconciliation":
				bal_qty = led.qty_after_transaction
				target_qty = led.qty_after_transaction
				target_qty += source_qty
		if bal_qty < src_rarb_locations[0].s_qty:
			frappe.throw(_("The Quantity is not available for "+frappe.bold(stock.item_code)+" at RARB Location "+frappe.bold(src_rarb_locations[0].rarb_id_src)+",Please use the currect RARB Location and try again..")+ '<br><br>' + _("Available qty is {0} {1}, you need {2} {3}").format(frappe.bold(bal_qty),frappe.bold(stock.stock_uom),frappe.bold(str(src_rarb_locations[0].s_qty)),frappe.bold(stock.stock_uom)), title=_('Insufficient Stock in RARB Warehouse'))

@frappe.whitelist()
def set_is_active(name,cur_date_py,docstatus):
	if int(cur_date_py) == 1:
		if int(docstatus) == 1:
			frappe.db.set_value("RARB Warehouse", name, "is_active", 1)
			frappe.db.commit()
		elif int(docstatus) == 2:
			frappe.db.set_value("RARB Warehouse", name, "is_active", 0)
			frappe.db.commit()
	elif int(cur_date_py) == 0:
		frappe.db.set_value("RARB Warehouse", name, "is_active", 0)
		frappe.db.commit()
