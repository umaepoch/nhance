# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json


class PackingItemInspection(Document):
	pass

@frappe.whitelist()
def update_packed_item_custom(pii_child2_doc):
	pii_child2_doc = json.loads(pii_child2_doc)
	for row in pii_child2_doc:
		pic_doc = frappe.get_doc( "Packed Item Custom",row["packing_item_link"] )
		pic_doc.wrapped =  row["wrapped"]
		pic_doc.current_warehouse =  row["current_warehouse"]
		pic_doc.packing_item_inspection_link = row["parent"]
		pic_doc.save()
