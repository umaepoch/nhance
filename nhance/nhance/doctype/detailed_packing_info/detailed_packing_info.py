# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class DetailedPackingInfo(Document):
	pass
ID_CHARECTER="/"

#create a json {packing_item :[id1,id2]}
#packing_items_data (detailed packing info first child table)
@frappe.whitelist()
def create_packing_item_custom_doc(packing_items_data,voucher_type,voucher_no):
	packing_items_data = json.loads(packing_items_data)
	packed_item_id_json ={}
	#print "came inside make_packing_item_doc",packing_items_data
	dpi_name = packing_items_data[0]["parent"]

	for packing_item_data in packing_items_data:
		packing_id_list = []  #all packing ids for each row
		packing_item_qty = packing_item_data["qty"]
		for i in range(packing_item_qty): #change it to range of packing_id list
			pit = frappe.new_doc("Packed Item Custom")
			pit.parent_item = packing_item_data["parent_item"]
			pit.voucher_type = voucher_type
			pit.voucher_no = voucher_no
			pit.packing_item = packing_item_data["packing_item"]
			pit.qty = 1 #one one each as of now later it will change ac to packing item config
			pit.packing_item_group = packing_item_data["item_group"]
			pit.current_warehouse =  packing_item_data["pi_progress_warehouse"]
			pit.current_rarb_id =  packing_item_data["rarb_location_pwh"]
			pit.save(ignore_permissions=True)
			#print ("Packed Item Custom name ",pit.name)
			packing_id_list.append(pit.name)
		create_material_rec(packing_item_data["packing_item"],packing_item_qty,packing_id_list,packing_item_data["pi_progress_warehouse"])
		packed_item_id_json[packing_item_data["packing_item"]] = packing_id_list
	dpi_details = {"voucher_type":voucher_type,"voucher_name":voucher_no,"dpi_name":dpi_name,"packed_item_id_json":packed_item_id_json,"dpi_packing_items_data":packing_items_data}
	update_packingId_in_detailedPackingInfo(dpi_name,packed_item_id_json)
	#print ("create pi inpection called**",dpi_details["packed_item_id_json"])
	create_pi_inspection(dpi_details)
	return "packing item transactions have been created"




