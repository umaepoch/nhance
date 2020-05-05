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
@frappe.whitelist()
def make_packing_item_doc(packing_items_data,si_name):
	packing_items_data = json.loads(packing_items_data)
	packed_item_id_json ={}
	print "came inside make_packing_item_doc",packing_items_data
	detailed_packing_info_doc_name = packing_items_data[0]["parent"]

	for packing_item_data in packing_items_data:
		packing_id_list = []
		packing_item_qty = packing_item_data["qty"]
		for i in range(packing_item_qty): #change it to range of packing_id list
			pit = frappe.new_doc("Packed Item Custom")
			pit.parent_item = packing_item_data["parent_item"]
			pit.voucher_type = "Sales Invoice"
			pit.voucher_no = si_name
			pit.packing_item = packing_item_data["packing_item"]
			pit.qty = 1 #one one each as of now later it will change ac to packing item config
			pit.packing_item_group = packing_item_data["item_group"]
			pit.save(ignore_permissions=True)
			packing_id_list.append(pit.name)
		packed_item_id_json[packing_item_data["packing_item"]] = packing_id_list
	update_packingId_in_detailedPackingInfo(detailed_packing_info_doc_name,packed_item_id_json)
	return "packing item transactions have been created"

@frappe.whitelist()
def make_packed_box_doc(packing_boxes_data,packing_items_data,si_name):
	packing_boxes_data = json.loads(packing_boxes_data)
	packing_items_data = json.loads(packing_items_data)
	print "came inside make_packed_box_doc",packing_items_data
	detailed_packing_info_doc_name = packing_boxes_data[0]["parent"]
	#packing_box_wise_data = {pb1:[{},{}],pb2:[{}]}
	packing_box_wise_data = {}

	for packing_box_data in packing_boxes_data:
		if packing_box_wise_data.get(packing_box_data["packing_box"]):
			packing_box_wise_data[packing_box_data["packing_box"]].append(packing_box_data)
		else:
			packing_box_wise_data[packing_box_data["packing_box"]] = [ packing_box_data ]

	for packing_box_name, packing_box_datas in packing_box_wise_data.items():
		pbc = frappe.new_doc("Packed Box Custom")
		packing_box_status = "Completed"
		pbc.packing_box =  packing_box_name
		pbc.voucher_type = "Sales Invoice"
		pbc.voucher_no = si_name

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
			print "packed_box_breif_details_child**********",packing_id_list
			for packing_id in packing_id_list:
				pbc_child_row2 = pbc.append('packed_box_breif_details_child', {})
				pbc_child_row2.parent_item = packing_box_data["parent_item"]
				pbc_child_row2.packing_item = packing_box_data["packing_item"]
				pbc_child_row2.packed_item = packing_id.strip()
				pbc_child_row2.packed_item_link = frappe.db.get_value("Packed Item Custom", {"packing_id":packing_id.strip()},"name")

		pbc.save(ignore_permissions=True)

def get_packing_id_list(parent_item,packing_item,packing_item_qty):
	packing_id_list=[]
	parent_child_item_name = parent_item + ID_CHARECTER + packing_item + ID_CHARECTER
	last_packing_id = get_last_packing_id (parent_child_item_name) if get_last_packing_id (parent_child_item_name) else parent_child_item_name + "0000"
	int_val = int(get_packing_id_details(last_packing_id).get("id_number"))
	for i in range(packing_item_qty):
		int_val += 1
		packing_id_list.append(parent_child_item_name + str(int_val).zfill(4))
	return packing_id_list

def get_last_packing_id(parent_child_item_name):
	last_packing_id = frappe.db.sql("""select
											max(packing_id) as max_packing_id
										from
											`tabPacked Item Custom`
										where packing_id like '"""+parent_child_item_name+"%""'""", as_dict=1)
	return last_packing_id[0].max_packing_id if last_packing_id else None

def get_packing_id_details(packing_id):
	temp_count = 0
	parent_item_index = 0
	child_item_index = 0
	for i in packing_id:
	    temp_count += 1
	    if(i == ID_CHARECTER):
	        if (parent_item_index == 0):
	            parent_item_index = temp_count
	        else:
	            child_item_index = temp_count

	id_dic = {"parent_item":packing_id[:(parent_item_index-1)],
	          "child_item":packing_id[parent_item_index:(child_item_index-1)],
	          "id_number":packing_id[child_item_index:]}
	#print("id_dic : ",id_dic)
	return id_dic

def update_packingId_in_detailedPackingInfo(doc_name,packed_item_id_json):
	detailed_packing_info_doc = frappe.get_doc( "Detailed Packing Info",doc_name )
	for packing_item, packing_item_id_list in packed_item_id_json.items():
		for item_row in getattr(detailed_packing_info_doc,"packing_details_review"): #loop over doc's item table
			if item_row.packing_item == packing_item:
				if item_row.packing_id: #already having packing id
					print "already having packing id as of now packing_id list will update for the first time only"
				else: #new packing id
					item_row.packing_id = "\n".join(packing_item_id_list)
	detailed_packing_info_doc.save()

