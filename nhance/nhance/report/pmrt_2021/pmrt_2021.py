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
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

company = []

def execute(filters=None):
    data = []
    columns = []
    columns = get_columns()
    master_bom = frappe.db.get_value('Project', filters.get("project"), 'master_bom')
    project_name = frappe.db.get_value('Project', filters.get("project"), 'name')
    company.append(frappe.db.get_value('BOM', master_bom, 'company'))
    project_warehouse =  frappe.db.get_value('Project', filters.get("project"), 'project_warehouse')
    reserve_warehouse =  frappe.db.get_value('Project', filters.get("project"), 'reserve_warehouse')

    if  master_bom and project_warehouse and reserve_warehouse:
        items_data = get__bom_items(master_bom)  # getting exploded items from master bom choosed in this project
        for item_data in items_data:
          item_code = item_data.item_code
          bom_item_qty = item_data.bi_qty
          sum_data_dic = get_sum_data_dic (item_code,bom_item_qty,master_bom,project_name,company,project_warehouse,reserve_warehouse)
          data.append(sum_data_dic)

    return columns, data

def get_sum_data_dic (item_code,bom_item_qty,master_bom,project_name,company,project_warehouse,reserve_warehouse):
    warehouse_qty = 0
    reserve_warehouse_qty = 0
    qty_consumed_in_manufacture = 0
    sreq_sub_not_approved = 0
    sreq_sub_not_ordered = 0
    po_total_qty = 0

    warehouse_qty = get_warehouse_qty(project_warehouse,item_code)  # get stock qty of project wh ac to wh and item code

    qty_consumed_in_manufacture = get_stock_entry_quantities(project_warehouse, item_code)  # sum of tabStock Entry quantyties ac to project_warehouse adn itemcode

    delta_qty = warehouse_qty - bom_item_qty  # stock qty of that item - qty required for that bom

    reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,item_code)  # get stock qty of reserve wh ac to wh and item code

    rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture  # sum of stocks in project and reserve wh qty and stock entry qty amde for manufacture

    sreq_sub_not_approved = get_sreq_sub_not_approved(item_code,project_name)  # not approved qtys in stock requisition ac to item code and stock requisition

    sreq_sub_not_ordered = get_sreq_sub_not_ordered(item_code,project_name)  # returnong total submitted sreq qty - (po qty + fulfilled qty ) .so that we will get to know how much need to order or transfer

    po_total_qty = get_po_total_qty(item_code,project_name)  # sum of (stock qty - recived qty) in all submitted po acc to item code and project name

    # not_in_col_Data_function_start_surN
    submitted_po = get_submitted_po(item_code, project_name)
    submitted_po = round(float(submitted_po), 2)

    draft_po = get_draft_po(item_code, project_name)
    draft_po = round(float(draft_po), 2)
    # not_in_col_Data_function_end_surN
    # print "submitted_po----------------",submitted_po

    # qty_planned_nrec = sreq_sub_not_approved + sreq_sub_not_ordered + po_total_qty         ####### old requirment
    qty_planned_nrec = sreq_sub_not_approved + sreq_sub_not_ordered + draft_po + submitted_po  ####### new Requirement (but not changed this in get col data_surN)
    if qty_planned_nrec < 0:
        qty_planned_nrec = 0
    tot_qty_covered = qty_planned_nrec + rw_pb_cons_qty
    short_qty = bom_item_qty - tot_qty_covered  # short_qty_got changed due to new requiremnet_surN
    if short_qty < 0:
        short_qty = 0

    #new pmrt_2021 changs_start
    """
    Stock Requisition (Approved Buying Price)
    Valuation Rate at the Generic Stores
    Valuation Rate in the Reserve Warehouse for the Project
    """
    budgeted_unit_rate = get_budgeted_unit_rate(item_code, project_name ,reserve_warehouse)
    current_val_rate = get_current_val_rate(item_code, project_name ,reserve_warehouse)
    purchase_price = get_purchase_price(item_code, project_name ,reserve_warehouse)
    fullfilled_rate = get_fullfilled_rate(item_code, project_name ,project_warehouse)

    #new pmrt_2021 changs_end


    sum_data_dic ={}
    sum_data_dic["item_code"] = str(item_code)
    sum_data_dic["bom_item_qty"] = str(bom_item_qty)
    sum_data_dic["project_warehouse_qty"] = str(warehouse_qty)
    sum_data_dic["delta_qty"] = str(delta_qty)

    sum_data_dic["reserve_warehouse_qty"] = str(reserve_warehouse_qty)
    sum_data_dic["qty_consumed_in_manufacture"] = str(qty_consumed_in_manufacture)
    sum_data_dic["rw_pb_cons_qty"] = str(rw_pb_cons_qty)

    sum_data_dic["sreq_sub_not_approved"] = str(sreq_sub_not_approved)
    sum_data_dic["sreq_sub_not_ordered"] = str(sreq_sub_not_ordered)
    sum_data_dic["draft_po"] = draft_po
    sum_data_dic["submitted_po"] = submitted_po
    sum_data_dic["po_total_qty"] = str(po_total_qty)

    sum_data_dic["qty_planned_nrec"] = str(qty_planned_nrec)
    sum_data_dic["tot_qty_covered"] = str(tot_qty_covered)
    sum_data_dic["short_qty"] = str(short_qty)

    sum_data_dic["project_wh"] = str(project_warehouse)
    sum_data_dic["reserve_wh"] = str(reserve_warehouse)
    sum_data_dic["budgeted_unit_rate"] = str(budgeted_unit_rate)
    sum_data_dic["current_val_rate"] = str(current_val_rate)
    sum_data_dic["purchase_price"] = str(purchase_price)
    sum_data_dic["fullfilled_rate"] = str(fullfilled_rate)
    sum_data_dic["budgetted_cost"] =  bom_item_qty *  budgeted_unit_rate #Budgeted Cost = BOM Item Qty *  Budgeted Unit Rate for Item (Stock UOM)
    sum_data_dic["valuation_cost"] = get_valuation_cost(bom_item_qty,fullfilled_rate,purchase_price,current_val_rate)  #Valuation Cost Fulfilled or Expected =BOM Item Qty *   Fulfilled Rate of Item

    return sum_data_dic



