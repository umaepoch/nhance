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
		po_name = po_data.name or ""
		date = po_data.transaction_date
		date = frappe.utils.formatdate(date, "dd-MM-yyyy")
		reqd_by_date = po_data.schedule_date
 		reqd_by_date = frappe.utils.formatdate(reqd_by_date, "dd-MM-yyyy")
		supplier = po_data.supplier or  ""
		supplier_name = po_data.supplier_name or  ""
		project_name = po_data.project or  ""
		item_code = po_data.item_code or  ""
		qty_puom = po_data.qty
		received_qty_puom = po_data.received_qty
		qty_to_receive_puom = po_data.qr
		stock_uom = po_data.stock_uom or  ""
		pur_uom = po_data.uom or  ""
		conversion_factor =  po_data.conversion_factor
		stock_qty =  po_data.stock_qty
		received_qty_suom =  received_qty_puom *  conversion_factor
		qty_to_receive_suom = stock_qty - received_qty_suom
		warehouse = po_data.warehouse or  ""
		item_name = po_data.item_name or  ""
		description = po_data.description or  ""
		brand = po_data.brand or  ""
		company = po_data.company or  ""

	 	data.append([ str(po_name),
		 str(date),
		 str(reqd_by_date),
		 str(supplier),
		 str(supplier_name),
		 str(project_name),
		 str(item_code),
		 str(qty_puom),
		 str(received_qty_puom),
		 str(qty_to_receive_puom),
		 str(pur_uom),
		 str(stock_uom),
		 str(conversion_factor),
		 str(qty_to_receive_suom),
 		 str(item_name),
		 str(warehouse),
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
		_("Qty(PUOM)")+"::100",
		_("Received Qty(PUOM)")+"::150",
		_("Qty to Receive(PUOM)")+"::150",
		_("Purchase UOM")+"::150",
		_("Stock UOM")+":Link/UOM:90",
		_("Conversion Factor")+"::150",
		_("Qty to Receive (SUOM)")+"::150",
		_("Item Name")+"::150",
		_("Warehouse")+"::150",
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
										po.supplier_name,
										poi.project,
										poi.item_code,
										poi.qty,
										poi.received_qty,
										(poi.qty - ifnull(poi.received_qty, 0)) qr,
										poi.stock_uom,
										poi.uom,
										poi.conversion_factor,
										poi.stock_qty ,
										poi.warehouse,
										poi.item_name ,
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
