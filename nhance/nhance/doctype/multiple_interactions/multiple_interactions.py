# -*- coding: utf-8 -*-
# Copyright (c) 2018, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint


class MultipleInteractions(Document):
	def on_submit(self):
		self.create_interactions()	

	def create_interactions(self):
		opp_temp_list = frappe.db.sql("""select mi.date, mi.type_of_interaction, mi.mode, mi.inbound_or_outbound, mi.customer, mi.interaction_status, mii.reference_doctype, mii.reference_document, mii.contact, mii.short_description, mii.complete_description, mii.todo, mii.equipment, mii.address from `tabMultiple Interactions` mi, `tabMultiple Interactions Item` mii where mii.parent = %s and mi.name = mii.parent""", self.name, as_dict = 1)
		if opp_temp_list:
			for record in opp_temp_list:
				if record.reference_document is not None and record.reference_document != "":
					if record.reference_doctype == "Opportunity":
						int_rec = frappe.db.sql("""select name from `tabOpportunity` where name = %s""", (record.reference_document), as_dict = 1)
						if int_rec:
							int_json = {
								"reference_doctype": record.reference_doctype,
								"reference_document": record.reference_document,
								"opportunity": record.reference_document,
								"date": record.date,
								"mode": record.mode,
								"type_of_interaction": record.type_of_interaction,
								"inbound_or_outbound": record.inbound_or_outbound,
								"customer": record.customer,
								"contact": record.contact,
								"address": record.address,
								"short_description": record.short_description,
								"complete_description": record.complete_description,
								"equipment": record.equipment
								}

						else:
							frappe.throw(_("This Reference document number does not exist - " + record.reference_document))

					elif record.reference_doctype == "Quotation":
						int_rec = frappe.db.sql("""select name from `tabQuotation` where name = %s""", (record.reference_document), as_dict = 1)
						if int_rec:
							int_json = {
								"reference_doctype": record.reference_doctype,
								"reference_document": record.reference_document,
								"quotation": record.reference_document,
								"date": record.date,
								"mode": record.mode,
								"type_of_interaction": record.type_of_interaction,
								"inbound_or_outbound": record.inbound_or_outbound,
								"customer": record.customer,
								"contact": record.contact,
								"address": record.address,
								"short_description": record.short_description,
								"complete_description": record.complete_description,
								"equipment": record.equipment
								}
						else:
							frappe.throw(_("This Reference document number does not exist - " + record.reference_document))

					elif record.reference_doctype == "Sales Order":
						int_rec = frappe.db.sql("""select name from `tabSales Order` where name = %s""", (record.reference_document), as_dict = 1)
						if int_rec:
							int_json = {
								"reference_doctype": record.reference_doctype,
								"reference_document": record.reference_document,
								"sales_order": record.reference_document,
								"date": record.date,
								"mode": record.mode,
								"type_of_interaction": record.type_of_interaction,
								"inbound_or_outbound": record.inbound_or_outbound,
								"customer": record.customer,
								"contact": record.contact,
								"address": record.address,
								"short_description": record.short_description,
								"complete_description": record.complete_description,
								"equipment": record.equipment
								}
						else:
							frappe.throw(_("This Reference document number does not exist - " + record.reference_document))


					elif record.reference_doctype == "Sales Invoice":
						int_rec = frappe.db.sql("""select name from `tabSales Invoice` where name = %s""", (record.reference_document), as_dict = 1)
						if int_rec:

							int_json = {
								"reference_doctype": record.reference_doctype,
								"reference_document": record.reference_document,
								"sales_invoice": record.reference_document,
								"date": record.date,
								"mode": record.mode,
								"type_of_interaction": record.type_of_interaction,
								"inbound_or_outbound": record.inbound_or_outbound,
								"customer": record.customer,
								"contact": record.contact,
								"address": record.address,
								"short_description": record.short_description,
								"complete_description": record.complete_description,
								"equipment": record.equipment
								}

						else:
							frappe.throw(_("This Reference document number does not exist - " + record.reference_document))


					doc = frappe.new_doc("Interactions")
					doc.update(int_json)
					doc.save()
					frappe.db.commit()
					docname = doc.name
					frappe.msgprint(_("Interaction record created - " + docname))




				else:
					frappe.throw(_("The Reference document number cannot be blank. "))
