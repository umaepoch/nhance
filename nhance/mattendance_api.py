from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
import requests


@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def create_biometric_attendance():
	reqData = json.loads(frappe.request.data)
	print "reqData json",reqData
	bio_aten = frappe.new_doc("Biometric Attendance Nhance")
	bio_aten.timestamp = reqData.get("time_stamp")
	bio_aten.employee_id = reqData.get("employee_id")
	bio_aten.source = "Mobile"
	bio_aten.is_permitted_location = "Yes"
	if reqData.get("punch_status") == "Check In":
		bio_aten.punch = 0
	if reqData.get("punch_status") == "Check Out":
		bio_aten.punch =1
	if reqData.get("punch_status") == "Lunch Out":
		bio_aten.punch = 2
	if reqData.get("punch_status") == "Lunch In":
		bio_aten.punch = 3
	if reqData.get("punch_status") == "Unknown Punch":
		bio_aten.punch = 10
	bio_aten.punch_status = reqData.get("punch_status")
	bio_aten.save(ignore_permissions=True)
	bio_aten.submit()
	return "Done"

@frappe.whitelist()
def testing():
	reqData = json.loads(frappe.request.data)
	print "reqData json",reqData
	return "hello"
