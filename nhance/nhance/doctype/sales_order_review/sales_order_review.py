# -*- coding: utf-8 -*-
# Copyright (c) 2019, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, getdate, comma_and, cint, nowdate, add_days
import json
import datetime
import time
class SalesOrderReview(Document):
	pass

@frappe.whitelist()
def make_document_review_detials(source_name, target_doc=None, ignore_permissions=False):
	def update_item(source, target, source_parent):
		target.delivery_date = source.delivery_date
		target.rate = source.rate
		target.price_list_rate = source.price_list_rate
		target.qty = flt(source.qty) - flt(source.ordered_qty)
		target.stock_qty = (flt(source.qty) - flt(source.ordered_qty)) * flt(source.conversion_factor)
		target.project = source_parent.project

	def update_tax(source, target, source_parent):
		target.account_head = source.account_head
		target.rate = source.rate
		target.cost_center = source.cost_center
		target.charge_type = source.charge_type
	def set_missing_values(source, target):
		target.is_pos = 0
		target.delivery_date = source.delivery_date
		target.transaction_date = source.transaction_date
		target.ignore_pricing_rule = source.ignore_pricing_rule
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
			"doctype": "Sales Order Review",
			"field_map": {

				"party_account_currency": "party_account_currency",
				"payment_terms_template": "payment_terms_template"
			},
			"validation": {
				"docstatus": ["=", 0]
			}
		},
		"Sales Order Item": {
					"doctype": "Sales Order Item Review",
					"field_map":  [
						["name", "sales_order_item"],
						["parent", "sales_order"],
						["stock_uom", "stock_uom"],
						["uom", "uom"],
						["conversion_factor", "conversion_factor"]

			 		],
					"field_no_map": [
						"rate",
						"price_list_rate"
					],
					"postprocess": update_item,
					"condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
				},
		"Sales Taxes and Charges": {
			"doctype": "Sales Taxes and Charges Review",
			"field_map":  [
				["parent", "sales_order"]
			],
			"postprocess": update_tax,
		},
		"Payment Schedule": {
			"doctype": "Payment Schedule Review",
			"field_map":  [
				["parent", "sales_order"]
			],
		},
		"Sales Team":{
			"doctype": "Sales Team Review",
			"field_map":  [
				["parent", "sales_order"]
			],
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist
@frappe.whitelist()
def get_doc_details(doctype):
	doc_details = frappe.get_meta(doctype).get("fields")
	return doc_details
@frappe.whitelist()
def get_review_templates(doctype):
	fields = frappe.db.sql("""select drt.label,drt.fieldname,drt.review_parameters,drt.field_label,drt.fieldtype,drt.options from `tabDocument Review Template Table` drt ,`tabDocument Review Templates` dr where dr.name = drt.parent AND dr.doc_type = %s and dr.is_default =1 and dr.docstatus =1""",doctype, as_dict=1)
	return fields

@frappe.whitelist()
def update_sales_order(sales_review,name,sales_order):
	review_doc_template = frappe.db.sql("""select drt.fieldname from `tabDocument Review Templates` dr ,`tabDocument Review Template Table` drt where dr.doc_type = "Sales Order" and dr.name = drt.parent and dr.is_default =1 and dr.docstatus =1""",as_dict=1)
	field_List = json.loads(sales_review)
	for sales in field_List:
		propose_new = sales['propose_new_value']
		reject_field = sales['reject_field']
		get_checked = frappe.get_all('Sales Order Review', filters={'name': name , sales['reject_field']:1}, fields=[sales['propose_new_value']])
		if get_checked:

			for new_list in get_checked:
				for rev in review_doc_template:
					propose = "propose_new_"+rev.fieldname
					if propose_new == propose:
						frappe.db.set_value("Sales Order",sales_order,rev.fieldname,new_list[str(propose_new)])
	frappe.db.commit()
	doc = frappe.get_doc("Sales Order",sales_order)
	doc.save()
	doc.submit()
	frappe.msgprint('"'+sales_order+'"'+" Sales order has been submitted")

@frappe.whitelist()
def update_sales_order_items(sales_review_item,name,sales_order,item_code):
	review_doc_template = frappe.db.sql("""select drt.fieldname from `tabDocument Review Templates` dr ,`tabDocument Review Template Table` drt where dr.doc_type = "Sales Order" and dr.name = drt.parent and dr.is_default =1 and dr.docstatus =1""",as_dict=1)
	item_table_name = frappe.db.sql("""select name from `tabSales Order Item` where parent = %s and item_code =%s""",(sales_order,item_code), as_dict=1)
	item_name = item_table_name[0].name
	field_List = json.loads(sales_review_item)

	for sales in field_List:
		propose_new = sales['propose_new_value']
		reject_field = sales['reject_field']
		get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': name , sales['reject_field']:1, "item_code" :item_code }, fields=[sales['propose_new_value']])
		if get_checked:
			for new_list in get_checked:
				for rev in review_doc_template:
					propose = "propose_new_"+rev.fieldname
					if propose_new == propose:
						frappe.db.set_value("Sales Order Item",item_name,rev.fieldname,new_list[str(propose_new)])
	doc = frappe.get_doc("Sales Order Item",item_name)
	doc.save()
@frappe.whitelist()
def update_sales_order_taxes(sales_review_taxes,name,sales_order,account_head,taxes_and_charges):
	review_doc_template = frappe.db.sql("""select drt.fieldname from `tabDocument Review Templates` dr ,`tabDocument Review Template Table` drt where dr.doc_type = "Sales Order" and dr.name = drt.parent and dr.is_default =1 and dr.docstatus =1""",as_dict=1)
	tax_table_name = frappe.db.sql("""select name from `tabSales Taxes and Charges` where parent = %s and account_head =%s""",(sales_order,account_head), as_dict=1)
	tax_name = tax_table_name[0].name
	field_List = json.loads(sales_review_taxes)

	for sales in field_List:
		propose_new = sales['propose_new_value']
		reject_field = sales['reject_field']
		get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': name , sales['reject_field']:1, "account_head" :account_head }, fields=[sales['propose_new_value']])
		if get_checked:
			for new_list in get_checked:
				for rev in review_doc_template:
					propose = "propose_new_"+rev.fieldname
					if propose_new == propose:
						frappe.db.set_value("Sales Taxes and Charges",tax_name,rev.fieldname,new_list[str(propose_new)])
	doc = frappe.get_doc("Sales Taxes and Charges",tax_name)
	doc.save()
@frappe.whitelist()
def update_sales_order_team(sales_review_sales_team,name,sales_order):
	review_doc_template = frappe.db.sql("""select drt.fieldname from `tabDocument Review Templates` dr ,`tabDocument Review Template Table` drt where dr.doc_type = "Sales Order" and dr.name = drt.parent and dr.is_default =1 and dr.docstatus =1""",as_dict=1)
	tax_table_name = frappe.db.sql("""select name from `tabSales Team` where parent = %s""",(sales_order), as_dict=1)
	tax_name = tax_table_name[0].name
	field_List = json.loads(sales_review_sales_team)

	for sales in field_List:
		propose_new = sales['propose_new_value']
		reject_field = sales['reject_field']
		get_checked = frappe.get_all('Sales Team Review', filters={'parent': name , sales['reject_field']:1}, fields=[sales['propose_new_value']])
		if get_checked:
			for new_list in get_checked:
				for rev in review_doc_template:
					propose = "propose_new_"+rev.fieldname
					if propose_new == propose:
						frappe.db.set_value("Sales Taxes and Charges",tax_name,rev.fieldname,new_list[str(propose_new)])
	doc = frappe.get_doc("Sales Team",tax_name)
	doc.save()
@frappe.whitelist()
def get_roles(user,role):
	user_data = frappe.db.sql("""select role from `tabHas Role` where parent = '"""+user+"""' AND role =%s """,role,as_dict=1)
	if user_data is not None:
		return user_data
	else:
		return None
@frappe.whitelist()
def get_check_box_cheched(sales_order,review):
	sales_order_no = sales_order.sales_order
	sales_order_docstatus = sales_order.docstatus
	if sales_order_docstatus == 0:
		frappe.db.set_value("Sales Order",sales_order_no,"under_review" , 1);
		#name = frappe.db.sql("""update `tab""" +doctype + """`set under_review = 1 where name = %s""",(name),as_dict=1)
	elif sales_order_docstatus == 1 or sales_order_docstatus == 2:
		frappe.db.set_value("Sales Order",sales_order_no,"under_review" , 0);
		#name = frappe.db.sql("""update `tab""" +doctype + """`set under_review = 1 where name = %s""",(name),as_dict=1)
	return True
@frappe.whitelist()
def get_sales_order_review(name):
	sales_order_review = frappe.db.sql("""select * from `tabSales Order Review` where sales_order = %s order by name DESC limit 1""",(name), as_dict =1)
	return sales_order_review
@frappe.whitelist()
def get_sales_order_review_with_so(name):
	sales_order_review = frappe.db.sql("""select * from `tabSales Order Review` where name = %s order by name DESC limit 1""",(name), as_dict =1)
	return sales_order_review
def get_sales_order_review_with_so_again(name):
	sales_order_review = frappe.db.sql("""select * from `tabSales Order Review` where sales_order = %s order by name DESC limit 1""",(name), as_dict =1)
	return sales_order_review
@frappe.whitelist()
def get_check_box_uncheck(sales_order):
	sales_order_no = sales_order.sales_order
	frappe.db.set_value("Sales Order",sales_order_no,"under_review" , 0);
	#name = frappe.db.sql("""update `tab""" +doctype + """`set under_review = 1 where name = %s""",(name),as_dict=1)
	return True
@frappe.whitelist()
def get_check_before_submit(doctype,name):
	review_details = get_review_templates(doctype)
	doctype_field = "Sales Order Review"
	review_doc_field = get_doc_details(doctype_field)
	creator = "SO Creator"
	overrider = "SO Overwritter"
	reviewer = "SO Reviewer"
	role_creator = get_roles(frappe.session.user,creator)
	role_reviewer = get_roles(frappe.session.user,reviewer)
	role_overrider = get_roles(frappe.session.user,overrider)
	if len(review_details) != 0:
		if role_reviewer is None:
			if role_overrider is None:
				if role_creator:
					check_for_sales_review = sales_order_review_values(name,sales_order)
					if check_for_sales_review == True:
						frappe.throw("Something changed in Sales Order Review, Please visit sales order review...")
				else:
					frappe.throw(" Access Rights Error! You do not have permission to perform this operation!")
			else:
				pass
		else:
			frappe.throw(" Access Rights Error! You do not have permission to perform this operation!")

@frappe.whitelist()
def create_sales_order(sales_review,name,sales_order):
	data = []
	doctype_field = "Sales Order Review"
	doctype_field_item = "Sales Order Item Review"
	doctype_field_taxes = "Sales Taxes and Charges Review"
	doctype = "Sales Order"
	created_new_doc = False
	submited_same_doc = False
	review_details = get_review_templates(doctype)
	review_doc_field = get_doc_details(doctype_field)
	review_doc_item_field = get_doc_details(doctype_field_item)
	review_doc_taxes_field = get_doc_details(doctype_field_taxes)
	for rev in review_details:
		if rev.field_label == "Parent Field":
			for r_doc in review_doc_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == r_doc.fieldname:
					reject_field = "reject_"+rev.fieldname
					get_checked = frappe.get_all('Sales Order Review', filters={'name': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Sales Order', filters={'name': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:

								created_new_doc = True
								break
		elif rev.field_label == "Item Field":
			for item_rev in review_doc_item_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == item_rev.fieldname:
					reject_field = "reject_"+rev.fieldname
					get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Sales Order Item', filters={'parent': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:

								created_new_doc = True
								break
		elif rev.field_label == "Tax Field":
			for taxes_review in review_doc_taxes_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == taxes_review.fieldname:
					reject_field = "reject_"+rev.fieldname
					get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Sales Taxes and Charges', filters={'parent': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:

								created_new_doc = True
								break
	if created_new_doc == False:
		doc = frappe.get_doc("Sales Order",sales_order)
		doc.save()
		doc.submit()
		frappe.msgprint(sales_order+" has been submitted")
		return False
	elif created_new_doc == True:
		#frappe.throw("value dones not matched")
		outerJson_Transfer = []
		creation_Date = datetime.datetime.now()
		company = frappe.db.get_single_value("Global Defaults", "default_company")
		sales_order_review = get_sales_order_review(name)
		return True



@frappe.whitelist()
def mapped_sales_order(source_name, target_doc=None, ignore_permissions=False):
	validate_sales_order = get_checked = frappe.get_all('Sales Order', filters={'so_reviewed': source_name}, fields=["name"])
	taxes_and_charges = ""
	if len(validate_sales_order) == 0:
		outerJson_Transfer = []
		doctype_field = "Sales Order Review"
		item_doc = "Sales Order Item Review"
		taxe_doc = "Sales Taxes and Charges Review"
		doctype = "Sales Order"
		created_new_doc = False
		submited_same_doc = False
		review_details = get_review_templates(doctype)
		review_doc_field = get_doc_details(doctype_field)
		review_item_field = get_doc_details(item_doc)
		review_taxes_field = get_doc_details(taxe_doc)
		customer = ""
		delivery_date = ""
		order_type = ""
		company = ""
		customer_address = ""
		shipping_address_name = ""
		contact_person = ""
		company_address = ""
		set_warehouse = ""
		apply_discount_on = ""
		base_discount_amount = 0.0
		additional_discount_percentage = 0.0
		discount_amount = 0.0
		project = ""
		source = ""
		campaign = ""
		item_code = ""
		tc_name = ""
		
		for rev in review_details:
			if rev.fieldname == "delivery_date" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["delivery_date","reject_delivery_date","accept_delivery_date","propose_new_delivery_date"])
				if get_checked[0].reject_delivery_date ==1:
					if get_checked[0].propose_new_delivery_date is not None:
						delivery_date = get_checked[0].propose_new_delivery_date

			elif rev.fieldname == "customer" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["customer","reject_customer","accept_customer","propose_new_customer"])
				if get_checked[0].reject_customer ==1:
					if get_checked[0].propose_new_customer is not None:
						customer = get_checked[0].propose_new_customer

			elif rev.fieldname == "order_type" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["order_type","reject_order_type","accept_order_type","propose_new_order_type"])
				if get_checked[0].reject_order_type ==1:
					if get_checked[0].propose_new_order_type is not None:
						order_type = get_checked[0].propose_new_order_type

			elif rev.fieldname == "company" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["company","reject_company","accept_company","propose_new_company"])
				if get_checked[0].reject_company ==1:
					if get_checked[0].propose_new_company is not None:
						company = get_checked[0].propose_new_company

			elif rev.fieldname == "customer_address" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["customer_address","reject_customer_address","accept_customer_address","propose_new_customer_address"])
				if get_checked[0].reject_customer_address ==1:
					if get_checked[0].propose_new_customer_address is not None:
						customer_address = get_checked[0].propose_new_customer_address

			elif rev.fieldname == "shipping_address_name" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["shipping_address_name","reject_shipping_address_name","accept_shipping_address_name","propose_new_shipping_address_name"])
				if get_checked[0].reject_shipping_address_name ==1:
					if get_checked[0].propose_new_shipping_address_name is not None:
						shipping_address_name = get_checked[0].propose_new_shipping_address_name

			elif rev.fieldname == "contact_person" and rev.field_label == "Parent Field":

				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["contact_person","reject_contact_person","accept_contact_person","propose_new_contact_person"])
				if get_checked[0].reject_contact_person ==1:
					if get_checked[0].propose_new_contact_person is not None:
						contact_person = get_checked[0].propose_new_contact_person

			elif rev.fieldname == "company_address" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["company_address","reject_company_address","accept_company_address","propose_new_company_address"])
				if get_checked[0].reject_company_address ==1:
					if get_checked[0].propose_new_company_address is not None:
						company_address = get_checked[0].propose_new_company_address

			elif rev.fieldname == "set_warehouse" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["set_warehouse","reject_set_warehouse","accept_set_warehouse","propose_new_set_warehouse"])
				if get_checked[0].reject_set_warehouse ==1:
					if get_checked[0].propose_new_set_warehouse is not None:
						set_warehouse = get_checked[0].propose_new_set_warehouse

			elif rev.fieldname == "apply_discount_on" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["apply_discount_on","reject_apply_discount_on","accept_apply_discount_on","propose_new_apply_discount_on"])
				if get_checked[0].reject_apply_discount_on ==1:
					if get_checked[0].propose_new_apply_discount_on is not None:
						apply_discount_on = get_checked[0].propose_new_apply_discount_on

			elif rev.fieldname == "base_discount_amount" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["base_discount_amount","reject_base_discount_amount","accept_base_discount_amount","propose_new_base_discount_amount"])
				if get_checked[0].reject_base_discount_amount ==1:
					if get_checked[0].propose_new_base_discount_amount is not None:
						base_discount_amount = get_checked[0].propose_new_base_discount_amount

			elif rev.fieldname == "additional_discount_percentage" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["additional_discount_percentage","reject_additional_discount_percentage","accept_additional_discount_percentage","propose_new_additional_discount_percentage"])
				if get_checked[0].reject_additional_discount_percentage ==1:
					if get_checked[0].propose_new_additional_discount_percentage is not None:
						additional_discount_percentage = get_checked[0].propose_new_additional_discount_percentage

			elif rev.fieldname == "discount_amount" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["discount_amount","reject_discount_amount","accept_discount_amount","propose_new_discount_amount"])
				if get_checked[0].reject_discount_amount ==1:
					if get_checked[0].propose_new_discount_amount is not None:
						discount_amount = get_checked[0].propose_new_discount_amount

			elif rev.fieldname == "project" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["project","reject_project","accept_project","propose_new_project"])
				if get_checked[0].reject_project ==1:
					if get_checked[0].propose_new_project is not None:
						project = get_checked[0].propose_new_project

			elif rev.fieldname == "source" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["source","reject_source","accept_source","propose_new_source"])
				if get_checked[0].reject_source ==1:
					if get_checked[0].propose_new_source is not None:
						source = get_checked[0].propose_new_source

			elif rev.fieldname == "campaign" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["campaign","reject_campaign","accept_campaign","propose_new_campaign"])
				if get_checked[0].reject_campaign ==1:
					if get_checked[0].propose_new_campaign is not None:
						campaign = get_checked[0].propose_new_campaign
			elif rev.fieldname == "tc_name" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["tc_name","reject_tc_name","accept_tc_name","propose_new_tc_name"])
				if get_checked[0].reject_tc_name ==1:
					if get_checked[0].propose_new_tc_name is not None:
						tc_name = get_checked[0].propose_new_tc_name
			elif rev.fieldname == "taxes_and_charges" and rev.field_label == "Parent Field":
				get_checked = frappe.get_all('Sales Order Review', filters={'name': source_name}, fields=["taxes_and_charges","reject_taxes_and_charges","accept_taxes_and_charges","propose_new_taxes_and_charges"])
				if get_checked[0].reject_taxes_and_charges ==1:
					if get_checked[0].propose_new_taxes_and_charges is not None:
						taxes_and_charges = get_checked[0].propose_new_taxes_and_charges
		def update_item(source, target_doc, source_parent):
			item_code = ""
			control_bom = ""
			qty = 0.0
			uom = ""
			conversion_factor = 0.0
			price_list_rate = 0.0
			margin_rate_or_amount = 0.0
			margin_type = ""
			rate_with_margin = 0.0
			discount_percentage = 0
			rate = 0.0
			weight_per_unit = 0.0
			weight_uom = ""
			item_delivery_date = ""
			warehouse = ""
			image = ""
			item_name = ""
			description = ""
			get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name, "item_code":source.item_code}, fields=["item_code"])
			if source.item_code == get_checked[0].item_code:
				for rev in review_details:
					if rev.fieldname == "item_code" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["item_code","reject_item_code","accept_item_code","propose_new_item_code"])
						if get_checked[0].reject_item_code ==1:
							if get_checked[0].propose_new_item_code is not None:
								item_code = get_checked[0].propose_new_item_code
					elif rev.fieldname == "item_name" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["item_name","reject_item_name","accept_item_name","propose_new_item_name"])
						if get_checked[0].reject_item_name ==1:
							if get_checked[0].propose_new_item_name is not None:
								item_name = get_checked[0].propose_new_item_name
					elif rev.fieldname == "description" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["description","reject_description","accept_description","propose_new_description"])
						if get_checked[0].reject_description ==1:
							if get_checked[0].propose_new_description is not None:
								description = get_checked[0].propose_new_description
					elif rev.fieldname == "qty" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["qty","reject_qty","accept_qty","propose_new_qty"])
						if get_checked[0].reject_qty ==1:
							if get_checked[0].propose_new_qty is not None:
								qty = get_checked[0].propose_new_qty


					elif rev.fieldname == "conversion_factor" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["conversion_factor","reject_conversion_factor","accept_conversion_factor","propose_new_conversion_factor"])
						if get_checked[0].reject_conversion_factor ==1:
							if get_checked[0].propose_new_conversion_factor is not None:
								conversion_factor = get_checked[0].propose_new_conversion_factor

					elif rev.fieldname == "uom" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["uom","reject_uom","accept_uom","propose_new_uom"])
						if get_checked[0].reject_uom ==1:
							if get_checked[0].propose_new_uom is not None:
								uom = get_checked[0].propose_new_uom

					elif rev.fieldname == "price_list_rate" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["price_list_rate","reject_price_list_rate","accept_price_list_rate","propose_new_price_list_rate"])
						if get_checked[0].reject_price_list_rate ==1:
							if get_checked[0].propose_new_price_list_rate is not None:
								price_list_rate = get_checked[0].propose_new_price_list_rate

					elif rev.fieldname == "margin_type" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["margin_type","reject_margin_type","accept_margin_type","propose_new_margin_type"])
						if get_checked[0].reject_margin_type ==1:
							if get_checked[0].propose_new_margin_type is not None:
								margin_type = get_checked[0].propose_new_margin_type

					elif rev.fieldname == "margin_rate_or_amount" and rev.field_label == "Item Field":

						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["margin_rate_or_amount","reject_margin_rate_or_amount","accept_margin_rate_or_amount","propose_new_margin_rate_or_amount"])
						if get_checked[0].reject_margin_rate_or_amount ==1:
							if get_checked[0].propose_new_margin_rate_or_amount is not None:
								margin_rate_or_amount = get_checked[0].propose_new_margin_rate_or_amount

					elif rev.fieldname == "rate_with_margin" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["rate_with_margin","reject_rate_with_margin","accept_rate_with_margin","propose_new_rate_with_margin"])
						if get_checked[0].reject_rate_with_margin ==1:
							if get_checked[0].propose_new_rate_with_margin is not None:
								rate_with_margin = get_checked[0].propose_new_rate_with_margin

					elif rev.fieldname == "discount_percentage" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["discount_percentage","reject_discount_percentage","accept_discount_percentage","propose_new_discount_percentage"])
						if get_checked[0].reject_discount_percentage ==1:
							if get_checked[0].propose_new_discount_percentage is not None:
								discount_percentage = get_checked[0].propose_new_discount_percentage

					elif rev.fieldname == "rate" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["rate","reject_rate","accept_rate","propose_new_rate"])
						if get_checked[0].reject_rate ==1:
							if get_checked[0].propose_new_rate is not None:
								rate = get_checked[0].propose_new_rate

					elif rev.fieldname == "weight_per_unit" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["weight_per_unit","reject_weight_per_unit","accept_weight_per_unit","propose_new_weight_per_unit"])
						if get_checked[0].reject_weight_per_unit ==1:
							if get_checked[0].propose_new_weight_per_unit is not None:
								weight_per_unit = get_checked[0].propose_new_weight_per_unit

					elif rev.fieldname == "weight_uom" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["weight_uom","reject_weight_uom","accept_weight_uom","propose_new_weight_uom"])
						if get_checked[0].reject_weight_uom ==1:
							if get_checked[0].propose_new_weight_uom is not None:
								weight_per_unit = get_checked[0].propose_new_weight_uom

					elif rev.fieldname == "delivery_date" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["delivery_date","reject_delivery_date","accept_delivery_date","propose_new_delivery_date"])
						if get_checked[0].reject_delivery_date ==1:
							if get_checked[0].propose_new_delivery_date is not None:
								item_delivery_date = get_checked[0].propose_new_delivery_date
					elif rev.fieldname == "warehouse" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["warehouse","reject_warehouse","accept_warehouse","propose_new_warehouse"])
						if get_checked[0].reject_warehouse ==1:
							if get_checked[0].propose_new_warehouse is not None:
								warehouse = get_checked[0].propose_new_warehouse
					elif rev.fieldname == "image" and rev.field_label == "Item Field":
						get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["image","reject_image","accept_image","propose_new_image"])
						if get_checked[0].reject_image ==1:
							if get_checked[0].propose_new_image is not None:
								image = get_checked[0].propose_new_image
				if item_name != "" and item_name != None:
					target_doc.item_name = item_name
				else:
					target_doc.item_name = source.item_name
				if item_code != "" and item_code != None:
					target_doc.item_code = item_code
				else:
					target_doc.item_code = source.item_code
				
				if description != "" and description != None:
					target_doc.description = description
				else:
					target_doc.description = source.description
				if delivery_date != "" and delivery_date != None:
					target_doc.delivery_date = delivery_date
				elif item_delivery_date != "" and item_delivery_date != None:
					target_doc.delivery_date = item_delivery_date
				else:
					target_doc.delivery_date = source.delivery_date
				
				if qty != 0.0 and qty != None:
					#target_doc.qty = qty
					target_doc.qty = flt(qty) - flt(source.ordered_qty)
				else:
					#target_doc.qty = source.qty
					target_doc.qty = flt(source.qty) - flt(source.ordered_qty)
				if uom != "" and uom != None:
					target_doc.uom = uom
				else:
					target_doc.uom = source.uom
				if price_list_rate != 0.0 and price_list_rate != None:
					target_doc.price_list_rate = price_list_rate
				else:
					target_doc.price_list_rate = source.price_list_rate
				if margin_type != "" and margin_type != None:
					target_doc.margin_type = margin_type
				else:
					target_doc.margin_type = source.margin_type
				if conversion_factor != 0.0 and conversion_factor != None:
					target_doc.conversion_factor = conversion_factor
					if qty != 0.0 and qty != None:
						target_doc.stock_qty = (flt(qty) - flt(source.ordered_qty)) * flt(conversion_factor)
					else:
						target_doc.stock_qty = (flt(source.qty) - flt(source.ordered_qty)) * flt(conversion_factor)
				else:
					target_doc.conversion_factor = source.conversion_factor
					if qty != 0.0 and qty != None:
						target_doc.stock_qty = (flt(qty) - flt(source.ordered_qty)) * flt(source.conversion_factor)
					else:
						target_doc.stock_qty = (flt(source.qty) - flt(source.ordered_qty)) * flt(source.conversion_factor)
				if margin_rate_or_amount != 0.0 and margin_rate_or_amount != None:
					target_doc.margin_rate_or_amount = margin_rate_or_amount
				else:
					target_doc.margin_rate_or_amount = source.margin_rate_or_amount
				if rate_with_margin != 0.0 and rate_with_margin != None:
					target_doc.rate_with_margin = rate_with_margin
				else:
					target_doc.rate_with_margin = source.rate_with_margin
				if discount_percentage != 0 and discount_percentage != None:
					target_doc.discount_percentage = discount_percentage
					target_doc.discount_amount = (float(source.price_list_rate)*float(discount_percentage))/100
				else:
					target_doc.discount_percentage = source.discount_percentage
				if rate != 0.0 and rate != None:
					target_doc.rate = rate
				else:
					target_doc.rate = source.rate
				if target_doc.discount_amount:
					target_doc.rate = source.price_list_rate - target_doc.discount_amount
				if weight_per_unit != 0.0 and weight_per_unit != None:
					target_doc.weight_per_unit = weight_per_unit
				else:
					target_doc.weight_per_unit = source.weight_per_unit
				if weight_uom != "" and weight_uom != None:
					target_doc.weight_uom = weight_uom
				else:
					target_doc.weight_uom = source.weight_uom
				if set_warehouse != "" and set_warehouse != None:
					target_doc.warehouse = set_warehouse
				elif warehouse != "" and warehouse != None:
					target_doc.warehouse = warehouse
				else:
					target_doc.warehouse = source.warehouse

				if image != "" and image != None:
					target_doc.image = image
				else:
					target_doc.image = source.image


		def update_tax(source, target_doc, source_parent):
			#target_doc.account_head = source.account_head
			#target_doc.rate = source.rate
			target_doc.cost_center = source.cost_center
			#target_doc.charge_type = source.charge_type
			account_head = ""
			row_id = 0
			charge_type = ""
			rate = 0.0

			get_checked_account = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': source_name, "account_head":source.account_head}, fields=["account_head"])
			if source.account_head == get_checked_account[0].account_head:
				for rev in review_details:
					if rev.fieldname == "account_head" and rev.field_label == "Tax Field":

						get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': source_name,"account_head":source.account_head}, fields=["account_head","reject_account_head","accept_account_head","propose_new_account_head"])
						if get_checked[0].reject_account_head ==1:
							if get_checked[0].propose_new_account_head is not None:
								account_head = get_checked[0].propose_new_account_head

					elif rev.fieldname == "row_id" and rev.field_label == "Tax Field":

						get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': source_name,"account_head":source.account_head}, fields=["row_id","reject_row_id","accept_row_id","propose_new_row_id"])
						if get_checked[0].reject_row_id ==1:
							if get_checked[0].propose_new_row_id is not None:
								row_id = get_checked[0].propose_new_row_id

					elif rev.fieldname == "charge_type" and rev.field_label == "Tax Field":

						get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': source_name,"account_head":source.account_head}, fields=["charge_type","reject_charge_type","accept_charge_type","propose_new_charge_type"])
						if get_checked[0].reject_charge_type ==1:
							if get_checked[0].propose_new_charge_type is not None:
								charge_type = get_checked[0].propose_new_charge_type

					elif rev.fieldname == "rate" and rev.field_label == "Tax Field":

						get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': source_name,"account_head":source.account_head}, fields=["rate","reject_rate","accept_rate","propose_new_rate"])
						if get_checked[0].reject_rate ==1:
							if get_checked[0].propose_new_rate is not None:
								rate = get_checked[0].propose_new_rate

				if rate != 0.0 and rate != None:
					#print "rate---------------",rate
					target_doc.rate = rate
				else:
					target_doc.rate = source.rate
				
		def set_missing_values(source, target):
			target.is_pos = 0

			if customer != "" and customer != None:
				target.customer = customer
			else:
				target.customer = source.customer
			if project != "" and project != None:
				target.project = project
			else:
				target.project = source.project
			if campaign != "" and campaign != None:
				target.campaign = campaign
			else:
				target.campaign = source.campaign

			if order_type != "" and order_type != None:
				target.order_type = order_type
			else:
				target.order_type = source.order_type
			#if source != "" and source != None:
				#target.source = source
			#else:
				#target.source = source.source

			if discount_amount != 0.0 and discount_amount != None:
				target.discount_amount = discount_amount
			else:
				target.discount_amount = source.discount_amount
			if shipping_address_name != "" and shipping_address_name != None:
				target.shipping_address_name = shipping_address_name
			else:
				target.shipping_address_name = source.shipping_address_name

			if company != "" and company != None:
				target.company = company
			else:
				target.company = source.company
			if apply_discount_on != "" and apply_discount_on != None:
				target.apply_discount_on = apply_discount_on
			else:
				target.apply_discount_on = source.apply_discount_on
			if additional_discount_percentage != 0.0 and additional_discount_percentage != None:
				target.additional_discount_percentage = additional_discount_percentage
			else:
				target.additional_discount_percentage = source.additional_discount_percentage
			if company_address != "" and company_address != None:
				target.company_address = company_address
			else:
				target.company_address = source.company_address

			if set_warehouse != "" and set_warehouse != None:
				target.set_warehouse = set_warehouse
			else:
				target.set_warehouse = source.set_warehouse
			if base_discount_amount != 0.0 and base_discount_amount != None:
				target.base_discount_amount = base_discount_amount
			else:
				target.base_discount_amount = source.base_discount_amount
			if contact_person != "" and contact_person != None:
				target.contact_person = contact_person
			else:
				target.contact_person = source.contact_person
			if customer_address != "" and customer_address != None:
				target.customer_address = customer_address
			else:
				target.customer_address = source.customer_address

			if delivery_date != "" and delivery_date != None:
				target.delivery_date = delivery_date
			else:
				target.delivery_date = source.delivery_date
			
			if tc_name != "" and tc_name != None:
				target.tc_name = tc_name
				get_checked = frappe.get_all('Terms and Conditions', filters={'name': tc_name}, fields=["terms"])
				target.terms = get_checked[0].terms
				
			else:
				target.tc_name = source.tc_name
				target.terms = source.terms
			if taxes_and_charges != "" and taxes_and_charges != None:
				target.taxes_and_charges = taxes_and_charges
				target.taxes = ""
				
			else:
				target.taxes_and_charges = source.taxes_and_charges
			nhance_settings = frappe.db.get_single_value("Nhance Settings","pch_post_review_so_series")
			if nhance_settings is not None:
				target.naming_series = nhance_settings
			target.transaction_date = source.transaction_date
			target.ignore_pricing_rule = source.ignore_pricing_rule
			target.flags.ignore_permissions = True
			target.run_method("set_missing_values")
			target.run_method("set_po_nos")
			target.run_method("calculate_taxes_and_totals")

			if source.loyalty_points and source.order_type == "Shopping Cart":
				target.redeem_loyalty_points = 1
		def postprocess(source, target):
			set_missing_values(source, target)

		doclist = get_mapped_doc("Sales Order Review", source_name, {
			"Sales Order Review": {
				"doctype": "Sales Order",
				"field_map": {
					"delivery_date":delivery_date,
					"party_account_currency": "party_account_currency",
					"payment_terms_template": "payment_terms_template",

				},
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Sales Order Item Review": {
						"doctype": "Sales Order Item",
						"field_map":  [
							["name", "sales_order_item"],
							["parent", "sales_order"],
							["stock_uom", "stock_uom"],
							["uom", "uom"],
							["conversion_factor", "conversion_factor"]

				 		],
						"field_no_map": [
							"rate",
							"price_list_rate"
						],
						"postprocess": update_item,
						"condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
					},
			"Sales Taxes and Charges Review": {
				"doctype": "Sales Taxes and Charges",
				"field_map":  [
					["parent", "sales_order"]
				],
				"postprocess": update_tax,
			},
			"Payment Schedule Review": {
				"doctype": "Payment Schedule",
				"field_map":  [
					["parent", "sales_order"]
				],
			},
			"Sales Team Review":{
				"doctype": "Sales Team",
				"field_map":  [
					["parent", "sales_order"]
				],
			}
		}, target_doc, postprocess, ignore_permissions=ignore_permissions)
		doclist.save()
		if taxes_and_charges != "" and taxes_and_charges != None:
			get_checked = frappe.get_list('Sales Taxes and Charges', filters={'parent': taxes_and_charges}, fields=["account_head","rate","description","charge_type","row_id","idx",'cost_center'] , order_by='idx')
			doc = frappe.get_doc("Sales Order",doclist.name)
			rows = {}
			for checked in get_checked:
				rows.update({
					'account_head':checked['account_head'],
					'rate':checked['rate'],
					'description':checked['description'],
					'charge_type':checked['charge_type'],
					'row_id':checked['row_id'],
					'cost_center':checked['cost_center']
				})
				doc.append("taxes",rows)
			doc.save()
		doc_refres = frappe.get_doc("Sales Order Review",source_name)
		frappe.msgprint("Sales Order "+frappe.bold(doclist.name)+" has been created to replace "+frappe.bold(doc_refres.sales_order)+" as a result of the Sales order Review Process.")
		return doclist.name
	else:
		frappe.msgprint(validate_sales_order[0].name+" Already accepted for this review")

	
