# -*- coding: utf-8 -*-
# Copyright (c) 2018, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint

class OpportunityTemplateMaster(Document):

	def before_save(self):
		self.validate_customer()

	def before_submit(self):
		self.create_customer()
		self.create_address()
		self.create_opportunity()
		self.create_proposal()
		self.create_interactions()

	def validate_customer(self):
		cust_err = 0
		for m in self.get('items'):

			if m.customer:
				pass
			else:
				frappe.msgprint(_("Customer code in Row {0} is blank.").format(m.idx))
				cust_err = 1
		if cust_err:


			frappe.throw(_("Please enter customer codes"))

	

	def create_customer(self):
		opp_temp_list = frappe.db.sql("""select oppti.customer as customer from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		if opp_temp_list:
			for record in opp_temp_list:

				if record.customer is not None and record.customer != "":

					cust_record = frappe.db.sql("""select name as customer from `tabCustomer` where name = %s""", record.customer, as_dict = 1)
					if cust_record:
						pass
					else:
						cust_json = {
							"customer_name": record.customer
							}					
						doc = frappe.new_doc("Customer")
						doc.update(cust_json)
						doc.save()
						frappe.db.commit()
						docname = doc.name
						frappe.msgprint(_("Customer Record created for - " + record.customer))
				else:
					frappe.throw(_("The customer name is blank."))


	def create_address(self):
		opp_temp_list = frappe.db.sql("""select oppti.customer as customer, address1, address2, city, state, pincode, contact_name, contact_phone, contact_email, contact_designation from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		if opp_temp_list:
			for record in opp_temp_list:
				if record.customer is not None and record.customer != "":
					if record.address1:
						addr_name = record.customer+"-Billing"
						addr_record = frappe.db.sql("""select name from `tabAddress` where name= %s""", addr_name, as_dict = 1)
						if addr_record:
							pass
						else:
							address_json = {
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
								}
							doc = frappe.new_doc("Address")
							doc.update(address_json)
							doc.save()
							frappe.db.commit()
							docname = doc.name
							frappe.msgprint(_("Address Record created for - " + docname))

					if record.contact_name:
						cont_name = record.contact_name+"-"+record.customer
						contact_record = frappe.db.sql("""select name from `tabContact` where name = %s""", cont_name, as_dict = 1)
				
						if contact_record:
							pass
						else:
							contact_json = {
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
								}
							doc = frappe.new_doc("Contact")
							doc.update(contact_json)
							doc.save()
							frappe.db.commit()
							docname = doc.name
							frappe.msgprint(_("Contact Record created for - " + docname))



	def create_opportunity(self):
		opp_temp_list = frappe.db.sql("""select oppti.opportunity_number as opportunity_number, oppti.salesperson_name, oppti.customer as customer, oppti.contact_name as contact, oppti.call_date from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		if opp_temp_list:
			for record in opp_temp_list:
				frappe.msgprint(_(record.opportunity_number))
				if record.opportunity_number is not None and record.opportunity_number != "":
					frappe.msgprint(_("Inside"))
					opp_record = frappe.db.sql("""select name from `tabOpportunity` where name = %s""", record.opportunity_number, as_dict = 1)
					frappe.msgprint(_(opp_record))
					if opp_record:
						pass
					else:
						frappe.throw(_("This Opportunity number does not exist - " + record.opportunity_number))

				else:
					frappe.msgprint(_("Opportunity not found. Creating new"))
					opp_json = {
						"customer": record.customer,
						"enquiry_from": "Customer",
						"sales_person": record.salesperson_name,
						"transaction_date": record.call_date
					}	
					doc = frappe.new_doc("Opportunity")
					doc.update(opp_json)
					doc.save()
					frappe.db.commit()
					docname = doc.name
					frappe.msgprint(_("Opportunity Record created for - " + docname))
					frappe.msgprint(_(self.name))
					frappe.msgprint(_(record.customer))
					temp_rec = frappe.db.sql("""select oppti.customer, oppti.opportunity_number from `tabOpportunityImportTemplate` oppti, `tabOpportunityTemplate Master` opptm where oppti.parent = %s and opptm.name = oppti.parent and oppti.customer = %s""", (self.name, record.customer))
					frappe.msgprint(_(temp_rec))
					frappe.db.sql("""update `tabOpportunityImportTemplate` oppti, `tabOpportunityTemplate Master` opptm set oppti.opportunity_number = %s where oppti.parent = %s and opptm.name = oppti.parent and oppti.customer = %s""", (docname, self.name, record.customer))
					frappe.db.commit()


	def create_proposal(self):
		opp_temp_list = frappe.db.sql("""select oppti.opportunity_number, oppti.proposal_stage_number as proposal_stage, oppti.customer, oppti.call_date, oppti.stage_date, oppti.stage, oppti.value, oppti.closing_date, oppti.probability_of_closure, oppti.support_needed, oppti.opportunity_purpose, oppti.buying_status, oppti.salesperson_name, oppti.call_date from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		if opp_temp_list:
			for record in opp_temp_list:
				if record.opportunity_number is not None and record.opportunity_number != "":
					if record.proposal_stage is not None and record.proposal_stage != "":
						prop_stage_record = frappe.db.sql("""select name from `tabProposal Stage` where name = %s""", record.proposal_stage, as_dict = 1)
						if prop_stage_record:
							pass
						else:
							frappe.throw(_("This Proposal Stage number does not exist - " + record.proposal_stage))
					else:	

						prop_record = frappe.db.sql("""select name from `tabOpportunity` where name = %s""", record.opportunity_number, as_dict = 1)
						if prop_record:
							
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
								"buying_status": record.buying_status,
								"sales_person": record.salesperson_name

							}
							doc = frappe.new_doc("Proposal Stage")
							doc.update(prop_json)
							doc.save()
							frappe.db.commit()
							docname = doc.name
							frappe.msgprint(_("Proposal Stage Record created - " + docname))
							frappe.msgprint(_(docname))
							frappe.msgprint(_(self.name))
							frappe.msgprint(_(record.customer))
							frappe.msgprint(_(record.opportunity_number))
							frappe.db.sql("""update `tabOpportunityImportTemplate` oppti, `tabOpportunityTemplate Master` opptm set oppti.proposal_stage_number = %s where oppti.parent = %s and opptm.name = oppti.parent and oppti.customer = %s and oppti.opportunity_number = %s and oppti.call_date = %s""", (docname, self.name, record.customer, record.opportunity_number, str(record.call_date)))
							frappe.db.commit()
						else:
							frappe.throw(_("This Opportunity number does not exist - " + record.opportunity_number))


				else:
					frappe.throw(_("This Opportunity number cannot be blank. "))

	def create_interactions(self):
		opp_temp_list = frappe.db.sql("""select oppti.opportunity_number, oppti.interactions_number as interaction_number, oppti.customer, oppti.type_of_interaction, oppti.inbound_or_outbound, opptm.import_date, oppti.short_description, oppti.complete_description, oppti.equipment, oppti.salesperson_name, oppti.call_date from `tabOpportunityTemplate Master` opptm, `tabOpportunityImportTemplate` oppti where oppti.parent = %s and opptm.name = oppti.parent""", self.name, as_dict = 1)
		if opp_temp_list:
			for record in opp_temp_list:
				if record.opportunity_number is not None and record.opportunity_number != "":
					if record.interaction_number is not None and record.interaction_number != "":
						int_record = frappe.db.sql("""select name from `tabInteractions` where name = %s""", record.interaction_number, as_dict = 1)
						if int_record:
							pass
						else:
							frappe.throw(_("This Interaction does not exist - " + record.interaction_number))
					else:	

						inter_record = frappe.db.sql("""select name from `tabOpportunity` where name = %s""", record.opportunity_number, as_dict = 1)
						if inter_record:
							int_json = {
								"reference_doctype": "Opportunity",
								"reference_document": record.opportunity_number,
								"opportunity": record.opportunity_number,
								"date": record.call_date,
								"type_of_interaction": record.type_of_interaction,
								"inbound_or_outbound": record.inbound_or_outbound,
								"customer": record.customer,
								"short_description": record.short_description,
								"complete_description": record.complete_description,
								"equipment": record.equipment,
								"sales_person": record.salesperson_name

							}
							doc = frappe.new_doc("Interactions")
							doc.update(int_json)
							doc.save()
							frappe.db.commit()
							docname = doc.name
							frappe.msgprint(_("Interaction record created - " + docname))
							frappe.db.sql("""update `tabOpportunityImportTemplate` oppti, `tabOpportunityTemplate Master` opptm set oppti.interactions_number = %s where oppti.parent = %s and opptm.name = oppti.parent and oppti.customer = %s and oppti.call_date = %s""", (docname, self.name, record.customer, str(record.call_date)))

							frappe.db.commit()
						else:
							frappe.throw(_("This Opportunity number does not exist - " + record.opportunity_number))


				else:
					frappe.throw(_("This Opportunity number cannot be blank. "))


