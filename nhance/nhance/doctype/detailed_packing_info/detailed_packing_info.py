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
		packing_id_list = []
		packing_item_qty = packing_item_data["qty"]
		for i in range(packing_item_qty): #change it to range of packing_id list
			pit = frappe.new_doc("Packed Item Custom")
			pit.parent_item = packing_item_data["parent_item"]
			pit.voucher_type = voucher_type
			pit.voucher_no = voucher_no
			pit.packing_item = packing_item_data["packing_item"]
			pit.qty = 1 #one one each as of now later it will change ac to packing item config
			pit.packing_item_group = packing_item_data["item_group"]
			pit.save(ignore_permissions=True)
			#print ("Packed Item Custom name ",pit.name)
			packing_id_list.append(pit.name)
		packed_item_id_json[packing_item_data["packing_item"]] = packing_id_list
	dpi_details = {"voucher_type":voucher_type,"voucher_name":voucher_no,"dpi_name":dpi_name,"packed_item_id_json":packed_item_id_json,"dpi_packing_items_data":packing_items_data}
	update_packingId_in_detailedPackingInfo(dpi_name,packed_item_id_json)
	#print ("create pi inpection called**",dpi_details["packed_item_id_json"])
	create_pi_inspection(dpi_details)
	return "packing item transactions have been created"


@frappe.whitelist()
def create_packing_box_custom_doc(packing_boxes_data,packing_items_data,voucher_type,voucher_no):
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
		pbc = frappe.new_doc("Packed Box Custom")
		packing_box_status = "Completed"
		pbc.packing_box =  packing_box_name
		pbc.voucher_type = voucher_type
		pbc.voucher_no = voucher_no

		pbc.set('packed_box_details_child', [])
		for packing_box_data in packing_box_datas:
			#include for loop later
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
		packing_box_id_json[packing_box_name] = pbc.name
	update_packingBoxId_in_detailedPackingInfo(dpi_name,packing_box_id_json)
	dpi_details = {"voucher_type":voucher_type,"voucher_name":voucher_no,"dpi_name":dpi_name,"packing_box_id_json":packing_box_id_json,"packing_boxes_data":packing_boxes_data}
	create_pbi_inspection(dpi_details)
	return "packing box transactions have been created"

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