@frappe.whitelist()
def create_packing_box_custom_doc(packing_boxes_data,packing_items_data,voucher_type,voucher_no):
	#need to add box's qty in future
	packing_boxes_data = json.loads(packing_boxes_data)
	packing_items_data = json.loads(packing_items_data)
	#print "came inside create_packing_box_custom_doc",packing_items_data
	dpi_name = packing_boxes_data[0]["parent"]
	#packing_box_wise_data = {pb1:[{},{}],pb2:[{}]}
	packing_box_wise_data = {}


	for packing_box_data in packing_boxes_data:
		if packing_box_wise_data.get(packing_box_data["packing_box"]):
			packing_box_wise_data[packing_box_data["packing_box"]].append(packing_box_data)
		else:
			packing_box_wise_data[packing_box_data["packing_box"]] = [ packing_box_data ]

	packing_box_id_json = {}

	for packing_box_name, packing_box_datas in packing_box_wise_data.items():
		print("pb_location_debug packing_box_datas",packing_box_datas)
		material_transfer_item_rows_list = []
		pbc = frappe.new_doc("Packed Box Custom")
		packing_box_status = "Completed"
		pbc.packing_box =  packing_box_name
		pbc.voucher_type = voucher_type
		pbc.voucher_no = voucher_no
		pbc.current_warehouse = packing_box_datas[0]["pb_progress_warehouse"]
		pbc.current_rarb_id = packing_box_datas[0]["pb_rarb_location_pwh"]

		pbc.set('packed_box_details_child', [])
		for packing_box_data in packing_box_datas:  # each packing item row inside packing box
			#include for loop later
			material_transfer_item_row_dic = {}
			material_transfer_item_row_dic["item_code"] = packing_box_data["packing_item"]
			material_transfer_item_row_dic["qty"] = packing_box_data["accepted_qty"]
			material_transfer_item_row_dic["s_wh"] = get_pi_wh(packing_items_data,packing_box_data["packing_item"])
			material_transfer_item_row_dic["t_wh"] = packing_box_data["pb_progress_warehouse"]
			material_transfer_item_row_dic["serial_no_list"] = packing_box_data["packing_id"]
			material_transfer_item_rows_list.append( material_transfer_item_row_dic );

			pbc_child_row1 = pbc.append('packed_box_details_child', {})
			pbc_child_row1.parent_item = packing_box_data["parent_item"]
			pbc_child_row1.packing_item = packing_box_data["packing_item"]
			pbc_child_row1.received_qty = packing_box_data["accepted_qty"]
			pbc_child_row1.actual_qty = packing_box_data["qty"]
			pbc_child_row1.packing_id = packing_box_data["packing_id"]

			if packing_box_data["qty"] >  packing_box_data["accepted_qty"] :
				packing_box_status = "Partially Completed"

		pbc.status = packing_box_status

		pbc.set('packed_box_breif_details_child', [])
		for packing_box_data in packing_box_datas:
			#include for loop later
			packing_id_str = packing_box_data["packing_id"]
			packing_id_list = list(packing_id_str.split("\n"))
			#print "packed_box_breif_details_child**********",packing_id_list
			for packing_id in packing_id_list:
				pbc_child_row2 = pbc.append('packed_box_breif_details_child', {})
				pbc_child_row2.parent_item = packing_box_data["parent_item"]
				pbc_child_row2.packing_item = packing_box_data["packing_item"]
				pbc_child_row2.packed_item = packing_id.strip()
				pbc_child_row2.packed_item_link = frappe.db.get_value("Packed Item Custom", {"packing_id":packing_id.strip()},"name")

		pbc.save(ignore_permissions=True)
		packing_box_id_list = [pbc.name] #need to change this after pbox qty get added
		pbox_qty = 1  #need to change this after pbox qty get added
		create_material_rec(packing_box_name,pbox_qty,packing_box_id_list,packing_box_datas[0]["pb_progress_warehouse"])
		#create_material_transfer(material_transfer_item_rows_list)
		create_material_issue(material_transfer_item_rows_list)
		packing_box_id_json[packing_box_name] = pbc.name
		if(frappe.get_doc( "Packed Box Custom",pbc.name )) :
			update_packingBox_in_packed_item_custom(pbc.name,packing_id_list) #one the box is created,box's packing items doc will be updated by there packing box id

	update_packingBoxId_in_detailedPackingInfo(dpi_name,packing_box_id_json)
	#updating box id on dpi and packed item custom
	dpi_details = {"voucher_type":voucher_type,"voucher_name":voucher_no,"dpi_name":dpi_name,"packing_box_id_json":packing_box_id_json,"packing_boxes_data":packing_boxes_data}
	create_pbi_inspection(dpi_details)
	return "packing box transactions have been created"

def get_pi_wh(packing_items_data,item_code) :
	for packing_item_data in packing_items_data:
		if  packing_item_data["packing_item"] == item_code :
			return packing_item_data["pi_progress_warehouse"]


def update_packingBox_in_packed_item_custom(pbc_name,packing_id_list):
	for packing_id in packing_id_list:
		packig_item_doc = frappe.get_doc( "Packed Item Custom",packing_id )
		packig_item_doc.packing_box = pbc_name
		packig_item_doc.current_warehouse = frappe.db.get_value("Packed Box Custom", {"name":pbc_name},"current_warehouse")
		packig_item_doc.current_rarb_id = frappe.db.get_value("Packed Box Custom", {"name":pbc_name},"current_rarb_id")
		#current_warehouse,current_rarb_id
		packig_item_doc.save(ignore_permissions=True)

def update_packingId_in_detailedPackingInfo(doc_name,packed_item_id_json):
	detailed_packing_info_doc = frappe.get_doc( "Detailed Packing Info",doc_name )
	for packing_item, packing_item_id_list in packed_item_id_json.items():
		for item_row in getattr(detailed_packing_info_doc,"packing_details_review"): #loop over doc's item table
			if item_row.packing_item == packing_item:
				if item_row.packing_id:
					#already having packing id
					pass
					#print "already having packing id as of now packing_id list will update for the first time only"
				else: #new packing id
					item_row.packing_id = "\n".join(packing_item_id_list)
	detailed_packing_info_doc.save()
	#print("from update_packingId_in_detailedPackingInfo saved ",getattr(detailed_packing_info_doc,"packing_details_review"))
	for item_row in getattr(detailed_packing_info_doc,"packing_details_review"):
		print("from update_packingId_in_detailedPackingInfo saved row",item_row.packing_id)

