# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from datetime import datetime
import datetime
from datetime import date, timedelta
class PrePurchaseOrders(Document):
	pass
@frappe.whitelist()
def get_doc_details(doctype):
	doc_details = frappe.get_meta(doctype).get("fields")
	return doc_details

@frappe.whitelist()
def make_approved_pre_purchase_order(source_name):
	date = datetime.datetime.now()
	date = date.strftime('%Y-%m-%d')
	pre_purchase_details = frappe.get_list("Pre Purchase Item", filters = {"parent":source_name} , fields=["*"])
	if pre_purchase_details:
		outerJson_Transfer = {
			"doctype": "Approved Pre Purchase Order",
			"docstatus": 0,
			"date":date,
			"pre_purchase_orders": source_name,
			"items": []
			}
		for items in pre_purchase_details:
			innerJson_Transfer ={
				"item_code":items['item'],
				"puom":items['puom'],
				"total_stock_qty":items['total_stock_qty'],
				"default_supplier":items['default_supplier'],
				"stock_uom":items['stock_uom'],
				"recommended_supplier":items['recommended_supplier'],
				"doctype": "Approved Pre Purchase Order",
				"recommended_qty":items['recommended_qty'],
				"recommended_rate":items['recommended_rate'],
				"conversion_factor":items['conversion_factor'],
				"qty_in_puom":items['qty_in_puom'],
				"last_n_highest":items['last_n_highest'],
				"last_n_lowest": "last_n_lowest",
				"last_n_average":items['last_n_average'],
				"number_of_transactions":items['number_of_transactions']
				}
			outerJson_Transfer["items"].append(innerJson_Transfer)
		doc = frappe.new_doc("Approved Pre Purchase Order")
		doc.update(outerJson_Transfer)
		doc.save()
		ret = doc.doctype
		if ret:
			return ret
@frappe.whitelist()
def get_verification(source_name):
	verification = frappe.get_list("Approved Pre Purchase Order", filters={"pre_purchase_orders":source_name},fields=['name'])
	if verification:
		return verification
	else:
		return None
		
