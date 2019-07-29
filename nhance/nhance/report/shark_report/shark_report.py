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
reload(sys)
sys.setdefaultencoding('utf-8')

sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []
	company = ""
        sales_order=""
	if filters.get("sales_order"):
                company = filters.get("company")
		sales_order = filters.get("sales_order")
	print "sales_order=============",sales_order

	
	print "entering under execute method----"

	columns = get_columns()
	po_details = fetching_po_details(sales_order)

	if po_details:
		print "so_details--------", po_details
	
	for po_data in po_details:
		ordered_qty = po_data["ordered_qty"]
		delivered_qty = po_data["delivered_qty"]
		pending_qty =ordered_qty - delivered_qty
		actual_qty = po_data['qty']
		Shortage_Qty=actual_qty -pending_qty
		if (pending_qty > 0 and actual_qty>0):
			sum_data.append([ po_data['item_code'],po_data['item_name'], po_data['ordered_qty'], po_data['delivered_qty'], 
			pending_qty, po_data['warehouse'],po_data['qty'],Shortage_Qty,po_data['stock_qty'], po_data['stock_uom'], po_data['supplier'],   po_data['rate']
                        ])
						 					     					    	
			
	return columns, sum_data

def fetching_po_details(sales_order):
	po_data = frappe.db.sql("""select 
					tso.name,tsoi.item_code,tsoi.qty as ordered_qty,tsoi.stock_uom as stock_uom, tsoi.delivered_qty,
					tsoi.warehouse as warehouse, tsoi.rate as rate,tsoi.supplier as supplier,tsoi.stock_qty,tb.warehouse,
                                        tb.actual_qty as qty,tsoi.item_name 
			from 
				`tabSales Order` tso,`tabSales Order Item` tsoi,`tabBin` tb 
			where 
				tso.name=tsoi.parent and tso.docstatus=1 and tsoi.item_code = tb.item_code and tso.name = '"""+sales_order+"""'""", as_dict=1)

	#po_data = frappe.db.sql(""" select tso.name,tsoi.item_code,tsoi.qty as ordered_qty,tsoi.stock_uom as stock_uom, tsoi.delivered_qty, tsoi.warehouse as warehouse, tsoi.rate as rate,tsoi.supplier as supplier,  (tsoi.qty-tsoi.delivered_qty) as pending_qty,tsoi.stock_qty,tb.warehouse,tb.actual_qty as qty from `tabSales Order` tso,`tabSales Order Item` tsoi,`tabBin` tb where tsoi.parent='SAL-ORD-2019-00001' and tso.name=tsoi.parent and tsoi.item_code=tb.item_code;""", as_dict=1)

	return po_data



def get_columns():
	"""return columns"""
	columns = [
		_("Item")+":Link/Item:100",
		_("Item Name")+"::100",
		_("Quantity")+":100",
		_("Delivered Quantity")+"::100",
		_("Pending Quantity")+"::100",
                _("Warehouse")+":Link/Warehouse:100",
                _("Available Qty")+"::100",
		_("Shortage/Excess Qty")+"::100",
		 ]
	return columns
