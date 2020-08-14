# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json


class PackingBoxInspection(Document):
	pass

def update_si(pbi_child1_doc,voucher_type,voucher_name):
	print "came inside update_si "
	pbc_doc_status_temp = 1
	for row in pbi_child1_doc:
		print " packing_box_link ",row["packing_box_link"]
		pbc_doc_status = frappe.db.get_value("Packed Box Custom", {"name":row["packing_box_link"]},"status")
		if(pbc_doc_status != "Completed"):
			pbc_doc_status_temp = 0
	if pbc_doc_status_temp == 1:
		frappe.db.set_value(voucher_type, voucher_name, "pch_ispackingboxescompleted", "True")
	else:
		frappe.db.set_value(voucher_type, voucher_name, "pch_ispackingboxescompleted", "False")

@frappe.whitelist()
def update_packed_box_custom(pbi_child1_doc,voucher_type,voucher_name):
	print "came inside update_packed_box_custom "
	pbi_child1_doc = json.loads(pbi_child1_doc)
	for row in pbi_child1_doc:
		pbc_doc = frappe.get_doc( "Packed Box Custom",row["packing_box_link"] )
		pbc_doc.wrapped =  row["wrapped"]
		pbc_doc.current_warehouse =  row["current_warehouse"]
		pbc_doc.current_rarb_id =  row["current_rarb_id"]
		pbc_doc.packing_box_inspection_link = row["parent"]
		pbc_doc.save()
	update_si(pbi_child1_doc,voucher_type,voucher_name)
