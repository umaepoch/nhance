# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from erpnext.stock.stock_balance import get_balance_qty_from_sle
import datetime
import time
import math
import json
import ast
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	global summ_data
	global company
	summ_data = []
	bom_items = []
	whse_items = []
	whse_qty = 0
	bom_qty = 0
	reserved_whse_qty = 0
	sum_qty = 0
	delta_qty = 0
	delta1_qty = 0
	whse_stock_entry_qty = 0
	max_additional_qty = 0
	company = filters.get("company")
	bom = filters.get("bom")
	quantity_to_make = filters.get("qty_to_make")
	include_exploded_items = filters.get("include_exploded_items")
	warehouse = filters.get("warehouse")
	reserve_warehouse = filters.get("reserve_warehouse")
	project_start_date = filters.get("start_date")
	columns = get_columns()

	if warehouse is not None:
		#print "warehouse-----------", warehouse
		whse_items = get_items_from_warehouse(warehouse)
		if whse_items is None:
			whse_items = []
		#print "whse_items-----------", whse_items
	if bom is not None:
		bom_items = get_bom_items(filters)
		if bom_items is None:
			bom_items = []
		#print "bom_items-----------", bom_items

	items_data = merge_items_list(whse_items,bom_items)
#	print "items_data-----------", items_data

	for item in sorted(items_data):
		qty_consumed_in_manufacture = 0
		dict_items = items_data[item]
		item_code = str(dict_items.item_code)
		bom_qty = dict_items.bom_qty
		bom_item_qty = dict_items.bi_qty
		
		if bom_qty!=0:
			required_qty = (bom_item_qty/bom_qty) * (float(quantity_to_make))
		else:
			required_qty = 0
		if warehouse is not None and warehouse is not "":
			whse_qty = get_warehouse_qty(warehouse,item_code)
			#whse_stock_entry_qty = get_stock_entry_quantities(warehouse,item_code,project_start_date)
			po_details = get_stock_entry_quantities(warehouse,item_code,project_start_date)
		else:
			whse_qty = 0
			whse_stock_entry_qty = 0

		if po_details:
			whse_stock_entry_qty = po_details['total_qty']
			qty_consumed_in_manufacture = po_details['qty_consumed_in_manufacture']
			#print "qty_consumed_in_manufacture--------------", qty_consumed_in_manufacture
			whse_qty = whse_qty + whse_stock_entry_qty
		if reserve_warehouse is not None and reserve_warehouse is not "":
			reserved_whse_qty = get_warehouse_qty(reserve_warehouse,item_code)
			#reserved_whse_stock_entry_qty = get_stock_entry_quantities(reserve_warehouse,item_code,project_start_date,whse_type)
			#po_details_for_rwhse = get_stock_entry_quantities(reserve_warehouse,item_code,project_start_date,whse_type)
		else:
			reserved_whse_qty = 0

		#delta_qty = whse_qty - bom_qty 
		delta_qty = whse_qty - required_qty
		#sum_qty = whse_qty + reserved_whse_qty

		sum_qty = whse_qty + reserved_whse_qty + qty_consumed_in_manufacture
		max_additional_qty = required_qty - (whse_qty + qty_consumed_in_manufacture)
	
		#delta1_qty = sum_qty - bom_qty
		delta1_qty = sum_qty - required_qty
		summ_data.append([str(item_code), str(bom_qty), str(bom_item_qty), str(required_qty), str(whse_qty), str(delta_qty), 
			str(reserved_whse_qty), str(qty_consumed_in_manufacture), str(max_additional_qty), str(sum_qty), str(delta1_qty)])
	#print "summ_data-----------", summ_data
	return columns, summ_data

def get_stock_entry_quantities(warehouse,item_code,project_start_date):
	total_qty = 0
	po_details = {}
	qty_consumed_in_manufacture = 0
	current_date = str(datetime.datetime.now())
	if project_start_date is None or project_start_date is "":
		project_start_date = "2000-01-01 00:00:00"
	#print "project_start_date-----", project_start_date
	details = frappe.db.sql("""select sed.item_code,sed.qty,se.purpose from `tabStock Entry Detail` sed, 
			`tabStock Entry` se where sed.item_code=%s and sed.s_warehouse=%s and se.purpose='Manufacture' and 
			sed.modified >='""" + str(project_start_date) +"""'and sed.modified <='""" + current_date + """' and 
			sed.parent=se.name and se.docstatus=1""", (item_code,warehouse), as_dict=1)

	if len(details)!=0:
		#print "details------------", details
		for entries in details:
			if entries['qty'] is None:
				qty = 0
			else:
				qty = float(entries['qty'])
			total_qty = total_qty + qty
			
		po_details = {"total_qty":total_qty, "qty_consumed_in_manufacture": total_qty}
	return po_details

