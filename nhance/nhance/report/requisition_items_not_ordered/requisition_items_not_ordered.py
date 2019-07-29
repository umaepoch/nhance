# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	unique_po_items_list = []
	data = []
	columns = get_columns()

	company = filters.get("company")


	sreq_datas  = get_sreq_datas(company)

	for sreq_data in sreq_datas :
		sreq_name = sreq_data['name']
		pos_list_tmp = sreq_data['po_list']
		sreq_items_data = get_sreq_items_data( sreq_name,filters )

		count = 1
		for sreq_item_data in sreq_items_data :

			sreq_item_code = sreq_item_data['item_code']
			total_qty = sreq_item_data ['qty']
			total_po_ord_qty = get_total_po_ord_qty ( sreq_name,sreq_item_code,filters )
			pending_qty = total_qty - total_po_ord_qty
			project = sreq_item_data['project']
			bom =  sreq_item_data['pch_bom_reference']

			data.append([
			sreq_name,
			sreq_item_code,
			total_qty,
			total_po_ord_qty,
			pending_qty,
			bom,
			project
			])
			#print "Data appending for "+ str(count) +"th time"
			count = count +1

	return columns, data

def get_columns():
	"""return columns"""
	columns = [
	_("SREQ No")+":Link/Stock Requisition:100",
	_("Item")+":Link/Item:100",
	_("Total Qty")+"::100",
	_("Ordered Qty")+"::140",
	_("Pending Qty")+"::100",
	_("BOM")+":Link/BOM:100",
	_("Project")+":Link/Project:100"
	 ]
	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("bom"):
		conditions += " and pch_bom_reference = '%s'" % frappe.db.escape(filters.get("bom"), percent=False)
	if filters.get("project"):
		conditions += " and project = '%s'" % frappe.db.escape(filters.get("project"), percent=False)
	return conditions

def po_get_conditions(filters):
	conditions = ""

	if filters.get("bom"):
		conditions += " and poi.pch_bom_reference = '%s'" % frappe.db.escape(filters.get("bom"), percent=False)
	if filters.get("project"):
		conditions += " and poi.project = '%s'" % frappe.db.escape(filters.get("project"), percent=False)

	conditions += " and po.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)
	return conditions


def get_sreq_datas(company):
	#print "suresh # DEBUG:  cond",conditions
	#select name from `tabStock Requisition` where company like "Epoch%" and name in (select parent from `tabStock Requisition Item`)
	#check = frappe.db.sql("""select name from `tabStock Requisition` where company=%s and na""", as_dict=1)
	#check = frappe.db.sql("""select name from `tabStock Requisition` where company = {0} and name in (select parent from `tabStock Requisition Item` where name ="217c40d2af") """.format(company), as_dict=1)
	#print "suresh # DEBUG:  check",check
	#workingFine sreq_data = frappe.db.sql("""select name,po_list,material_request_type from `tabStock Requisition` where docstatus=1 and material_request_type='Purchase' """, as_dict=1)

	sreq_data = frappe.db.sql("""select name,po_list,material_request_type from `tabStock Requisition` where docstatus=1 and material_request_type='Purchase' and company = %s  """,(company) ,as_dict=1)
	#print "sreq_data",sreq_data
	return sreq_data

def get_sreq_items_data( sreq_name,filters ):
	conditions = get_conditions(filters)
	#print "from get_sreq_items_data conditions",conditions
	sreq_name = str(sreq_name)
	query = "select item_code,qty,pch_bom_reference,project from `tabStock Requisition Item` where parent={} {}".format("'"+sreq_name+"'",conditions)
	#print "sreq query",query
	#sreq_items_data = frappe.db.sql("""select item_code,qty,pch_bom_reference,project from `tabStock Requisition Item` where parent={} {} """.format(sreq_name,conditions),as_dict=1)
	sreq_items_data = frappe.db.sql(query,as_dict=1)

	#print "from get_sreq_items_data sreq_items_data",sreq_items_data

	return sreq_items_data

def get_total_po_ord_qty ( sreq_name,sreq_item_code,filters):
	conditions = po_get_conditions(filters)
	query = "select sum(poi.qty) total_qty from `tabPurchase Order Item` poi,`tabPurchase Order` po where  po.name =poi.parent and poi.item_code={} and po.stock_requisition_id={} {}".format("'"+sreq_item_code+"'","'"+sreq_name+"'",conditions)
	#print "po query",query
	total_po_ord_qty_list = frappe.db.sql(query,as_dict=1)
	#total_po_ord_qty_list = frappe.db.sql("""select sum(poi.qty) total_qty from `tabPurchase Order Item` poi,`tabPurchase Order` po  where po.name =poi.parent and poi.item_code=%s and po.stock_requisition_id=%s""",(sreq_item_code,sreq_name),as_dict=1)
	total_po_ord_qty = 0
	if total_po_ord_qty_list[0]['total_qty']:
		total_po_ord_qty = total_po_ord_qty_list[0]['total_qty']

	return total_po_ord_qty
