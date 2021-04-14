# Copyright (c) 2013, ​Riverstone Infotech​ and contributors
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
#reload(sys)
#sys.setdefaultencoding('utf-8')

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
	
	att_details = fetching_previous_day_attendance_details(filters)
	for att_data in att_details:
		sum_data.append([att_data['name'],att_data['attendance_date'].strftime("%d-%m-%Y"),att_data['employee_name'], att_data['department'], 
			att_data['designation'],att_data['shift'],att_data['status']
					])

	print("sum_data",sum_data)
	return columns, sum_data

def fetching_previous_day_attendance_details(filters):
    condition = get_conditions(filters)
    sql_str = frappe.db.sql("""select em.name,
	att.attendance_date,
	em.employee_name,em.department,em.designation, att.shift,att.status from `tabEmployee` em,`tabAttendance` att  where  em.name=att.employee
 %s  order by att.attendance_date desc""" %
		condition, as_dict=1)
	#print("sql",sql_str)
    return sql_str
					
def get_columns():
	"""return columns"""
	columns = [
		_("Employee")+":Link/Employee:200",
		_("Attendance Date")+"::200",
		_("Employee Name")+"::200",
		_("Department")+"::100",
		_("Designation")+"::100",
		_("Shift")+"::100",
       	_("Status")+"::100",
		
		 ]
	return columns


def get_conditions(filters):
	conditions=""
	if filters.get("from_date"):
    		conditions += 'and att.attendance_date >= %s'  % frappe.db.escape(filters.get("from_date"), percent=False)
	if filters.get("to_date"):
    		conditions +='and att.attendance_date <= %s' % frappe.db.escape(filters.get("to_date"), percent=False)
	return conditions



    		

	

