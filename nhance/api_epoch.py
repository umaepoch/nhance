from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words
from frappe.model.naming import make_autoname

from frappe import msgprint, _, throw, utils
#from erpnext.hr.doctype.process_payroll.process_payroll import get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from frappe.model.mapper import get_mapped_doc
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications
from frappe.jobs.background_jobs import enqueue

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


