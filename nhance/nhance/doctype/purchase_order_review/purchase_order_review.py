# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, getdate, comma_and, cint, nowdate, add_days
import json
import datetime
import time
class PurchaseOrderReview(Document):
	pass
@frappe.whitelist()
def make_purchase_order_review(source_name, target_doc=None, ignore_permissions=False):
	docname = "Purchase Order"
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
			"doctype": "Purchase Order Review",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"payment_terms_template": "payment_terms_template"
			},
			"validation": {
				"docstatus": ["=", 0]
			}
		},
		"Purchase Order Item": {
			"doctype": "Purchase Order Item Review",
			"field_map":  [
				["name", "purchase_order_item"],
				["parent", "purchase_order"],
				["stock_uom", "stock_uom"],
				["uom", "uom"],
				["conversion_factor", "conversion_factor"]
		
			],
			"field_no_map": [
				"rate",
				"price_list_rate"
			],
			"condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		},
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges Review",
				"field_map":  [
				["parent", "purchase_order"]
				]
				
		},
		"Payment Schedule": {
			"doctype": "Payment Schedule Review",
			"field_map":  [
				["parent", "purchase_order"]
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
	fields = frappe.db.sql("""select drt.label,drt.fieldname,drt.review_parameters,drt.field_label,drt.fieldtype,drt.options from `tabDocument Review Template Table` drt ,`tabDocument Review Templates` dr where dr.name = drt.parent AND dr.doc_type = %s and dr.is_default =1 and dr.docstatus =1""",(doctype), as_dict=1)
	return fields
@frappe.whitelist()
def get_roles(user,role):
	user_data = frappe.db.sql("""select role from `tabHas Role` where parent = '"""+user+"""' AND role =%s """,role,as_dict=1)
	if user_data is not None:
		return user_data
	else:
		return None
@frappe.whitelist()
def get_doc_details(doctype):
	doc_details = frappe.get_meta(doctype).get("fields")
	return doc_details
@frappe.whitelist()
def create_purchase_order(sales_review,name,sales_order):
	data = []
	doctype_field = "Purchase Order Review"
	doctype_field_item = "Purchase Order Item Review"
	doctype_field_taxes = "Purchase Taxes and Charges Review"
	doctype = "Purchase Order"
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
					get_checked = frappe.get_all('Purchase Order Review', filters={'name': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Purchase Order', filters={'name': sales_order}, fields=[str(rev.fieldname)])
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
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Purchase Order Item', filters={'parent': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:
							
								created_new_doc = True
								break
		elif rev.field_label == "Tax Field":
			for taxes_review in review_doc_taxes_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == item_rev.fieldname:
					reject_field = "reject_"+rev.fieldname
					get_checked = frappe.get_all('Purchase Taxes and Charges Review', filters={'parent': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Purchase Taxes and Charges', filters={'parent': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:
							
								created_new_doc = True
								break			
	if created_new_doc == False:
		doc = frappe.get_doc("Purchase Order",sales_order)
		doc.save()
		doc.submit()
		frappe.msgprint('"'+sales_order+'"'+"Base Purchase Order has been submitted")
		return False
	elif created_new_doc == True:
		#frappe.throw("value dones not matched")
		outerJson_Transfer = []
		creation_Date = datetime.datetime.now()
		company = frappe.db.get_single_value("Global Defaults", "default_company")
		supplier = ""
		return True
@frappe.whitelist()
def mapped_purchase_order(source_name, target_doc=None, ignore_permissions=False):
	outerJson_Transfer = []
	doctype_field = "Purchase Order Review"
	item_doc = "Purchase Order Item Review"
	taxe_doc = "Purchase Taxes and Charges Review"
	doctype = "Purchase Order"
	created_new_doc = False
	submited_same_doc = False
	review_details = get_review_templates(doctype)
	review_doc_field = get_doc_details(doctype_field)
	review_item_field = get_doc_details(item_doc)
	review_taxes_field = get_doc_details(taxe_doc)
	supplier = ""
	schedule_date = ""
	supplier_address = ""
	shipping_address = ""
	contact_person = ""
	company_address = ""
	set_warehouse = ""
	apply_discount_on = ""
	base_discount_amount = 0.0
	additional_discount_percentage = 0.0
	discount_amount = 0.0
	item_code = ""
	for rev in review_details:
		if rev.fieldname == "schedule_date" and rev.field_label == "Parent Field":
			
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["schedule_date","reject_schedule_date","accept_schedule_date","propose_new_schedule_date"])
			if get_checked[0].reject_schedule_date ==1:
				if get_checked[0].propose_new_schedule_date is not None:
					schedule_date = get_checked[0].propose_new_schedule_date
				

		elif rev.fieldname == "supplier" and rev.field_label == "Parent Field":
			
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["supplier","reject_supplier","accept_supplier","propose_new_supplier"])
			if get_checked[0].reject_supplier ==1:
				if get_checked[0].propose_new_supplier is not None:
					supplier = get_checked[0].propose_new_supplier
				

		elif rev.fieldname == "supplier_address" and rev.field_label == "Parent Field":
			
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["supplier_address","reject_supplier_address","accept_supplier_address","propose_new_supplier_address"])
			if get_checked[0].reject_supplier_address ==1:
				if get_checked[0].propose_new_supplier_address is not None:
					supplier_address = get_checked[0].propose_new_supplier_address
				

		elif rev.fieldname == "shipping_address" and rev.field_label == "Parent Field":
			
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["shipping_address","reject_shipping_address","accept_shipping_address","propose_new_shipping_address"])
			if get_checked[0].reject_shipping_address ==1:
				if get_checked[0].propose_new_shipping_address is not None:
					shipping_address = get_checked[0].propose_new_shipping_address
				

		elif rev.fieldname == "contact_person" and rev.field_label == "Parent Field":
			
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["contact_person","reject_contact_person","accept_contact_person","propose_new_contact_person"])
			if get_checked[0].reject_contact_person ==1:
				if get_checked[0].propose_new_contact_person is not None:
					contact_person = get_checked[0].propose_new_contact_person
				

		elif rev.fieldname == "set_warehouse" and rev.field_label == "Parent Field":
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["set_warehouse","reject_set_warehouse","accept_set_warehouse","propose_new_set_warehouse"])
			if get_checked[0].reject_set_warehouse ==1:
				if get_checked[0].propose_new_set_warehouse is not None:
					set_warehouse = get_checked[0].propose_new_set_warehouse
				

		elif rev.fieldname == "apply_discount_on" and rev.field_label == "Parent Field":
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["apply_discount_on","reject_apply_discount_on","accept_apply_discount_on","propose_new_apply_discount_on"])
			if get_checked[0].reject_apply_discount_on ==1:
				if get_checked[0].propose_new_apply_discount_on is not None:
					apply_discount_on = get_checked[0].propose_new_apply_discount_on
				

		elif rev.fieldname == "base_discount_amount" and rev.field_label == "Parent Field":
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["base_discount_amount","reject_base_discount_amount","accept_base_discount_amount","propose_new_base_discount_amount"])
			if get_checked[0].reject_base_discount_amount ==1:
				if get_checked[0].propose_new_base_discount_amount is not None:
					base_discount_amount = get_checked[0].propose_new_base_discount_amount
				

		elif rev.fieldname == "additional_discount_percentage" and rev.field_label == "Parent Field":
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["additional_discount_percentage","reject_additional_discount_percentage","accept_additional_discount_percentage","propose_new_additional_discount_percentage"])
			if get_checked[0].reject_additional_discount_percentage ==1:
				if get_checked[0].propose_new_additional_discount_percentage is not None:
					additional_discount_percentage = get_checked[0].propose_new_additional_discount_percentage
				

		elif rev.fieldname == "discount_amount" and rev.field_label == "Parent Field":
			get_checked = frappe.get_all('Purchase Order Review', filters={'name': source_name}, fields=["discount_amount","reject_discount_amount","accept_discount_amount","propose_new_discount_amount"])
			if get_checked[0].reject_discount_amount ==1:
				if get_checked[0].propose_new_discount_amount is not None:
					discount_amount = get_checked[0].propose_new_discount_amount
				
		
		
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
		bom = ""
		project = ""
		warehouse = ""
		item_schedule_date = ""
		expected_delivery_date = ""
		get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name, "item_code":source.item_code}, fields=["item_code"])
		if source.item_code == get_checked[0].item_code:
			for rev in review_details:
					
				if rev.fieldname == "qty" and rev.field_label == "Item Field":
			
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["qty","reject_qty","accept_qty","propose_new_qty"])
					if get_checked[0].reject_qty ==1:
						if get_checked[0].propose_new_qty is not None:
							qty = get_checked[0].propose_new_qty
						

				
				
				elif rev.fieldname == "conversion_factor" and rev.field_label == "Item Field":
			
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["conversion_factor","reject_conversion_factor","accept_conversion_factor","propose_new_conversion_factor"])
					if get_checked[0].reject_conversion_factor ==1:
						if get_checked[0].propose_new_conversion_factor is not None:
							conversion_factor = get_checked[0].propose_new_conversion_factor
						
				elif rev.fieldname == "uom" and rev.field_label == "Item Field":
			
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["uom","reject_uom","accept_uom","propose_new_uom"])
					if get_checked[0].reject_uom ==1:
						if get_checked[0].propose_new_uom is not None:
							uom = get_checked[0].propose_new_uom
						

				elif rev.fieldname == "discount_percentage" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["discount_percentage","reject_discount_percentage","accept_discount_percentage","propose_new_discount_percentage"])
					if get_checked[0].reject_discount_percentage ==1:
						if get_checked[0].propose_new_discount_percentage is not None:
							discount_percentage = get_checked[0].propose_new_discount_percentage
						

				elif rev.fieldname == "rate" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["rate","reject_rate","accept_rate","propose_new_rate"])
					if get_checked[0].reject_rate ==1:
						if get_checked[0].propose_new_rate is not None:
							rate = get_checked[0].propose_new_rate
						

				elif rev.fieldname == "weight_per_unit" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["weight_per_unit","reject_weight_per_unit","accept_weight_per_unit","propose_new_weight_per_unit"])
					if get_checked[0].reject_weight_per_unit ==1:
						if get_checked[0].propose_new_weight_per_unit is not None:
							weight_per_unit = get_checked[0].propose_new_weight_per_unit
						

				elif rev.fieldname == "weight_uom" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["weight_uom","reject_weight_uom","accept_weight_uom","propose_new_weight_uom"])
					if get_checked[0].reject_weight_uom ==1:
						if get_checked[0].propose_new_weight_uom is not None:
							weight_uom = get_checked[0].propose_new_weight_uom
						

				elif rev.fieldname == "bom" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["bom","reject_bom","accept_bom","propose_new_bom"])
					if get_checked[0].reject_bom ==1:
						if get_checked[0].propose_new_bom is not None:
							bom = get_checked[0].propose_new_bom
						

				elif rev.fieldname == "project" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["project","reject_project","accept_project","propose_new_project"])
					if get_checked[0].reject_project ==1:
						if get_checked[0].propose_new_project is not None:
							project = get_checked[0].propose_new_project
						

				elif rev.fieldname == "warehouse" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["warehouse","reject_warehouse","accept_warehouse","propose_new_warehouse"])
					if get_checked[0].reject_warehouse ==1:
						if get_checked[0].propose_new_warehouse is not None:
							warehouse = get_checked[0].propose_new_warehouse
						

				elif rev.fieldname == "expected_delivery_date" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["expected_delivery_date","reject_expected_delivery_date","accept_expected_delivery_date","propose_new_expected_delivery_date"])
					if get_checked[0].reject_expected_delivery_date ==1:
						if get_checked[0].propose_new_expected_delivery_date is not None:
							expected_delivery_date = get_checked[0].propose_new_expected_delivery_date

				elif rev.fieldname == "schedule_date" and rev.field_label == "Item Field":
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': source_name,"item_code":source.item_code}, fields=["schedule_date","reject_schedule_date","accept_schedule_date","propose_new_schedule_date"])
					if get_checked[0].reject_schedule_date ==1:
						if get_checked[0].propose_new_schedule_date is not None:
							item_schedule_date = get_checked[0].propose_new_schedule_date	

			if schedule_date != "" and schedule_date != None:
				target_doc.schedule_date = schedule_date
			elif item_schedule_date != "" and item_schedule_date != None:
				target_doc.schedule_date = item_schedule_date 
			else:
				target_doc.schedule_date = source.schedule_date
			if qty != 0.0 and qty != None:
				#target_doc.qty = qty
				target_doc.qty = flt(qty)
			else:
				#target_doc.qty = source.qty
				target_doc.qty = flt(source.qty)
			if uom != "" and uom != None:
				target_doc.uom = uom
			else:
				target_doc.uom = source.uom
			if price_list_rate != 0.0 and price_list_rate != None:
				target_doc.price_list_rate = price_list_rate
			else:
				target_doc.price_list_rate = source.price_list_rate
			if conversion_factor != 0.0 and conversion_factor != None:
				target_doc.conversion_factor = conversion_factor
				if qty != 0.0 and qty != None:
					target_doc.stock_qty = flt(qty) * flt(conversion_factor)
				else:
					target_doc.stock_qty = flt(source.qty) * flt(conversion_factor)
			else:
				target_doc.conversion_factor = source.conversion_factor
				if qty != 0.0 and qty != None:
					target_doc.stock_qty = flt(qty) * flt(source.conversion_factor)
				else:
					target_doc.stock_qty = flt(source.qty) * flt(source.conversion_factor)
			if bom != "" and bom != None:
				target_doc.bom = bom
			else:
				target_doc.bom = source.bom
			
			if discount_percentage != 0 and discount_percentage != None:
				target_doc.discount_percentage = discount_percentage
			else:
				target_doc.discount_percentage = source.discount_percentage
			if rate != 0.0 and rate != None:
				target_doc.rate = rate
			else:
				target_doc.rate = source.rate
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
			elif warehouse != None and warehouse != "":
				target_doc.warehouse = warehouse
			else:
				target_doc.warehouse = source.warehouse
			if project != "" and project != None:
				target_doc.project = project
			else:
				target_doc.project = source.project
			if expected_delivery_date != "" and expected_delivery_date != None:
				target_doc.expected_delivery_date = expected_delivery_date
			else:
				target_doc.expected_delivery_date = source.expected_delivery_date

	def update_tax(source, target_doc, source_parent):
		#target_doc.account_head = source.account_head
		#target_doc.rate = source.rate
		target_doc.cost_center = source.cost_center
		#target_doc.charge_type = source.charge_type
		account_head = ""
		row_id = 0
		charge_type = ""
		rate = 0.0
		
		get_checked_account = frappe.get_all('Purchase Taxes and Charges Review', filters={'parent': source_name, "account_head":source.account_head}, fields=["account_head"])
		if source.account_head == get_checked_account[0].account_head:
			for rev in review_details:
				if rev.fieldname == "rate" and rev.field_label == "Tax Field":
			
					get_checked = frappe.get_all('Purchase Taxes and Charges Review', filters={'parent': source_name,"account_head":source.account_head}, fields=["rate","reject_rate","accept_rate","propose_new_rate"])
					if get_checked[0].reject_rate ==1:
						if get_checked[0].propose_new_rate is not None:
							rate = get_checked[0].propose_new_rate
						else:
							rate = get_checked[0].rate
					elif get_checked[0].accept_rate ==1:
						rate = get_checked[0].rate
					else:
						rate = get_checked[0].rate
			if rate != 0.0 and rate != None:
				#print "rate---------------",rate
				target_doc.rate = rate
			else:
				target_doc.rate = source.rate
	def set_missing_values(source, target):
		target.is_pos = 0
		
		if supplier != "" and supplier != None:
			target.supplier = supplier
		else:
			target.supplier = source.supplier
		
		if discount_amount != 0.0 and discount_amount != None:
			target.discount_amount = discount_amount
		else:
			target.discount_amount = source.discount_amount
		if shipping_address != "" and shipping_address != None:
			target.shipping_address = shipping_address
		else:
			target.shipping_address = source.shipping_address
		
		if apply_discount_on != "" and apply_discount_on != None:
			target.apply_discount_on = apply_discount_on
		else:
			target.apply_discount_on = source.apply_discount_on
		if additional_discount_percentage != 0.0 and additional_discount_percentage != None:
			target.additional_discount_percentage = additional_discount_percentage
		else:
			target.additional_discount_percentage = source.additional_discount_percentage
		
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
		if supplier_address != "" and supplier_address != None:
			target.supplier_address = supplier_address
		else:
			target.supplier_address = source.supplier_address
		
		if schedule_date != "" and schedule_date != None:
			target.schedule_date = schedule_date
		else:
			target.schedule_date = source.schedule_date
		
		target.transaction_date = source.transaction_date
		target.ignore_pricing_rule = source.ignore_pricing_rule
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
		
							
	def postprocess(source, target):
		set_missing_values(source, target)
		
	doclist = get_mapped_doc("Purchase Order Review", source_name, {
		"Purchase Order Review": {
			"doctype": "Purchase Order",
			"field_map": {
				"schedule_date":schedule_date,
				"party_account_currency": "party_account_currency",
				"payment_terms_template": "payment_terms_template",
				
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Purchase Order Item Review": {
					"doctype": "Purchase Order Item",
					"field_map":  [
						["name", "purchase_order_item"],
						["parent", "purchase_order"],
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
		"Purchase Taxes and Charges Review": {
			"doctype": "Purchase Taxes and Charges",
			"field_map":  [
				["parent", "purchase_order"]
			],
			"postprocess": update_tax,
		},
		"Payment Schedule Review": {
			"doctype": "Payment Schedule",
			"field_map":  [
				["parent", "purchase_order"]
			],
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)
	doclist.save()
	frappe.msgprint("New Purchase Order has been Created "+doclist.name)			
	return doclist.name
@frappe.whitelist()
def check_before_submit(before_submit,data):
	reviewer = "PO Reviewer"
	creator = "PO Creator"
	overritter = "PO Revisor"
	reviewer_roles = get_roles(frappe.session.user,reviewer)
	creator_roles = get_roles(frappe.session.user,creator)
	overwriter_roles = get_roles(frappe.session.user,overritter)
	sales_order_review = get_sales_order_review(before_submit.name)
	if sales_order_review:
		name = sales_order_review[0].name
		#print "frappe ------------",frappe.session.user
		if sales_order_review[0].docstatus ==1:
			get_varification = sales_order_review_values(sales_order_review[0].name,before_submit.name)
			if len(overwriter_roles) ==0:
				if reviewer_roles:
					if get_varification == True:
						frappe.throw("You cann't submit because something has changed in link doctype Sales Order Review "+frappe.bold(sales_order_review[0].name))
				elif creator_roles:
					if get_varification == True:
						frappe.throw("You cann't submit because something has changed in link doctype Sales Order Review "+frappe.bold(sales_order_review[0].name))
				
				else:
					frappe.throw("Dear user "+ frappe.bold(frappe.session.user) + " you don't have permission to ignore Purchase order review "+ frappe.bold(name))	
		
		else:
			frappe.throw("Please submit first Sales Order Review "+frappe.bold(name))
@frappe.whitelist()
def get_sales_order_review(name):
	sales_order_review = frappe.db.sql("""select * from `tabPurchase Order Review` where purchase_order = %s order by name DESC limit 1 """,name, as_dict =1)
	return sales_order_review
def sales_order_review_values(name,sales_order):
	data = []
	doctype_field = "Purchase Order Review"
	doctype_field_item = "Purchase Order Item Review"
	doctype_field_taxes = "Purchase Taxes and Charges Review"
	doctype = "Purchase Order"
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
					get_checked = frappe.get_all('Purchase Order Review', filters={'name': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Purchase Order', filters={'name': sales_order}, fields=[str(rev.fieldname)])
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
					get_checked = frappe.get_all('Purchase Order Item Review', filters={'parent': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Purchase Order Item', filters={'parent': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:
							
								created_new_doc = True
								break
		elif rev.field_label == "Tax Field":
			for taxes_review in review_doc_taxes_field:
				proposed_new = "propose_new_"+rev.fieldname
				#proposed_new_value = "propose_new_"+r_doc.fieldname
				if proposed_new == item_rev.fieldname:
					reject_field = "reject_"+rev.fieldname
					get_checked = frappe.get_all('Purchase Taxes and Charges Review', filters={'parent': name , reject_field:1}, fields=[str(proposed_new)])
					get_original_order_data = frappe.get_all('Purchase Taxes and Charges', filters={'parent': sales_order}, fields=[str(rev.fieldname)])
					if get_checked:
						if get_checked[0][str(proposed_new)] is not None:
							if get_checked[0][str(proposed_new)] != get_original_order_data[0][str(rev.fieldname)]:
							
								created_new_doc = True
								break
	return created_new_doc

@frappe.whitelist()
def get_check_box_cheched(sales_order,review):
	sales_order_no = sales_order.purchase_order
	sales_order_docstatus = sales_order.docstatus
	if sales_order_docstatus == 0:
		frappe.db.set_value("Purchase Order",sales_order_no,"under_review" , 1);
		#name = frappe.db.sql("""update `tab""" +doctype + """`set under_review = 1 where name = %s""",(name),as_dict=1)
	elif sales_order_docstatus == 1 or sales_order_docstatus == 2: 
		frappe.db.set_value("Purchase Order",sales_order_no,"under_review" , 0);
		#name = frappe.db.sql("""update `tab""" +doctype + """`set under_review = 1 where name = %s""",(name),as_dict=1)
	return True
