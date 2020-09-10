# -*- coding: utf-8 -*-
# Copyright (c) 2020, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DailySiteReport(Document):
	pass

@frappe.whitelist()
def get_resource_master(project):
	
	list_resource = frappe.db.sql("""select rc.resource_deployed from `tabProject Resource Deployment` rm , `tabResource Requirement` rc where rm.project = %s and  rm.name = rc.parent and rm.docstatus =1 and rm.is_default=1""",(project), as_dict=1)
	#print "list_resource----------",list_resource
	return list_resource

@frappe.whitelist()
def get_skill_master(project,resource_deployed):
	list_resource = frappe.db.sql("""select rc.skill_level from `tabProject Resource Deployment` rm , `tabResource Requirement` rc where rm.project = %s and rc.resource_deployed = %s and  rm.name = rc.parent and rm.docstatus =1 and rm.is_default=1""",(project,resource_deployed), as_dict=1)
	skill = list_resource[0].skill_level
	skill = skill.split("-")
	skill = skill[0]
	return skill

@frappe.whitelist()
def get_skill_level_master(project,resource_deployed):
	list_resource = frappe.db.sql("""select rc.skill_level from `tabProject Resource Deployment` rm , `tabResource Requirement` rc where rm.project = %s and rc.resource_deployed = %s and  rm.name = rc.parent and rm.docstatus = 1 and rm.is_default =1""",(project,resource_deployed), as_dict=1)
	skill = list_resource[0].skill_level
	skill = skill.split("-")
	skill = skill[1]
	return skill