def get_production_order_status(production_order):
	details = frappe.db.sql("""select status from `tabProduction Order` where name=%s and status not in('Cancelled')""", 			                production_order, as_dict=1)
	if len(details)== 0:
		return None
	else:
		return details[0]['status']

def merge_items_list(whse_items,bom_items):
	items_map = {}
	if bom_items:
		for data in bom_items:
			item_code = data['item_code']
			bi_qty = data['bi_qty']
			bo_qty = data['bo_qty']
			#print "bom_item_qty--------", bi_qty
			key = (item_code)
			if key not in items_map:
				items_map[key] = frappe._dict({"item_code": item_code,"bi_qty": float(bi_qty),"bom_qty": bo_qty})
	if whse_items:
		for whse_items_data in 	whse_items:
			whse_item = whse_items_data['item_code']
			if whse_item not in items_map:
				key = whse_item
				items_map[key] = frappe._dict({"item_code": whse_item,"bi_qty": 0.0,"bom_qty": 0.0})
	return items_map

def get_warehouse_qty(warehouse,item_code):
	whse_qty = 0
	details = frappe.db.sql("""select actual_qty from `tabBin` where warehouse=%s and item_code=%s and actual_qty > 0 """, 					(warehouse,item_code), as_dict=1)
	if len(details)!=0:
		if details[0]['actual_qty'] is not None:
			whse_qty = details[0]['actual_qty']
	return whse_qty

def get_bom_qty(bom,item_code):
	bom_qty = 0
	details = frappe.db.sql("""select qty from `tabBOM Item` where parent=%s and item_code=%s""", (bom,item_code), as_dict=1)
	if len(details)!=0:
		if details[0]['qty'] is not None:
			bom_qty = details[0]['qty']
	return bom_qty

def get_items_from_warehouse(warehouse):
	whse_items = frappe.db.sql("""select item_code,actual_qty from `tabBin` where warehouse = %s and actual_qty > 0 group by item_code""", 					warehouse, as_dict=1)
	if len(whse_items)==0:
		whse_items = None
	return whse_items

def get_bom_items(filters):
	conditions = get_conditions(filters)
	#print "---------conditions::", conditions
	if filters.get("include_exploded_items") == "Y":
		#print "in------------Y"
		return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code, bi.stock_qty as bi_qty from `tabBOM` bo, `tabBOM Explosion Item` bi where bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1" %s order by bo.name, bi.item_code""" % conditions, as_dict=1)
	else:
		return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code, bi.stock_qty as bi_qty from `tabBOM` bo, `tabBOM Item` bi where bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1" %s order by bo.name, bi.item_code""" % conditions, as_dict=1)

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " and bo.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)

	if filters.get("bom"):
		conditions += " and bi.parent = '%s'" % frappe.db.escape(filters.get("bom"), percent=False)
	return conditions

@frappe.whitelist()
def fetch_project_details(project):
	details = frappe.db.sql("""select start_date,project_warehouse,reserve_warehouse,master_bom,core_team_coordinator,planner from 					`tabProject` where name=%s""", project, as_dict=1)
	return details

@frappe.whitelist()
def get_report_data():
	report_data = []
	details = {}
	for rows in summ_data:
		item_code = rows[0]
		bom_qty = rows[1]
		qty = rows[10]
		qty_in_reserved_whse = rows[6]
		qty_in_production_whse = rows[4]
		total_qty = rows[9]
		details = 											{"item_code":item_code,"bom_qty":bom_qty,"qty":qty,"qty_in_reserved_whse":qty_in_reserved_whse,"qty_in_production_whse":qty_in_production_whse,"total_qty":total_qty}
		report_data.append(details)
	return report_data
	
def get_columns():
	"""return columns"""
	columns = [
		_("Item Code")+":Link/BOM:100",
		_("BOM Qty")+"::100",
		_("BOM Item Qty")+"::100",
		_("Required Qty")+"::100",
		_("Quantity in Production Bench")+"::140",
		_("Delta Qty")+"::100",
		_("Quantity in Reserve Warehouse")+"::150",
		_("Quantity Consumed in Manufacture")+"::150",
		_("Max additional Qty")+"::150",
		_("Sum Qty")+":Link/UOM:90",
		_("Sum Qty - Required Qty")+"::100"
		 ]
	return columns