def update_packingBoxId_in_detailedPackingInfo(doc_name,packing_box_id_json):
	detailed_packing_info_doc = frappe.get_doc( "Detailed Packing Info",doc_name )
	for packing_box, packing_box_id in packing_box_id_json.items():
		for item_row in getattr(detailed_packing_info_doc,"detailed_packing_box"):
			if item_row.packing_box == packing_box:
				if item_row.packing_box_id:
					pass
				else:
					item_row.packing_box_id = packing_box_id
	detailed_packing_info_doc.save()

def create_pi_inspection(dpi_details):
	pii = frappe.new_doc("Packing Item Inspection")
	pii.voucher_type =  dpi_details["voucher_type"]
	pii.voucher_name = dpi_details["voucher_name"]
	pii.dpi_name = dpi_details["dpi_name"]
	dpi_packing_items_data = dpi_details["dpi_packing_items_data"] #(detailed packing info first child table)
	packed_item_id_json = dpi_details["packed_item_id_json"]
	#print("packed_item_id_json",packed_item_id_json)
	#print("dpi_packing_items_data",dpi_packing_items_data)

	pii.set('packing_item_inspection_child', [])
	for dpi_packing_item in dpi_packing_items_data:
		pii_tb1_row = pii.append('packing_item_inspection_child', {})
		pii_tb1_row.parent_item = dpi_packing_item["parent_item"]
		pii_tb1_row.packing_item = dpi_packing_item["packing_item"]
		pii_tb1_row.qty = dpi_packing_item["qty"]

		if dpi_packing_item["pi_progress_warehouse"]:
			pii_tb1_row.pi_progress_warehouse = dpi_packing_item["pi_progress_warehouse"]
			if dpi_packing_item["rarb_location_pwh"]:
				pii_tb1_row.rarb_location_pwh = dpi_packing_item["rarb_location_pwh"]
		if dpi_packing_item["pi_target_warehouse"]:
			pii_tb1_row.pi_target_warehouse = dpi_packing_item["pi_target_warehouse"]
			if dpi_packing_item["rarb_location_twh"]:
				pii_tb1_row.rarb_location_twh = dpi_packing_item["rarb_location_twh"]

		#pii_tb1_row.packing_id = dpi_packing_item["packing_id"] #problem in packing id for the first transaction if pacig id is already that time
		#its getting populating will fix it later
	pii.set('packing_item_inspection_progress_wh', [])

	for dpi_packing_item in dpi_packing_items_data:
		packing_item_id_list = packed_item_id_json[dpi_packing_item["packing_item"]]
		for packing_item_id in packing_item_id_list:
			#print("packing_item_id",packing_item_id)
			pii_tb2_row = pii.append('packing_item_inspection_progress_wh', {})
			pii_tb2_row.parent_item = dpi_packing_item["parent_item"]
			pii_tb2_row.packing_item = dpi_packing_item["packing_item"]
			pii_tb2_row.packing_item_link = packing_item_id
			pii_tb2_row.test_feield_pi = packing_item_id
			if dpi_packing_item["pi_progress_warehouse"]:
				pii_tb2_row.current_warehouse = dpi_packing_item["pi_progress_warehouse"]
				pii_tb2_row.pi_progress_warehouse = dpi_packing_item["pi_progress_warehouse"]
				if dpi_packing_item["rarb_location_pwh"]:
					pii_tb2_row.rarb_location_pwh = dpi_packing_item["rarb_location_pwh"]
					pii_tb2_row.current_rarb_id = dpi_packing_item["rarb_location_pwh"]
			if dpi_packing_item["pi_target_warehouse"]:
				pii_tb2_row.pi_target_warehouse = dpi_packing_item["pi_target_warehouse"]
				if dpi_packing_item["rarb_location_twh"]:
					pii_tb2_row.rarb_location_twh = dpi_packing_item["rarb_location_twh"]
	pii.save(ignore_permissions=True)
	dpi = frappe.get_doc( "Detailed Packing Info",pii.dpi_name )
	dpi.packing_item_inspection_link = 	pii.name
	dpi.save(ignore_permissions=True)

