# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
import time
import math
import json
import ast
import sys

sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []
	from_date = filters.get("from_date")
	print("from_date",from_date)
	to_date = filters.get("to_date")
	print("to_date",to_date)
	global data
	global condition
	
	columns = get_columns()
	
	att_details = fetching_previous_day_attendance_details_department_wise(filters)
	for ds in att_details:
		sum_data.append([ds.department,ds.present,ds.absent,ds.present+ds.absent])
	#print("sum_data",sum_data)
	return columns, sum_data

def fetching_previous_day_attendance_details_department_wise(filters):
	condition = get_conditions(filters)
	sql_str = frappe.db.sql("""select e.department as department,count(case when att.status='Absent'  then 1 end) as absent,count(case when att.status='Present' then 1 end) as present from `tabAttendance` att,`tabEmployee` e where e.name=att.employee 
	%s  group by department""" %
		condition, as_dict=1)
	return sql_str

def get_columns():
	"""return columns"""
	columns = [
			_("Department")+":Link/Department:200",
			_("Present")+"::100",
			_("Absent")+"::100",
			_("Total Records")+"::100",
			]
	return columns

def get_conditions(filters):
	conditions=""
	if filters.get("from_date"):
		conditions += 'and att.attendance_date >= %s'  % frappe.db.escape(filters.get("from_date"), percent=False)
	if filters.get("to_date"):
		conditions +='and att.attendance_date <= %s' % frappe.db.escape(filters.get("to_date"), percent=False)
	return conditions

