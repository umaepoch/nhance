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

def execute(filters=None):
	global item_map
	global whs_flag
	global whse
	global iwb_map
	global company
	global planning_warehouse
	global bom_for_validation
	global qty_to_make
	global reference_no
	global summ_data
	global required_date
	global required_date_count
	global curr_stock_balance

	reference_no = filters.get("reference_no")
	qty_to_make = filters.get("qty_to_make")
	bom_for_validation = filters.get("bom")
	company = filters.get("company")
	planning_warehouse = filters.get("planning_warehouse")
	required_date = filters.get("required_on")
	curr_stock_balance = filters.get("current_stock_balance")

	if not filters: filters = {}
	validate_filters(filters)
	columns = get_columns()
	item_map = get_item_details(filters)
	# print "item_map===>>",item_map
	iwb_map = get_item_warehouse_map(filters)
	#print "iwb_map==>>",iwb_map

	data = []
	summ_data = []
	item_prev = ""
	item_work = ""
	item_count = 0
	total_delta_qty = 0
	tot_bal_qty = 0
	tot_p_bal_qty = 0
	reqd_qty = 0
	p_reqd_qty = 0
	tot_bi_qty = 0
	tot_reqd_qty = 0
	tot_p_reqd_qty = 0
	total_p_delta_qty = 0
	conv_factor = 1
	loop_count = 1
	for (bom, item, bi_item, whse) in sorted(iwb_map):
		qty_dict = iwb_map[(bom, item, bi_item, whse)]

		if item_map[bi_item]["purchase_uom"] is None or item_map[bi_item]["purchase_uom"] is "":
			print "purchase_uom is empty....."
			purchase_UOM = item_map[bi_item]["stock_uom"]
			item_map[bi_item]["purchase_uom"] = purchase_UOM
			conv_factor = 1
		else:
			convert_factor = frappe.db.sql("""select conversion_factor as conversion_factor from `tabUOM Conversion Detail` t2 where t2.parent = %s and uom = %s""", (bi_item, item_map[bi_item]["stock_uom"]))
			if convert_factor:
				conv_factor = convert_factor[0][0]
			else:
				conv_factor = 1
		bal_qty = qty_dict.bal_qty
		bal_qty_puom = bal_qty/conv_factor
		#bal_qty_puom = 0.5
		
		if bi_item != " ":
			data.append([
							bom,
 							item,
 							item_map[bi_item]["description"],
							item_map[bi_item]["item_group"],
							item_map[bi_item]["item_name"],
							item_map[bi_item]["stock_uom"],
							item_map[bi_item]["purchase_uom"],
							qty_dict.bal_qty,
							qty_dict.bi_qty,
							whse,
							qty_dict.project,
							qty_dict.bom_qty,
 							bi_item,
							qty_dict.qty_to_make,
							conv_factor,
							bal_qty_puom,
						])
		else:

			data.append([
							bom,
 							bi_item, 
							item_map[item]["description"],
							item_map[item]["item_group"],
							item_map[item]["item_name"],
							item_map[item]["stock_uom"],
							item_map[item]["purchase_uom"],
							qty_dict.bal_qty,
 							qty_dict.bi_qty,
							whse,
							qty_dict.project, 
							qty_dict.bom_qty, 
							bi_item, 
							qty_dict.qty_to_make,
							conv_factor,
							bal_qty_puom,
						])


	for rows in data:
		item_work = rows[12]

		if item_prev == item_work:
			item_count = item_count + 1
			tot_bal_qty =float(tot_bal_qty + rows[7])
			tot_p_bal_qty = float(tot_p_bal_qty + rows[15])
			reqd_qty = (rows[8] / rows[11]) * flt(rows[13])
			p_reqd_qty = reqd_qty / rows[14]
			tot_bi_qty = rows[8]
			tot_reqd_qty = reqd_qty
			tot_p_reqd_qty = p_reqd_qty
			if check_for_whole_number_itemwise(item_work):
				tot_reqd_qty = math.ceil(tot_reqd_qty)
				#tot_p_reqd_qty = math.ceil(tot_p_reqd_qty)
			summ_data.append([rows[0], rows[1], rows[11], rows[2],
		rows[3], rows[4], rows[5], rows[6], rows[12], " ", " ", rows[7], " ", " ", rows[15], " ", rows[9], rows[14]
			])
		if (item_prev != item_work or loop_count == len(data)):
			if item_count > 1:
				length = len(summ_data)
				count = length - item_count
				data_array = summ_data[count]
				data_array[9] = " "
				data_array[10] = " "
				data_array[12] = " "
				data_array[13] = " "
				data_array[15] = " "
				#tot_bal_qty = tot_bal_qty + rows[6]
				total_delta_qty = tot_reqd_qty - tot_bal_qty
				total_p_delta_qty = tot_p_reqd_qty - tot_p_bal_qty
				print "############-total_p_delta_qty::", total_p_delta_qty
				if total_delta_qty < 0:
					total_delta_qty = 0
					total_p_delta_qty = 0
				#tot_p_reqd_qty = 10.71
				#tot_p_bal_qty = 53.9
				summ_data.append([rows[0], " ", " ", data_array[3], " ", data_array[5], data_array[6], data_array[7], data_array[8],
				tot_bi_qty, round(tot_reqd_qty,2),
				tot_bal_qty, round(total_delta_qty,2), round(tot_p_reqd_qty,2), tot_p_bal_qty, round(total_p_delta_qty,2), " ", data_array[17]
				])
			if item_prev != item_work:
				item_count = 1
				reqd_qty = (rows[8] / rows[11]) * flt(rows[13])
				p_reqd_qty = reqd_qty / rows[14]
				if check_for_whole_number_itemwise(item_work):
					reqd_qty = math.ceil(reqd_qty)
					#p_reqd_qty = math.ceil(p_reqd_qty)
				tot_bal_qty = rows[7]
				tot_p_bal_qty = rows[15]
				total_delta_qty = reqd_qty - tot_bal_qty
				total_p_delta_qty = p_reqd_qty - tot_p_bal_qty
				if total_delta_qty < 0:
					total_delta_qty = 0
					total_p_delta_qty = 0
				#p_reqd_qty = 5.8
				#tot_p_bal_qty = 53.9
				summ_data.append([rows[0], rows[1], rows[11], rows[2],
				rows[3], rows[4],
				rows[5], rows[6], rows[12], rows[8],round(reqd_qty,2) ,tot_bal_qty,round(total_delta_qty,2), round(p_reqd_qty,2), tot_p_bal_qty, round(total_p_delta_qty,2), rows[9], rows[14]
				])
		item_prev = item_work
		loop_count = loop_count + 1
	required_date_count = False


	return columns, summ_data



