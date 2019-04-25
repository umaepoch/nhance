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
       sreq_total_qty = 0
       po_total_qty = 0

       warehouse_qty = get_warehouse_qty(project_warehouse,item_code)
       qty_consumed_in_manufacture= get_stock_entry_quantities(project_warehouse,item_code)

       delta_qty = warehouse_qty - bom_item_qty

       reserve_warehouse_qty = get_warehouse_qty(reserve_warehouse,item_code)

       rw_pb_cons_qty = reserve_warehouse_qty + warehouse_qty + qty_consumed_in_manufacture

       sreq_total_qty = get_sreq_total_qty(item_code,project_name) # have to create project custom field and add to query condition
       po_total_qty = get_po_total_qty(item_code,project_name) # have to create project custom field and add to query condition

       qty_planned_nrec = sreq_total_qty + po_total_qty
       tot_qty_covered =  qty_planned_nrec +  rw_pb_cons_qty

       short_qty =  bom_item_qty - tot_qty_covered

       if short_qty < 0:
         short_qty = 0

       sum_data.append([str(item_code),str(bom_item_qty),str(warehouse_qty),str(delta_qty),
             str(reserve_warehouse_qty),str(qty_consumed_in_manufacture),str(rw_pb_cons_qty),str(sreq_total_qty),str(po_total_qty),str(qty_planned_nrec),
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
   _("Quantity consumed in Manufacturte")+"::150",
   _("RW+PB+Consumed QTY")+"::150",
   _("SREQs  Submitted but not Ordered")+":Link/UOM:90",
   _("PO Quantities Ordered but not Delivered")+"::150",
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

def get_sreq_total_qty(item_code,project_name):
 sreq_datas = frappe.db.sql("""select sri.project, sri.item_code,sri.qty,sri.quantity_to_be_ordered,sri.parent,sri.uom,sri.warehouse,sri.schedule_date,sri.stock_uom,sri.description,sr.docstatus,sr.transaction_date,sr.schedule_date from `tabStock Requisition Item` sri,`tabStock Requisition` sr where sri.item_code=%s  and sri.parent=sr.name and sr.docstatus=1 and sri.project=%s""",(item_code,project_name), as_dict=1)
 sreq_total_qty = 0
 quantity_to_be_ordered = 0

 for sreq_data in sreq_datas:
   if sreq_data['quantity_to_be_ordered']:
     quantity_to_be_ordered = float(sreq_data['quantity_to_be_ordered'])
   sreq_total_qty = sreq_total_qty + quantity_to_be_ordered

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
def get_col_data():
 return sum_data


@frappe.whitelist()
def fetch_project_details(project):
 details = frappe.db.sql("""select start_date,project_warehouse,reserve_warehouse,master_bom,core_team_coordinator,planner from 	`tabProject` where name=%s""", project, as_dict=1)
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
   sreq_qty =c[7]
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
def	make_stock_requisition(project,company,col_data,workflowStatus,required_date):

   col_data = eval(col_data)
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
     short_qty = c[11]
     short_qty = float(short_qty)

     item_data_key = get_item_data(item_code)
     item_data = item_data_key[0]

     innerJson_transfer ={
         "doctype": "Stock Requisition Item",
         "item_code": item_code,
         "qty": c[11],
         "schedule_date": required_date ,
         "warehouse":reserve_warehouse,
         "uom": item_data['stock_uom'],
         "stock_uom": item_data['stock_uom'],
         "description": item_data['description'],
         "sreq_made_from_pmrt":"Yes",
         "project":project
       }
     if short_qty > 0:
       newJson_requisition["items"].append(innerJson_transfer)

   if newJson_requisition["items"]:
         doc = frappe.new_doc("Stock Requisition")
         doc.update(newJson_requisition)
         doc.save()
         """if workflowStatus == "Approved":
           doc.submit()
         else:
           doc.save() """
         ret =  doc.doctype
         return ret
   else:
     return null