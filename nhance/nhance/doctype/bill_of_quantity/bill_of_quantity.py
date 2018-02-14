# -*- coding: utf-8 -*-
# Copyright (c) 2017, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint
from frappe.model.document import Document

class BillofQuantity(Document):
	
	def on_submit(self):
		self.boq_val_1()
#		self.boq_val_2()
		self.boq_val_3()
		self.update_prices()

	def boq_val_1(self):

		company = self.company

		boq_val1 = frappe.db.sql("""select boqi.item_code from `tabBill of Quantity Item` boqi, `tabBill of Quantity` boq where boqi.parent = %s and boqi.parent = boq.name and boqi.immediate_parent_item = boq.item""", self.name, as_dict = 1)
		if boq_val1:
			pass
		else:
			frappe.throw(_("There should at least be 1 line item for the main item - " + self.item))

#	def boq_val_2(self):
#		boq_rm_flag = 0 
#		boq_wo_rm = frappe.db.sql("""select boqi.item_code from `tabBill of Quantity Item` boqi, `tabBill of Quantity` boq, `tabItem` it where boqi.parent = %s and boqi.parent = boq.name and it.item_group != "Raw Material" and boqi.item_code = it.name""", self.name, as_dict = 1)
#		if boq_wo_rm:
#			for boq_items in boq_wo_rm:
#				boq_sel_items = frappe.db.sql("""select boqi.item_code from `tabBill of Quantity Item` boqi, `tabBill of Quantity` boq where boqi.parent = %s and boqi.parent = boq.name and boqi.immediate_parent_item = %s""", (self.name, boq_items.item_code), as_dict = 1)
#				if boq_sel_items:
#					pass
#				else:
#					frappe.throw(_("Item is defined as Sub Assembly but does not have any raw materials defined - " + boq_items.item_code))

		

	def boq_val_3(self):
		boq_dup_rec = frappe.db.sql("""select boqi.item_code as item_code, boqi.immediate_parent_item as ipi, count(*) as qty 
 FROM `tabBill of Quantity Item` boqi where boqi.parent = %s
 GROUP BY boqi.item_code, boqi.immediate_parent_item HAVING count(*)> 1""", self.name, as_dict=1)
		if boq_dup_rec:
			frappe.msgprint(_("Duplicate records present"))
			for record in boq_dup_rec:
				frappe.msgprint(_("Item -" + record.item_code + ", Immediate Parent Item -" + record.ipi))
			frappe.throw(_("Can't submit BoQ. There are duplicate records present. Please remove them first"))


	def update_prices(self):
		update_price_list = frappe.db.sql("""select boqi.item_code as item_code, boqi.manual_price as manual_price, boqi.price as price_name, boq.selling_price_list as selling_price_list from `tabBill of Quantity` boq, `tabBill of Quantity Item` boqi where boqi.parent = %s and manual_price > 0 and update_price = 1 and boq.name = boqi.parent""", self.name, as_dict = 1)
		if update_price_list:
			for record in update_price_list:
				if record.price_name is not None and record.price_name != "":
					price_record = frappe.get_doc("Item Price", record.price_name)
					if price_record:
						rate = record.manual_price

#						price_record.update
						frappe.db.sql("""update `tabItem Price` pr set pr.price_list_rate = %s where pr.name = %s""", (rate, price_record.name))
						frappe.msgprint(_("Price list updated for - " + record.item_code + "= " + str(record.manual_price)))
				else:
					price_json = {
						"price_list": record.selling_price_list,
						"item_code": record.item_code,
						"price_list_rate": record.manual_price
								}
					doc = frappe.new_doc("Item Price")
					doc.update(price_json)
					doc.save()
					frappe.db.commit()
					docname = doc.name
					frappe.msgprint(_("Price Record created for - " + record.item_code + " - " + docname))



	