def get_columns():
		"""return columns"""
		columns = [
		_("BOM")+":Link/BOM:100",
		_("Item")+":Link/Item:100",
		_("BOM Qty")+"::100",
		_("Description")+"::140",
		_("Item Group")+"::100",
		_("Item Name")+"::150",
		_("Stock UOM")+":Link/UOM:90",
		_("Purchase UOM")+":Link/UOM:90",
		_("BOM Item")+":Link/Item:100",
		_("BoM Item Qty")+"::100",
		_("Required Qty")+"::100",
		_("Balance Qty")+":Float:100",
		_("Delta Qty")+"::100",
		_("Required Qty(P UoM)")+"::100",
		_("Balance Qty(P UoM)")+":Float:100",
		_("Delta Qty(P UoM)")+"::100",
		_("Warehouse")+"::100",
		_("Conversion Factor")+"::100"


		 ]
		return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("company"):
		conditions += " and bo.company = '%s'" % frappe.db.escape(filters.get("company"), percent=False)

	if filters.get("item_code"):
		conditions += " and bi.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)
	if filters.get("bom"):
		conditions += " and bi.parent = '%s'" % frappe.db.escape(filters.get("bom"), percent=False)

	return conditions


#       if filters.get("warehouse"):
#             conditions += " and warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)



def get_sales_order_entries(filters):
	conditions = get_conditions(filters)

	if filters.get("include_exploded_items") == "Y":
		return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code as bi_item, bi.stock_qty as bi_qty
					from `tabBOM` bo, `tabBOM Explosion Item` bi where bo.name = bi.parent and bo.docstatus = "1" %s
					order by bo.name, bi.item_code""" % conditions, as_dict=1)
	else:
		return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code as bi_item, bi.stock_qty as bi_qty
					from `tabBOM` bo, `tabBOM Item` bi where bo.name = bi.parent and bo.docstatus = "1" %s
					order by bo.name, bi.item_code""" % conditions, as_dict=1)




