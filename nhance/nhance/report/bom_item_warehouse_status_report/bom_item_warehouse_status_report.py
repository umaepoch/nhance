# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime,comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from datetime import datetime
import time
import json
import math
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	global bom
	global summ_data
	columns = get_columns()
	requested_by = filters.get("docIds")
	if filters.get("for") == "Project":
		requested_by = filters.get("master_bom_hidden")
	items_data = get_items_data(requested_by)
	data = []
	summ_data = []
	if len(items_data)!=0:
		for items in items_data:
			data.append([
				items['purchase_order'],
				items['item_code'],
				items['total_qty'],
				items['received_qty'],
				items['pending_qty'],
				items['expected_delivery_date'],
				items['updated_delivery_date']
				  ])	
	for rows in data:
		summ_data.append([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6]])

	return columns, summ_data

def get_columns():
		"""return columns"""
		columns = [
		 _("PO")+":Link/Item:100",
		_("Item")+":Link/Item:100",
		_("Quantities Ordered")+"::100",
		_("Quantities Delivered")+"::140",
		_("Quantities Yet To Be Delivered")+"::100",
		_("Expected Delivery Date")+"::100",
		_("Updated Delivery Date")+"::100"
		 ]
		return columns

@frappe.whitelist()
def fetch_Records(docName):
	records = []
	if docName == "Sales Order":
		records = frappe.db.sql("""select name from `tab"""+ docName +"""` where docstatus = 1 and status<>'Cancelled'""")
		#print "##########-Doc Records::", records
	elif docName == "Project":
		records = frappe.db.sql("""select name from `tab"""+ docName +"""` where status not in('Completed','Cancelled')""")
		#print "##########-Doc Records::", records 
	elif docName == "BOM":
		records = frappe.db.sql("""select name  from `tabBOM` where docstatus=1""");
	return records

def get_items_data(requested_by):
	print "#####-requested_by::", requested_by
	items_details = []
	if requested_by != "null":
		records = frappe.db.sql("""select name,po_list from `tabStock Requisition` where requested_by =%s and docstatus=1""", (requested_by), as_dict=1)
		#print "####-records::", records
		if len(records)!=0:
			check_flag = False
			for name in records:
				stock_requistion_id = name['name']
				po = name['po_list']
				print "------po_list::", po
				if po is not None and po is not "" and po != 'NULL':
					check_flag = True
					splitted_po = po.split(",")
					if len(splitted_po)!=0:
						for po in splitted_po:
							print "------splitted_po's::", po
							po_items = get_po_items(po)
							for po_items_data in po_items:
								po_items_data['purchase_order'] = po
								items_details.append(po_items_data)
			if check_flag is not True:
				frappe.msgprint("There is no Purchase Order For "+requested_by)
		else:
			frappe.msgprint("Records Not Found For "+requested_by)
	else:
		frappe.msgprint("Master BOM Not Found In The Project..")
	return items_details

def get_po_items(po):
	total_qty = 0
	received_qty = 0
	pending_qty = 0
	data_list = []
	po_items = frappe.db.sql("""select tpoi.item_code,tpoi.qty,tpoi.received_qty,tpoi.expected_delivery_date from `tabPurchase Order Item` 				tpoi,`tabPurchase Order` tpo where tpoi.parent=%s and tpo.docstatus=1 and tpo.name=tpoi.parent""", (po), as_dict=1)
	purchase_receipt = frappe.db.sql("""select parent from `tabPurchase Receipt Item` where purchase_order=%s""", (po), as_dict=1)

	if len(purchase_receipt)!=0:
		purchase_receipt_id = purchase_receipt[0]['parent']
		if purchase_receipt_id is not None:
			purchase_receipt = frappe.db.sql("""select posting_date from `tabPurchase Receipt` where name=%s""", 					   (purchase_receipt_id), as_dict=1)
			posting_date = purchase_receipt[0]['posting_date']
		else:
			posting_date = ""
	else:
		posting_date = ""
	for items in po_items:
		total_qty = items['qty']
		received_qty = items['received_qty']
		pending_qty = float(total_qty) - float(received_qty);
		data={
		"item_code":items['item_code'],
		"total_qty":total_qty,
		"received_qty":received_qty,
		"pending_qty":pending_qty,
		"expected_delivery_date":items['expected_delivery_date'],
		"updated_delivery_date":posting_date
		}

		data_list.append(data)
	#print "---------------po_details-------------------------------", data
	return data_list


@frappe.whitelist()
def get_master_bom(docId,docName):
	records = ""
	records = frappe.db.sql("""select master_bom from `tabProject` where name=%s""", (docId), as_dict=1)
	if records[0]['master_bom'] is None:
		records = "null"
	return records