def create_pbi_inspection(dpi_details):
	pbi = frappe.new_doc("Packing Box Inspection")
	pbi.voucher_type =  dpi_details["voucher_type"]
	pbi.voucher_name = dpi_details["voucher_name"]
	pbi.dpi_name = dpi_details["dpi_name"]
	packing_boxes_data = dpi_details["packing_boxes_data"] #(detailed packing info second child table)
	packing_box_id_json = dpi_details["packing_box_id_json"]

	pbi.set('packing_box_inspection_child', [])
	actual_packing_box_list= []
	for packing_box_data in packing_boxes_data:
		if packing_box_data["packing_box"] not in actual_packing_box_list:
			actual_packing_box_list.append(packing_box_data["packing_box"])
			pbi_tb1_row = pbi.append('packing_box_inspection_child', {})
			pbi_tb1_row.packing_box =  packing_box_data["packing_box"]
			pbi_tb1_row.packing_box_link = packing_box_id_json [packing_box_data["packing_box"]]


			if packing_box_data["pb_progress_warehouse"]:
				pbi_tb1_row.current_warehouse = packing_box_data["pb_progress_warehouse"]
				pbi_tb1_row.pb_progress_warehouse = packing_box_data["pb_progress_warehouse"]
				if packing_box_data["pb_rarb_location_pwh"]:
					pbi_tb1_row.pb_rarb_location_pwh = packing_box_data["pb_rarb_location_pwh"]
					pbi_tb1_row.current_rarb_id = packing_box_data["pb_rarb_location_pwh"]

			if packing_box_data["pb_target_warehouse"]:
				pbi_tb1_row.pb_target_warehouse = packing_box_data["pb_target_warehouse"]
				if packing_box_data["pb_rarb_location_twh"]:
					pbi_tb1_row.pb_rarb_location_twh = packing_box_data["pb_rarb_location_twh"]

	pbi.save(ignore_permissions=True)
	dpi = frappe.get_doc( "Detailed Packing Info",pbi.dpi_name )
	dpi.packing_box_inspection_link = 	pbi.name
	dpi.save(ignore_permissions=True)

#this api is not used now
def create_material_transfer(material_transfer_item_rows_list):
	print ("material_transfer_item_rows_list :",material_transfer_item_rows_list)
	se = frappe.new_doc("Stock Entry")
	se.purpose = "Material Transfer"
	se.company = "Epoch Consulting"

	se.set('items', [])
	for material_transfer_item in material_transfer_item_rows_list :
		se_item = se.append('items', {})
		se_item.item_code = material_transfer_item["item_code"]
		se_item.s_warehouse =  material_transfer_item["s_wh"]
		se_item.t_warehouse =  material_transfer_item["t_wh"]
		se_item.uom = "Nos"
		se_item.qty = material_transfer_item["qty"]
		se_item.serial_no = material_transfer_item["serial_no_list"]
		se_item.conversion_factor = 1
		se_item.stock_uom = "Nos"
	se.save(ignore_permissions=True)
	frappe.db.commit()
	se.submit()

def create_material_issue(material_transfer_item_rows_list) :
	se = frappe.new_doc("Stock Entry")
	se.purpose = "Material Issue"
	details = frappe.get_doc("Nhance Settings")
	se.company = details.company_name

	se.set('items', [])
	for material_transfer_item in material_transfer_item_rows_list :
		se_item = se.append('items', {})
		se_item.item_code = material_transfer_item["item_code"]
		se_item.s_warehouse =  material_transfer_item["s_wh"]
		se_item.uom = frappe.db.get_value("Item", {"item_code":material_transfer_item["item_code"]},"stock_uom")
		se_item.qty = material_transfer_item["qty"]
		se_item.serial_no = material_transfer_item["serial_no_list"]
		se_item.conversion_factor = 1
		se_item.stock_uom = frappe.db.get_value("Item", {"item_code":material_transfer_item["item_code"]},"stock_uom")
	se.save(ignore_permissions=True)
	frappe.db.commit()
	se.submit()

def create_material_rec(item_code,qty,doc_name_list,warehouse):

	serial_no_list =  "\n".join(doc_name_list)
	se = frappe.new_doc("Stock Entry")
	se.purpose = "Material Receipt"
	details = frappe.get_doc("Nhance Settings")
	se.company = details.company_name

	se.set('items', [])
	for i in range(1) :
		se_item = se.append('items', {})
		se_item.item_code = item_code
		se_item.t_warehouse =  warehouse
		se_item.uom = frappe.db.get_value("Item", {"item_code":item_code},"stock_uom")
		se_item.qty =qty
		se_item.serial_no = serial_no_list
		se_item.conversion_factor = 1
		se_item.stock_uom = frappe.db.get_value("Item", {"item_code":item_code},"stock_uom")
	se.save(ignore_permissions=True)
	frappe.db.commit()
	se.submit()
