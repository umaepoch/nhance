from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint
from frappe.model.mapper import get_mapped_doc

from frappe.model.naming import make_autoname

from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications


@frappe.whitelist()
def make_proposal_stage(source_name, target_doc=None):

	target_doc = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Proposal Stage",
			"field_map": {
				"name": "reference_name"
			 }
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions(source_name, target_doc=None):

	target_doc = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Interactions",
			"field_map": {
				"name": "opportunity",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions_quot(source_name, target_doc=None):
	src_name = "Quotation"
	target_doc = get_mapped_doc("Quotation", source_name, {
		"Quotation": {
			"doctype": "Interactions",
			"field_map": {
				"name": "quotation",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions_so(source_name, target_doc=None):
	src_name = "Sales Order"
	target_doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Interactions",
			"field_map": {
				"name": "sales_order",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions_si(source_name, target_doc=None):
	src_name = "Sales Invoice"
	target_doc = get_mapped_doc("Sales Invoice", source_name, {
		"Sales Invoice": {
			"doctype": "Interactions",
			"field_map": {
				"name": "reference_document",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc


@frappe.whitelist()
def set_proposal_stage_values(opportunity):

        
	max_closing_date = frappe.db.sql("""select max(closing_date) from `tabProposal Stage` where reference_name=%s""",
				(opportunity))
				
        sc_rec = frappe.db.sql("""select value, closing_date, stage, opportunity_purpose, buying_status, support_needed, competition_status
		from `tabProposal Stage`
		where reference_name=%s and closing_date = %s""",
		(opportunity, max_closing_date))
        return sc_rec

def set_missing_values(source, target_doc):
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")


@frappe.whitelist()

def make_quotation(source_name, target_doc=None):

	boq_record = frappe.get_doc("Bill of Quantity", source_name)
	
	company = boq_record.company

	boq_record_items = frappe.db.sql("""select boqi.item_code as boq_item, boq.customer as customer, boqi.qty as qty, boqi.price as price, boqi.selling_price as amount, boqi.markup as markup, boqi.print_in_quotation as piq, boqi.list_in_boq as list_in_boq, boqi.next_exploded as next_exploded from `tabBill of Quantity` boq, `tabBill of Quantity Item` boqi where boqi.parent = %s and boq.name = boqi.parent and boqi.print_in_quotation = 1 """ , (boq_record.name), as_dict=1)

	if boq_record_items:
		newJson = {
				"company": company,
				"doctype": "Quotation",
				"customer": boq_record.customer,
				"items": [
				]
				}
	
		for record in boq_record_items:
			item = record.boq_item
			qty = record.qty
			piq = record.piq
			lib = record.list_in_boq
			next_exploded = record.next_exploded
			markup = record.markup
			if item:
				item_record = frappe.get_doc("Item", item)

				innerJson =	{
					"doctype": "Quotation Item",
					"item_code": item,
					"description": item_record.description,
					"uom": item_record.stock_uom,
					"qty": qty,
					"rate": record.amount,
					"display_in_quotation": piq,
					"list_in_boq": lib,
					"next_exploded": next_exploded,
					"markup": markup

					}
		
				newJson["items"].append(innerJson)

		doc = frappe.new_doc("Quotation")
		doc.update(newJson)
		doc.save()
		frappe.db.commit()
		docname = doc.name
		frappe.msgprint(_("Quotation Created - " + docname))
			
	else:				
		frappe.throw(_("There are no Quotations to be created."))
		

@frappe.whitelist()
def make_bom(source_name, target_doc=None):

	boq_record = frappe.get_doc("Bill of Quantity", source_name)
	set_bom_level(boq_record)
	company = boq_record.company
	max_bom_level = frappe.db.sql("""select max(bom_level) from `tabBill of Quantity Item`""")
	x = 1
	bom_level = int(max_bom_level[0][0])
	for x in xrange(bom_level, 0, -1):
		boq_record_items = frappe.db.sql("""select distinct boqi.immediate_parent_item as bom_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = %s order by boqi.immediate_parent_item""" , (boq_record.name, x), as_dict=1)

		if boq_record_items:
						
			for boq_record_item in boq_record_items:
				bom_main_item = boq_record_item.bom_item
				bom_qty = 1

				boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.part_of_despatch_list as pod from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s and boqi.bom_level = %s order by boqi.item_code""" , (boq_record.name, bom_main_item, x), as_dict=1)
			
				if boq_record_bom_items:
					
					newJson = {
					"company": company,
					"doctype": "BOM",
					"item": bom_main_item,
					"quantity": bom_qty,
					"items": [
					]
					}
					
					for record in boq_record_bom_items:
						item = record.qi_item
						qty = record.qty
						pod_list = record.pod

						if item:
							item_record = frappe.get_doc("Item", item)
		
							innerJson =	{
								"doctype": "BOM Item",
								"item_code": item,
								"description": item_record.description,
								"uom": item_record.stock_uom,
								"qty": qty,
								"part_of_despatch_list": pod_list
								
				
								}
		
							newJson["items"].append(innerJson)

					doc = frappe.new_doc("BOM")
					doc.update(newJson)
					doc.save()
					frappe.db.commit()
					doc.submit()
					docname = doc.name
					frappe.msgprint(_("BOM Created - " + docname))

				else:
					frappe.msgprint(_("There are no BOM Items present in the quotation. Could not create a BOM for this Item."))



def set_bom_level(boq_record):

	boq_record_items = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, boq_record.item), as_dict=1)
	if boq_record_items:
		for row in boq_record_items:
			bom_record_level1 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level1:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "1" where boqi.parent = %s and boqi.immediate_parent_item = %s""", (boq_record.name, boq_record.item))


	boq_record_items2 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 1""" , (boq_record.name), as_dict=1)
	if boq_record_items2:
		for row in boq_record_items2:
			bom_record_level2 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level2:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "2" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))

	boq_record_items3 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 2""" , (boq_record.name), as_dict=1)
	if boq_record_items3:
		for row in boq_record_items3:
			bom_record_level3 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level3:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "3" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))

	boq_record_items4 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 3""" , (boq_record.name), as_dict=1)
	if boq_record_items4:
		for row in boq_record_items4:
			bom_record_level4 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level4:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "4" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))

	boq_record_items5 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 4""" , (boq_record.name), as_dict=1)
	if boq_record_items5:
		for row in boq_record_items5:
			bom_record_level5 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level5:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "5" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))

	boq_record_items6 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 5""" , (boq_record.name), as_dict=1)
	if boq_record_items6:
		for row in boq_record_items6:
			bom_record_level6 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level6:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "6" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))
							

	boq_record_items7 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 6""" , (boq_record.name), as_dict=1)
	if boq_record_items7:
		for row in boq_record_items7:
			bom_record_level7 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level7:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "7" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))

	boq_record_items8 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 7""" , (boq_record.name), as_dict=1)
	if boq_record_items8:
		for row in boq_record_items8:
			bom_record_level8 = frappe.db.sql("""select boqi.item_code, boqi.immediate_parent_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s""" , (boq_record.name, row.item_code), as_dict=1)
			for record in bom_record_level8:
				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "8" where boqi.parent = %s and boqi.item_code = %s and boqi.immediate_parent_item = %s""", (boq_record.name, record.item_code, record.immediate_parent_item))

