# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
class DocumentReviewDetails(Document):
	pass

@frappe.whitelist()
def make_document_review_detials(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		target.is_pos = 0
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
#		set company address
#		target.update(get_company_address(target.company))
#		if target.company_address:
#			target.update(get_fetch_values("Documents Review Details", 'company_address', target.company_address))
#		set the redeem loyalty points if provided via shopping cart
		if source.loyalty_points and source.order_type == "Shopping Cart":
			target.redeem_loyalty_points = 1
	def postprocess(source, target):
		set_missing_values(source, target)
#		Get the advance paid Journal Entries in Sales Invoice Advance
#		target.set_advances()
	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Document Review Details",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"payment_terms_template": "payment_terms_template"
			},
			"validation": {
				"docstatus": ["=", 0]
			}
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist
@frappe.whitelist()
def make_document_review(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		target.is_pos = 0
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
#		set company address
#		target.update(get_company_address(target.company))
#		if target.company_address:
#			target.update(get_fetch_values("Documents Review Details", 'company_address', target.company_address))
#		 set the redeem loyalty points if provided via shopping cart
#		if source.loyalty_points and source.order_type == "Shopping Cart":
#			target.redeem_loyalty_points = 1
	def postprocess(source, target):
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Sales Invoice Advance
		#target.set_advances()
	doclist = get_mapped_doc("Purchase Order", source_name, {
		"Purchase Order": {
			"doctype": "Document Review Details",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"payment_terms_template": "payment_terms_template"
			},
			"validation": {
				"docstatus": ["=", 0]
			}
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist

@frappe.whitelist()
def get_fields_details(docName):
	fields = frappe.db.sql("""select drt.label,drt.fieldname,drt.review_parameters,drt.field_label,drt.fieldtype,drt.options from `tabDocument Review Template Table` drt ,`tabDocument Review Templates` dr where dr.name = drt.parent AND dr.name = %s""",(docName), as_dict=1)
	return fields

@frappe.whitelist()
def get_sales_order_details(docIds,docName):
	sales_details = {}
#	print "docIds=============",docIds
#	print "docName=============",docName
	doc_details = frappe.get_meta(docName).get("fields")
	item_table = ""
	tax_table = ""
	order = frappe.db.sql("""select * from `tab""" +docName + """` where name = %s""",(docIds), as_dict=1)
#	item = frappe.db.sql("""select * from `tabSales Order Item` where parent = %s""",(docIds), as_dict=1)
#	taxes = frappe.db.sql("""select * from `tabSales Taxes and Charges` where parent = %s""",(docIds), as_dict=1)

	'''
	elif docName == "Purchase Order":
		order = frappe.db.sql("""select * from `tab""" +DocName + """` where name = %s""",(docIds), as_dict=1)
		item = frappe.db.sql("""select * from `tabPurchase Order Item` where parent = %s""",(docIds), as_dict=1)
		taxes = frappe.db.sql("""select * from `tabPurchase Taxes and Charges` where parent = %s""",(docIds), as_dict=1)
		sales_details["order"] =order
		sales_details["item"] =item
		sales_details["taxes"] =taxes
	'''
	for fields in doc_details:
		if fields.fieldname == "items":
			item_table = fields.options
		elif fields.fieldname == "taxes":
			tax_table = fields.options
	item = frappe.db.sql("""select * from `tab""" +item_table + """` where parent = %s""",(docIds), as_dict=1)
	taxes = frappe.db.sql("""select * from `tab""" +tax_table + """` where parent = %s""",(docIds), as_dict=1)
#	print "taxes=================",taxes
	sales_details["order"] =order
	sales_details["item"] =item
	sales_details["taxes"] =taxes
#	print "sales_details============",sales_details
	return sales_details
@frappe.whitelist()
def get_name(DocName):
	table = "`tab"+str(DocName)+"`"
	name = frappe.db.sql("""select name from `tab""" +DocName + """`""",as_dict=1)
	return name

@frappe.whitelist()
def get_doc_fields(doctype):
	doc_details = frappe.get_meta(doctype).get("fields")
	return doc_details

@frappe.whitelist()
def get_check_box_cheched(doctype,name):
	name = frappe.db.sql("""update `tab""" +doctype + """`
	set under_review = 1 where name = %s""",(name),as_dict=1)
	return name
@frappe.whitelist()
def get_uncheck_box_cheched(doctype,source_docname):
	name = frappe.db.sql("""update `tab""" +doctype + """`
	set under_review = 0 where name = %s""", source_docname, as_dict=1)
	return name