@frappe.whitelist()
def check_before_submit(before_submit,data):
	creator = "SO Creator"
	reviewer = "SO Reviewer"
	overritter = "SO Overwritter"
	role_creator = get_roles(frappe.session.user,creator)
	role_reviewer = get_roles(frappe.session.user,reviewer)
	role_overrider = get_roles(frappe.session.user,overritter)
	sales_order_review = get_sales_order_review(before_submit.name)
	#print "role_creator------------",role_creator
	#print "role_reviewer------------",role_reviewer
	if len(role_reviewer) == 0:
		if len(role_overrider) == 0:
			if role_creator:
				if sales_order_review:
					if sales_order_review[0].docstatus ==1:
						get_varification = sales_order_review_values(sales_order_review[0].name,before_submit.name)

						if get_varification == True:
							frappe.throw("something has changed in link doctype Sales Order Review "+sales_order_review[0].name)
					else:
						frappe.throw("Please submit first Sales Order Review "+sales_order_review[0].name)
			else:
				frappe.throw("Access Rights Error! You do not have permission to perform this operation!")
		else:
			pass
	else:
		frappe.throw(" Access Rights Error! You do not have permission to perform this operation!")
	'''
	if sales_order_review[0].name is not None:
		if sales_order_review[0].docstatus == 1:
			if reviewer_roles is not None and reviewer_roles is not "":
				get_varification = sales_order_review_values(sales_order_review[0].name,before_submit.name)
				if get_varification == True:
					froppe.throw("something has changed Sales Order Review "+sales_order_review[0].name)
			elif creator_roles is not None and reviewer_roles is not "":
				get_varification = sales_order_review_values(sales_order_review[0].name,before_submit.name)
				if get_varification == True:
					froppe.throw("something has changed Sales Order Review "+sales_order_review[0].name)

			elif reviewer_roles is None and reviewer_roles is  "":
				froppe.throw("Dear user "+ frappe.user + " you don't have permission " + '"' + overwriter_roles + '"' + "to ignore sales order review " + sales_order_review[0].name)

	'''

