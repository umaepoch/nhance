# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime,comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from datetime import datetime
import datetime
import time
import json
import math
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	po_entries = fetch_purchase_order_entries()
	if po_entries:
		#print po_entries
		for po in po_entries:
			po_name = po.name
			posting_date = po.creation
			posting_date = posting_date.strftime('%d-%m-%Y')
			supplier = po.supplier
			#print "po_name-------------",po_name
			po_items = fetch_po_records(po_name)
			if po_items:
				ordered_qty = 0
				received_qty = 0
				balance_qty = 0

				ordered_qty_in_stock_uom = 0
				ordered_qty_in_purchase_uom = 0

				received_qty_in_stock_uom = 0
				received_qty_in_purchase_uom = 0

				balance_qty_in_stock_uom = 0
				balance_qty_in_purchase_uom = 0

				for items_data in po_items:
					item_code = items_data['item_code']
					ordered_qty = items_data['qty']
					received_qty = items_data['received_qty']
					balance_qty = ordered_qty - received_qty
					pch_bom_reference =  items_data['pch_bom_reference']
					if items_data['stock_uom'] == items_data['uom']:
						conversion_factor = 1

					ordered_qty_in_stock_uom = ordered_qty
					data.append([posting_date,po_name,supplier,item_code,ordered_qty,received_qty,
					balance_qty,pch_bom_reference])


	return columns, data

def fetch_purchase_order_entries():
	records = frappe.db.sql("""select name,creation,supplier from `tabPurchase Order` where docstatus = 1""", as_dict=1)
	return records

def fetch_po_records(po):
	records = frappe.db.sql("""select * from `tabPurchase Order Item` where parent = %s""", po, as_dict=1)
	return records

def get_columns():
	"""return columns"""
	columns = [
		_("Date")+"::100",
		_("Purchase Order")+":Link/Purchase Order:140",
		_("Supplier Name")+"::140",
		_("Item Code")+":Link/Item:100:140",
		_("Ordered Qty (Stock UOM)")+"::100",
		_("Received Qty (Stock UOM)")+"::100",
		_("Balance Qty  (Stock UOM)")+"::100",
		_("Project / BOM")+"::110"
		 ]
	return columns