def get_columns():
	columns = [
		{"label": ("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
		{"label": ("BOM Item Qty"), "fieldname": "bom_item_qty", "width": 100},
		{"label": ("PB WAREHOUSE QTY"), "fieldname": "project_warehouse_qty", "width": 100},
		{"label": ("DELTA QTY (PB-BOM item qty)"), "fieldname": "delta_qty", "width": 100},

		{"label": ("RW WAREHOUSE QTY"), "fieldname": "reserve_warehouse_qty",  "width": 100},
		{"label": ("Quantity consumed in Manufacture"), "fieldname": "qty_consumed_in_manufacture",   "width": 100},
		{"label": ("RW+PB+Consumed QTY"), "fieldname": "rw_pb_cons_qty",  "width": 100},

		{"label": ("SREQs  Submitted but not Approved"), "fieldname": "sreq_sub_not_approved", "width": 100},
		{"label": ("SREQs  Submitted but not Fulfilled"), "fieldname": "sreq_sub_not_ordered",  "width": 100},
		{"label": ("Draft PO Qty"), "fieldname": "draft_po",  "width": 100},
		{"label": ("PO Quantities Ordered but not Delivered"), "fieldname": "submitted_po", "width": 100},
		{"label": ("POs Quantities Ordered but not Delivered"), "fieldname": "po_total_qty",  "width": 100},

		{"label": ("Sum Quantity Planned but Not Received Material"), "fieldname": "qty_planned_nrec", "width": 100},
		{"label": ("Total Quantity Covered"), "fieldname": "tot_qty_covered",  "width": 100},
		{"label": ("Short Qty (Excess Quantity is reported as 0)"), "fieldname": "short_qty", "width": 100},
		{"label": ("Project WH"), "fieldname": "project_wh", "width": 100},
		{"label": ("Reserve Wh"), "fieldname": "reserve_wh", "width": 100},
        {"label": ("Budgeted Unit Rate for Item(Stock UOM)"), "fieldname": "budgeted_unit_rate", "width": 100},
        {"label": ("Current Valuation Rate of Item(Stock UOM)"), "fieldname": "current_val_rate", "width": 100},
        {"label": ("Purchase Price of Item"), "fieldname": "purchase_price", "width": 100},
        {"label": ("Fulfilled Rate of Item"), "fieldname": "fullfilled_rate", "width": 100},
        {"label": ("Budgeted Cost"), "fieldname": "budgetted_cost", "width": 100},
        {"label": ("Valuation Cost Fulfilled or Expected"), "fieldname": "valuation_cost", "width": 100}
    ]

	return columns

def get__bom_items(master_bom):
     return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code, bi.stock_qty as bi_qty from `tabBOM` bo, `tabBOM Explosion Item` bi where bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1"and bi.parent = '%s' order by bo.name, bi.item_code""" % master_bom, as_dict=1)

def get_warehouse_qty(warehouse,item_code):
 whse_qty = 0
 details = frappe.db.sql("""select actual_qty from `tabBin` where warehouse=%s and item_code=%s and actual_qty > 0 """, (warehouse,item_code), as_dict=1)
 if len(details)!=0:
   if details[0]['actual_qty'] is not None:
     whse_qty = details[0]['actual_qty']
 return whse_qty

def get_stock_entry_quantities(warehouse,item_code):
    total_qty = 0
    po_details = {}
    qty_consumed_in_manufacture = 0

    details = frappe.db.sql("""select sed.item_code,sed.qty,se.purpose from `tabStock Entry Detail` sed,
        `tabStock Entry` se where sed.item_code=%s and sed.s_warehouse=%s and se.purpose='Manufacture' and
        sed.parent=se.name and se.docstatus=1""", (item_code,warehouse), as_dict=1)

    if len(details)!=0:
      for entries in details:
        if entries['qty'] is None:
          qty = 0
        else:
          qty = float(entries['qty'])
        total_qty = total_qty + qty
    return total_qty

def get_sreq_sub_not_approved(item_code,project_name):
    total_not_appr_qty = 0
    not_approved_qty = 0
    sreq_datas = frappe.db.sql("""select
                                        sri.project, sri.item_code,sri.qty
                                  from
                                        `tabStock Requisition Item` sri,`tabStock Requisition` sr
                                  where
                                        sri.item_code=%s  and sri.parent=sr.name
                                        and sr.docstatus= 0 and sri.project=%s
                                        and sr.workflow_state = 'Pending Approval' """,(item_code,project_name), as_dict=1)
    #print "PMRT new total_not_appr_qtysreq_datas ",sreq_datas

    for sreq_data in sreq_datas:
        if sreq_data['qty']:
            not_approved_qty = float(sreq_data['qty'])
        total_not_appr_qty = total_not_appr_qty + not_approved_qty

    return total_not_appr_qty

#approved_buying_price_rate of sreq
#Valuation Rate at the Generic Stores
#Valuation Rate in the Reserve Warehouse for the Project
#if none of above not exists return 0 for now

def  get_valuation_cost(bom_item_qty,fullfilled_rate,purchase_price,current_val_rate) :
    valuation_cost = 0
    if fullfilled_rate > 0 :
        valuation_cost = bom_item_qty * fullfilled_rate
        return valuation_cost
    elif purchase_price > 0 :
        valuation_cost = bom_item_qty * purchase_price
        return valuation_cost
    elif current_val_rate > 0 :
        valuation_cost = bom_item_qty * current_val_rate
        return valuation_cost
    else:
        return valuation_cost

def get_sreq_item_data(item_code, project_name) :
    sreq_datas = frappe.db.sql("""select
                                               budgeted__rate,approved_buying_price_rate
                                          from
                                                `tabStock Requisition Item` sri,`tabStock Requisition` sr
                                          where
                                                sri.item_code=%s  and sri.parent=sr.name 
                                                and sr.docstatus= 1 and sri.project=%s""",
                               (item_code, project_name), as_dict=1)
    return sreq_datas

def get_budgeted_unit_rate(item_code, project_name,reserve_warehouse):

    avg_approved_buying_price = 0
    sreq_datas = get_sreq_item_data(item_code, project_name)

    if sreq_datas and sreq_datas[0]["approved_buying_price_rate"] > 0:
        avg_approved_buying_price = sreq_datas[0]["approved_buying_price_rate"]
        return avg_approved_buying_price

    elif  sreq_datas and  sreq_datas[0]["budgeted__rate"] > 0 : #if approve_price of sreq not exists
        avg_approved_buying_price = sreq_datas[0]["budgeted__rate"]
        return avg_approved_buying_price
    else:
        return avg_approved_buying_price

"""
Valuation Rate at the Generic Stores
Valuation Rate in the Reserve Warehouse for the Project
Stock Requisition (Approved Buying Price)
"""

def  get_wh_val_rate(item_code, warehouse) :
    sle_data = frappe.db.sql("""select
                                               item_code,valuation_rate,warehouse
                                          from
                                                `tabStock Ledger Entry` sl
                                          where
                                                sl.item_code=%s  and sl.warehouse =%s and sl.actual_qty >= 0  order by creation desc limit 1
                                               """,
                             (item_code, warehouse), as_dict=1)

    return sle_data[0]["valuation_rate"] if sle_data else None

def get_current_val_rate(item_code, project_name ,reserve_warehouse):
    cur_val_rate = 0
    generic_price_wh = frappe.db.get_single_value("Nhance Settings", "pmrt_generic_wh")

    if get_wh_val_rate(item_code, generic_price_wh) :
        cur_val_rate = get_wh_val_rate(item_code, generic_price_wh)
        return cur_val_rate
    elif  get_wh_val_rate(item_code, reserve_warehouse) :
        cur_val_rate = get_wh_val_rate(item_code, reserve_warehouse)
        return cur_val_rate
    else:
        return cur_val_rate

"""
Incoming Rate For Purchase Transactions (Purchase Receipt or Purchase Invoice) for Reserve Warehouse
Incoming Rate For Purchase Transactions (Purchase Receipt or Purchase Invoice) for Generic Warehouse
"""
def get_purchase_price(item_code, project_name ,reserve_warehouse):
    purchase_price = 0
    generic_price_wh = frappe.db.get_single_value("Nhance Settings", "pmrt_generic_wh")
    reserve_wh_purchase_transaction_sle_data = get_purchase_transaction_sle_data(item_code, reserve_warehouse)
    if reserve_wh_purchase_transaction_sle_data :
        purchase_price = get_sle_data_weighted_average(reserve_wh_purchase_transaction_sle_data,"incoming_rate")
        return purchase_price
    else:
        generic_wh_purchase_transaction_sle_data = get_purchase_transaction_sle_data(item_code, generic_price_wh)
        if generic_wh_purchase_transaction_sle_data:
            purchase_price = get_sle_data_weighted_average(generic_wh_purchase_transaction_sle_data, "incoming_rate")
            return purchase_price
        else:
            return purchase_price

"""
Incoming Rate for +ve Actual Qty for Reserve Warehouse
"""
def get_fullfilled_rate(item_code, project_name ,project_warehouse) :
    fullfilled_rate = 0
    project_wh_sle_data = get_inward_stock_ledger_entry_data(item_code, project_warehouse)
    if project_wh_sle_data:
        fullfilled_rate = get_sle_data_weighted_average(project_wh_sle_data, "incoming_rate")
        return fullfilled_rate
    else:
        return fullfilled_rate



def get_sle_data_weighted_average(sle_data ,rate_field) :
    sum_up_price_temp = 0
    sum_down_price_temp = 0

    for sle_dic in sle_data:
        if sle_dic.get(rate_field) > 0 : #not considering transaction have rate field as 0 in weighted  average calculation
            price_temp = sle_dic.get("actual_qty") * sle_dic.get(rate_field)
            sum_up_price_temp += price_temp
            sum_down_price_temp += sle_dic.get("actual_qty")

    if sum_up_price_temp > 0 and  sum_down_price_temp > 0 :
        weighted_average_price = sum_up_price_temp / sum_down_price_temp
    else:
        weighted_average_price = 0
    return weighted_average_price

def get_purchase_transaction_sle_data(item_code, warehouse):
    sle_data = frappe.db.sql("""select
                                           item_code,actual_qty,incoming_rate,valuation_rate,warehouse
                                      from
                                            `tabStock Ledger Entry` sl
                                      where
                                            sl.item_code=%s  and sl.warehouse =%s and sl.actual_qty >= 0 and sl.voucher_type in ('Purchase Receipt','Purchase Invoice')
                                           """,
                               (item_code, warehouse),as_dict=1)
    return sle_data

def get_inward_stock_ledger_entry_data(item_code, warehouse):
    sle_data = frappe.db.sql("""select
                                           item_code,actual_qty,incoming_rate,valuation_rate,warehouse
                                      from
                                            `tabStock Ledger Entry` sl
                                      where
                                            sl.item_code=%s  and sl.warehouse =%s and sl.actual_qty >= 0
                                           """,
                               (item_code, warehouse),as_dict=1)
    return sle_data


def get_sreq_sub_not_ordered(item_code,project_name):
    sreq_datas = frappe.db.sql("""select sri.project, sri.item_code,sri.qty,sri.stock_qty,sri.fulfilled_quantity,sri.quantity_to_be_ordered,sri.parent,sri.uom,sri.warehouse,sri.schedule_date,sri.stock_uom,sri.description,sr.docstatus,sr.transaction_date,sr.schedule_date from `tabStock Requisition Item` sri,`tabStock Requisition` sr where sri.item_code=%s  and sri.parent=sr.name and sr.docstatus=1 and sri.project=%s""",(item_code,project_name), as_dict=1)
    #print "sreq_datas---------------",sreq_datas
    po_draft_qty = frappe.db.sql("""select qty,parent,stock_qty from `tabPurchase Order Item` where item_code = %s and project = %s and docstatus = 0""",(item_code,project_name), as_dict=1)
    po_submitted_qty = frappe.db.sql("""select qty,parent,stock_qty from `tabPurchase Order Item` where item_code = %s and project = %s and docstatus = 1""",(item_code,project_name), as_dict=1)

    sreq_total_qty = 0
    quantity_to_be_ordered = 0
    #print "total db data",sreq_datas
    '''
    for sreq_data in sreq_datas:
        if sreq_data['quantity_to_be_ordered']:
              quantity_to_be_ordered = float(sreq_data['quantity_to_be_ordered'])
              sreq_total_qty = sreq_total_qty + quantity_to_be_ordered
              print "Yes quantity_to_be_ordered is there ::",sreq_data['item_code'],quantity_to_be_ordered
              print "sreq_total_qty from loop",sreq_data['item_code'], sreq_total_qty
	'''
    draft_qty = 0
    submitted_qty = 0
    sreq_qty = 0
    sreq_stock_qty=0
    sreq_fulfilled_qty=0#jyoti added
    for srq in sreq_datas:
      sreq_qty += srq.qty
      sreq_stock_qty += srq.stock_qty
      sreq_fulfilled_qty += srq.fulfilled_quantity#jyoti added
    for drft in po_draft_qty:
        if drft:
            draft_qty += drft.stock_qty
    for submit in po_submitted_qty:
      if submit:
        submitted_qty += submit.stock_qty
    total_po_qty = draft_qty + submitted_qty

    sreq_total_qty = 0.0
    if len(sreq_datas) > 0:
	#sreq_total_qty = sreq_stock_qty -total_po_qty
    	sreq_total_qty = sreq_stock_qty -(total_po_qty+sreq_fulfilled_qty)#jyoti changed formula
    if sreq_total_qty < 0:
        sreq_total_qty =0
    sreq_total_qty = round(float(sreq_total_qty),2)
    #returnong total submitted sreq qty - (po qty + fulfilled qty ) .so that we will get to know how much need to order or transfer
    return sreq_total_qty


def get_po_total_qty(item_code,project_name):
 po_total_qty = 0
 po_datas = frappe.db.sql("""select po.name,poi.item_code,poi.qty,poi.project,poi.project,poi.received_qty,poi.conversion_factor,poi.stock_qty  from `tabPurchase Order` po ,`tabPurchase Order Item` poi where po.name=poi.parent and po.docstatus=1 and po.status != 'Closed' and poi.item_code=%s and poi.project = %s""",(item_code,project_name), as_dict=1)
 for po_data in po_datas:
   calculated_qty = po_data['stock_qty'] - ( po_data['received_qty'] * po_data['conversion_factor'] )
   calculated_qty = round(calculated_qty,2)
   po_total_qty = po_total_qty + calculated_qty
 return po_total_qty


def  get_item_data(item_code):
 item_data =  frappe.db.sql("""select *  from `tabItem` where item_code = %s """,item_code ,as_dict=1)
 return  item_data

def get_master_bom_qty(master_bom):
 master_bom_qty_key =  frappe.db.sql("""select quantity from `tabBOM` where name= %s; """,master_bom ,as_dict=1)
 master_bom_qty = master_bom_qty_key[0]['quantity']

 return master_bom_qty




@frappe.whitelist()
def get_col_data(onclick_project):
    onclick_sum_data = []
    master_bom = frappe.db.get_value('Project', onclick_project, 'master_bom')
    project_name = frappe.db.get_value('Project',onclick_project, 'name')
    company.append(frappe.db.get_value('BOM', master_bom, 'company'))
    project_warehouse =  frappe.db.get_value('Project', onclick_project, 'project_warehouse')
    reserve_warehouse =  frappe.db.get_value('Project', onclick_project, 'reserve_warehouse')

    if  master_bom and project_warehouse and reserve_warehouse:
        items_data = get__bom_items(master_bom)  #exploded items

        for item_data in items_data:
            item_code = item_data.item_code
            bom_item_qty = item_data.bi_qty
            sum_data_dic = get_sum_data_dic(item_code, bom_item_qty, master_bom, project_name, company,
                                            project_warehouse, reserve_warehouse)
            onclick_sum_data.append(sum_data_dic)
    return onclick_sum_data





@frappe.whitelist()
def fetch_project_details(project):
 details = frappe.db.sql("""select start_date,project_warehouse,reserve_warehouse,master_bom from 	`tabProject` where name=%s""", project, as_dict=1)
 return details

@frappe.whitelist()
def	 get_workflowStatus(master_bom,col_data):
 col_data = eval(col_data)
 workflowStatus_list = []
 workflowStatus = ""
 bom_qty = get_master_bom_qty(master_bom)

 for c in col_data:
   item_code = c.get("item_code")
   bom_item_qty = c.get("bom_item_qty")
   bom_item_qty = float(bom_item_qty)
   sreq_qty =c.get("po_total_qty")
   sreq_qty = float(sreq_qty)

   differnce = (bom_qty*bom_item_qty)-sreq_qty
   differnce = 5

   if differnce > 0:
     workflowStatus_list.append("Approved")
   else:
     workflowStatus_list.append("Pending Approval")

 if "Pending Approval" in workflowStatus_list:
   workflowStatus = "Pending Approval"
 else:
   workflowStatus = "Approved"

 return workflowStatus


@frappe.whitelist()
def make_stock_requisition(project,company,col_data,required_date,master_bom):


    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ PMRT cache Bug sum_data :",sum_data

    col_data = eval(col_data)
    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ PMRT cache Bug  col_data ",col_data
    reserve_warehouse =  frappe.db.get_value('Project',project , 'reserve_warehouse')

    innerJson_requisition = " "
    innerJson_transfer = " "
    newJson_requisition = ""
    ret = ""
    workflow = frappe.get_all("Workflow",filters={"Document_type": "Stock Requisition" , "is_active":1}, fields=["is_active","name"])
    if workflow:
	    newJson_requisition = {
	    "company": company ,
	    "doctype": "Stock Requisition",
	    "title": "Purchase",
	    "material_request_type": "Purchase",
	    "workflow_state": "Pending Approval",
	    "requested_by":project,
	    "items": []
	    }
    else:
        newJson_requisition = {
          "company": company ,
          "doctype": "Stock Requisition",
          "title": "Purchase",
          "material_request_type": "Purchase",
          "docstatus": 1,
          "requested_by":project,
          "items": []
          }
    for c in col_data:

        item_code = c.get("item_code")
        short_qty = c.get("short_qty")
        short_qty = float(short_qty) #not updated yet because of new requirment

        item_data_key = get_item_data(item_code)
        item_data = item_data_key[0]

        innerJson_transfer ={
        "doctype": "Stock Requisition Item",
        "item_code": item_code,
        "qty": c.get("short_qty"),
        "schedule_date": required_date ,
        "warehouse":reserve_warehouse,
        "uom": item_data['stock_uom'],
        "stock_uom": item_data['stock_uom'],
        "description": item_data['description'],
        "sreq_made_from_pmrt":"Yes",
        "project":project,
        "pch_bom_reference": master_bom
        }
        #print "pch_bom_reference checking innerJson_transfer**********",innerJson_transfer
        if short_qty > 0:
            newJson_requisition["items"].append(innerJson_transfer) #end of for

    #print "pch_bom_reference checking newJson_requisition**********",newJson_requisition

    if newJson_requisition["items"]:
        doc = frappe.new_doc("Stock Requisition")
        doc.update(newJson_requisition)
        doc.save()
        """if workflowStatus == "Approved":  #check get_workflowStatus fun in js side for future purpose
        doc.submit()
        else:
        doc.save() """
        ret =  doc.doctype
        return ret
    else:
        return "failed"

def get_submitted_po(item_code,project_name):
	submitted = frappe.db.sql("""select qty,stock_qty, parent, item_code, project from `tabPurchase Order Item` where item_code = %s and project = %s and docstatus = 1""",(item_code, project_name),as_dict=1)
	#print "submitted------------------",submitted
	total_submitted_qty = 0
	for purchase in submitted:
		if purchase:
			total_submitted_qty += purchase.stock_qty
		else:
			total_submitted_qty += 0
	#print "total_submitted_qty---------------",total_submitted_qty
	return total_submitted_qty

def get_draft_po(item_code,project_name):
	draft = frappe.db.sql("""select qty,stock_qty, parent, item_code, project from `tabPurchase Order Item` where item_code = %s and project = %s and docstatus = 0""",(item_code, project_name),as_dict=1)
	#print "draft------------------",draft
	total_draft_qty = 0
	for purchase in draft:
		if purchase:
			total_draft_qty += purchase.stock_qty
		else:
			total_draft_qty += 0
	#print "total_draft_qty---------------",total_draft_qty
	return total_draft_qty

"""
what is fullfilled qty

same function for both
"""

"""
col data and execute short_qty calculation are different need to fix that

check with jay for column before short qty git changed in new requirement but not updated in col data function

follow the comments ends with

   _("Sum Quantity Planned but Not Received Material")+"::150",
      _("Total Quantity Covered")+"::150",
      _("Short Qty (Excess Quantity is reported as 0)")+"::150"

Column name ("Sum Quantity Planned but Not Received Material") - column funtionality has been changed in last update .so that next 2 columns values also got changed .But the data which we use to make stock reuistion has not updated with same new column funcionality,that was still in previous version .
Because of this you may end up requesting wrong qty in stock requisition from what you see on report .

i am going to fix this with  by writting a common functionality for both showing report data and stock requisition data

"""

"""
sreq js functionality
on submit updating qty to be order on stock requisition fro m db side


fulfilled qty
qty to be order understand this 2 functionalities
now i am good to enhance things on pmrt


"""
