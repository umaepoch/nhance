# -*- coding: utf-8 -*-
# Copyright (c) 2018, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint

class OpportunityTemplateMaster(Document):
	def on_submit(self):
		self.create_customer()
		self.create_address()
#		self.create_opportunity()
#		self.create_proposal()
#		self.create_interactions()	



	def create_customer(self):
		opp_temp_list = frappe.db.sql("""select oppti.customer as customer from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		frappe.msgprint(_(opp_temp_list))
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.customer))
				if record.customer is not None and record.customer != "":
					frappe.msgprint(_("Inside 1"))
					cust_record = frappe.db.sql("""select name as customer from `tabCustomer` where name = %s""", record.customer, as_dict = 1)
					frappe.msgprint(_(cust_record))
					if cust_record:
						pass
					else:
						frappe.msgprint(_("New Customer"))
						cust_json = {
							"customer_name": record.customer
							}					
						doc = frappe.new_doc("Customer")
						doc.update(cust_json)
						doc.save()
						frappe.db.commit()
						docname = doc.name
						frappe.msgprint(_("Customer Record created for - " + record.customer + " - " + docname))
				else:
					frappe.throw(_("The customer name is blank."))


	def create_address(self):
		opp_temp_list = frappe.db.sql("""select oppti.customer as customer, address1, address2, city, state, pincode, contact_name, contact_phone, contact_email, contact_designation from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		frappe.msgprint(_(opp_temp_list))
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.customer))
				if record.customer is not None and record.customer != "":
					frappe.msgprint(_("Inside 1"))
					if record.address1:
						addr_record = frappe.db.sql("""select address_line1 from `tabAddress` where address_line1 = %s""", record.address1, as_dict = 1)
						if addr_record:
							pass
						else:
							address = frappe.get_doc({
								'doctype': 'Address',
								'address_title': record.customer,
								'address_line1': record.address1,
								'address_line2': record.address2,
								'city': record.city,
								'state': record.state,
								'pincode': record.pincode,
								'links': [{
									'link_doctype': 'Customer',
									'link_name': record.customer
								}]
								}).insert()


					if record.contact_name:
						contact_record = frappe.db.sql("""select first_name from `tabContact` where first_name = %s""", record.contact_name, as_dict = 1)
						if contact_record:
							pass
						else:
							contact = frappe.get_doc({
								'doctype': 'Contact',
								'first_name': record.contact_name,
								'mobile_no': record.contact_phone,
								'email_id': record.contact_email,
								'designation': record.contact_designation,
								'is_primary_contact': 1,
								'links': [{
									'link_doctype': 'Customer',
									'link_name': record.customer
									}]
								}).insert()