def get_item_warehouse_map(filters):
	iwb_map = {}
	sle = get_sales_order_entries(filters)
	company = filters.get("company")
	total_stock = 0
	temp_whse = []
	item_flag = {}

	whs_flag = 0
	qty_to_make = filters.get("qty_to_make")

	if filters.get("warehouse"):
		temp_whse = filters.get("warehouse")


		if temp_whse == 'All':
			whse, whs_flag = get_warehouses(company)
		else:
			whse, whs_flag = get_whs_branch(temp_whse, filters)

	else:
		whse = get_warehouses(company)



	for d in sle:

		item_flag[d.bi_item] = False
		total_stock = get_total_stock(d.bi_item)

		if total_stock > 0:
			if whs_flag == 1:
				for w in whse:
					whse_stock = get_stock(d.bi_item, w)
					if whse_stock > 0:
						key = (d.bom_name, d.bo_item, d.bi_item, w)

						if key not in iwb_map:
							item_flag[d.bi_item] = True
							iwb_map[key] = frappe._dict({
											"opening_qty": 0.0, "opening_val": 0.0,
											"in_qty": 0.0, "in_val": 0.0,
											"out_qty": 0.0, "out_val": 0.0,
											"bal_qty": 0.0, "bom_qty": 0.0,
											"bi_qty": 0.0, "qty_to_make": 0.0,
											"val_rate": 0.0, "uom": None
									})
							qty_dict = iwb_map[(d.bom_name, d.bo_item, d.bi_item, w)]
							qty_dict.bal_qty = whse_stock
							qty_dict.bi_qty = d.bi_qty
							qty_dict.bom_qty = d.bo_qty
							qty_dict.qty_to_make = qty_to_make
							#qty_dict.delta_qty=(qty_dict.bal_qty-(d.bi_qty * flt(qty_to_make)))
							qty_dict.project = d.project
			else:
				key = (d.bom_name, d.bo_item, d.bi_item, whse)
				if key not in iwb_map:
					item_flag[d.bi_item] = True
					iwb_map[key] = frappe._dict({
									"opening_qty": 0.0, "opening_val": 0.0,
									"in_qty": 0.0, "in_val": 0.0,
									"out_qty": 0.0, "out_val": 0.0,
									"bal_qty": 0.0, "bom_qty": 0.0,
									"bi_qty": 0.0, "qty_to_make": 0.0,
									"val_rate": 0.0, "uom": None
							})
					qty_dict = iwb_map[(d.bom_name, d.bo_item, d.bi_item, whse)]
					qty_dict.bal_qty = get_stock(d.bi_item, whse)
					qty_dict.bi_qty = d.bi_qty
					qty_dict.bom_qty = d.bo_qty
					qty_dict.qty_to_make = qty_to_make
					#qty_dict.delta_qty=(qty_dict.bal_qty-(d.bi_qty * flt(qty_to_make)))
					qty_dict.project = d.project
		else:
			key = (d.bom_name, d.bo_item, d.bi_item, " ")
			if key not in iwb_map:
				item_flag[d.bi_item] = True
				iwb_map[key] = frappe._dict({
								   "opening_qty": 0.0, "opening_val": 0.0,
								   "in_qty": 0.0, "in_val": 0.0,
								   "out_qty": 0.0, "out_val": 0.0,
								   "bal_qty": 0.0, "bom_qty": 0.0,
								   "bi_qty": 0.0, "qty_to_make": 0.0,
								   "val_rate": 0.0, "uom": None
						   })
				qty_dict = iwb_map[(d.bom_name, d.bo_item, d.bi_item, " ")]

				qty_dict.bal_qty = 0

				qty_dict.bi_qty = d.bi_qty
				qty_dict.bom_qty = d.bo_qty
				qty_dict.qty_to_make = qty_to_make
				#qty_dict.delta_qty=(qty_dict.bal_qty-(d.bi_qty * flt(qty_to_make)))
				qty_dict.project = d.project
		if item_flag.get(d.bi_item) == False:
			key = (d.bom_name, d.bo_item, d.bi_item, " ")
			if key not in iwb_map:
				iwb_map[key] = frappe._dict({
								   "opening_qty": 0.0, "opening_val": 0.0,
								   "in_qty": 0.0, "in_val": 0.0,
								   "out_qty": 0.0, "out_val": 0.0,
								   "bal_qty": 0.0, "bom_qty": 0.0,
								   "bi_qty": 0.0, "qty_to_make": 0.0,
								   "val_rate": 0.0, "uom": None
						   })
				qty_dict = iwb_map[(d.bom_name, d.bo_item, d.bi_item, " ")]
				qty_dict.bal_qty = 0
				qty_dict.bi_qty = d.bi_qty
				qty_dict.bom_qty = d.bo_qty
				qty_dict.qty_to_make = qty_to_make
				#qty_dict.delta_qty=(qty_dict.bal_qty-(d.bi_qty * flt(qty_to_make)))
				qty_dict.project = d.project
	del sle[:]
	return iwb_map

