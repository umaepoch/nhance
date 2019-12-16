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
	
