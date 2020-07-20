from __future__ import unicode_literals
import frappe
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications
from datetime import datetime
import sys
import os
import operator
import frappe
import json
import time
import math
import base64
import ast
parent_list = []
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
def make_interactions_cust(source_name, target_doc=None):
	src_name = "Customer"
	target_doc = get_mapped_doc("Customer", source_name, {
		"Customer": {
			"doctype": "Interactions",
			"field_map": {
				"name": "customer"

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
	x = 0
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
		for x in xrange(bom_level + 1):
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
	#print "###############-item_details::", item_details
	return item_details


@frappe.whitelist()
def calculate_overtime_and_food(employee, start_date, end_date):
#	overtime_fa_amount = frappe.db.sql("""select sum(ofe.overtime_amount) as overtime, sum(food_allowance_amount) as food_allowance, sum(attendance_bonus) as attendance_bonus
#			from `tabOvertime and Other Allowances` ofa, `tabOvertime and Other Allowances Employees` ofe where ofe.employee = %s and ofa.from_date >= %s and ofa.to_date <= %s and ofe.parent = ofa.name and ofa.docstatus = 1""",
#			(employee, start_date, end_date), as_dict=1)

	overtime_fa_amount = frappe.db.sql("""select sum(ofe.overtime_hours) as overtime_hours, sum(ofe.overtime_amount) as overtime, sum(food_allowance_amount) as food_allowance, sum(attendance_bonus) as attendance_bonus
			from `tabOvertime and Other Allowances` ofa, `tabOvertime and Other Allowances Employees` ofe where ofe.employee = %s and ofa.from_date >= %s and ofa.to_date <= %s and ofe.parent = ofa.name and ofa.docstatus = 1""",
			(employee, start_date, end_date), as_dict=1)

	return overtime_fa_amount


@frappe.whitelist()
def get_uom_list(item_code):
	records = frappe.db.sql("""select t2.uom as uom from `tabUOM Conversion Detail` t2 where t2.parent = %s""", (item_code))

	if records:
#		frappe.msgprint(_(records[0].warehouse))
#		return records[0].warehouse
		return records
	else:
		return

@frappe.whitelist()
def get_stock_uom(item_code):
	records = frappe.db.sql("""select stock_uom as uom from `tabItem` where item_code = %s""", (item_code))

	if records:
#		frappe.msgprint(_(records[0].warehouse))
#		return records[0].warehouse
		return records
	else:
		return

@frappe.whitelist()
def get_user_role():
	userrole = frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	if userrole:
		return userrole
	else:
		return 1

@frappe.whitelist()
def get_user_role_status(approval_a, dt):
	frappe.msgprint(_("Inside api"))
	frappe.msgprint(_(approval_a))
	role_status = ""
	userrole = frappe.db.get_value("User",{"name":frappe.session.user},"role_profile_name")
	frappe.msgprint(_(userrole))
	if userrole:
		if approval_a == "Rejected":
			role_status = "Rejected"
			return role_status
		else:
			workflow_records = frappe.db.sql("""select at.approval_level, at.approval_role, at.approval_status from `tabApproval Master` am, `tabApproval Transition` at where at.parent = am.name and am.document_type = %s""", (dt), as_dict = 1)
			if workflow_records:
				for wfw in workflow_records:
					if userrole == wfw.approval_role:
						if wfw.approval_status:
							role_status = wfw.approval_status
						else:
							role_status = "Approved by " + userrole

				if role_status:
					frappe.msgprint(_(role_status))
					return role_status
				else:
					return 0
			else:
				frappe.msgprint(_("There are no Approval workflow records set for doctype: " + dt))
				return 0
	else:
		return 0

@frappe.whitelist()
def delete_rarb(warehouse):
	upd_old_rarb_det = frappe.db.sql("""select name from `tabRARB Detail` where warehouse = %s and active = 1""", warehouse, as_dict=1)
	whs_rec = frappe.db.sql("""select version from `tabWarehouse` where name = %s""", warehouse)
	frappe.msgprint(_(whs_rec[0]))
	ver = whs_rec[0][0] + 1
	ver = str(ver).zfill(3)
	curr_date = utils.today()
	if upd_old_rarb_det:
		for rec in upd_old_rarb_det:
			rarb_rec = frappe.get_doc("RARB Detail", rec.name)
			sys_id = rec.name + "-" + ver
			newJson = {
				"system_id": sys_id,
				"doctype": "RARB Detail",
				"next_level_rarb": rarb_rec.next_level_rarb,
				"next_level_rarb_number": rarb_rec.next_level_rarb_number,
				"warehouse": rarb_rec.warehouse,
				"item": rarb_rec.item,
				"attribute_1": rarb_rec.attribute_1,
				"attribute_2": rarb_rec.attribute_2,
				"attribute_3": rarb_rec.attribute_3,
				"length": rarb_rec.length,
				"width": rarb_rec.width,
				"height": rarb_rec.height,
				"max_permissible_weight": rarb_rec.max_permissible_weight,
				"reqd_to_select_bin": rarb_rec.reqd_to_select_bin,
				"active": 0
				}
			doc = frappe.new_doc("RARB Detail")
			doc.update(newJson)
			doc.save()
			frappe.db.commit()

	frappe.db.sql("""update `tabWarehouse` set version = %s where name = %s""", (ver, warehouse))
	frappe.db.sql("""delete from `tabRARB Locations` where parent in (select name from `tabRARB` where warehouse = %s and active = 1)""", warehouse, as_dict=1)
	frappe.db.sql("""delete from `tabRARB Detail` where warehouse = %s and active = 1""", warehouse, as_dict=1)
	frappe.db.sql("""delete from `tabRARB` where warehouse = %s and active = 1""", warehouse, as_dict=1)



@frappe.whitelist()
def validate_rarb(warehouse):
	frappe.msgprint(_("Inside Validate RARB"))
	exists = ""
	rarb_rec = frappe.db.sql("""Select name from `tabRARB` where name = %s""", warehouse, as_dict=1)
	if rarb_rec:
		exists = 1
	else:
		exists = 0
	return exists

@frappe.whitelist()
def generate_rarb(warehouse, rooms, aisle, rack, bin_no):
	room = int(rooms) + 1
	ais = int(aisle) + 1
	rac = int(rack) + 1
	bin_n = int(bin_no) + 1
	newJson = {
		"system_id": warehouse,
		"rarb_id": warehouse,
		"doctype": "RARB Detail",
		"next_level_rarb": "Room",
		"next_level_rarb_number": room,
		"warehouse": warehouse,
		"active": 1
		}
	doc = frappe.new_doc("RARB Detail")
	doc.update(newJson)
	doc.save()
	frappe.db.commit()
	newJson_wh = {
			"higher_rarb": warehouse,
			"warehouse": warehouse,
			"active": 1,
				"rarb_locations": [
				]
			}

	for w in xrange(1, room):
		room_id = warehouse + "-Room-" + str(w)
		rarb_room = "Room-" + str(w)
		newJson = {
			"system_id": room_id,
			"rarb_id": rarb_room,
			"doctype": "RARB Detail",
			"next_level_rarb": "Aisle",
			"next_level_rarb_number": aisle,
			"warehouse": warehouse,
			"active": 1
			}
		innerJson_wh =	{
				"rarb_location": room_id

				}

		newJson_wh["rarb_locations"].append(innerJson_wh)
		doc = frappe.new_doc("RARB Detail")
		doc.update(newJson)
		doc.save()
		frappe.db.commit()
		newJson_rm = {
			"higher_rarb": room_id,
			"warehouse": warehouse,
			"active": 1,
				"rarb_locations": [
				]
			}

		for x in xrange(1, ais):
			aisle_id = warehouse + "-Aisle-" + str(w) + "-" + str(x)
			rarb_aisle = "Aisle-" + str(w) + "-" + str(x)
			newJson = {
				"system_id": aisle_id,
				"rarb_id": rarb_aisle,
				"doctype": "RARB Detail",
				"next_level_rarb": "Rack",
				"next_level_rarb_number": rack,
				"warehouse": warehouse,
				"active": 1

				}
			innerJson_rm =	{
				"rarb_location": aisle_id

				}
			newJson_rm["rarb_locations"].append(innerJson_rm)

			doc = frappe.new_doc("RARB Detail")
			doc.update(newJson)
			doc.save()
			frappe.db.commit()
			newJson_ai = {
			"higher_rarb": aisle_id,
			"warehouse": warehouse,
			"active": 1,
				"rarb_locations": [
				]
			}

			for y in xrange(1, rac):
				rac_id = warehouse + "-Rack-" + str(w) + "-" + str(x)+ "-" + str(y)
				rarb_rack = "Rack-" + str(w) + "-" + str(x)+ "-" + str(y)
				newJson = {
					"system_id": rac_id,
					"rarb_id": rarb_rack,
					"doctype": "RARB Detail",
					"next_level_rarb": "Bin",
					"next_level_rarb_number": bin_no,
					"warehouse": warehouse,
					"active": 1

				}
				innerJson_ai =	{
					"rarb_location": rac_id

					}
				newJson_ai["rarb_locations"].append(innerJson_ai)

				doc = frappe.new_doc("RARB Detail")
				doc.update(newJson)
				doc.save()
				frappe.db.commit()
				newJson_rac = {
					"higher_rarb": rac_id,
					"warehouse": warehouse,
					"active": 1,
					"rarb_locations": [
						]
					}
				for z in xrange(1, bin_n):
					bin_id = warehouse + "-Bin-" + str(w) + "-" + str(x)+ "-" + str(y)+ "-" + str(z)
					rarb_bin = "Bin-" + str(w) + "-" + str(x)+ "-" + str(y)+ "-" + str(z)
					newJson = {
						"system_id": bin_id,
						"rarb_id": rarb_bin,
						"doctype": "RARB Detail",
						"warehouse": warehouse,
						"active": 1
						}
					innerJson_rac =	{
						"rarb_location": bin_id

						}
					newJson_rac["rarb_locations"].append(innerJson_rac)

					doc = frappe.new_doc("RARB Detail")
					doc.update(newJson)
					doc.save()
					frappe.db.commit()

				doc_rac = frappe.new_doc("RARB")
				doc_rac.update(newJson_rac)
				doc_rac.save()
				frappe.db.commit()

			doc_ai = frappe.new_doc("RARB")
			doc_ai.update(newJson_ai)
			doc_ai.save()
			frappe.db.commit()

		doc_rm = frappe.new_doc("RARB")
		doc_rm.update(newJson_rm)
		doc_rm.save()
		frappe.db.commit()

	doc_wh = frappe.new_doc("RARB")
	doc_wh.update(newJson_wh)
	doc_wh.save()
	frappe.db.commit()
	frappe.throw(_("RARBs created"))
	return

@frappe.whitelist()
def make_po_in_draft(purchase_items,purchase_taxes,purchase_order_details,payment_schedule):
	name = ""
	title = ""
	owner = ""
	taxes_and_charges = ""
	company = ""
	supplier = ""
	stopped_po=""
	schedule_date = ""
	stock_req = ""
	stock_req_id = ""
	busyvoucherno = ""
	item_lines_to_print = 0
	apply_discount_on = ""
	project = ""
	additional_discount_percentage = 0
	remark = ""
	material_req = ""
	payment_terms = ""
	due_date = ""
	payment_term = ""
	return_doc = ""
	inner_json_for_items = ""
	inner_json_for_taxes = ""
	required_date = datetime.now()
	purchase_order_details = ast.literal_eval(purchase_order_details)
	purchase_taxes = ast.literal_eval(purchase_taxes)
	purchase_items = ast.literal_eval(purchase_items)
	payment_schedule = ast.literal_eval(payment_schedule)
	for data in purchase_order_details:
		title = data["title"]
		owner = data["owner"]
		taxes_and_charges = data["taxes_and_charges"]
		company = data["company"]
		supplier = data["supplier"]
		stopped_po = data["name"]
		schedule_date = data["schedule_date"]
		stock_req =  data["stock_req"]
		busyvoucherno =  data["busyvoucherno"]
		item_lines_to_print = data["item_lines_to_print"]
		additional_discount_percentage = data["additional_discount_percentage"]
		project = data["project"]
		remark = data["remark"]
		material_req = data["material_req"]
		payment_terms = data["payment_terms_template"]
		apply_discount_on = data["apply_discount_on"]
		name = data["name"]
	for data in payment_schedule:
		due_date = data['due_date']

	outer_json = {
		"doctype": "Purchase Order",
		"title" : title,
		"creation" : required_date,
		"docstatus" : 0,
		"owner" : owner,
		"taxes_and_charges" :taxes_and_charges,
		"company" : company,
		"due_date" : due_date,
		"supplier" : supplier,
		"stopped_po":stopped_po,
		"schedule_date" :schedule_date,
		"stock_req" : stock_req,
		"stock_requisition_id" : stock_req_id,
		"additional_discount_percentage" :additional_discount_percentage,
		"busyvoucherno" : busyvoucherno,
		"item_lines_to_print" : item_lines_to_print,
		"project" : project,
		"tracking_no" : remark,
		"material_request" : material_req,
		"payment_terms_template":payment_terms,
		"apply_discount_on" :apply_discount_on,
		"items":[],
		"taxes":[]
		}

	for data in purchase_items:
		item_code = data['item_code']
		received_qty = data['received_qty']
		target_warehouse = data['warehouse']
		last_purchase_price = data["last_purchase_rate"]
		parentfield = data["parentfield"]
		qty_as_per_stock_uom = data['stock_qty']
		rate = data['rate']
		pending_qty = qty_as_per_stock_uom-received_qty
		pending = hash(round(pending_qty, 1))
		if pending > 0:
			inner_json_for_items = {
				"item_code": item_code,
				"doctype": "Purchase Order Item",
				"qty": pending_qty,
				"schedule_date": required_date,
				"last_purchase_price" : last_purchase_price,
				"parentfield" : parentfield,
				"warehouse":target_warehouse,
				"qty_as_per_stock_uom":qty_as_per_stock_uom,
				"rate":rate
			}
			outer_json["items"].append(inner_json_for_items)
	for data in purchase_taxes:
		charge_type = data['charge_type']
		account_head = data['account_head']
		rate = data['rate']
		tax_amount = data["tax_amount"]
		description = data["description"]

		inner_json_for_taxes = {
			"charge_type" : charge_type,
			"account_head":account_head,
			"rate":rate,
			"tax_amount": tax_amount,
			"description" :description,
		}

		if "row_id" in data:
			row_id = data["row_id"]
			if row_id is not None:
				inner_json_for_taxes["row_id"] = row_id
		outer_json["taxes"].append(inner_json_for_taxes)
	doc = frappe.new_doc("Purchase Order")
	doc.update(outer_json)
	doc.save()
	return_doc = doc.doctype
	frappe.msgprint("Purchase Order is Created  :  "+doc.name)
	po_doc = frappe.get_doc("Purchase Order", name)
	po_doc.set_status(update = True , status = "Closed")
	po_doc.save()
	return_doc = po_doc.doctype
	if return_doc:
		return return_doc

@frappe.whitelist()
def make_sreq(stock_requisition_list,company,stopped_po):
	required_date = datetime.now()
	return_doc = ""
	innerJson = " "
	sreq_items = json.loads(stock_requisition_list)
	sreq_items = json.dumps(sreq_items)
	sreq_items_list = ast.literal_eval(sreq_items)
	outerJson = {
			"doctype": "Stock Requisition",
			"company": company,
			"title": "Purchase",
			"workflow_state": "Pending Approval",
			"docstatus": 0,
			"purpose": "Purchase",
			"requested_by": stopped_po,
			"items": []
			}
	for data in sreq_items_list:
		innerJson = {
			"doctype": "Stock Requisition Item",
			"item_code": data['item_code'],
			"qty": data['qty'],
			"schedule_date": required_date,
			"warehouse":data['warehouse']
		}
		outerJson["items"].append(innerJson)
	doc = frappe.new_doc("Stock Requisition")
	doc.update(outerJson)
	doc.save()

@frappe.whitelist()
def fetch_stopped_po_items(stopped_po):
	items = []
	items = frappe.db.sql("""select item_code,qty,rate,price_list_rate,received_qty from `tabPurchase Order Item` where parent=%s""", 					(stopped_po), as_dict = 1)
	if items:
		return items
	else:
		return items

@frappe.whitelist()
def for_item_code():
	item_code_details = frappe.db.sql("""select name,current from `tabSeries` where name='FI-'""",as_dict=1)
	return item_code_details


@frappe.whitelist()
def series_update(current_num,name):
	updated = frappe.db.sql("""UPDATE `tabSeries` SET current = '"""+current_num+"""' where name = %s""",(name),as_dict=1)
	return updated

@frappe.whitelist()
def user_details(user):
	user_data = frappe.db.sql("""select role from `tabHas Role` where parent = '"""+user+"""' AND role ='Sales Prospector' """,as_dict=1)
	return user_data

@frappe.whitelist()
def get_bom_list_for_so(item_code):
	records = frappe.db.sql("""select name  from `tabBOM` where item=%s and docstatus=1""", (item_code), as_dict=1)
	return records

##- Start of making .PRN file for Purchase Invoice Doc.
@frappe.whitelist()
def make_prnfile(invoice,ncopies,label):
	#print "-------invoice-------------", invoice
	invoice_data = frappe.get_doc("Purchase Invoice", invoice)
	printer_details = frappe.get_doc("Label Printer", label)
	address = printer_details.address
	split_address = address.split("\n")
	items_list = invoice_data.items
	posting_date = invoice_data.posting_date
	date_of_import = posting_date.strftime("%m/%y")
	#file_path = os.path.expanduser('~') +'/ERPNext_PINV_PRN.PRN'

	fname = str(invoice) + "_" + str(posting_date) +".PRN"
	save_path = 'site1.local/private/files'
	file_name = os.path.join(save_path, fname)
	ferp = frappe.new_doc("File")
	ferp.file_name = fname
	ferp.folder = "Home/Labels"
	ferp.is_private = 1
	ferp.file_url = "/private/files/"+fname

	prn_file = open(file_name,"w+")

	for items in items_list:
		copies = 1
		qty = items.qty
		total_copies = int(qty) * int(ncopies)
		item_record = frappe.get_doc("Item", items.item_code)
		price_list = frappe.get_doc("Item Price", {"item_code": items.item_code, "price_list": "Standard Selling"}, "price_list_rate")

		for copies in xrange(total_copies):
			prn_file.write("<xpml><page quantity='0' pitch='50.8 mm'></xpml>G0\015" +"\n")
			prn_file.write("n\015"+"\n")
			prn_file.write("M0500\015"+"\n")
			prn_file.write("MT\015"+"\n")
			prn_file.write("O0214\015"+"\n")
			prn_file.write("V0\015"+"\n")
			prn_file.write("t1\015"+"\n")
			prn_file.write("Kf0070\015"+"\n")
			prn_file.write("SG\015"+"\n")
			prn_file.write("c0000\015"+"\n")
			prn_file.write("e\015"+"\n")
			prn_file.write("<xpml></page></xpml><xpml><page quantity='1' pitch='50.8 mm'></xpml>L\015"+"\n")
			prn_file.write("D11\015"+"\n"+"H14\015"+"\n"+"PG\015"+"\n"+"PG\015"+"\n"+"SG\015"+"\n"+"ySPM\015"+"\n"+"A2\015"+"\n")
			prn_file.write("1911C1001760021" + str(items.item_name)+"\015"+"\n") #product-name
			prn_file.write("4911C0801000013" + str(items.item_code)+"\015"+"\n") #Barcode
			prn_file.write("1e8404201270018C0201&E0$2" + str(items.item_code)+"\015"+"\n") #ProductCode
			#prn_file.write("1911C1001570260" + "Black"+"\n") #item-color
			#prn_file.write("1911C1001570260" + "L" +"\n") #item-size
			prn_file.write("1911C1001050019Month & Yr of Import" +"\015"+ "\n")
			prn_file.write("1911C10010501600" + str(date_of_import) + "\015"+ "\n")
			prn_file.write("1911C1200800019M.R.P." +"\015"+ "\n")
			prn_file.write("1911C1200800105" + str(price_list.price_list_rate) +"\015"+"\n") #selling price
			prn_file.write("1911A0800670148Inclusive of all taxes" +"\015"+ "\n")
			prn_file.write("1911A0800990227Qty" +"\015"+ "\n")
			prn_file.write("1911A0800830227" + str(items.qty) + " " +str(items.stock_uom) +"\015"+ "\n") # Qty and UOM
			if len(split_address)!=0:
				if len(split_address) == 3:
					prn_file.write("1911C0800400012" + str(split_address[0]) +"\015"+ "\n")
					prn_file.write("1911C08002500206,"+ str(split_address[1]) +"\015"+ "\n")
					prn_file.write("1911C0800090005"+str(split_address[2]) +"\015"+ "\n")
				else:
					prn_file.write("1911C0800400012" + str(split_address[0]) +"\015"+ "\n")
			prn_file.write("Q0001\015"+"\n")
			prn_file.write("E\015"+"\n")
			prn_file.write("<xpml></page></xpml><xpml><end/></xpml>\015"+"\n")
	ferp.save()
	prn_file.close()
	frappe.msgprint(_("PRN File created - Please check File List to download the file"))
##- End of- making .PRN file for Purchase Invoice Doc.

## Start of- Set up an Auto E-Mail report to Supplier.
def send_mail_custom(recipient,content):
	frappe.sendmail(recipients=[recipient],
        sender="erptest@meritsystems.com",
        subject="Purchase Order Alert", content=content)

@frappe.whitelist()
def getPoData():
	send_email_check=frappe.db.get_single_value ('Stock Settings','send_daily_reminders_to_suppliers')
	if send_email_check:
		today_date = utils.today()
		day_name = datetime.datetime.strptime(today_date,'%Y-%m-%d').strftime('%A')

		#if day_name == "Sunday":
			#print "The mails are not send on sunday"
		if day_name == "Saturday":
			one_day_after = add_days(utils.today(),1)
			two_days_after= add_days(utils.today(),2)
			request_doc=frappe.db.sql("""select  name from `tabPurchase Order` where schedule_date in (%s,%s) and docstatus=1""", (one_day_after,two_days_after),as_dict = 1)

			for doc in request_doc:
				po_doc=frappe.get_doc("Purchase Order",doc['name'])
				supplier_email=getSupplierEmail(po_doc.supplier)
				content = getSupplierContent(doc.name)
				send_mail_custom(supplier_email,content)
		else:
			request_doc=frappe.db.sql("""select  name from `tabPurchase Order` where schedule_date=%s and docstatus=1""",one_day_after,as_dict = 1)
			for doc in request_doc:
				po_doc=frappe.get_doc("Purchase Order",doc['name'])
				supplier_email=getSupplierEmail(po_doc.supplier)
				content = getSupplierContent(doc.name)
				send_mail_custom(supplier_email,content)
	else:
		pass

@frappe.whitelist()
def getSupplierEmail(supplier):
	supplier_doc=frappe.get_all("Contact",filters=[["Dynamic Link","link_doctype","=","Supplier"],["Dynamic Link","link_name","=",supplier]],fields=["email_id"])
	return supplier_doc[0].email_id


@frappe.whitelist()
def getSupplierContent(po_name):
	content = ""
	content ="<p> <h2>Following Items are need to be delivered for Purchase order :{0}</h2> </p><ol>".format(po_name)
	content+="<table border=2px > <tr> <th> Sr No</th> <th>Product Description</th> <th> Qty</th> <th>UOM</th> <th>Rate</th> <th>Amount<th> </tr>"

	po_items = frappe.db.sql("""select idx,description,qty,uom,rate,amount from `tabPurchase Order Item` where parent = %s order by idx """ , (po_name), as_dict=1)
	for po_item in po_items:
		content += "<tr> <td align='center'>{0}</td> <td align='center'>{1}</td> <td align='center'>{2}</td> <td align='center'>{3}</td> <td align='right'>{4}</td> <td align='right'>{5}</td> </tr>".format(po_item.idx,po_item.description, po_item.qty,po_item.uom,po_item.rate,po_item.amount)
	return content
## End of- Set up an Auto E-Mail report to Supplier

## Start of- Rounding and Charging Off for Purchase Receipt.
@frappe.whitelist()
def make_stock_entry(materialIssueList,mterialReceiptList,company):
	#print "company-------------", company
	materialItemsIssue=eval(materialIssueList)
	mterialItemsReceipt=eval(mterialReceiptList)
	basic_rate = 0
	ret = ""
	difference_account = frappe.db.get_single_value("Stock Settings", "material_round_off_amounts_changed_to")
	#print "difference_account -------------", difference_account
	if(len(materialItemsIssue)!=0):
		outerJson_Transfer = {
			"naming_series": "STE-",
			"doctype": "Stock Entry",
			"title": "Material Issue",
			"docstatus": 1,
			"purpose": "Material Issue",
			"company": company,
			"items": []
					}
		for items in materialItemsIssue:
			if items['rate'] is not None:
				basic_rate = items['rate']

			innerJson_Transfer =	{
				"s_warehouse":items['warehouse'],
				"qty":items['qty'],
				"item_code":items['item_code'],
				"basic_rate": basic_rate,
				"doctype": "Stock Entry Detail"
			}
			if difference_account is not None:
				innerJson_Transfer["expense_account"] = difference_account
			outerJson_Transfer["items"].append(innerJson_Transfer)
		#print "########-Final make_stock_entry Json::", outerJson_Transfer
		doc = frappe.new_doc("Stock Entry")
		doc.update(outerJson_Transfer)
		doc.save()
		ret = doc.doctype
		if ret:
			frappe.msgprint("Stock entry is created for Material Issue : "+doc.name)

	if(len(mterialItemsReceipt)!=0):
		outerJson_Transfer = {
			"naming_series": "STE-",
			"doctype": "Stock Entry",
			"title": "Material Receipt",
			"docstatus": 1,
			"purpose": "Material Receipt",
			"company": company,
			"items": []
			}
		for items in mterialItemsReceipt:
			if items['rate'] is not None:
				basic_rate = items['rate']
			innerJson_Transfer =	{
				"t_warehouse":items['warehouse'],
				"qty":items['qty'],
				"item_code":items['item_code'],
				"basic_rate": basic_rate,
				"doctype": "Stock Entry Detail"
			}
			if difference_account is not None:
				innerJson_Transfer["expense_account"] = difference_account
			outerJson_Transfer["items"].append(innerJson_Transfer)
		#print "########-Final make_stock_entry Json::", outerJson_Transfer
		doc = frappe.new_doc("Stock Entry")
		doc.update(outerJson_Transfer)
		doc.save()
		ret = doc.doctype
		if ret:
			frappe.msgprint("Stock entry is created for Material Receipt : "+doc.name)
## End of- Rounding and Charging Off for Purchase Receipt.

@frappe.whitelist()
def fetch_delivery_note_list(name):
	delivery_note_list = frappe.db.sql("""select name from `tabDelivery Note` where pch_sales_invoice=%s """, name, as_dict = 1)
	return delivery_note_list

@frappe.whitelist()
def fax_number_test():
	doctype = "Warehouse"
	left = ""
	right = ""
	parent = "GMP - EPCH"
	if parent:
		left = frappe.db.sql("select lft, rgt from `tab{0}` where name=%s"
			.format(doctype), parent, as_dict=1)
		if left is not None and len(left)!=0:
			lft = left[0]['lft']
			rgt = left[0]['rgt']
			#print "lft----------", lft
			#print "rgt----------", rgt

	return left

@frappe.whitelist()
def make_bom_for_boq_lite(source_name, target_doc=None):
	boq_record = frappe.get_doc("BOQ Lite", source_name)
	company = boq_record.company
	name = boq_record.name

	boq_lite_items = frappe.db.sql("""select distinct boqi.immediate_parent_item as bom_item from `tabBOQ Lite Item` boqi where boqi.parent=%s""", boq_record.name,  as_dict=1)

	if boq_lite_items:
		raw_boms = []
		for parent in boq_lite_items:
			bom_main_item = parent.bom_item
			boq_records = frappe.db.sql("""select * from `tabBOQ Lite Item` where parent=%s and immediate_parent_item=%s and is_raw_material='No' order by immediate_parent_item desc""", (boq_record.name,bom_main_item), as_dict=1)
			#print "bom_main_item--------", bom_main_item
			'''
			name_bom = "BOM-"+str(bom_main_item)+"-"
			len_name_bom = len(name_bom)
			check_status = frappe.db.sql("""select max(name) as name from `tabBOM` where name LIKE '"""+name_bom+"%""'""", as_dict = 1)
			for check in check_status:
				name_check = check.name
				var = name_check.split("-")
			increas_no = var[-1]
			increased_no = int(increas_no)+1
			#print "increas_no--------------",increas_no
			#print "increas_no--------------",int(increas_no)+1
			convert = "{0:len(increas_no)}".format(increased_no)
			'''
			if not boq_records:
				bom_qty = 1
				raw_boms.append(bom_main_item)
				boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.is_raw_material as is_raw_material from `tabBOQ Lite Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s order by boqi.item_code""" , (source_name, bom_main_item), as_dict=1)

				if boq_record_bom_items:

					outer_json = {
						"company": company,
						"doctype": "BOM",
						"item": bom_main_item,
						"quantity": bom_qty,
						"pch_boq_lite_reference": name,
						"items": []
						}

					for record in boq_record_bom_items:
						item = record.qi_item
						qty = record.qty
						if item:
							item_record = frappe.get_doc("Item", item)
							innerJson ={
								"doctype": "BOM Item",
								"item_code": item,
								"description": item_record.description,
								"uom": item_record.stock_uom,
								"stock_uom": item_record.stock_uom,
								"qty": qty
								}
							outer_json["items"].append(innerJson)

					if outer_json["items"]:
						doc = frappe.new_doc("BOM")
						doc.update(outer_json)
						doc.save()
						frappe.db.commit()
						doc.submit()
						docname = doc.name
						frappe.msgprint(_("BOM Created - " + docname))
		if raw_boms:
			#print "raw_boms--------------", raw_boms
			global parent_list
			parent_list = []
			for bom_item in raw_boms:
				parent = frappe.db.sql("""select immediate_parent_item as bom_main_item  from `tabBOQ Lite Item` where parent=%s and item_code=%s""", (boq_record.name,bom_item), as_dict=1)
				if parent:
					for main_item in parent:
						bom_main_item = main_item.bom_main_item
						#print "*****parent for*****",bom_item, bom_main_item
						if bom_main_item not in parent_list:
							parent_list.append(bom_main_item)
							submit_assembly_boms(name,bom_main_item,company)
					#print "*****parent_list*****", parent_list


def submit_assembly_boms(name,bom_main_item,company):

	boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.is_raw_material as is_raw_material from `tabBOQ Lite Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s order by boqi.item_code""", (name, bom_main_item),as_dict=1)
	bom_qty = 1
	if boq_record_bom_items:
		outer_json = {
			"company": company,
			"doctype": "BOM",
			"item": bom_main_item,
			"quantity": bom_qty,
			"pch_boq_lite_reference": name,
			"items": []
			}

		for record in boq_record_bom_items:
			item = record.qi_item
			qty = record.qty
			if item:
				item_record = frappe.get_doc("Item", item)
				innerJson ={
					"doctype": "BOM Item",
					"item_code": item,
					"description": item_record.description,
					"uom": item_record.stock_uom,
					"stock_uom": item_record.stock_uom,
					"qty": qty
					}
				outer_json["items"].append(innerJson)
		if outer_json["items"]:
			doc = frappe.new_doc("BOM")
			doc.update(outer_json)
			'''
			name_bom = "BOM-"+str(bom_main_item)+"-"
			check_status = frappe.db.sql("""select max(name) from `tabBOM` where name LIKE '"""+name_bom+"%""'""", as_dict = 1)
			print "check_status-------------",check_status
			'''
			doc.save()
			frappe.db.commit()
			doc.submit()
			docname = doc.name
			frappe.msgprint(_("BOM Created - " + docname))

		parent = frappe.db.sql("""select immediate_parent_item as bom_main_item  from `tabBOQ Lite Item` where parent=%s and item_code=%s""", (name,bom_main_item), as_dict=1)
		for main_item in parent:
			parent_item = main_item.bom_main_item

			multi_parent_list = check_multiple_parent_items(name,parent_item)
			#print "***2nd**parent for*****", bom_main_item, parent_item
			if multi_parent_list:
				for parent in multi_parent_list:
					if parent not in parent_list:
						parent_list.append(parent)
						submit_assembly_boms(name,parent,company)
			else:
				if parent_item  not in parent_list:
					parent_list.append(parent_item)
					submit_assembly_boms(name,parent_item,company)

def check_multiple_parent_items(name,parent_item):
	sub_parent_items = []
	parent_items = frappe.db.sql("""select item_code as bom_main_item  from `tabBOQ Lite Item` where parent=%s and immediate_parent_item=%s""", (name,parent_item), as_dict=1)
	if parent_items:
		for parent in parent_items:
			sub_parent = parent['bom_main_item']
			sub_items = frappe.db.sql("""select * from `tabBOQ Lite Item` where parent=%s and immediate_parent_item=%s""", (name,sub_parent), as_dict=1)
			if sub_items and sub_parent not in parent_list and sub_parent not in sub_parent_items:
				sub_parent_items.append(sub_parent)
				check_multiple_parent_items(name,sub_parent)
	sub_parent_items.reverse()
	sub_parent_items.append(parent_item)
	return sub_parent_items

@frappe.whitelist()
def get_conversion_factor(parent,uom):
	records = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent=%s and uom=%s""", (parent, uom), as_dict=1)
	if records:
		conversion_factor = records[0]['conversion_factor']
		return conversion_factor

@frappe.whitelist()
def update_boq_lite_item(item_code,name,is_raw_material):
	records = frappe.db.sql("""update `tabBOQ Lite Item` set is_raw_material = '"""+ str(is_raw_material)+"""' where parent=%s and item_code=%s""", (name, item_code))
	frappe.db.commit()


@frappe.whitelist()
def fetch_qty_available_in_swh(item_code,swh):
	details = frappe.db.sql("""select actual_qty from `tabBin` where item_code=%s and warehouse=%s""", (item_code,swh), as_dict=1)
	if details:
		return details[0]['actual_qty']
	else:
		return 0

@frappe.whitelist()
def fetch_nhance_settings_details():
	details = frappe.get_doc("Nhance Settings")
	return details

@frappe.whitelist()
def make_material_receipt(mterialReceiptList,difference_account):
	mt_receipt_items = eval(mterialReceiptList)
	company = frappe.db.get_single_value("Global Defaults", "default_company")

	if mt_receipt_items:
		basic_rate = 0
		outerJson_Transfer = {
			"naming_series": "STE-",
			"doctype": "Stock Entry",
			"title": "Material Receipt",
			"docstatus": 1,
			"purpose": "Material Receipt",
			"company": company,
			"items": []
			}

		for items in mt_receipt_items:
			if items['basic_rate'] is not None:
				basic_rate = items['basic_rate']
			innerJson_Transfer =	{
				"t_warehouse":items['t_warehouse'],
				"qty":items['qty'],
				"item_code":items['item_code'],
				"stock_uom":items['stock_uom'],
				"uom":items['uom'],
				"conversion_factor":items['conversion_factor'],
				"valuation_rate":items['valuation_rate'],
				"basic_rate": basic_rate,
				"doctype": "Stock Entry Detail"
			}
			if difference_account is not None:
				innerJson_Transfer["expense_account"] = difference_account
			outerJson_Transfer["items"].append(innerJson_Transfer)
		#print "########-Final make_stock_entry Json::", outerJson_Transfer
		doc = frappe.new_doc("Stock Entry")
		doc.update(outerJson_Transfer)
		doc.save()
		#doc.submit()
		#ret = doc.doctype
		doc_name = doc.name
		if doc_name:
			return doc_name

## Expense Account details of Stock Entry Begins...
@frappe.whitelist()
def match_item_groups(item_code):
	details = frappe.db.sql("""select ig.pch_issue_diffaccount,i.item_code from `tabItem Group` ig, `tabItem` i where i.item_group = ig.name and i.name = %s""",(item_code), as_dict=1)
	return details
## Expense Account details of Stock Entry end...


#Project_material_requisition_tool PMRT (suresh)
@frappe.whitelist()
def get_po_items_qty_ac_to_sreq( stockRequisitionID ):
	po_items_qty_ac_to_sreq = frappe.db.sql("""select po.name,po.stock_requisition_id,poi.item_code,poi.qty,poi.received_qty,poi.stock_qty,poi.conversion_factor,poi.project  from `tabPurchase Order` po ,`tabPurchase Order Item` poi where po.name=poi.parent and po.docstatus=1 and po.status != 'Closed' and po.stock_requisition_id = %s """,(stockRequisitionID), as_dict=1)
	item_data = {}

	for po_item_qty_ac_to_sreq in po_items_qty_ac_to_sreq:

		if po_item_qty_ac_to_sreq['item_code'] in item_data.keys():
			ordered_qty = po_item_qty_ac_to_sreq['stock_qty']
			ordered_qty = round(ordered_qty,2)
			item_data_key =  po_item_qty_ac_to_sreq['item_code']
			sum_qty = item_data[ item_data_key ] + ordered_qty
			item_data[ item_data_key ] = sum_qty
		else:
			ordered_qty = po_item_qty_ac_to_sreq['stock_qty']
			ordered_qty = round(ordered_qty,2)
			item_data_local =	{po_item_qty_ac_to_sreq['item_code']: ordered_qty}
			item_data.update( item_data_local)
	return item_data


@frappe.whitelist()
def get_sreq_items_data(stockRequisitionID):
	sreq_items_data = frappe.db.sql(""" select sri.item_code,sri.qty,sri.quantity_to_be_ordered,sri.quantity_ordered,sri.fulfilled_quantity,sr.pch_is_submitted_sreq_updated from `tabStock Requisition` sr,`tabStock Requisition Item` sri where sr.name= %s and sri.parent=sr.name """,(stockRequisitionID), as_dict=1)
	return sreq_items_data

@frappe.whitelist()
def update_sreq_items_data(updated_sreq_items_data,stockRequisitionID): #from po submission

	updated_sreq_items_data = json.loads(updated_sreq_items_data)
	#print "updated_sreq_items_data--------------------",updated_sreq_items_data
	for updated_sreq_item_data in updated_sreq_items_data:
		sreq_item_code = updated_sreq_item_data['sreq_item_code']
		quantity_ordered = updated_sreq_item_data['quantity_ordered']
		#quantity_to_be_order =  updated_sreq_item_data ['quantity_to_be_order']
		#fulfilled_qty =  updated_sreq_item_data ['fulfilled_qty']
		#frappe.db.sql("""update `tabStock Requisition Item` sri  set sri.quantity_ordered = %s, sri.quantity_to_be_ordered =%s, fulfilled_quantity=%s where sri.parent = %s and sri.item_code = %s """, (quantity_ordered, quantity_to_be_order,fulfilled_qty,stockRequisitionID,sreq_item_code))
		frappe.db.sql("""update `tabStock Requisition Item` sri  set sri.quantity_ordered = %s where sri.parent = %s and sri.item_code = %s """, (quantity_ordered,stockRequisitionID,sreq_item_code))#jyoti changed previous query to this


	return "done"

@frappe.whitelist()
def update_submitted_po(name,sreq_no):
	frappe.db.sql("""update `tabPurchase Order` set pch_is_submitted_po_updated='Yes' where name=%s and stock_requisition_id=%s """, (name,sreq_no))

@frappe.whitelist()
def update_cancelled_po(name,sreq_no):
	frappe.db.sql("""update `tabPurchase Order` set pch_is_cancelled_po_updated='Yes' where name=%s and stock_requisition_id=%s """, (name,sreq_no))

@frappe.whitelist()
def update_submitted_sreq( stockRequisitionID):
	frappe.db.sql("""update `tabStock Requisition` set pch_is_submitted_sreq_updated='Yes' where name=%s """, (stockRequisitionID))

@frappe.whitelist()
def update_sreq_items_data_on_sreq_approvel(updated_sreq_items_data,stockRequisitionID): #from sreq approval_level

	updated_sreq_items_data = json.loads(updated_sreq_items_data)

	for updated_sreq_item_data in updated_sreq_items_data:
		sreq_item_code = updated_sreq_item_data['sreq_item_code']
		quantity_to_be_order =  updated_sreq_item_data ['quantity_to_be_order']
		frappe.db.sql("""update `tabStock Requisition Item` sri  set  sri.quantity_to_be_ordered =%s where sri.parent = %s and sri.item_code = %s """, ( quantity_to_be_order,stockRequisitionID,sreq_item_code))

	return "done"

@frappe.whitelist() #from material transfer
def update_sreq_items_fulfilled_qty(updated_sreq_items_data,stockRequisitionID):
	updated_sreq_items_data = json.loads(updated_sreq_items_data)
	for updated_sreq_item_data in updated_sreq_items_data:
		sreq_item_code = updated_sreq_item_data['sreq_item_code']
		fulfilled_qty =  updated_sreq_item_data ['fulfilled_quantity']

		frappe.db.sql("""update `tabStock Requisition Item` sri set fulfilled_quantity=%s where sri.parent = %s and sri.item_code = %s """, (fulfilled_qty,stockRequisitionID,sreq_item_code))

#PMRT end

@frappe.whitelist()
def cancel_stock_entry_material_receipt(pch_ste_pull_short_rm):
    frappe.db.sql("""update `tabStock Entry` set docstatus=2 where name=%s""", pch_ste_pull_short_rm)
    frappe.db.commit()
    frappe.msgprint("The Stock Entry is cancelled successfully!!")
    return 1

#jyoti
@frappe.whitelist()
def get_serial_number_details(duplicate_serial):
    #print "coming inside get_serial_number_details---"
    serial_no_list = frappe.db.sql("""select max(serial_no) as serial_no from `tabSerial No` where serial_no like '"""+duplicate_serial+"%""'""", as_dict=1)
    #print "serial_no_list----",serial_no_list
    return serial_no_list


#jyoti
@frappe.whitelist()
def get_file_url_pressure(attached_to_name):
    #print "coming inside get_file_url---"
    pressure = 'P'
    get_file_url_pressure = frappe.db.sql("""select File_url from `tabFile` where  attached_to_name='"""+attached_to_name+"""' and file_name LIKE '"""+pressure+"%""'""" , as_dict=1)
    #url=get_file_url_pressure[0]['File_url']
    #print "get_file_url_pressure----",get_file_url_pressure[0]['File_url']
    #link="<a href= " + get_file_url_pressure[0]['File_url'] + " target = _blank>" + get_file_url_pressure[0]['File_url'] + "<br/>" + "</a>"
    #serial=frappe.db.sql("""select name from `tabSerial No test` where name='"""+attached_to_name+"""'  """ , as_dict=1)
    #serial_number=serial[0]['name']
    #print "serial----",serial[0]['name']
    #frappe.set_value("Serial No test",serial_number,"pch1_pressure_test",get_file_url_pressure);
    return get_file_url_pressure

#jyoti
@frappe.whitelist()
def get_file_url_coc(attached_to_name):
    #print "coming inside get_file_url---"
    coc = 'C'
    get_file_url_coc1= frappe.db.sql("""select File_url from `tabFile` where  attached_to_name='"""+attached_to_name+"""' and file_name LIKE '"""+coc+"%""'""" , as_dict=1)
    #print "serial_no_list----",serial_no_list
    return get_file_url_coc1

#jyoti
@frappe.whitelist()
def get_file_url_build_sheet(attached_to_name):
    #print "coming inside get_file_url---"
    build_sheet = 'B'
    get_file_url_build= frappe.db.sql("""select File_url from `tabFile` where  attached_to_name='"""+attached_to_name+"""' and file_name LIKE '"""+build_sheet+"%""'""" , as_dict=1)
    #print "serial_no_list----",serial_no_list
    return get_file_url_build



#jyoti
@frappe.whitelist()
def get_combined_pdf(attached_to_name):
    #print "coming inside get_file_url---"
    combined = 'combined'+attached_to_name
    get_combined_file_url = frappe.db.sql("""select File_url from `tabFile` where   attached_to_name LIKE '"""+combined+"%""'""" , as_dict=1)
    #print "serial_no_list----",serial_no_list
    return get_combined_file_url

#jyoti
@frappe.whitelist()
def get_purchse_receipt_revision_no(item_code,purchase_document_no):
    get_revision = frappe.db.sql("""select revision_number from  `tabPurchase Receipt Item` where  item_code='"""+item_code+"""' and parent='"""+purchase_document_no+"""' """, as_dict=1)
    #print "sales_record----",sales_record
    #print "get_revision-----",get_revision
    return get_revision


#jyoti
@frappe.whitelist()
def get_stock_entry_revision_no(item_code,purchase_document_no):
    get_stock_revision_no = frappe.db.sql("""select revision_number from  `tabStock Entry Detail` where  item_code='"""+item_code+"""' and parent='"""+purchase_document_no+"""' """, as_dict=1)
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    return get_stock_revision_no



#jyoti
@frappe.whitelist()
def get_purchase_revision_no(item_code,parent):
    get_serial_no=frappe.db.sql("""select serial_no from  `tabPurchase Receipt Item` where  item_code='"""+item_code+"""' and parent='"""+parent+"""' """, as_dict=1)
    #print "get_serial_no----",get_serial_no
    test=get_serial_no[0]['serial_no'].split('\n');
    #print "test----",test
    for serial_list in test:
		#revision=frappe.db.sql("""select revision_number from  `tabPurchase Receipt Item` where  item_code='"""+item_code+"""' and parent='"""+parent+"""' """, as_dict=1)
	    revision=frappe.db.sql("""select revision_number from  `tabPurchase Receipt Item` where  item_code='"""+item_code+"""' and parent='"""+parent+"""' """, as_dict=1)
		#print "revision----",revision
	    revision_number=revision[0]['revision_number']
		#print "revision_number----",revision_number
	    frappe.set_value("Serial No",serial_list,"revision_number",revision_number);



    return get_serial_no



#jyoti
@frappe.whitelist()
def get_revision_no_stock(item_code,parent):
    get_stock_serial_no=frappe.db.sql("""select serial_no from  `tabStock Entry Detail` where  item_code='"""+item_code+"""' and parent='"""+parent+"""' """, as_dict=1)
    #print "get_stock_serial_no----",get_stock_serial_no
    test=get_stock_serial_no[0]['serial_no'].split('\n');
    #print "test----",test
    for serial_list in test:
	    #print serial_list
	    revision=frappe.db.sql("""select revision_number from  `tabStock Entry Detail` where  item_code='"""+item_code+"""' and parent='"""+parent+"""' """, as_dict=1)
	    #print "revision----",revision
	    revision_number=revision[0]['revision_number']
	    #print "revision_number----",revision_number
	    frappe.set_value("Serial No",serial_list,"revision_number",revision_number);



    return get_stock_serial_no


#jyoti
@frappe.whitelist()
def get_merge_file_url(attached_to_name):
    #print "coming inside get_merge_file_url_list---"
    get_merge_file_url_list = frappe.db.sql("""select File_url from `tabFile` where attached_to_name=%s""",attached_to_name)
    #print get_merge_file_url_list
    combined = 'combined'+attached_to_name
    get_combined_file_url = frappe.db.sql("""select File_url from `tabFile` where   attached_to_name LIKE '"""+combined+"%""'""" , as_dict=1)
    #print "get_combined_file_url",get_combined_file_url
    if get_combined_file_url==[]:
    	#print("entered in if") 
    	name1=attached_to_name+".pdf"
    	#print "namepdf",name1
    	test2=[]
    	test3=[]
    	for test in get_merge_file_url_list:
		#print "test",str(test)
            for test1 in test:
	    		#print "test1",str(test1)
            	test2.append(str(test1))
            		#print "_____",test2
        	#print "test2",test2 
    	for files in test2:
        	#print "files",str(files)
        	n=8
        	res = files[7:]
		#print "res",res
	        test3.append(str(res))
	#print "test3",test3 
    
    	path = '/home/frappe/frappe-bench/sites/site1.local/public/files/'

    	#pdf_files = ['today.pdf','today1.pdf','cocpf96ad96.pdf']
    	pdf_files = test3 
    	#print "pdf_files",pdf_files

    	merger = PdfFileMerger()
    	#print "-----------------------"
    	for files in pdf_files:
        	#print "entered in for loop"
		#print "files",files
          	#print "file path",path + files
        	merger.append(PdfFileReader(file(path + files, 'rb')), import_bookmarks=False)
    		#merger.append(path + files)
        	#print "+++++++++++",path+name1
    	fname = attached_to_name
    	combined='combined'+attached_to_name
    	save_path = 'site1.local/public/files'
    	file_name = os.path.join(save_path, fname)
    	ferp = frappe.new_doc("File")
    	ferp.file_name = fname+".pdf"
    	ferp.folder = "Home/Attachments"
    	ferp.is_private =0
    	ferp.file_url = "/files/"+fname+".pdf"
    	ferp.attached_to_doctype="Serial No"
    	ferp.attached_to_name=combined
    	#if not os.path.exists(path+name1):
    	merger.write(path+name1)
    	#print ".............."
    	merger.close()
    	source=path+name1
    	target=os.path.join(save_path, fname)
    	copyfile(source,target);
    	#print "successufully copied"
    	ferp.save()
    	frappe.msgprint(_("File created - Please check File List to download the file"))
    	#frappe.db.sql("""update `tabSerial No` set created_combined_pdf=1 where name=%s""",name)
    	#frappe.db.commit()
    	#frappe.msgprint(_("combined_pdf created-"))
    return get_merge_file_url_list


#jyoti
@frappe.whitelist()
def get_income_account_from_item(item_code,company):
    income_account_item = frappe.db.sql("""select income_account,expense_account from `tabItem Default` where parent='"""+item_code+"""' and company='"""+company+"""' """, as_dict=1)
    income_account=income_account_item[0]['income_account']
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    
    return income_account

@frappe.whitelist()
def get_expense_account_from_item(item_code,company):
    expense_account_item = frappe.db.sql("""select income_account,expense_account from `tabItem Default` where parent='"""+item_code+"""' and company='"""+company+"""' """, as_dict=1)
    print("expense_account_item",expense_account_item);
    expense_account=expense_account_item[0]['expense_account']
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    
    return expense_account

@frappe.whitelist()
def get_income_account(customer):
    income_account = frappe.db.sql("""select pch_overriding_income_account from  `tabCustomer` where  customer_name='"""+customer+"""'  """, as_dict=1)
    #overriding_income_account=income_account[0]['pch_overriding_income_account']
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    
    return income_account


@frappe.whitelist()
def get_expense_account(customer):
    expense_account = frappe.db.sql("""select pch_overriding_expense_account from  `tabCustomer` where  customer_name='"""+customer+"""'  """, as_dict=1)
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    return expense_account

@frappe.whitelist()
def get_expense_account_company(company):
    expense_account_company = frappe.db.sql("""select default_expense_account from  `tabCompany` where  name='"""+company+"""'  """, as_dict=1)
    expense_account_company_detail=expense_account_company[0]['default_expense_account']
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    
    return expense_account_company_detail


@frappe.whitelist()
def get_income_account_company(company):
    income_account_company = frappe.db.sql("""select default_income_account from  `tabCompany` where  name='"""+company+"""'  """, as_dict=1)
    income_account_company_detail=income_account_company[0]['default_income_account']
    #print "sales_record----",sales_record
    #print "get_stock_revision_no-----",get_stock_revision_no
    
    return income_account_company_detail

#jyoti
@frappe.whitelist()
def get_stock_qty(item_code,warehouse):
    
    qty = frappe.db.sql("""select concat_ws(" ", posting_date, posting_time) as date from `tabStock Ledger Entry` where item_code='"""+item_code+"""' and warehouse='"""+warehouse+"""' """, as_dict=1)
    #print("qty",qty)
    return qty


@frappe.whitelist()
def get_balance_qty(item_code,warehouse,posting_date):
    
    balance_qty = frappe.db.sql("""select posting_time from `tabStock Ledger Entry` where item_code='"""+item_code+"""' and warehouse='"""+warehouse+"""' and posting_date='"""+posting_date+"""' """, as_dict=1)
    #print("balance_qty",balance_qty)
    return balance_qty


