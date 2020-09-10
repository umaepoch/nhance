# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ResourceMaster(Document):
	def on_submit(self):
		self.manage_default_cocpf()

	def on_cancel(self):
		frappe.db.set(self, "is_default", 0)
		self.manage_default_cocpf()

	def on_update_after_submit(self):
		self.manage_default_cocpf()

	def manage_default_cocpf(self):
		""" Uncheck others if current one is selected as default,
		    update default bom in item master
		"""
		if self.is_default:
		    from frappe.model.utils import set_default
		    set_default(self, "resource")
		   
		else:
		    frappe.db.set(self, "is_default", 0)
