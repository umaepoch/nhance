# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
import time
import math
import json
import ast
import sys


def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []
	serial_no = filters.get("item_serial_no")
	delivery_note=filters.get("delivery_note")
	columns = get_columns()
	serial_no_details = fetching_serial_no_details(filters)

	
	for serial_data in serial_no_details:
		item_code = serial_data['item_code'],
		item_name = serial_data['item_name'],
		serial_no=serial_data['serial_no'],
		coc=serial_data['pch1_coc'],
		pressure_test=serial_data['pch1_pressure_test'],
		build_sheet=serial_data['pch1_build_sheet'],
		combined_pdf=serial_data['pch1_combined_pdf']
		supplier=serial_data[''],
		company=serial_data[''],
		customer=serial_data['customer'],
		purchase_document_no=serial_data['po_no'],
		purchase_date=serial_data['po_date'],
		delivery_document_no=serial_data['delivery_document_no'],
		delivery_date=serial_data['delivery_date'],
		
		data.append([serial_data['item_code'],serial_data['item_name'],serial_data['serial_no'],serial_data['pch1_coc'], serial_data['pch1_pressure_test'],serial_data['pch1_build_sheet'],serial_data['pch1_combined_pdf'],serial_data[''],serial_data[''],serial_data['customer'],serial_data['po_no'],serial_data['po_date'],serial_data['delivery_document_no'],serial_data['delivery_date']
					])
			 					     					    	
	
			 					     					   
	return columns, data


		

