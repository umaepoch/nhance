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
sum_data = []

def execute(filters=None):
  global sum_data
  sum_data = []
  columns = []
  columns = get_columns()
  master_bom = frappe.db.get_value('Project', filters.get("project"), 'master_bom')
  project_name = frappe.db.get_value('Project', filters.get("project"), 'name')
  company.append(frappe.db.get_value('BOM', master_bom, 'company'))
  project_warehouse =  frappe.db.get_value('Project', filters.get("project"), 'project_warehouse')
  reserve_warehouse =  frappe.db.get_value('Project', filters.get("project"), 'reserve_warehouse')

  if  master_bom and project_warehouse and reserve_warehouse:
    items_data = get__bom_items(master_bom)  #exploded items

    for item_data in sorted(items_data):
      item_code = item_data.item_code
      bom_item_qty = item_data.bi_qty
      warehouse_qty = 0
      reserve_warehouse_qty = 0
      qty_consumed_in_manufacture= 0
      sreq_sub_not_approved = 0
      sreq_sub_not_ordered = 0
      po_total_qty = 0

      warehouse_qty = get_warehouse_qty(project_warehouse,item_code)
      qty_consumed_in_manufacture= get_stock_entry_quantities(project_warehouse,item_code)

      delta_qty = warehouse_qty - bom_item_qty

      reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,item_code)

      rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture

      sreq_sub_not_approved = get_sreq_sub_not_approved(item_code,project_name)
      sreq_sub_not_ordered = get_sreq_sub_not_ordered(item_code,project_name) # have to create project custom field and add to query condition
      po_total_qty = get_po_total_qty(item_code,project_name) # have to create project custom field and add to query condition

      submitted_po = get_submitted_po(item_code,project_name)

      draft_po = get_draft_po(item_code,project_name)
      draft_po = round(float(draft_po),2)
      submitted_po = round(float(submitted_po),2)
      #print "submitted_po----------------",submitted_po


      # qty_planned_nrec = sreq_sub_not_approved + sreq_sub_not_ordered + po_total_qty         ####### old requirment
      qty_planned_nrec = sreq_sub_not_approved + sreq_sub_not_ordered + draft_po + submitted_po    ####### new Requirement
      if qty_planned_nrec < 0:
        qty_planned_nrec = 0
      tot_qty_covered =  qty_planned_nrec +  rw_pb_cons_qty
      short_qty =  bom_item_qty - tot_qty_covered
      if short_qty < 0:
        short_qty = 0
      sum_data.append([str(item_code),str(bom_item_qty),str(warehouse_qty),str(delta_qty),
        str(reserve_warehouse_qty),str(qty_consumed_in_manufacture),str(rw_pb_cons_qty),str(sreq_sub_not_approved),str(sreq_sub_not_ordered),draft_po,submitted_po,str(po_total_qty),str(qty_planned_nrec),
        str(tot_qty_covered),str(short_qty)])

  return columns, sum_data

def get_columns():
    """return columns"""
    columns = [
      _("Item Code")+"::100",
      _("BOM Item Qty")+"::100",
      _("PB WAREHOUSE QTY")+"::100",
      _("DELTA QTY (PB-BOM item qty)")+"::140",
      _("RW WAREHOUSE QTY")+"::100",
      _("Quantity consumed in Manufacture")+"::150",
      _("RW+PB+Consumed QTY")+"::150",
      _("SREQs  Submitted but not Approved")+"::90",
      _("SREQs  Submitted but not Fulfilled")+"::90",#ordered changed to fulfilled
      _("Draft PO Qty ")+"::90",
      _("PO Quantities Ordered but not Delivered")+"::90",
      _("POs Quantities Ordered but not Delivered")+"::150",
      _("Sum Quantity Planned but Not Received Material")+"::150",
      _("Total Quantity Covered")+"::150",
      _("Short Qty (Excess Quantity is reported as 0)")+"::150"
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
    sreq_stock_qty += srq.sreq_stock_qty
    sreq_fulfilled_qty += srq.fulfilled_quantity #jyoti added

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
    columns = []
    columns = get_columns()
    master_bom = frappe.db.get_value('Project', onclick_project, 'master_bom')
    project_name = frappe.db.get_value('Project',onclick_project, 'name')
    company.append(frappe.db.get_value('BOM', master_bom, 'company'))
    project_warehouse =  frappe.db.get_value('Project', onclick_project, 'project_warehouse')
    reserve_warehouse =  frappe.db.get_value('Project', onclick_project, 'reserve_warehouse')

    if  master_bom and project_warehouse and reserve_warehouse:
        items_data = get__bom_items(master_bom)  #exploded items

        for item_data in sorted(items_data):
            item_code = item_data.item_code
            bom_item_qty = item_data.bi_qty
            warehouse_qty = 0
            reserve_warehouse_qty = 0
            qty_consumed_in_manufacture= 0
            sreq_sub_not_approved = 0
            sreq_sub_not_ordered = 0
            po_total_qty = 0

            warehouse_qty = get_warehouse_qty(project_warehouse,item_code)
            qty_consumed_in_manufacture= get_stock_entry_quantities(project_warehouse,item_code)

            delta_qty = warehouse_qty - bom_item_qty

            reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,item_code)

            rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture

            sreq_sub_not_approved = get_sreq_sub_not_approved(item_code,project_name)
            sreq_sub_not_ordered = get_sreq_sub_not_ordered(item_code,project_name) # have to create project custom field and add to query condition
            po_total_qty = get_po_total_qty(item_code,project_name) # have to create project custom field and add to query condition

            qty_planned_nrec = sreq_sub_not_approved + sreq_sub_not_ordered + po_total_qty
            tot_qty_covered =  qty_planned_nrec +  rw_pb_cons_qty

            short_qty =  bom_item_qty - tot_qty_covered

            if short_qty < 0:
              short_qty = 0

            onclick_sum_data.append([str(item_code),str(bom_item_qty),str(warehouse_qty),str(delta_qty),
                  str(reserve_warehouse_qty),str(qty_consumed_in_manufacture),str(rw_pb_cons_qty),str(sreq_sub_not_approved),str(sreq_sub_not_ordered),str(po_total_qty),str(qty_planned_nrec),
                  str(tot_qty_covered),str(short_qty)])
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
   item_code = c[0]
   bom_item_qty = c[1]
   bom_item_qty = float(bom_item_qty)
   sreq_qty =c[9]
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
def	make_stock_requisition(project,company,col_data,required_date,master_bom):


    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ PMRT cache Bug sum_data :",sum_data

    col_data = eval(col_data)
    #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ PMRT cache Bug  col_data ",col_data
    reserve_warehouse =  frappe.db.get_value('Project',project , 'reserve_warehouse')

    innerJson_requisition = " "
    innerJson_transfer = " "
    ret = ""
    newJson_requisition = {
    "company": company ,
    "doctype": "Stock Requisition",
    "title": "Purchase",
    "material_request_type": "Purchase",
    "workflow_state": "Pending Approval",
    "requested_by":project,
    "items": []
    }
    for c in col_data:

        item_code = c[0]
        short_qty = c[12]
        short_qty = float(short_qty)

        item_data_key = get_item_data(item_code)
        item_data = item_data_key[0]

        innerJson_transfer ={
        "doctype": "Stock Requisition Item",
        "item_code": item_code,
        "qty": c[12],
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

