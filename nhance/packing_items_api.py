from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words


@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def make_detailed_packing_info_doc(cur_doc_items):
	cur_doc_items = json.loads(cur_doc_items)
	print ("came inside make_detailed_packing_info_doc",cur_doc_items)
	packing_items_json={}
	packing_boxes_json={}
	for item in cur_doc_items :
		item_master_doc = frappe.get_doc("Item", item["item_code"])
		packing_items_json[item["item_code"]]= get_parent_packing_items_list(item_master_doc,item["qty"])
		packing_boxes_json[item["item_code"]]= get_parent_item_box_list(item_master_doc,item["qty"])

	#print "packing_items_json whole",packing_items_json
	#print "packing_boxes_json whole",packing_boxes_json

	dpi = frappe.new_doc("Detailed Packing Info")
	dpi.voucher_type = cur_doc_items[0]["parenttype"]
	dpi.voucher_no = cur_doc_items[0]["parent"]
	#dpi.si_name = cur_doc_items[0]["parent"]
	print ("came next to new doc creation")

	#Detailed Packing Item Child
	dpi.set('packing_details_review', [])
	for parent_item_key, pi_datas in packing_items_json.items(): #iterate over parent_item
		for pi_data in pi_datas :
			 # create Detailed Packing Items doc with child table for each pi_data row=pi_Data
			 dpi_items = dpi.append('packing_details_review', {})
			 dpi_items.parent_item =  parent_item_key
			 dpi_items.packing_item =  pi_data["packing_item"]
			 dpi_items.qty =  pi_data["qty"]
			 dpi_items.item_group = pi_data["packing_item_group"]

	#Detailed Packing Box Child
	dpi.set('detailed_packing_box', [])
	for parent_item_key, pb_datas in packing_boxes_json.items(): #iterate over parent_item  for packing box
		for pb_data in pb_datas :
			 # create Detailed Packing Items doc with child table for each pi_data row=pi_Data
			 dpi_box_row = dpi.append('detailed_packing_box', {})
			 dpi_box_row.packing_box = pb_data["packing_box_name"]
			 dpi_box_row.parent_item =  parent_item_key
			 dpi_box_row.packing_item =  pb_data["packing_item"]
			 dpi_box_row.qty =  pb_data["packing_box_qty"]

	dpi.save(ignore_permissions=True)
	return packing_items_json

def get_parent_packing_items_list(item_master_doc ,doc_qty):
	#packing item collection data
	parent_packing_items_list=[]
	for child_item in item_master_doc.packing_item_configuration :
		child_item_details={}
		child_item_details["packing_item"] = child_item.packing_item
		child_item_details["qty"] = child_item.qty * doc_qty
		child_item_details["packing_item_group"] = child_item.packing_item_group
		parent_packing_items_list.append(child_item_details)
	return parent_packing_items_list

def get_parent_item_box_list(item_master_doc,doc_qty):
	#packing box collection data
	parent_item_box_list = []
	for child_item in item_master_doc.packing_box_configuration :
		packing_box_details = {}
		packing_box_details["packing_box_name"] = child_item.packing_box
		packing_box_details["packing_item"] = child_item.packing_item
		packing_box_details["packing_box_qty"] = child_item.qty * doc_qty
		parent_item_box_list.append(packing_box_details)
	return parent_item_box_list

@frappe.whitelist()
def make_shipment(voucher_no):
	voucher_type = "Sales Invoice"
	tableName = "`tab{} Item`".format(voucher_type)
	items = frappe.db.sql("""
	select
	parent,item_code,item_name,description,qty,uom,conversion_factor,stock_qty,rate,amount
	from
	"""+tableName+"""
	where
	parent = %s""",( voucher_no), as_dict=1)

	dn_name = create_delivery_note(items,voucher_type,voucher_no)

	"""

	ispackingboxescompleted =  frappe.db.get_value(voucher_type, {"name":voucher_no},"pch_ispackingboxescompleted")
	if ispackingboxescompleted:
		dn_name = create_delivery_note(items,voucher_type,voucher_no)
	else:
		frappe.msgprint("Cannot make shipment .Packing boxes are not fully completed", raise_exception=True)
		"""
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
	#create_pboxes_and_items(voucher_type,voucher_no,dn.name)
	return dn.name

@frappe.whitelist()
def test_fun_sur():
	si_name="SINV-00066"
	dpi_name = frappe.db.get_value("Detailed Packing Info", {"si_name":si_name},"name")
	pboxes_and_items_doc = frappe.new_doc("Packing Boxes and Items")
	pboxes_and_items_doc.si_name = si_name
	detailed_packing_info_doc = frappe.get_doc( "Detailed Packing Info",dpi_name )
	pboxes_and_items_doc.set('detailed_packing_box', detailed_packing_info_doc.detailed_packing_box)
	pboxes_and_items_doc.set('pb_and_pi_link', [])
	for dpi_box_row in detailed_packing_info_doc.detailed_packing_box:
		print "dpi_box_row",dpi_box_row
		print "dpi_box_row type",type(dpi_box_row)
		pbox_id = dpi_box_row.packing_box_id
		print "pbox_id",pbox_id
		pbox_custom_doc = frappe.get_doc( "Packed Box Custom",pbox_id )
		packed_box_breif_details_child = pbox_custom_doc.packed_box_breif_details_child
		for row in packed_box_breif_details_child:
			child2 = pboxes_and_items_doc.append('pb_and_pi_link', {})
			child2.packing_box = pbox_id
			child2.packing_item = row.packed_item_link
			print "packed_item_link",row.packed_item_link
	#pboxes_and_items_doc.save(ignore_permissions=True)




@frappe.whitelist()
def make_packing_item_doc_entity(cur_doc_items):
	"""
	create transaction for each quantity in each row of above box
	finsh one complete cycle and show demo by 2 or 3
	then start the same for packing box
	"""




#response came :{"GlassTable":[{"packing_item":"TableStand","packing_item_group":"Packing Items","qty":4},{"packing_item":"TableGlass","packing_item_group":"Packing Items","qty":1}]}
