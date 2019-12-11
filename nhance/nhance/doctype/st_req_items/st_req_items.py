# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from erpnext.controllers.print_settings import print_settings_for_item_table
from frappe.model.document import Document


class StReqItems(Document):
	def __setup__(self):
		print_settings_for_item_table(self)

def on_doctype_update():
	frappe.db.add_index("Material Request Item", ["item_code", "warehouse"])
