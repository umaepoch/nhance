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
		self.boq_val_2()
		self.boq_val_3()
		self.boq_val_4()
		self.update_prices()
	
	def before_save(self):

		self.validate_uom_is_interger()

	def validate(self):
		self.validate_main_item()

	def validate_main_item(self):
		item = self.get_item_det(self.item)
		uom_err = 0

		if not item:
			frappe.throw(_("Item {0} does not exist in the system or has expired").format(self.item))
		else:
			ret = frappe.db.get_value("Item", self.item, ["description", "stock_uom", "item_name"])
			self.description = ret[0]
			self.uom = ret[1]
			self.item_name= ret[2]

		for m in self.get('items'):
			if flt(m.uom_qty) <= 0:
				frappe.throw(_("Quantity required for Item {0} in row {1}").format(m.item_code, m.idx))

			item_uom = frappe.db.get_value("Item", m.item_code, ["stock_uom"])
			m.stock_uom = item_uom

			if m.unit_of_measure:

				conv_factor = self.get_uom_det(m.item_code, m.unit_of_measure)
				if (conv_factor == 1 and m.stock_uom != m.unit_of_measure):
					frappe.msgprint(_("Conversion factor not set for UOM - {0} to Stock UOM - {1} for Item {2} in Row {3}").format(m.unit_of_measure, m.stock_uom, m.item_code, m.idx))
					uom_err = 1
				else:
					m.qty = float(m.uom_qty * conv_factor)
					m.conversion_factor = conv_factor
			else:
				m.unit_of_measure = m.stock_uom
				m.qty = m.uom_qty
				m.conversion_factor = 1

		if uom_err:
			frappe.throw(_("Please correct StockUoM errors before updating BOQ"))




	def boq_val_1(self):

		company = self.company

		boq_val1 = frappe.db.sql("""select boqi.item_code from `tabBill of Quantity Item` boqi, `tabBill of Quantity` boq where boqi.parent = %s and boqi.parent = boq.name and boqi.immediate_parent_item = boq.item""", self.name, as_dict = 1)
		if boq_val1:
			pass
		else:
			frappe.throw(_("There should at least be 1 line item for the main item - " + self.item))

	def boq_val_2(self):
		
		boq_sub = frappe.db.sql("""select boqvi.item_group as item_group from `tabBOQ Validation Item` boqvi, `tabBOQ Validation` boqv where boqvi.parent = boqv.name and boqv.type_of_validation = "Sub Assemblies" and boqv.validation_on = "ItemGroup" and boqv.docstatus != "2" order by boqvi.item_group""", as_dict = 1)
		if boq_sub:
			for boq_sub_items in boq_sub:
				boq_wo_rm = frappe.db.sql("""select boqi.item_code from `tabBill of Quantity Item` boqi, `tabBill of Quantity` boq, `tabItem` it where boqi.parent = %s and boqi.parent = boq.name and it.item_group = %s and boqi.item_code = it.name""", (self.name, boq_sub_items.item_group), as_dict = 1)

				if boq_wo_rm:
					for boq_items in boq_wo_rm:
						boq_sel_items = frappe.db.sql("""select boqi.item_code from `tabBill of Quantity Item` boqi, `tabBill of Quantity` boq where boqi.parent = %s and boqi.parent = boq.name and boqi.immediate_parent_item = %s""", (self.name, boq_items.item_code), as_dict = 1)
						if boq_sel_items:
							pass
						else:
							frappe.msgprint(_("Item is defined as Sub Assembly but does not have any raw materials defined.")) 
							frappe.throw(_("Item - " + boq_items.item_code + ", Item Group - " + boq_sub_items.item_group))

		

	def boq_val_3(self):
		boq_dup_rec = frappe.db.sql("""select boqi.item_code as item_code, boqi.immediate_parent_item as ipi, count(*) as qty 
 FROM `tabBill of Quantity Item` boqi where boqi.parent = %s
 GROUP BY boqi.item_code, boqi.immediate_parent_item HAVING count(*)> 1""", self.name, as_dict=1)
		if boq_dup_rec:
			frappe.msgprint(_("Duplicate records present"))
			for record in boq_dup_rec:
				frappe.msgprint(_("Item -" + record.item_code + ", Immediate Parent Item -" + record.ipi))
			frappe.throw(_("Can't submit BoQ. There are duplicate records present. Please remove them first"))
	
	def boq_val_4(self):
		boq_zero_rec = frappe.db.sql("""select boqi.item_code as item_code, boqi.qty as qty from `tabBill of Quantity Item` boqi where boqi.parent = %s and (boqi.qty <=0 or boqi.qty is NULL)""", self.name, as_dict = 1)
		if boq_zero_rec:
			for record in boq_zero_rec:
				frappe.msgprint(_(record.item_code + ",   Qty:  " + str(record.qty)))
			frappe.throw(_("Can't Submit. These Items have qty less than or equal to 0. Please modify them and then save."))


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

	
	def validate_uom_is_interger(self):
		from erpnext.utilities.transaction_base import validate_uom_is_integer
		validate_uom_is_integer(self, "stock_uom", "qty", "Bill of Quantity Item")

	def get_item_det(self, item_code):
		item = frappe.db.sql("""select name, item_name, docstatus, description, image,
			is_sub_contracted_item, stock_uom, default_bom, last_purchase_rate
			from `tabItem` where name=%s""", item_code, as_dict = 1)

		if not item:
			frappe.throw(_("Item: {0} does not exist in the system").format(item_code))

		return item

	def get_uom_det(self, item_code, uom):
		convert_factor = frappe.db.sql("""select conversion_factor as conversion_factor from `tabUOM Conversion Detail` t2 where t2.parent = %s and uom = %s""", (item_code, uom))
		if convert_factor:
			conv_factor = convert_factor[0][0]
		else:
			conv_factor = 1
		return conv_factor



