# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PercentagesSalaryDispensed(Document):
	pass

#salary slip creation####################################################################3

@frappe.whitelist()
def create_salary_slip(name):
	doc = frappe.get_doc("Payroll Entry", name)
	doc.check_permission('write')
	doc.created = 1
	emp_details = get_emp_list(doc)
	
	emp_list = [d.employee for d in get_emp_list(doc)]
	if emp_list:
		args = frappe._dict({
			"salary_slip_based_on_timesheet": doc.salary_slip_based_on_timesheet,
			"payroll_frequency": doc.payroll_frequency,
			"start_date": doc.start_date,
			"end_date": doc.end_date,
			"company": doc.company,
			"posting_date": doc.posting_date,
			"deduct_tax_for_unclaimed_employee_benefits": doc.deduct_tax_for_unclaimed_employee_benefits,
			"deduct_tax_for_unsubmitted_tax_exemption_proof": doc.deduct_tax_for_unsubmitted_tax_exemption_proof,
			"payroll_entry": doc.name
			
		})
		if len(emp_list) > 30:
			frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=emp_list, args=args)
		else:
			create_salary_slips_for_employees(emp_list, args, publish_progress=False)

def get_emp_list(doc):
	"""
		Returns list of active employees based on selected criteria
		and for which salary structure exists
	"""
	cond = doc.get_filter_condition()
	cond += doc.get_joining_releiving_condition()

	condition = ''
	if doc.payroll_frequency:
		condition = """and payroll_frequency = '%(payroll_frequency)s'"""% {"payroll_frequency": doc.payroll_frequency}

	sal_struct = frappe.db.sql_list("""
			select
				name from `tabSalary Structure`
			where
				docstatus = 1 and
				is_active = 'Yes'
				and company = %(company)s and
				ifnull(salary_slip_based_on_timesheet,0) = %(salary_slip_based_on_timesheet)s
				{condition}""".format(condition=condition),
			{"company": doc.company, "salary_slip_based_on_timesheet":doc.salary_slip_based_on_timesheet})
	if sal_struct:
		cond += "and t2.salary_structure IN %(sal_struct)s "
		cond += "and %(from_date)s >= t2.from_date"
		emp_list = frappe.db.sql("""
			select
				distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
			from
				`tabEmployee` t1, `tabSalary Structure Assignment` t2
			where
				t1.name = t2.employee
				and t2.docstatus = 1
		%s order by t2.from_date desc
		""" % cond, {"sal_struct": tuple(sal_struct), "from_date": doc.end_date}, as_dict=True)
		
		return emp_list
def create_salary_slips_for_employees(employees, args, publish_progress=True):
	salary_slips_exists_for = get_existing_salary_slips(employees, args)
	count=0
	for emp in employees:
		if emp not in salary_slips_exists_for:
			employee_salary_structure = get_salary_structure(emp)
			#print "emp--------------",emp
			salary_dispensed = get_salary_dispensed(emp)
			#print "salary_dispensed------------",salary_dispensed
			for emp_str in employee_salary_structure.earnings:
				
				if emp_str.use_correction_factor_as_per_percentage_salary_dispensed == 1:
					emp_str.amount = float(emp_str.amount) * float(salary_dispensed[0].percentage)/100
				
			args.update({
				"doctype": "Salary Slip",
				"employee": emp,
				"pch_salary_structure":employee_salary_structure.name,
				"salary_dispensed": salary_dispensed[0].name,
				"earnings": employee_salary_structure.earnings,
				"deductions": employee_salary_structure.deductions
			})
			ss = frappe.get_doc(args)
			ss.insert()
			count+=1
			if publish_progress:
				frappe.publish_progress(count*100/len(set(employees) - set(salary_slips_exists_for)),
					title = _("Creating Salary Slips..."))

	payroll_entry = frappe.get_doc("Payroll Entry", args.payroll_entry)
	payroll_entry.db_set("salary_slips_created", 1)
	payroll_entry.submit()
	payroll_entry.notify_update()
	
def get_existing_salary_slips(employees, args):
	return frappe.db.sql_list("""
		select distinct employee from `tabSalary Slip`
		where docstatus!= 2 and company = %s
			and start_date >= %s and end_date <= %s
			and employee in (%s)
	""" % ('%s', '%s', '%s', ', '.join(['%s']*len(employees))),
		[args.company, args.start_date, args.end_date] + employees)
