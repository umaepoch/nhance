# -*- coding: utf-8 -*-
# Copyright (c) 2017, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import msgprint, _, throw
from frappe.model.document import Document

class Interactions(Document):

	def before_save(self):
		self.set_missing_customer_details()

	def on_refresh(self):
		self.set_missing_customer_details()

	def set_missing_customer_details(self):
		if getattr(self, "customer", None):
			from erpnext.accounts.party import _get_party_details
			party_details = _get_party_details(self.customer,
				ignore_permissions=self.flags.ignore_permissions,
				doctype=self.doctype)
			self.address = party_details.customer_address
			self.contact = party_details.contact_person

