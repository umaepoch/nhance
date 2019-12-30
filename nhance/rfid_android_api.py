from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words



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

#associate_doctype_rfid_tags()
@frappe.whitelist()
def associate_doctype_rfid_tags(doc_type , doc_no,scanned_rfid_tag_data):
	scanned_rfid_tag_data = json.loads(scanned_rfid_tag_data)
	doc_to_be_update = frappe.get_doc(doc_type ,doc_no)
	for tag_position in scanned_rfid_tag_data:
		doc_to_be_update.db_set(tag_position, scanned_rfid_tag_data[tag_position])
		doc_to_be_update.save()

	updated_doc = frappe.get_doc(doc_type ,doc_no)
	is_updated = 1
	for tag_position in scanned_rfid_tag_data: #validation loop
		none_check = getattr(updated_doc,tag_position)
		if none_check == None  and  scanned_rfid_tag_data[tag_position] == " "  :
			pass
		elif scanned_rfid_tag_data[tag_position] != getattr(updated_doc,tag_position) :
			is_updated = 0
			break
		else:
			pass

		if scanned_rfid_tag_data[tag_position] == getattr(updated_doc,tag_position) : #debugging
			pass
	return is_updated

@frappe.whitelist()
def sample_update():
	#print "***** Enters Sample update scanned_rfid_tag_data",scanned_rfid_tag_data
	rfid_tag_details_doc = frappe.get_doc( "Item", "Vehicle")
	fetch_data = getattr(rfid_tag_details_doc,"item_code")
	return fetch_data

@frappe.whitelist()
def update_rfid_tag_details_child_doc( doc_type,doc_no,matched_rfid_tag_details_name,rfid_tag_position ):
	is_child_doc_updation_complete = 0
	rfid_tag_details_doc = frappe.get_doc( "RFID Tag Details",matched_rfid_tag_details_name )
	is_last_row_ed_updated = False
	last_row_idx = 0 	# lastrow
	for roww in rfid_tag_details_doc.rfid_tag_association_details:
		last_row_idx = last_row_idx +1

	for roww in rfid_tag_details_doc.rfid_tag_association_details:
		if roww.idx == last_row_idx:
			roww.pch_rfid_association_end_date = utils.now()
			rfid_tag_details_doc.save()
			is_last_row_ed_updated = True

	if is_last_row_ed_updated == True:
		row = rfid_tag_details_doc.append('rfid_tag_association_details',{})
		row.pch_rfid_association_start_date = utils.now()
		row.tag_association = rfid_tag_position
		row.pch_rfid_docid_associated_with = doc_no
		row.pch_rfid_doctype_associated_with = doc_type
		row.idx = last_row_idx+1  #new rows
		rfid_tag_details_doc.save()
		is_child_doc_updation_complete = 1
	return is_child_doc_updation_complete

@frappe.whitelist()
def	create_rfid_tag_details_doc( scanned_rfid_tag_data,tag_association,pch_rfid_docid_associated_with,pch_rfid_doctype_associated_with):

      rfid_child_doc_json = " "
      rfid_doc_json = {
      "doctype": "RFID Tag Details",
      "rfid_tag": scanned_rfid_tag_data,
      "rfid_tag_association_details": []
      }

      rfid_child_doc_json ={
      "doctype": "RFID Tag Association Details",
      "tag_association": tag_association,
      "pch_rfid_docid_associated_with": pch_rfid_docid_associated_with,
      "pch_rfid_doctype_associated_with": pch_rfid_doctype_associated_with ,
      "idx":1
      }
      rfid_doc_json["rfid_tag_association_details"].append(rfid_child_doc_json) #end of for

      #print "create_rfid_tag_details_doc checking rfid_doc_json**********",rfid_doc_json

      doc = frappe.new_doc("RFID Tag Details")
      doc.update(rfid_doc_json)
      doc.save()
      is_created = 1
      return is_created