def sales_order_review_values(name,sales_order):
	data = []
	doctype_field = "Sales Order Review"
	doctype_field_item = "Sales Order Item Review"
	doctype_field_taxes = "Sales Taxes and Charges Review"
	doctype = "Sales Order"
	created_new_doc = False
	submited_same_doc = False
	review_details = get_review_templates(doctype)
	review_doc_field = get_doc_details(doctype_field)
	review_doc_item_field = get_doc_details(doctype_field_item)
	review_doc_taxes_field = get_doc_details(doctype_field_taxes)
	for rev in review_details:
		if rev.field_label == "Parent Field":
			for r_doc in review_doc_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == r_doc.fieldname:
					reject_field = "reject_"+rev.fieldname
					accept_field = "accept_"+rev.fieldname
					get_checked = frappe.get_all('Sales Order Review', filters={'name': name}, fields=[str(rev.fieldname),str(proposed_new),str(accept_field),str(reject_field)])
					get_original_order_data = frappe.get_all('Sales Order', filters={'name': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						for check in get_checked:
							for checked in get_original_order_data:
								if check[str(accept_field)] == 1:
									if check[str(rev.fieldname)] != checked[str(rev.fieldname)]:

										created_new_doc = True
										break
								elif check[str(reject_field)] == 1:		
									if check[str(proposed_new)] is not None:
										if check[str(proposed_new)] != checked[str(rev.fieldname)]:

											created_new_doc = True
											break
		elif rev.field_label == "Item Field":
			for item_rev in review_doc_item_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == item_rev.fieldname:
					reject_field = "reject_"+rev.fieldname
					accept_field = "accept_"+rev.fieldname
					get_checked = frappe.get_all('Sales Order Item Review', filters={'parent': name}, fields=[str(rev.fieldname),str(proposed_new),str(accept_field),str(reject_field),'item_code'])
					get_original_order_data = frappe.get_all('Sales Order Item', filters={'parent': sales_order}, fields=[str(rev.fieldname),'item_code'])
					#print "get_checked--------------",get_checked
					#print "get_original_order_data--------------",get_original_order_data
					if get_checked:
						for check in get_checked:
							for checked in get_original_order_data:
								if check['item_code'] == checked['item_code']:
									if check[str(accept_field)] == 1:
										if check[str(rev.fieldname)] != checked[str(rev.fieldname)]:

											created_new_doc = True
											break
									elif check[str(reject_field)] == 1:		
										if check[str(proposed_new)] is not None:
											if check[str(proposed_new)] != checked[str(rev.fieldname)]:

												created_new_doc = True
												break
		elif rev.field_label == "Tax Field":
			for taxes_review in review_doc_taxes_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == taxes_review.fieldname:
					reject_field = "reject_"+rev.fieldname
					accept_field = "accept_"+rev.fieldname
					get_checked = frappe.get_all('Sales Taxes and Charges Review', filters={'parent': name}, fields=[str(rev.fieldname),str(proposed_new),str(accept_field),str(reject_field),'account_head'])
					get_original_order_data = frappe.get_all('Sales Taxes and Charges', filters={'parent': sales_order}, fields=[str(rev.fieldname),'account_head'])
					if get_checked:
						for check in get_checked:
							for checked in get_original_order_data:
								if check['account_head'] == checked['account_head']:
									if check[str(accept_field)] == 1:
										if check[str(rev.fieldname)] != checked[str(rev.fieldname)]:

											created_new_doc = True
											break
									elif check[str(reject_field)] == 1:		
										if check[str(proposed_new)] is not None:
											if check[str(proposed_new)] != checked[str(rev.fieldname)]:

												created_new_doc = True
												break
	return created_new_doc

@frappe.whitelist()
def remove_submit_permission_with_so(user,so_reviewed,name):

	#print "hello i am comming"
	role_so_creator = "SO Creator"
	role_so_overriter = "SO Overwritter"
	roles = frappe.get_all('Has Role', filters={'parent': user }, fields=['role'])
	validations = True
	defined_role = get_roles(user,role_so_creator)
	overritter_role = get_roles(user,role_so_overriter)
	check_for_review = get_sales_order_review_with_so(so_reviewed)
	check_for_sales_review = get_sales_order_review_with_so_again(name)
	#print "check_for_review---------------",check_for_review
	doctype = "Sales Order"
	if len(defined_role) != 0:
		if check_for_review:
			if check_for_sales_review:
				#print "check_for_sales_review-------------",check_for_sales_review
				validation = sales_order_review_values(check_for_sales_review[0].name,name)
				#print "validation--------------",validation
				if validation == True:
					validations = False
					frappe.throw("The values approved in the Sales Order Review document "+frappe.bold(check_for_sales_review[0].name)+" are different from the values you are using in this Sales Order document. Please review and change the values and try again. Or initiate a new document review if these are the values you want to use!")
				else:
					validations = True
			else:
				validation = sales_order_review_values(so_reviewed,name)
				if validation == True:
					validations = False
					frappe.throw("The values approved in the Sales Order Review document "+frappe.bold(so_reviewed)+" are different from the values you are using in this Sales Order document. Please review and change the values and try again. Or initiate a new document review if these are the values you want to use!")
				else:
					validations = True
	else:
		validations = False
		frappe.throw("Access Rights Error! You do not have permission to perform this operation!")

	return validations
@frappe.whitelist()
def remove_submit_permission(user,name):
	current_doc = frappe.get_doc("Sales Order",  name)
	validations = True
	role_so_overrite = "SO Overwritter"
	role_creator = "SO Creator"
	roles = frappe.get_all('Has Role', filters={'parent': user }, fields=['role'])
	creator_role = get_roles(user,role_creator)
	defined_role = get_roles(user,role_so_overrite)
	#check_for_review = sales_order_review_data(name)
	check_for_review = get_sales_order_review(name)
	doctype = "Sales Order"
	review_template = get_review_templates(doctype)
	if len(review_template) != 0:
		if len(check_for_review) != 0:
			if check_for_review[0].docstatus == 1:
				validation = sales_order_review_values(check_for_review[0].name,name)
				if validation == True:
					validations = False
					frappe.throw("The values approved in the Sales Order Review document "+frappe.bold(check_for_review[0].name)+" are different from the values you are using in this Sales Order document. Please review and change the values and try again. Or initiate a new document review if these are the values you want to use!")
				else:
					validations = True
					
			else:
				validations = False
				frappe.throw("Please Submit first Purchase Order Review "+frappe.bold(check_for_review[0].name))
		else:
			validations = False
			frappe.throw("This document cannot be submitted until a review is completed.  Please assign to a reviewer.")
	
	return validations

@frappe.whitelist()
def check_item_review_field(current_doc,review_doc,name):
	validation = True
	reviewer = "SO Reviewer"
	defined_role = get_roles(frappe.session.user,reviewer)
	if defined_role:
		review_details = get_review_templates(review_doc)
		review_doc_field = get_doc_details(current_doc)
		for current in review_doc_field:
			for rev in review_details:
				#print "rev--------------",rev

				accept_field = "accept_"+rev.fieldname
				reject_field = "reject_"+rev.fieldname
				if accept_field == current.fieldname:
					if rev.field_label == "Item Field":
						propose_new = "propose_new_"+rev.fieldname
						doc_details = frappe.get_all("Sales Order Item Review", filters={'parent': name}, fields=[accept_field,reject_field,propose_new] )
						#print "doc-------------",doc_details
						for doc in doc_details:
							if doc[str(accept_field)] == 1:
								pass
							elif doc[str(reject_field)] == 1:
								if doc[str(propose_new)] is not None and doc[str(propose_new)] is not 0 and doc[str(propose_new)] is not 0.0:
									pass
								else:
									frappe.throw("Please specify value in proposed new value field called "+frappe.bold(propose_new))
									validation = False
									break
							else:
								frappe.throw("Please give review either accept or reject for field "+frappe.bold(rev.fieldname))
								validation = False
								break
		return validation
	else:
		frappe.throw("Access Rights Error! You do not have permission to perform this operation!")
@frappe.whitelist()
def check_parent_review_field(current_doc,review_doc,name):
	validation = True
	reviewer = "SO Reviewer"
	defined_role = get_roles(frappe.session.user,reviewer)
	if defined_role:
		review_details = get_review_templates(review_doc)
		review_doc_field = get_doc_details(current_doc)
		for current in review_doc_field:
			for rev in review_details:
				#print "rev--------------",rev

				accept_field = "accept_"+rev.fieldname
				reject_field = "reject_"+rev.fieldname
				if accept_field == current.fieldname:
					if rev.field_label == "Parent Field":
						propose_new = "propose_new_"+rev.fieldname
						doc_details = frappe.get_all("Sales Order Review", filters={'name': name}, fields=[accept_field,reject_field,propose_new] )
						for doc in doc_details:
							if doc[str(accept_field)] == 1:
								pass
							elif doc[str(reject_field)] == 1:
								if doc[str(propose_new)]!= None and doc[str(propose_new)] != 0 and doc[str(propose_new)] != 0.0:
									pass
								else:
									validation = False
									frappe.throw("Please specify value in proposed new value field called "+frappe.bold(propose_new))
									break
							else:
								validation = False
								frappe.throw("Please give review either accept or reject for field "+frappe.bold(rev.fieldname))
								break
		return validation
	else:
		frappe.throw("Access Rights Error! You do not have permission to perform this operation!")
@frappe.whitelist()
def check_taxes_review_field(current_doc,review_doc,name):
	validation = True
	reviewer = "SO Reviewer"
	defined_role = get_roles(frappe.session.user,reviewer)
	if defined_role:
		review_details = get_review_templates(review_doc)
		review_doc_field = get_doc_details(current_doc)
		for current in review_doc_field:
			for rev in review_details:
				accept_field = "accept_"+rev.fieldname
				reject_field = "reject_"+rev.fieldname
				if accept_field == current.fieldname:
					if rev.field_label == "Tax Field":
						propose_new = "propose_new_"+rev.fieldname
						doc_details = frappe.get_all("Sales Taxes and Charges Review", filters={'parent': name}, fields=[accept_field,reject_field,propose_new] )
						for doc in doc_details:
							if doc[str(accept_field)] == 1:
								pass
							elif doc[str(reject_field)] == 1:
								if doc[str(propose_new)] != None and doc[str(propose_new)] != 0 and doc[str(propose_new)] != 0.0:
									pass
								else:
									frappe.throw("Please specify value in proposed new value field called "+frappe.bold(propose_new))
									validation = False
									break
							else:
								frappe.throw("Please give review either accept or reject for field "+frappe.bold(rev.fieldname))
								validation = False
								break
		return validation
	else:
		frappe.throw("Access Rights Error! You do not have permission to perform this operation!")
def sales_order_review_data(name):
	sales_order_review = frappe.db.sql("""select * from `tabSales Order Review` where sales_order = %s and docstatus =1 order by sales_order desc limit 1""",(name), as_dict =1)
	return sales_order_review