@frappe.whitelist()
def make_cust_project(source_name, target_doc=None):
	global alloc_whse
	def postprocess(source, doc):
		doc.project_type = "External"
		sales_record = frappe.get_doc("Sales Order", source_name)
		customer = sales_record.customer
		doc.project_name = customer + "-" + source_name[-5:]
 		doc.production_bench = get_free_workbenches()

		if doc.production_bench:
			pass
		else:
			frappe.msgprint(_("There is no free production bench available. Please allocate manually"))

	doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Project",
			"validation": {
				"docstatus": ["=", 1]
			},
			"field_map":{
				"name" : "sales_order",
				"base_grand_total" : "estimated_costing",
			}
		},
		"Sales Order Item": {
			"doctype": "Project Task",
			"field_map": {
				"description": "title",
			},
		}
	}, target_doc, postprocess)

	return doc

@frappe.whitelist()
def get_free_workbenches():

	workbench_warehouses = frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse = "Production Benches - PISPL" order by name""", as_dict=1)

	for whse_record in workbench_warehouses:
		alloc_whse = frappe.db.sql("""select is_active from `tabProject` where production_bench = %s and is_active = "Yes" order by name""", (whse_record["name"]), as_dict=1)
		if alloc_whse:
			pass
		else:
			return whse_record["name"]


@frappe.whitelist()
def get_price(item, price_list):
	item_price_list = frappe.db.sql("""select price_list_rate as item_price from `tabItem Price` where price_list = %s and item_code = %s""", (price_list, item), as_dict = 1)
	return item_price_list[0]["item_price"]

	
