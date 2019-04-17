# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime,comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from datetime import datetime
import time
import math
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

company = []
data = []

def execute(filters=None):
	global data
	data = []
	columns = []
	columns = get_columns()

	all_po_datas =  get_all_po_datas()

	for po_data in all_po_datas:
		 po_name = po_data.name
		 date = po_data.transaction_date
		 reqd_by_date = po_data.schedule_date
		 supplier = po_data.supplier
		 supplier_name = po_data.supplier_name
		 project_name = po_data.project
		 item_code = po_data.item_code
		 qty = po_data.qty
		 received_qty = po_data.received_qty
		 qty_to_receive = po_data.qr
		 stock_uom = po_data.stock_uom
		 pur_stock_uom = po_data.uom
		 qty_to_receive_pur_uom = po_data.received_qty
		 warehouse = po_data.warehouse
		 item_name = po_data.item_name
		 description = po_data.description
		 brand = po_data.brand
		 company = po_data.company

	 	 data.append([ str(po_name),
		 str(date),
		 str(reqd_by_date),
		 str(supplier),
		 str(supplier_name),
		 str(project_name),
		 str(item_code),
		 str(qty),
		 str(received_qty),
		 str(qty_to_receive),
		 str(stock_uom),
		 str(pur_stock_uom),
		 str(qty_to_receive_pur_uom),
		 str(warehouse),
		 str(item_name),
		 str(description),
		 str(brand),
		 str(company)
		 ])

	return columns, data


def get_columns():
	"""return columns"""
	columns = [
		_("Purchase Order")+"::100",
		_("Date")+"::100",
		_("Reqd by Date")+"::100",
		_("Supplier")+"::140",
		_("Supplier Name")+"::140",
		_("Project")+"::140",
		_("Item Code")+"::100",
		_("Qty")+"::100",
		_("Received Qty")+"::150",
		_("Qty to Receive")+"::150",
		_("Stock UOM")+":Link/UOM:90",
		_("Purchase UOM")+"::150",
		_("Quantity to Receive in Purchase UOM")+"::150",
		_("Warehouse")+"::150",
		_("Item Name")+"::150",
		_("Description")+"::150",
		_("Brand")+"::150",
		_("Company")+"::150"
	]
	return columns

def get_all_po_datas():
	all_po_datas = frappe.db.sql("""select
										po.name,
										po.transaction_date ,
										poi.schedule_date ,
										po.supplier ,
										po.supplier_name",
										poi.project,
										poi.item_code,
										poi.qty",
										poi.received_qty,
										(poi.qty - ifnull(poi.received_qty, 0)) qr,
										poi.stock_uom,
										poi.uom",
										poi.warehouse,
										poi.item_name ",
										poi.description ,
										poi.brand,
										po.company

									 from
									 	`tabPurchase Order` po,`tabPurchase Order Item` poi

									 where
										 po.docstatus = 1 and
										 po.status not in ('Stopped', 'Closed') and
										 poi.parent = po.name and
										 ifnull(poi.received_qty, 0) < ifnull(poi.qty, 0)

						 			order by
										 po.transaction_date asc""", as_dict=1)


	return all_po_datas
