# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange
import json
import datetime

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	emp_map = get_employee_details()

	holiday_list = [emp_map[d]["holiday_list"] for d in emp_map if emp_map[d]["holiday_list"]]
	default_holiday_list = frappe.get_cached_value('Company',  filters.get("company"),  "default_holiday_list")
	holiday_list.append(default_holiday_list)
	holiday_list = list(set(holiday_list))
	holiday_map = get_holiday(holiday_list, filters["month"])

	data = []
	leave_types = frappe.db.sql("""select name from `tabLeave Type`""", as_list=True)
	leave_list = [d[0] for d in leave_types]
	columns.extend(leave_list)

	for emp in sorted(att_map):
		emp_det = emp_map.get(emp)
		if not emp_det:
			continue

		row = [emp, emp_det.employee_name, emp_det.branch, emp_det.department, emp_det.designation,
			emp_det.company]

		total_p = total_a = total_l = 0.0
		for day in range(filters["total_days_in_month"]):
			status = att_map.get(emp).get(day + 1, "None")
			status_map = {"Present": "P", "Absent": "A", "Half Day": "HD", "On Leave": "L", "None": "", "Holiday":"<b>H</b>"}
			if status == "None" and holiday_map:
				emp_holiday_list = emp_det.holiday_list if emp_det.holiday_list else default_holiday_list
				if emp_holiday_list in holiday_map and (day+1) in holiday_map[emp_holiday_list]:
					status = "Holiday"
			row.append(status_map[status])

			if status == "Present":
				total_p += 1
			elif status == "Absent":
				total_a += 1
			elif status == "On Leave":
				total_l += 1
			elif status == "Half Day":
				total_p += 0.5
				total_a += 0.5
				total_l += 0.5

		row += [total_p, total_l, total_a]
		if not filters.get("employee"):
			filters.update({"employee": emp})
			conditions += " and employee = %(employee)s"
		elif not filters.get("employee") == emp:
			filters.update({"employee": emp})

		leave_details = frappe.db.sql("""select leave_type, status, count(*) as count from `tabAttendance`\
			where leave_type is not NULL %s group by leave_type, status""" % conditions, filters, as_dict=1)
		
		leaves = {}
		for d in leave_details:
			if d.status == "Half Day":
				d.count = d.count * 0.5
			if d.leave_type in leaves:
				leaves[d.leave_type] += d.count
			else:
				leaves[d.leave_type] = d.count

		for d in leave_list:
			if d in leaves:
				row.append(leaves[d])
			else:
				row.append("0.0")
		
		data.append(row)
	return columns, data

def get_columns(filters):
	columns = [
		_("Employee") + ":Link/Employee:120", _("Employee Name") + "::140", _("Branch")+ ":Link/Branch:120",
		_("Department") + ":Link/Department:120", _("Designation") + ":Link/Designation:120",
		 _("Company") + ":Link/Company:120"
	]

	for day in range(filters["total_days_in_month"]):
		columns.append(cstr(day+1) +"::20")

	columns += [_("Total Present") + ":Float:80", _("Total Leaves") + ":Float:80",  _("Total Absent") + ":Float:80"]
	return columns

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql("""select employee, day(attendance_date) as day_of_month,
		status from tabAttendance where docstatus = 1 %s order by employee, attendance_date""" %
		conditions, filters, as_dict=1)

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.status

	return att_map

def get_conditions(filters):
	if not (filters.get("month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)

	filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(filters.month) + 1

	filters["total_days_in_month"] = monthrange(cint(filters.year), filters.month)[1]

	conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"

	return conditions, filters
def get_condition(filters):
	if not (filters['month'] and filters['year']):
		msgprint(_("Please select month and year"), raise_exception=1)

	filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(filters['month']) + 1

	filters["total_days_in_month"] = monthrange(cint(filters['year']), filters['month'])[1]

	conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"

	if filters['company']: conditions += " and company = %(company)s"
	
	if 'employee' in filters: conditions += " and employee = %(employee)s"

	return conditions, filters

def get_employee_details():
	emp_map = frappe._dict()
	for d in frappe.db.sql("""select name, employee_name, designation, department, branch, company,
		holiday_list from tabEmployee""", as_dict=1):
		emp_map.setdefault(d.name, d)

	return emp_map

def get_holiday(holiday_list, month):
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(d, frappe.db.sql_list('''select day(holiday_date) from `tabHoliday`
				where parent=%s and month(holiday_date)=%s''', (d, month)))

	return holiday_map

@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(attendance_date) from tabAttendance ORDER BY YEAR(attendance_date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)

@frappe.whitelist()
def create_leave_application(filters):
	if not filters: filters = {}
	filters = json.loads(filters)
	
	conditions, filters = get_condition(filters)
	columns = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	emp_map = get_employee_details()
	
	holiday_list = [emp_map[d]["holiday_list"] for d in emp_map if emp_map[d]["holiday_list"]]
	default_holiday_list = frappe.get_cached_value('Company',  filters.get("company"),  "default_holiday_list")
	holiday_list.append(default_holiday_list)
	holiday_list = list(set(holiday_list))
	holiday_map = get_holiday(holiday_list, filters["month"])

	data = []
	leave_types = frappe.db.sql("""select name from `tabLeave Type`""", as_list=True)
	leave_list = [d[0] for d in leave_types]
	columns.extend(leave_list)
	for att in att_map:
		#print "att--------------",att
		employee_attendace = att_map[att]
		day =1
		employee_joining_date = frappe.get_value("Employee", att , "date_of_joining")
		role = "Leave Approver"
		roles = get_roles(role)
	
		while day <= filters["total_days_in_month"]:
			#print "employee_attendace-----------",employee_attendace
			if day in employee_attendace:
				if employee_attendace[day] == "Absent":
					date = str(filters['year'])+"-"+str(filters['month'])+"-"+str(day)
					date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
					if date_time_obj.date() > employee_joining_date:
						check_leave_application = get_leave_application(date_time_obj.date(),att)
						#print "check_leave_application------------",check_leave_application
						if check_leave_application == False:
							doc = frappe.new_doc("Leave Application")
							doc.employee = att
							doc.from_date = date_time_obj.date()
							doc.to_date = date_time_obj.date()
							doc.leave_approver = roles[0].parent
							doc.posting_date = date_time_obj.date()
							doc.leave_type = "Leave Without Pay"
							doc.status = "Approved"
							#doc.insert(ignore_permission = True)
							doc.save()
							doc.submit()
					
			day +=1

def get_roles(role):
	user_data = frappe.db.sql("""select parent from `tabHas Role` where  role =%s """,role,as_dict=1)
	if user_data is not None:
		return user_data
	else:
		return None
def get_leave_application(date_time_obj,employee):
	leave_application = frappe.db.sql("""select name from `tabLeave Application` where employee = %s and from_date <= %s and to_date = %s and docstatus =1 """,(employee,date_time_obj,date_time_obj), as_dict=1)
	if len(leave_application) != 0:
		return True
	else:
		return False