def fetching_serial_no_details(filters):
        condition = ''
        value = ()
	if filters.get("customer_po"):
                condition = "where dn.po_no=%s"
                value = (filters["customer_po"],)
		#print "condition",condition
		user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
		#print "user",user
		for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
		#print "for_value",for_value
		if for_value!=():
			for_value_user=for_value[0][0]
			if for_value_user==user:
				#print "for_value_user",for_value_user
				condition ="""where dn.po_no=%s and sn.customer='"""+for_value_user+"""' """
				serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition}  and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note"  and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)
		else:
			serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition} and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)

        elif filters.get("item_code"):
                condition = "where sn.item_code=%s"
                value = (filters["item_code"],)
		#print "condition",condition
		user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
		#print "user",user
		for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
		#print "for_value",for_value
		if for_value!=():
			for_value_user=for_value[0][0]
			if for_value_user==user:
				#print "for_value_user",for_value_user
				condition ="""where sn.item_code=%s and sn.customer='"""+for_value_user+"""' """
				serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition}  and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note"  and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)
		else:
			serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition} and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)

	elif filters.get("item_serial_no"):
                condition = "where sn.serial_no=%s"
                value = (filters["item_serial_no"],)
		#print "condition",condition
		user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
		#print "user",user
		for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
		#print "for_value",for_value
		if for_value!=():
			for_value_user=for_value[0][0]
			if for_value_user==user:
				#print "for_value_user",for_value_user
				condition ="""where sn.serial_no=%s and sn.customer='"""+for_value_user+"""' """
				serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition}  and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note"  and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)
		else:
			serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition} and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)

	elif filters.get("delivery_note"):
		user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
		#print "user",user
                condition = "where delivery_document_no=%s"
                value = (filters["delivery_note"],)
		#print "condition",condition
		serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn {condition} and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and   sn.delivery_document_no=dn.name  """.format(condition=condition),value, as_dict=1)

	elif filters.get("sales_order_acknowleggement"):
                condition = "where dni.against_sales_order=%s"
                value = (filters["sales_order_acknowleggement"],)
		#print "condition",condition
		#print "value",value
		user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
		#print "user",user
		for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
		#print "for_value",for_value
		if for_value!=():
			for_value_user=for_value[0][0]
			if for_value_user==user:
				#print "for_value_user",for_value_user
				condition ="""where dni.against_sales_order=%s and sn.customer='"""+for_value_user+"""' """
				serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn,`tabDelivery Note Item` dni  {condition}  and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note"  and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)
		else:
			serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn ,`tabDelivery Note Item` dni {condition} and sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and sn.delivery_document_no=dn.name   """.format(condition=condition),value, as_dict=1)

	else:
		user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
		#print "user",user
		for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
		#print "for_value",for_value
		if for_value!=():
			for_value_user=for_value[0][0]
			if for_value_user==user:
        			serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn  where sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and sn.delivery_document_no=dn.name and sn.customer='"""+for_value_user+"""' """, as_dict=1)
		else:
			serial_details = frappe.db.sql("""select sn.pch1_coc,sn.pch1_pressure_test,sn.pch1_build_sheet,sn.pch1_combined_pdf,"","",sn.customer,dn.po_no,dn.po_date,sn.delivery_document_no,sn.delivery_date,sn.item_code,sn.item_name,sn.serial_no
			from 
				`tabSerial No` sn ,`tabDelivery Note` dn  where sn.delivery_document_type!="Null" and sn.delivery_document_type="Delivery Note" and sn.delivery_document_no=dn.name  """, as_dict=1)
		
        return serial_details


@frappe.whitelist()
def get_delivery_document_no():
	user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
	print "user",user
	for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
	print "for_value",for_value
	if for_value!=():
		for_value_user=for_value[0][0]
		if for_value_user==user:
			delivery_no = frappe.db.sql("""select distinct(delivery_document_no) from `tabSerial No` where delivery_document_type="Delivery Note" and customer='"""+for_value_user+"""' """, as_dict=1)
	else:
		delivery_no = frappe.db.sql("""select distinct(delivery_document_no) from `tabSerial No` where delivery_document_type="Delivery Note" """, as_dict=1)
	
	
	return delivery_no

@frappe.whitelist()
def get_item_code():
	user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
	print "user",user
	for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
	print "for_value",for_value
	if for_value!=():
		for_value_user=for_value[0][0]
		if for_value_user==user:
			item_code = frappe.db.sql("""select distinct(item_code) from `tabSerial No` where delivery_document_type="Delivery Note" and delivery_document_type!="Null" and customer='"""+for_value_user+"""' """, as_dict=1)
	else:
		item_code = frappe.db.sql("""select distinct(item_code) from `tabSerial No` where delivery_document_type="Delivery Note" and delivery_document_type!="Null" """, as_dict=1)
	
	
	return item_code

@frappe.whitelist()
def get_item_serial_no():
	user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
	print "user",user
	for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
	print "for_value",for_value
	if for_value!=():
		for_value_user=for_value[0][0]
		if for_value_user==user:
			serial_no = frappe.db.sql("""select distinct(name) from `tabSerial No` where delivery_document_type="Delivery Note" and delivery_document_type!="Null" and customer='"""+for_value_user+"""' """, as_dict=1)
	else:
		serial_no = frappe.db.sql("""select distinct(name) from `tabSerial No` where delivery_document_type="Delivery Note" and delivery_document_type!="Null" """, as_dict=1)
	
	
	return serial_no

@frappe.whitelist()
def get_sales_order_no():
	user=frappe.db.get_value("User",{"name":frappe.session.user},"full_name")
	#print "user",user
	for_value = frappe.db.sql("""select for_value from `tabUser Permission` where for_value='"""+user+"""' """)
	#print "for_value",for_value
	if for_value!=():
		for_value_user=for_value[0][0]
		if for_value_user==user:
			sales_order_no = frappe.db.sql("""select dni.against_sales_order from `tabDelivery Note Item` dni, `tabSerial No` sn,`tabDelivery Note` dn where sn.delivery_document_type="Delivery Note" and sn.delivery_document_type!="Null" and  sn.delivery_document_no=dni.parent and dn.name=sn.delivery_document_no and dni.against_sales_order!="Null" and customer='"""+for_value_user+"""' """, as_dict=1)
			#print "sales_order_no",sales_order_no
	else:
		sales_order_no = frappe.db.sql("""select dni.against_sales_order from `tabDelivery Note Item` dni, `tabSerial No` sn,`tabDelivery Note` dn where sn.delivery_document_type="Delivery Note" and sn.delivery_document_type!="Null" and  sn.delivery_document_no=dni.parent and dn.name=sn.delivery_document_no and dni.against_sales_order!="Null" """, as_dict=1)
		#print "sales_order_no",sales_order_no
	
	return sales_order_no

def get_columns():
	"""return columns"""
	columns = [
		_("Item Code")+"::100",
		_("Item Name")+"::100",
		_("Item Serial No")+":Link/Serial No:100",
		_("CoC")+"::100",
		_("Pressure Test")+"::100",
		_("Assembly build sheet")+"::100",
		_("Combined Pdf")+"::100",
		_("DNV-GL Product Certification")+"::100",
		_("CE Approval")+"::100",
		_("Customer Name")+"::100",
		_("Customer PO")+"::100",
		_("Date (customer PO)")+"::100",
		_("Delivery Note ")+":Link/Delivery Note:100",
		_("Date ( Delivery note)")+"::100",
		
		 ]
	return columns
