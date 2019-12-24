from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json



@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def frappe_db_talk_check():
	#checking
	permitted_doctypes = frappe.db.sql("""select permitted_doctype from `tabRFID Association Permitted for DocTypes`""",as_dict=1)
	return permitted_doctypes

@frappe.whitelist()
def get_permitted_doctype_data():
	permitted_doctypes = frappe.db.sql("""select permitted_doctype,number_of_rfid_tags_per_record from `tabRFID Association Permitted for DocTypes`""",as_dict=1)
	return permitted_doctypes

@frappe.whitelist()
def custom_json_object_check(doc_type , doc_no,scanned_rfid_tag_data):
	#print "suresh_android..*** scanned_rfid_tag_data:",scanned_rfid_tag_data
	scanned_rfid_tag_data = json.loads(scanned_rfid_tag_data)
	#print "suresh_android..*** doc_type ,doc_no",doc_type,doc_no

	doc_to_be_update = frappe.get_doc(doc_type ,doc_no)

	for tag_position in scanned_rfid_tag_data:
		doc_to_be_update.db_set(tag_position, scanned_rfid_tag_data[tag_position])
		doc_to_be_update.save()

	#print "**********************************doc updated with respectiv vals"

	updated_doc = frappe.get_doc(doc_type ,doc_no)
	#print "***** Enters custom_json_object_check  after before update pch_rfid_tag1",updated_doc.pch_rfid_tag1
	#print "***** Enters custom_json_object_check   after before update pch_rfid_tag2",updated_doc.pch_rfid_tag2
	is_updated = 1
	for tag_position in scanned_rfid_tag_data: #validation loop
		none_check = getattr(updated_doc,tag_position)
		if none_check == None  and  scanned_rfid_tag_data[tag_position] == " "  :
			#print "***************from pass",tag_position
			pass
		elif scanned_rfid_tag_data[tag_position] != getattr(updated_doc,tag_position) :
			#print "***************from elif",tag_position
			is_updated = 0
			break
		else:
			pass
			#print "***************validation debugging uupdated tag_position",tag_position

		if scanned_rfid_tag_data[tag_position] == getattr(updated_doc,tag_position) : #debugging
			pass
			#print "***************validation debugging uupdated status",tag_position

	return is_updated

@frappe.whitelist()
def sample_update():

	#print "***** Enters Sample update scanned_rfid_tag_data",scanned_rfid_tag_data
	doc_upda = frappe.get_doc( "Item", "Vehicle")
	#print "**********************************type of doc ",type(doc_upda)
	fetch_data = getattr(doc_upda,"item_code")
	return fetch_data





"""
	for tag_position in scanned_rfid_tag_data:
		doc_to_be_update.db_set(tag_position, scanned_rfid_tag_data[tag_position])
		doc_to_be_update.save()
		print "suresh_android..*** Entered for looop saved",tag_position
		"""

	#return "custom api updation done"