def get_warehouses(company):
		whse = frappe.db.sql("""select name from `tabWarehouse` where company = %s""", company)
		whse_list = [row[0] for row in whse]
		whs_flag = 1
		return whse_list, whs_flag

def get_whs_branch(temp_whs, filters):
	whse = frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse = %s""", temp_whs)
	whse_list = [row[0] for row in whse]
	if whse_list:
		whs_flag = 1
		return whse_list, whs_flag
	else:
		whs_flag = 0
		whse = filters.get("warehouse")
		return whse, whs_flag

def get_stock(bi_item, warehouse):
	item_stock = get_balance_qty_from_sle(bi_item, warehouse)
	return item_stock

def get_total_stock(item_code):

	item_stock = flt(frappe.db.sql("""select sum(actual_qty)
			from `tabStock Ledger Entry`
			where item_code=%s""",
			(item_code))[0][0])

	stock_recon = flt(frappe.db.sql("""select sum(qty_after_transaction)
			from `tabStock Ledger Entry`
			where item_code=%s and voucher_type = 'Stock Reconciliation'""",
			(item_code))[0][0])

	tot_stock = item_stock + stock_recon
	return tot_stock

def get_stock_val(item_code, warehouse):

	item_stock_val = flt(frappe.db.sql("""select sum(stock_value)
			from `tabStock Ledger Entry`
			where item_code=%s and warehouse = %s""",
			(item_code, warehouse))[0][0])

	stock_recon_val = flt(frappe.db.sql("""select sum(stock_value_difference)
			from `tabStock Ledger Entry`
			where item_code=%s and voucher_type = 'Stock Reconciliation'""",
			(item_code))[0][0])

	tot_stock_val = item_stock_val + stock_recon_val

	return tot_stock_val

def get_item_details(filters):
		condition = ''
		value = ()
		if filters.get("item_code"):
				condition = "AND item_code=%s"
				value = (filters["item_code"],)



		items = frappe.db.sql("""select item_group, item_name, stock_uom, purchase_uom, t1.name,conversion_factor, brand, description
				from tabItem t1 JOIN `tabUOM Conversion Detail` t2 where t1.item_code = t2.parent {condition}""".format(condition=condition), value, as_dict=1)

		return dict((d.name, d) for d in items)

def validate_filters(filters):
		if not (filters.get("item_code") or filters.get("warehouse")):
				sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
				if sle_count > 500000:
						frappe.throw(_("Please set filter based on Item or Warehouse"))



@frappe.whitelist()
def check_for_whole_number(bomno):
	return (frappe.db.sql("""select must_be_whole_number from `tabUOM` where name IN (select uom from `tabBOM`where name = %s) """, (bomno))[0][0])

def check_for_whole_number_itemwise(item):
	return (frappe.db.sql("""select must_be_whole_number from `tabUOM` where name IN (select stock_uom from `tabItem`where name = %s) """, (item))[0][0])

def get_Uom_Data(purchase_uom):
	must_be_whole_number = frappe.db.sql("""select must_be_whole_number  from `tabUOM` where uom_name = %s """, (purchase_uom), as_dict=1)
	return must_be_whole_number


@frappe.whitelist()
def make_stock_requisition(args, planning_warehouse, required_date, reference_no):

	global required_date_count
#	if getdate(required_date) == getdate(datetime.now().strftime('%Y-%m-%d')):
	if required_date == getdate(datetime.now().strftime('%Y-%m-%d')):
		if required_date_count == False:
			required_date_count = True
			frappe.throw(_("Required Date is set to today's date, if you still want to proceed click on 'Stock Requisition' again"))

	test_whole_number = check_for_whole_number(bom_for_validation)
	if test_whole_number and float(qty_to_make) % 1 != 0:
		frappe.throw("Quantity to Make should be whole number")
	innerJson_requisition = " "
	innerJson_transfer = " "
	ret = ""

	newJson_transfer = {
	"company": company,
	"doctype": "Stock Requisition",
	"title": "Material Transfer",
	"material_request_type": "Material Transfer",
	"quantity_to_make": qty_to_make,
	"requested_by" : reference_no,
	"items": [
]
}

	newJson_requisition = {
	"company": company,
	"doctype": "Stock Requisition",
	"title": "Purchase",
	"material_request_type": "Purchase",
	"quantity_to_make": qty_to_make,
	"requested_by" : reference_no,
	"items": [
]
}

	no_requisition = 0
	no_transfer = 0
	required = ""
	delta_qty = ""
	whse_map = {}
	empty_desc = []
	empty_uom = []
	for rows in summ_data:
		required = str(rows[10]).strip()
		if required and rows[11] and planning_warehouse != (rows[16]) :
			if whse_map:
				if whse_map.get(planning_warehouse):
					if rows[10] > whse_map.get(planning_warehouse):
						rows[10] = rows[10] - whse_map.get(planning_warehouse)
						#rows[9] = required
						rows[11] = rows[11] - whse_map.get(planning_warehouse)
					else:
						rows[10] = 0
				whse_map.clear()
			item_code = rows[8]
			if rows[10]:
				if rows[3] == "<br>" or rows[3] == "<div><br></div>" or str(rows[3]) == "":
					empty_desc.append(rows[7])
				if rows[6] == "":
					empty_uom.append(rows[8])
				no_transfer = no_transfer + 1
				if rows[10] < rows[11]:
					req_qty = rows[10]
					if req_qty > 0:
						innerJson_transfer ={
						"doctype": "Stock Requisition Item",
						"item_code": rows[8],
						"qty": req_qty,
						"schedule_date": required_date,
						"warehouse":planning_warehouse,
						"uom": rows[6],
						"stock_uom": rows[6],
						"conversion_factor":rows[17],
						"description": rows[3]
				   		}
						newJson_transfer["items"].append(innerJson_transfer)

				if rows[10] >= rows[11]:
					balance_qty = rows[11]
					if balance_qty > 0:
						innerJson_transfer =	{
						"doctype": "Stock Requisition Item",
						"item_code": rows[8],
						"qty": balance_qty,
						"schedule_date": required_date,
						"warehouse":planning_warehouse,
						"uom":rows[6],
						"stock_uom": rows[6],
						"conversion_factor":rows[17],
						"description": rows[3]
				   		}
						newJson_transfer["items"].append(innerJson_transfer)
		else:
			if str(rows[12]).strip():
				whse_map[(rows[12])] = rows[11]

	if no_transfer == 0:
		frappe.msgprint("Planning Warehouse has all the item !! Stock transfer is not required")
	elif curr_stock_balance == 1:
		if empty_uom:
			frappe.throw(_("UOM for  {0} is empty,Please add UOM in Item Master Doctype.").format(frappe.bold(comma_and(empty_uom))))
		if empty_desc:
			frappe.throw(_("Description for  {0} is empty,Please add description in Item Master Doctype.").format(frappe.bold(comma_and(empty_desc))))
		doc = frappe.new_doc("Stock Requisition")
		doc.update(newJson_transfer)
		print "####################-newJson_transfer::", newJson_transfer
		if args == "as a draft":
			doc.save()
		else:
			doc.submit()
		ret = doc.doctype


	
	for rows in summ_data:

		if curr_stock_balance == 1:
			delta_qty = str(rows[12]).strip()
		else:
			delta_qty = str(rows[10]).strip()
		if (delta_qty and float(delta_qty) != 0.0):
			if rows[3] == "<br>" or rows[3] == "<div><br></div>" or str(rows[3]) == "":
				empty_desc.append(rows[8])
			if rows[6] == "":
				empty_uom.append(rows[8])
			no_requisition = no_requisition + 1
			if delta_qty > 0:
				innerJson_requisition =	{
				"doctype": "Stock Requisition Item",
				"item_code": rows[8],
				"qty": delta_qty,
				"schedule_date": required_date,
				"warehouse":planning_warehouse,
				"uom":rows[6],
				"conversion_factor":rows[17],
				"description": rows[3]
		   		}

				newJson_requisition["items"].append(innerJson_requisition)
	del summ_data[:]
	del required
	del test_whole_number
	del delta_qty
	if no_requisition == 0:
		frappe.msgprint("All Items are in Stock !! Stock Requisition is not required ")
	else:
		if empty_uom:
			frappe.throw(_("UOM for  {0} is empty,Please add UOM in Item Master Doctype.").format(frappe.bold(comma_and(empty_uom))))
		if empty_desc:
			frappe.throw(_("Description for  {0} is empty,Please add description in Item Master Doctype.").format(frappe.bold(comma_and(empty_desc))))
		doc = frappe.new_doc("Stock Requisition")
		doc.update(newJson_requisition)
		if args == "as a draft":
			doc.save()
		else:
			doc.submit()
		ret = doc.doctype
	if ret:
		return ret
