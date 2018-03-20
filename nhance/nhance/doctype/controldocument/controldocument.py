# -*- coding: utf-8 -*-
# Copyright (c) 2018, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, throw
from frappe.model.document import Document

class ControlDocument(Document):
	
	def on_submit(self):
		self.manage_default_cd()
		self.change_default_cd()

	def on_cancel(self):
		frappe.db.set(self, "is_active", 0)
		frappe.db.set(self, "is_default", 0)

		self.manage_default_cd()

	def on_update_after_submit(self):
		self.manage_default_cd()


	def manage_default_cd(self):
		""" Uncheck others if current one is selected as default,
		"""
		if self.is_default and self.is_active:
			from frappe.model.utils import set_default
			role = frappe.get_doc("Role Profile", self.user)
			if role.default_controldocument != self.name:
				frappe.db.set_value('Role Profile', self.user, 'default_controldocument', self.name)
		else:
#			frappe.db.set(self, "is_default", 0)
			role = frappe.get_doc("Role Profile", self.user)
			if role.default_controldocument == self.name:
				frappe.db.set_value('Role Profile', self.user, 'default_controldocument', self.name)

	def change_default_cd(self):		
		cd_list = frappe.db.sql("""select name from `tabControlDocument` where user = %s and name != %s""", (self.user, self.name), as_dict = 1)
		if cd_list:
			for cds in cd_list:
				cd_rec = frappe.get_doc("ControlDocument", cds.name)
				if cd_rec:
					frappe.db.sql("""update `tabControlDocument` set is_default = 0 where name = %s""", cd_rec.name)

