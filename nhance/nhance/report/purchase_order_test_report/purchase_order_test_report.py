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
#reload(sys)
#sys.setdefaultencoding('utf-8')

sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []

	if filters.get("company"):
		company = filters.get("company")

	#print "entering under execute method----"

	columns = get_columns()
	po_details = fetching_po_details()

	if po_details:
		#print "po_details--------", po_details
		for po_data in po_details:
			if po_data['pending_qty'] > 0:
				sum_data.append([po_data['name'], po_data['item_code'], po_data['ordered_qty'], po_data['received_qty'], po_data['pending_qty'], po_data['warehouse'], po_data['stock_uom'], po_data['supplier'], po_data['rate']])


	return columns, sum_data





def fetching_po_details():
	#po_data = frappe.db.sql(""" select tpo.name, tpoi.item_code, tpoi.qty as ordered_qty, tpoi.received_qty, (tpoi.qty-tpoi.received_qty > 0) as pending_qty from `tabPurchase Order` tpo, `tabPurchase Order Item` tpoi where tpo.name=tpoi.parent and tpo.docstatus=1""", as_dict=1)

	po_data = frappe.db.sql(""" select tpo.name, tpoi.item_code, tpoi.qty as ordered_qty, tpoi.stock_uom as stock_uom, tpoi.received_qty, tpoi.warehouse as warehouse, tpoi.rate as rate, tpo.supplier as supplier, (tpoi.qty-tpoi.received_qty) as pending_qty from `tabPurchase Order` tpo, `tabPurchase Order Item` tpoi where tpoi.parent='PUR-ORD-2019-00005' and tpo.name=tpoi.parent and tpo.docstatus=1;""", as_dict=1)

	if po_data:
		return po_data
	else:
 		return None


@frappe.whitelist()
def get_report_data():
	report_data = []
	details = {}
	for rows in sum_data:
		#print "row-----", rows
		po = rows[0]
		warehouse = rows[5]
		item = rows[1]
		ordered_qty = rows[2]
		received_qty = rows[3]
		pending_qty = rows[4]
		stock_uom = rows[6]
		supplier = rows[7]

		details = {"purchase_order": po, "item": item, "ordered_qty": ordered_qty, "received_qty": received_qty, "pending_qty": pending_qty, "warehouse": warehouse, "stock_uom": stock_uom, "supplier": supplier}

		report_data.append(details)
	return report_data


@frappe.whitelist()
def make_purchase_receipt():

	required_date = datetime.now()
	company = frappe.db.get_single_value("Global Defaults", "default_company")

	purchase_receipt_items_json = {}

	purchase_receipt_json = {
		"doctype": "Purchase Receipt",
		"title" : "Purchase Receipt",
		"posting_date" : required_date,
		"docstatus" : 0,
		"company" : company,
		"schedule_date" :required_date,
		"supplier" :"ABC",
		"items":[]
		}

	for rows in sum_data:
		#print "rows------", rows
		purchase_receipt_items_json =	{
			"item_code": rows[1],
			"qty": rows[4],
			"stock_uom": rows[6],
			"rate": rows[8],
			"warehouse": rows[5],
			"purchase_order": rows[0],
			"doctype": "Purchase Receipt Item"
			}
		purchase_receipt_json["items"].append(purchase_receipt_items_json)

	doc = frappe.new_doc("Purchase Receipt")
	doc.update(purchase_receipt_json)
	doc.save()
	ret = doc.doctype
	if ret:
		frappe.msgprint("Purchase Receipt is created successfully : "+doc.name)


def get_columns():
	"""return columns"""
	columns = [
		_("PO")+":Link/Purchase Order:100",
		_("Item")+":Link/Item:100",
		_("Ordered Qty")+":100",
		_("Received Quantity")+"::100",
		_("Pending Quantity")+"::100"
		 ]
	return columns
