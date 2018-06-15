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
		self.create_opportunity()
		self.create_proposal()
		self.create_interactions()	



	def create_customer(self):
		opp_temp_list = frappe.db.sql("""select oppti.customer as customer from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		frappe.msgprint(_(opp_temp_list))
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.customer))
				if record.customer is not None and record.customer != "":
					frappe.msgprint(_("Inside Customer"))
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
					frappe.msgprint(_("Inside Address"))
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



	def create_opportunity(self):
		opp_temp_list = frappe.db.sql("""select oppti.opportunity_number as opportunity_number, oppti.customer as customer, oppti.contact_name as contact from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		frappe.msgprint(_(opp_temp_list))
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.customer))
				if record.opportunity_number is not None and record.opportunity_number != "":
					frappe.msgprint(_("Inside Opportunity"))
					opp_record = frappe.db.sql("""select name as opportunity from `tabOpportunity` where name = %s""", record.opportunity_number, as_dict = 1)
					frappe.msgprint(_(opp_record))
					if opp_record:
						pass
					else:
						frappe.throw(_("This Opportunity number does not exist - " + record.opportunity_number))

				else:
					frappe.msgprint(_("New Opportunity"))
					opp_json = {
						"customer": record.customer,
						"enquiry_from": "Customer"
					}	
					frappe.msgprint(_(opp_json))				
					doc = frappe.new_doc("Opportunity")
					doc.update(opp_json)
					doc.save()
					frappe.db.commit()
					docname = doc.name
					frappe.msgprint(_("Opportunity Record created for - " + docname))
					frappe.msgprint(_(docname))
					frappe.msgprint(_(self.name))
					frappe.msgprint(_(record.customer))
					frappe.db.sql("""update `tabOpportunityImportTemplate` oppti, `tabOpportunityTemplate Master` opptm set oppti.opportunity_number = %s where oppti.parent = %s and opptm.name = oppti.parent and oppti.customer = %s""", (docname, self.name, record.customer))


	def create_proposal(self):
		opp_temp_list = frappe.db.sql("""select oppti.opportunity_number, oppti.stage_date, oppti.stage, oppti.value, oppti.closing_date, oppti.probability_of_closure, oppti.support_needed, oppti.opportunity_purpose, oppti.buying_status from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		frappe.msgprint(_(opp_temp_list))
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.opportunity_number))
				if record.opportunity_number is not None and record.opportunity_number != "":
					frappe.msgprint(_("Inside Proposal Stage"))
					frappe.msgprint(_(record.opportunity_number))
					prop_record = frappe.db.sql("""select name as opportunity from `tabOpportunity` where name = %s""", record.opportunity_number, as_dict = 1)
					frappe.msgprint(_(prop_record))
					if prop_record:
						frappe.msgprint(_("New Proposal"))
						prop_json = {
							"stage_doctype": "Opportunity",
							"document_number": record.opportunity_number,
							"reference_name": record.opportunity_number,
							"stage_date": record.stage_date,
							"stage": record.stage,
							"value": record.value,
							"closing_date": record.closing_date,
							"probability_of_closure": record.probability_of_closure,
							"support_needed": record.support_needed,
							"buying_status": record.buying_status

						}
						frappe.msgprint(_(prop_json))					
						doc = frappe.new_doc("Proposal Stage")
						doc.update(prop_json)
						doc.save()
						frappe.db.commit()
						docname = doc.name
						frappe.msgprint(_("Proposal Stage Record created for - " + docname))


					else:
						frappe.throw(_("This Opportunity number does not exist - " + record.opportunity_number))


				else:
					frappe.throw(_("This Opportunity number cannot be blank. "))

	def create_interactions(self):
		opp_temp_list = frappe.db.sql("""select oppti.opportunity_number, oppti.customer, oppti.type_of_interaction, oppti.inbound_or_outbound, opptm.import_date from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		frappe.msgprint(_(opp_temp_list))
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.opportunity_number))
				if record.opportunity_number is not None and record.opportunity_number != "":
					frappe.msgprint(_("Inside Interactions"))
					int_record = frappe.db.sql("""select name as opportunity from `tabOpportunity` where name = %s""", record.opportunity_number, as_dict = 1)
					frappe.msgprint(_(int_record))
					if int_record:
						frappe.msgprint(_("New Interaction"))
						int_json = {
							"reference_doctype": "Opportunity",
							"reference_document": record.opportunity_number,
							"opportunity": record.opportunity_number,
							"date": record.import_date,
							"type_of_interaction": record.type_of_interaction,
							"inbound_or_outbound": record.inbound_or_outbound,
							"customer": record.customer,
							"short_description": record.short_description,
							"complete_description": record.complete_description,
							"equipment": record.equipment

						}
						frappe.msgprint(_(int_json))					
						doc = frappe.new_doc("Interactions")
						doc.update(int_json)
						doc.save()
						frappe.db.commit()
						docname = doc.name
						frappe.msgprint(_("Interaction record created - " + docname))


					else:
						frappe.throw(_("This Opportunity number does not exist - " + record.opportunity_number))


				else:
					frappe.throw(_("This Opportunity number cannot be blank. "))
