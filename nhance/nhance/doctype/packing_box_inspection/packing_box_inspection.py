# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json


class PackingBoxInspection(Document):
	pass

@frappe.whitelist()
def update_packed_box_custom(pbi_child1_doc):
	pbi_child1_doc = json.loads(pbi_child1_doc)
	for row in pbi_child1_doc:
		pbc_doc = frappe.get_doc( "Packed Box Custom",row["packing_box_link"] )
		pbc_doc.wrapped =  row["wrapped"]
		pbc_doc.current_warehouse =  row["current_warehouse"]
		pbc_doc.packing_box_inspection_link = row["parent"]
		pbc_doc.save()
