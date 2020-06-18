# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

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
	columns, data = [], []
	columns = get_columns()
	dpi_pb_child_details = get_dpi_pb_child_details(filters)
	for dpi_pb_child_row in dpi_pb_child_details :
		pb_custom_data = get_pb_custom_data(dpi_pb_child_row["packing_box_id"])
		for pb_custom_child1_row in pb_custom_data :
			data.append([
			dpi_pb_child_row["voucher_type"],
			dpi_pb_child_row["voucher_no"],
			dpi_pb_child_row["name"],
			dpi_pb_child_row["packing_box"],
			dpi_pb_child_row["packing_box_id"],
			pb_custom_child1_row["packing_item"],
			pb_custom_child1_row["actual_qty"],
			pb_custom_child1_row["received_qty"],
			pb_custom_child1_row["status"]
			])
	return columns, data

def get_columns():
    columns = [
	  _("Voucher type")+"::150",
	  _("Voucher no")+"::150",
	  _("DPI")+":Link/Detailed Packing Info:150",
      _("Packing Box")+":Link/Packed Box Custom:150",
	  _("Packing Box ID")+":Link/Packed Box Custom:150",
	  _("PBs Packet Item")+":Link/Item:150",
      _("PBs PI Expected qty")+"::150",
      _("PBs PI Received qty")+"::150",
      _("PB Status")+"::150"
       ]
    return columns

def get_dpi_pb_child_details(filters):
	dpi_name = frappe.db.get_value("Detailed Packing Info", {"voucher_no":filters.voucher_no},"name")
	dpi_pb_child_details = frappe.db.sql("""select dpi.name,dpi.voucher_type,dpi.voucher_no,dpipb.packing_box,dpipb.packing_box_id from `tabDetailed Packing Info` dpi,`tabDetailed Packing Box Child` dpipb where  dpi.name = dpipb.parent and dpi.name = %s""",dpi_name, as_dict=1)
	return dpi_pb_child_details

def get_pb_custom_data(packing_box_id):
	pb_custom_data = frappe.db.sql("""select pbc.status,pbdc.actual_qty,pbdc.received_qty,pbdc.packing_item from `tabPacked Box Custom` pbc,`tabPacked Box Details Child` pbdc where pbc.name = pbdc.parent and pbc.name = %s""", packing_box_id, as_dict=1)
	return pb_custom_data

@frappe.whitelist()
def make_shipment(voucher_type,voucher_no):
	tableName = "`tab{} Item`".format(voucher_type)
	items = frappe.db.sql("""
	select
	parent,item_code,item_name,description,qty,uom,conversion_factor,stock_qty,rate,amount
	from
	"""+tableName+"""
	where
	parent = %s""",( voucher_no), as_dict=1)

	ispackingboxescompleted =  frappe.db.get_value(voucher_type, {"name":voucher_no},"pch_ispackingboxescompleted")
	if ispackingboxescompleted:
		dn_name = create_delivery_note(items,voucher_type,voucher_no)
	else:
		frappe.msgprint("Cannot make shipment .Packing boxes are not fully completed", raise_exception=True)
	return dn_name

def create_delivery_note(items,voucher_type,voucher_no):
	dn = frappe.new_doc("Delivery Note")
	dn.customer = frappe.db.get_value(voucher_type, {"name":voucher_no},"customer")
	dn.set('items', [])
	for item in items :
		dn_items = dn.append('items', {})
		dn_items.item_code =  item["item_code"]
		dn_items.item_name =   item["item_name"]
		dn_items.description =   item["description"]
		dn_items.uom = item["uom"]
		dn_items.qty = item["qty"]
		dn_items.warehouse =  "Stores - EPCH"
		dn_items.target_warehouse =  "Yard - EPCH"
	dn.save(ignore_permissions=True)
	create_pboxes_and_items(voucher_type,voucher_no,dn.name)
	return dn.name

def create_pboxes_and_items(voucher_type,voucher_no,dn_name):
	dpi_name = frappe.db.get_value("Detailed Packing Info", {"voucher_no":voucher_no},"name")
	pboxes_and_items_doc = frappe.new_doc("Packing Boxes and Items")
	pboxes_and_items_doc.voucher_type = voucher_type
	pboxes_and_items_doc.voucher_no = voucher_no
	pboxes_and_items_doc.dn_name = dn_name
	detailed_packing_info_doc = frappe.get_doc( "Detailed Packing Info",dpi_name )
	pboxes_and_items_doc.set('detailed_packing_box', detailed_packing_info_doc.detailed_packing_box)
	pboxes_and_items_doc.set('pb_and_pi_link', [])
	for dpi_box_row in detailed_packing_info_doc.detailed_packing_box:
		pbox_id = dpi_box_row.packing_box_id
		pbox_custom_doc = frappe.get_doc( "Packed Box Custom",pbox_id )
		packed_box_breif_details_child = pbox_custom_doc.packed_box_breif_details_child
		for row in packed_box_breif_details_child:
			child2 = pboxes_and_items_doc.append('pb_and_pi_link', {})
			child2.packing_box = pbox_id
			child2.packing_item = row.packed_item
	pboxes_and_items_doc.save(ignore_permissions=True)