@frappe.whitelist()
def check_for_whole_number(bomno):
	return (frappe.db.sql("""select must_be_whole_number from `tabUOM` where name IN (select uom from `tabBOM`where name = %s) """,(bomno)))

@frappe.whitelist()
#def make_issue(item_code,project,qty,planner,core_team_coordinator):
def make_issue(issue_items):
	return_doc = ""
	issue_list = json.loads(issue_items)
	issue_list = json.dumps(issue_list)
	issue_list = ast.literal_eval(issue_list)
	#print "----------------------issue_list", issue_list
	for item in issue_list:
		issue_assign = []
		item_code = issue_list[0]['item_code']
		bom_qty = issue_list[0]['bom_qty']
		project = issue_list[0]['project']
		planner = issue_list[0]['planner']
		qty_in_reserved_whse = issue_list[0]['qty_in_reserved_whse']
		qty_in_production_whse = issue_list[0]['qty_in_production_whse']
		total_qty = issue_list[0]['total_qty']
		core_team_coordinator = issue_list[0]['core_team_coordinator']
		
		if bom_qty is None:
			bom_qty = 0
		if qty_in_reserved_whse is None:
			qty_in_reserved_whse = 0
		if qty_in_production_whse is None:
			qty_in_production_whse = 0
		if total_qty is None:
			total_qty = 0
		if core_team_coordinator != "null" and core_team_coordinator is not None:
			issue_assign.append(core_team_coordinator)
		if planner != "null" and planner is not None:
			issue_assign.append(planner)

		#Start of Table format data for Description field in Issue doc..
		description = "<table border=2>"
		description = description + "<tr backgroundcolor=green>"
		description = description + "<td>Raw Material:&nbsp;&nbsp;&nbsp;</td>" + "<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + item_code +"</td>"
		description = description + "</tr>"

		description = description + "<tr backgroundcolor=green>"
		description = description + "<td>Required Quantity:&nbsp;&nbsp;&nbsp;</td>" + "<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(bom_qty) +"</td>"
		description = description + "</tr>"

		description = description + "<tr backgroundcolor=green>"
		description = description + "<td>Qty in Reserve Warehouse:&nbsp;&nbsp;&nbsp;</td>" + "<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(qty_in_reserved_whse) +"</td>"
		description = description + "</tr>"

		description = description + "<tr backgroundcolor=green>"
		description = description + "<td>Qty in Production Warehouse:&nbsp;&nbsp;&nbsp;</td>" + "<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(qty_in_production_whse) +"</td>"
		description = description + "</tr>"

		description = description + "<tr backgroundcolor=green>"
		description = description + "<td>Total Quantity:&nbsp;&nbsp;&nbsp;</td>" + "<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(total_qty) +"</td>"
		description = description + "</tr>"

		description = description + "</table>"

		bottom_description = "<table>"
		bottom_description = bottom_description + "<tr>"
		bottom_description = bottom_description + "<td>As you can see the Quantity of raw materials issued for this project is more than the quantity required.</td>"
		bottom_description = bottom_description + "</tr>"

		bottom_description = bottom_description + "<tr>"
		bottom_description = bottom_description + "<td>Thiscould be because:</td>"
		bottom_description = bottom_description + "</tr>"

		bottom_description = bottom_description + "<tr>"
		bottom_description = bottom_description + "<td>1.The BOM is not updated - Please update the BOM, and/or</td>"
		bottom_description = bottom_description + "</tr>"

		bottom_description = bottom_description + "<tr>"
		bottom_description = bottom_description + "<td>2.Errors have been made while transferring quantities - Please correct the errors.</td>"
		bottom_description = bottom_description + "</tr>"
	
		description = description + "<br>" + "<br>" + bottom_description
		#End of making Table format data for Description field in Issue doc..
		
		#Start of Making ToDo List for an Specific Issue..
		OuterJson_Transfer = {
		"company": company,
		"doctype": "Issue",
		"issue_type": "Planning/Production",
		"subject": "More Raw Material than Required for Project " + str(project),
		"description" : description
		}

		doc = frappe.new_doc("Issue")
		doc.update(OuterJson_Transfer)
		doc.save()
		return_doc = doc.doctype
		docName = doc.name

		for assined_user in issue_assign:
			to_do_object = {
			"description": "More Raw Material than Required for Project " + str(project),
			"company": company,
			"doctype": "ToDo",
			"owner": assined_user,
			"reference_type": "Issue",
			"reference_name": docName
			}
	
			to_do_doc = frappe.new_doc("ToDo")
			to_do_doc.update(to_do_object)
			to_do_doc.save()
		#End of Making ToDo List for an Specific Issue..
	if return_doc:
		return return_doc