def get_salary_structure(emp):
	doc = frappe.db.sql(""" select salary_structure from `tabSalary Structure Assignment` where employee = %s order by name DESC limit 1""",emp, as_dict=1)[0].salary_structure
	#print "doc------------",doc
	struct_doc = frappe.get_doc("Salary Structure", doc)
	return struct_doc

def get_salary_dispensed(emp):
	
	doc = frappe.db.sql("""select sd.name , ed.percentage from `tabPercentages Salary Dispensed` sd , `tabEmployee Dispensed` ed where ed.employee = %s and sd.name = ed.parent and sd.is_default = 1 and sd.docstatus =1 """,emp, as_dict=1)
	if len(doc) == 0:
		frappe.throw("Percentages Salary Dispensed is not created for this "+emp )
	else:
		return doc
def make_is_default(data, details):
	#print "details-----------",details
	#frappe.db.set_value("Salary Despensed", data.name, "is_default" , 1)
	doc = frappe.db.sql("""select name from `tabPercentages Salary Dispensed` where is_default =1""", as_dict=1)
	for sal in doc:
		if sal.name != data.name:
			frappe.db.set_value("Percentages Salary Dispensed", sal.name, "is_default" , 0)

def on_cancel_is_default(data, details):
	frappe.db.set_value("Percentages Salary Dispensed", data.name, "is_default" , 0)
	doc = frappe.db.sql(""" select name from `tabPercentages Salary Dispensed` where docstatus =1  order by name DESC limit 1""",as_dict=1)[0].name
	frappe.db.set_value("Percentages Salary Dispensed", doc, "is_default" , 1)

def submit_salary_slips(name):
	doc = frappe.get_doc("Payroll Entry", name)
	doc.check_permission('write')
	ss_list = get_sal_slip_list(doc,ss_status=0)
	if len(ss_list) > 30:
		frappe.enqueue(submit_salary_slips_for_employees, timeout=600, payroll_entry=doc, salary_slips=ss_list)
	else:
		submit_salary_slips_for_employees(doc, ss_list, publish_progress=False)

def get_sal_slip_list(doc, ss_status, as_dict=False):
		"""
			Returns list of salary slips based on selected criteria
		"""
		cond = doc.get_filter_condition()

		ss_list = frappe.db.sql("""
			select t1.name, t1.salary_structure from `tabSalary Slip` t1
			where t1.docstatus = %s and t1.start_date >= %s and t1.end_date <= %s
			and (t1.journal_entry is null or t1.journal_entry = "") and ifnull(salary_slip_based_on_timesheet,0) = %s %s
		""" % ('%s', '%s', '%s','%s', cond), (ss_status, doc.start_date, doc.end_date, doc.salary_slip_based_on_timesheet), as_dict=as_dict)
		return ss_list

def submit_salary_slips_for_employees(payroll_entry, salary_slips, publish_progress=True):
	submitted_ss = []
	not_submitted_ss = []
	frappe.flags.via_payroll_entry = True

	count = 0
	for ss in salary_slips:
		ss_obj = frappe.get_doc("Salary Slip",ss[0])
		if ss_obj.net_pay<0:
			not_submitted_ss.append(ss[0])
		else:
			try:
				ss_obj.submit()
				submitted_ss.append(ss_obj)
			except frappe.ValidationError:
				not_submitted_ss.append(ss[0])

		count += 1
		if publish_progress:
			frappe.publish_progress(count*100/len(salary_slips), title = _("Submitting Salary Slips..."))

	if submitted_ss:
		payroll_entry.make_accrual_jv_entry()
		frappe.msgprint(_("Salary Slip submitted for period from {0} to {1}")
			.format(ss_obj.start_date, ss_obj.end_date))

		payroll_entry.email_salary_slip(submitted_ss)

	payroll_entry.db_set("salary_slips_submitted", 1)
	payroll_entry.notify_update()

	if not submitted_ss and not not_submitted_ss:
		frappe.msgprint(_("No salary slip found to submit for the above selected criteria OR salary slip already submitted"))

	if not_submitted_ss:
		frappe.msgprint(_("Could not submit some Salary Slips"))

@frappe.whitelist()
def get_salary_dispensedes(salary_component):
	doc = frappe.get_doc("Salary Component", salary_component)
	if doc.use_correction_factor_as_per_percentage_salary_dispensed == 1:
		return True
	else:
		return False

