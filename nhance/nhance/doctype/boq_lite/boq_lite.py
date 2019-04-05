# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint
from frappe.model.document import Document

class BOQLite(Document):

	def on_submit(self):
		self.boq_val_1()

	def validate(self):
		self.validate_main_item()

	def validate_main_item(self):
		for m in self.get('items'):
			if flt(m.qty) <= 0:
				frappe.throw(_("Quantity required for Item {0} in row {1}").format(m.item_code, m.idx))

	def boq_val_1(self):

		company = self.company

		boq_val1 = frappe.db.sql("""select boqi.item_code from `tabBOQ Lite Item` boqi, `tabBOQ Lite` boq where boqi.parent = %s and boqi.parent = boq.name and boqi.immediate_parent_item = boq.item""", self.name, as_dict = 1)
		if boq_val1:
			pass
		else:
			frappe.throw(_("The Item " + self.item + " for which you are making the BOM is not linked correctly to child items. Please check, correct and try again!"))


@frappe.whitelist()
def fetch_parent_list(parent):
	boq_record_items = frappe.db.sql("""select distinct boqi.immediate_parent_item as bom_item from `tabBOQ Lite Item` boqi where boqi.parent = %s order by boqi.immediate_parent_item""", parent)
	return boq_record_items

