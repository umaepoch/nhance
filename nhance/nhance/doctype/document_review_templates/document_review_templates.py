# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DocumentReviewTemplates(Document):
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
		    set_default(self, "doc_type")
		   
		else:
		    frappe.db.set(self, "is_default", 0)

@frappe.whitelist()
def get_doc_details(doctype):
	#print "hey i am in-----"
	#doc_details = frappe.get_doc(doctype,docids);
	#global_doc_details = frappe.get_doc("Global Defaults");
	#print "global_doc_details---------",global_doc_details.default_company
	doc_details = frappe.get_meta(doctype).get("fields")
	#doc_details = frappe.get_doc("DocType", doctype)
	
	'''
	for field in doc_details:
    		# add to child table (assuming it is called fields)
   		 row = self.append('fields', {})
   		 row.label = field.label
	#print "doc_details----------",doc_details
	'''
	#doc_details =  frappe.client.get_doc(doctype);
	#doc_details = ""
	return doc_details
@frappe.whitelist()
def get_doc_details_itmes(doctype):
	#print "hey i am in-----"
	#doc_details = frappe.get_doc(doctype,docids);
	#global_doc_details = frappe.get_doc("Global Defaults");
	#print "global_doc_details---------",global_doc_details.default_company
	doc_details = frappe.get_meta(doctype).get("fields")
	#doc_details = frappe.get_doc("DocType", doctype)
	
	'''
	for field in doc_details:
    		# add to child table (assuming it is called fields)
   		 row = self.append('fields', {})
   		 row.label = field.label
	print "doc_details----------",doc_details
	'''
	#doc_details =  frappe.client.get_doc(doctype);
	#doc_details = ""
	return doc_details

@frappe.whitelist()
def get_details_itme(item_code):
	item_details = frappe.get_doc("Item", item_code)
	return item_details

@frappe.whitelist()
def get_item_price_list(item_code):
	item_details = frappe.get_doc("Item Price", item_code)
	return item_details

@frappe.whitelist()
def get_taxes_details(taxes_doc,taxes_and_charges):
	taxes_details = frappe.get_doc(taxes_doc, taxes_and_charges)
	return taxes_details
@frappe.whitelist()
def get_current_doc_details(cur_name):
	taxes_details = frappe.db.sql("""select * from `tabDocument Review Template Table` where parent = %s""",(cur_name),as_dict=1)
	#print "taxes_details============",taxes_details
	return taxes_details

