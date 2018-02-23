from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint
from frappe.model.mapper import get_mapped_doc

from frappe.model.naming import make_autoname
import sys

from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications


@frappe.whitelist()
def make_proposal_stage(source_name, target_doc=None):


	target_doc = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Proposal Stage",
			"field_map": {
				"doctype": "stage_doctype",
				"name": "document_number"
			 }
		}
	
	}, target_doc, set_missing_values)


	return target_doc

@frappe.whitelist()
def make_proposal_stage_q(source_name, target_doc=None):


	target_doc = get_mapped_doc("Quotation", source_name, {
		"Quotation": {
			"doctype": "Proposal Stage",
			"field_map": {
				"name": "document_number",
				"doctype": "stage_doctype"
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
				"name": "opportunity"

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
				"name": "quotation"
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
				"name": "sales_order"

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
				"name": "sales_invoice",
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

#@frappe.whitelist()
#def set_opp_stages(opportunity):

#	opp_record = frappe.get_doc("Opportunity", opportunity)
#	frappe.msgprint(_(opp_record.name))
#	check_field = 0
        
#	stage_records = frappe.db.sql("""select name as stage_name, opportunity_purpose, buying_status, closing_date, stage, value, competition_status, support_needed from `tabProposal Stage` where document_number=%s""", (opportunity), as_dict = 1)
#	frappe.msgprint(_(stage_records))
#	for row in stage_records:
#		check_field = 0
#		frappe.msgprint(_(row.stage_name))
#		for record in opp_record.opp_stage:
#			frappe.msgprint(_(record))
#			if row.stage_name == record.stage_name:
#				check_field = 1
#		frappe.msgprint(_(row.name))
#		if chec_field == 0:
#			child_row = opp_record.append("opp_stage", {})
#			child_row.stage_name = row.name
#			child_row.opportunity_purpose = row.opportunity_purpose
#			child_row.buying_status = row.buying_status
#			child_row.closing_date = row.closing_date
#			child_row.stage = row.stage
#			child_row.value = row.value
#			child_row.competition_status = row.competition_status
#			child_row.support_needed = row.support_needed
#
#		opp_record.save()
#		frappe.db.commit()	

		
	return

				
			

def set_missing_values(source, target_doc):
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")


@frappe.whitelist()

def make_quotation(source_name, target_doc=None):
	boq_record = frappe.get_doc("Bill of Quantity", source_name)
	set_bom_level(boq_record)
	get_assembly_price(source_name)
	
	company = boq_record.company

	boq_record_items = frappe.db.sql("""select boqi.item_code as boq_item, boqi.immediate_parent_item, boq.customer as customer, boqi.qty as qty, boqi.sub_assembly_price as amount, boqi.markup as markup, boqi.print_in_quotation as piq, boqi.list_in_boq as list_in_boq, boqi.next_exploded as next_exploded from `tabBill of Quantity` boq, `tabBill of Quantity Item` boqi where boqi.parent = %s and boq.name = boqi.parent and boqi.print_in_quotation = '1'""" , (boq_record.name), as_dict=1)

	if boq_record_items:
		newJson = {
				"company": company,
				"doctype": "Quotation",
				"customer": boq_record.customer,
				"boq": source_name,
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
					"grouping": record.immediate_parent_item

					}
		
				newJson["items"].append(innerJson)

		doc = frappe.new_doc("Quotation")
		doc.update(newJson)
		doc.save()
		frappe.db.commit()
		docname = doc.name
		frappe.msgprint(_("Quotation Created - " + docname))
			
	else:	
		boq_main_item = frappe.db.sql("""select boq.item as boq_item, boq.customer as customer from `tabBill of Quantity` boq where boq.name = %s""" , (boq_record.name), as_dict=1)

		if boq_main_item:
			newJson = {
				"company": company,
				"doctype": "Quotation",
				"customer": boq_record.customer,
				"boq": source_name,
				"items": [
				]
			}
	
			tot_ass_price = flt(frappe.db.sql("""select sum(sub_assembly_price)
				from `tabBill of Quantity Item` boqi
				where boqi.parent=%s""",
				(boq_record.name))[0][0])
			if tot_ass_price == 0:
				
				tot_ass_price = flt(frappe.db.sql("""select sum(selling_price * qty)
				from `tabBill of Quantity Item` boqi
				where boqi.parent=%s""",
				(boq_record.name))[0][0])
			for record in boq_main_item:
				item = record.boq_item
				qty = 1
				piq = 1
				lib = 1

				if item:
					item_record = frappe.get_doc("Item", item)

					innerJson =	{
						"doctype": "Quotation Item",
						"item_code": item,
						"description": item_record.description,
						"uom": item_record.stock_uom,
						"qty": qty,
						"rate": tot_ass_price,
						"display_in_quotation": piq,
						"list_in_boq": lib,
#						"next_exploded": next_exploded,
#						"grouping": record.immediate_parent_item
	
						}
		
					newJson["items"].append(innerJson)

			doc = frappe.new_doc("Quotation")
			doc.update(newJson)
			doc.save()
			frappe.db.commit()
			docname = doc.name
			frappe.msgprint(_("Quotation Created - " + docname))

					
	

@frappe.whitelist()
def make_bom(source_name, target_doc=None):
	boq_record = frappe.get_doc("Bill of Quantity", source_name)
	company = boq_record.company
	max_bom_level = frappe.db.sql("""select max(bom_level) from `tabBill of Quantity Item` boqi where boqi.parent = %s""", (boq_record.name))
	x = 1
#	if max_bom_level > 0:
	if max_bom_level[0][0] is None or max_bom_level[0][0] is "":
		frappe.msgprint(_("Please create Quotation first"))	
		return	
	else:

		bom_level = int(max_bom_level[0][0])
		
#	else:
#		bom_level = 0

	if bom_level == 0:
		boq_record_items = frappe.db.sql("""select distinct boqi.immediate_parent_item as bom_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = 0 order by boqi.immediate_parent_item""" , (boq_record.name), as_dict=1)

		if boq_record_items:
						
			for boq_record_item in boq_record_items:
				bom_main_item = boq_record_item.bom_item
				bom_qty = 1

				boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.part_of_despatch_list as pod from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s and boqi.bom_level = 0 order by boqi.item_code""" , (boq_record.name, bom_main_item), as_dict=1)
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
								"stock_uom": item_record.stock_uom,
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

	else:
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
									"stock_uom": item_record.stock_uom,
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

			if bom_record_level1:
				for record in bom_record_level1:
					frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "1" where boqi.parent = %s and boqi.immediate_parent_item = %s""", (boq_record.name, boq_record.item))
			else:

				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.bom_level = "0" where boqi.parent = %s and boqi.item_code = %s""", (boq_record.name, row.item_code))


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
	item_price_list = frappe.db.sql("""select name as price, price_list_rate as item_price from `tabItem Price` where price_list = %s and item_code = %s""", (price_list, item), as_dict = 1)
	if item_price_list:
#		return item_price_list[0]["item_price"]
		return item_price_list[0]["price"], item_price_list[0]["item_price"]
		
	else:	
		return 0



@frappe.whitelist()
def get_contact(customer):
	contact = frappe.db.sql("""select con.name from `tabContact` con, `tabDynamic Link` dy where dy.link_name = %s and dy.parent = con.name""", (customer))
	
	return contact


@frappe.whitelist()
def get_address(customer):
	address = frappe.db.sql("""select ad.name from `tabAddress` ad, `tabDynamic Link` dy where dy.link_name = %s and dy.parent = ad.name""", (customer))

	return address
	

@frappe.whitelist()
def get_assembly_price(frm):
	boq_record = frappe.get_doc("Bill of Quantity", frm)
	company = boq_record.company
	max_bom_level = frappe.db.sql("""select max(bom_level) from `tabBill of Quantity Item` where parent = %s""", frm)

	x = 1
	sub_ass_price = 0
	markup_per = 1
	bom_level = int(max_bom_level[0][0])
	for x in xrange(bom_level, 0, -1):

		boq_record_items = frappe.db.sql("""select distinct boqi.immediate_parent_item as bom_item from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.bom_level = %s order by boqi.immediate_parent_item""" , (boq_record.name, x), as_dict=1)

		if boq_record_items:
			
			for boq_record_item in boq_record_items:
				bom_main_item = boq_record_item.bom_item
				markup_rec = frappe.db.sql("""select boqi.markup as markup, boqi.discount as discount, boqi.qty as qty from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.item_code = %s""" , (boq_record.name, bom_main_item))
#				markup = markup_rec.markup
				if markup_rec:
					markup = markup_rec[0][0]
					discount = markup_rec[0][1]
					bom_main_qty = markup_rec[0][2]
				else:
					markup = 0
					bom_main_qty = 1
				bom_qty = 1
				sub_ass_price = 0

				boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.selling_price as selling_price, boqi.sub_assembly_price as sap from `tabBill of Quantity Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s and boqi.bom_level = %s order by boqi.item_code""" , (boq_record.name, bom_main_item, x), as_dict=1)
				if boq_record_bom_items:
										
					for record in boq_record_bom_items:
						item = record.qi_item
						qty = record.qty
						selling_price = record.selling_price
						sap = flt(record.sap)
						if sap != 0.0:

							sub_ass_price = sub_ass_price + flt(sap * qty)

						else:

							sub_ass_price = sub_ass_price + (selling_price * qty)

				markup_per = flt(markup/100) + 1
				disc_per = 1 - flt(discount/100)
				sub_ass_price = (sub_ass_price * markup_per * disc_per)

				frappe.db.sql("""update `tabBill of Quantity Item` boqi set boqi.sub_assembly_price = %s where boqi.parent = %s and boqi.item_code = %s""", (sub_ass_price, boq_record.name, bom_main_item))
						


@frappe.whitelist()
def make_opp_quotation(source_name, target_doc=None):
	frappe.throw(_("Inside Api - Opportunity to Quotation"))
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
		quotation = frappe.get_doc(target)

		company_currency = frappe.db.get_value("Company", quotation.company, "default_currency")
		party_account_currency = get_party_account_currency("Customer", quotation.customer,
			quotation.company) if quotation.customer else company_currency

		quotation.currency = party_account_currency or company_currency

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(quotation.currency, company_currency,
				quotation.transaction_date)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=quotation.company)
		if taxes.get('taxes'):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		if not source.with_items:
			quotation.opportunity = source.name

	doclist = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Quotation",
			"field_map": {
				"enquiry_from": "quotation_to",
				"opportunity_type": "order_type",
				"name": "enq_no",
			}
		},
		"Opportunity Item": {
			"doctype": "Quotation Item",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",
				"uom": "stock_uom"
			},
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def get_item_price_details(item_code):
	
	item_details = []
	supplier_details = []
	last_3Days_Details = frappe.db.sql("""select rate,parent from `tabPurchase Order Item` as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 3 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by creation desc limit 3""", (item_code), as_dict=1)
	#print "############-length of last_3Days_Details[0]['parent']::", (last_3Days_Details)
	i=0
	for po_Number in last_3Days_Details:
		last_3Days_po_Number = last_3Days_Details[i]['parent']
		last_3Days_supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s and DATE(creation) > (NOW() - INTERVAL 3 DAY) order by creation desc limit 3""", last_3Days_po_Number, as_dict=1)
		supplier_details.extend(last_3Days_supplier)
		i = i + 1
	#print "###-supplier_details::", supplier_details
	max_last_180Days_Details = frappe.db.sql("""select parent,rate as max_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate desc limit 1) t1""", (item_code), as_dict=1)
	#print "#######-max_last_180Days_Details::", max_last_180Days_Details
	if len(max_last_180Days_Details)!=0:
		max_last_180Days_po_Number = max_last_180Days_Details[0]['parent']
		max_last_180Days_supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s""", max_last_180Days_po_Number, as_dict=1)
		max_last_180Days_Details.extend(max_last_180Days_supplier)

	min_last_180Days_Details = frappe.db.sql("""select parent,rate as min_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate asc limit 1) t1""", (item_code), as_dict=1)
	if len(min_last_180Days_Details)!=0:
		#print "#######-min_last_180Days_Details::", min_last_180Days_Details
		min_last_180Days_po_Number = min_last_180Days_Details[0]['parent']
		min_last_180Days_supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s""", min_last_180Days_po_Number, as_dict=1)
		min_last_180Days_Details.extend(min_last_180Days_supplier)

	last_180Days_Avg_Price = frappe.db.sql("""select avg(rate) as avg_price from `tabPurchase Order Item` as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled'))""", (item_code), as_dict=1)

	#last_3Days_Details.extend(last_3Days_supplier)
	item_details.append(last_3Days_Details)
	item_details.append(max_last_180Days_Details)
	item_details.append(min_last_180Days_Details)
	item_details.append(last_180Days_Avg_Price)
	item_details.append(supplier_details)
	print "###############-item_details::", item_details
	return item_details
