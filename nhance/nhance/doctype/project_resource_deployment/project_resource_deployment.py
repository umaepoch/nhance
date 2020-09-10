# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProjectResourceDeployment(Document):
	def on_submit(self):
		self.manage_default_cocpf()

	def on_cancel(self):
		frappe.db.set(self, "is_default", 0)
		self.manage_default_cocpf()

	def on_update_after_submit(self):
		self.manage_default_cocpf()

	def manage_default_cocpf(self):
		""" Uncheck others if current one is selected as default,
		    update default bom in item master
		"""
		if self.is_default:
		    from frappe.model.utils import set_default
		    set_default(self, "project")
		   
		else:
		    frappe.db.set(self, "is_default", 0)


@frappe.whitelist()
def get_project_resource_plan(project):
	project_plans = frappe.db.sql("""select name from `tabProject Resource Plan`  where project = %s and docstatus =1 order by name desc limit 1 """,project, as_dict=1)
	if project_plans:
		project_plan = frappe.db.sql("""select * from  `tabSkills Needed` where parent = %s""",project_plans[0].name, as_dict=1)
		return project_plan

@frappe.whitelist()
def get_resource_and_skill(resource_deployed , skill_level):
	skills = skill_level.split("- ")
	check_resource = frappe.db.sql(""" select rm.resource from `tabResource Master` rm , `tabResource Child` rc where rm.resource =%s and rm.name = rc.parent and rc.skill =%s and rc.level =%s """,(resource_deployed,skills[0],skills[1] ), as_dict=1 )
	if len(check_resource) != 0:
		return True
	else:
		return False
@frappe.whitelist()
def get_resource_master(skill_level):
	skills = skill_level.split("-")
	#print "skills----------------",skills[0],skills[1]
	skill = skills[0].strip()
	level = skills[1].strip()
	#print "skills----------------",skill,level
	list_resource = frappe.db.sql("""select rm.resource from `tabResource Master` rm , `tabResource Child` rc where  rm.name = rc.parent and rc.skill =%s and rc.level =%s and rm.docstatus =1""",(skill,level ), as_dict=1)
	#print "list_resource----------------",list_resource
	return list_resource
