# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from datetime import date,datetime
def execute(filters=None):
	start_date = filters.get("from_date")
	end_data = filters.get("to_date")
	status = filters.get("status")
	columns, data = [], []
	columns = get_columns()
	if status is None:
		purchase_order = get_purchase_order(start_date,end_data)
	if status:
		purchase_order = get_purchase_order_with_status(start_date,end_data,status)
	for purchase in purchase_order:
		posting_date = purchase.creation
		posting_date = posting_date.strftime('%d-%m-%Y')
		schedule_date = purchase.schedule_date
		schedule_date = schedule_date.strftime('%d-%m-%Y')
		data.append([purchase.name,purchase.supplier,purchase.workflow_state,posting_date,schedule_date,purchase.grand_total])
	return columns, data


def get_columns():
	"""return columns"""
	columns = [
		_("Purchase Order")+":Link/Purchase Order:120",
		_("Supplier Name")+"::120",
		_("Workflow State")+"::120",
		_("Posting Date")+"::120",
		_("Schedul Date")+"::120",
		_("Grand Total")+"::100"
		 ]
	return columns

def get_purchase_order(start_date,end_data):
	start_date = str(start_date)+" 00:00:00:00"
	end_data = str(end_data)+" 23:59:59"
	
	purchase = frappe.db.sql("""select * from `tabPurchase Order` where creation >= %s and creation <= %s""",(start_date,end_data), as_dict =1)

	return purchase

def get_purchase_order_with_status(start_date,end_data,status):
	start_date = str(start_date)+" 00:00:00:00"
	end_data = str(end_data)+" 23:59:59"
	
	purchase = frappe.db.sql("""select * from `tabPurchase Order` where creation >= %s and creation <= %s and workflow_state = %s""",(start_date,end_data,status), as_dict =1)

	return purchase

@frappe.whitelist()
def purchase_order_detials(start_date,end_date):
	purchase = get_purchase_order(start_date,end_date)
	return purchase

@frappe.whitelist()
def purchase_order_with_status(purchase_data):
	#with_status_details = eval(with_status_details)
	start_date = ""
	end_date = ""
	status = ""
	for status_with in eval(purchase_data):
		
		start_date = status_with['start_date']
		end_date = status_with['end_date']
		status = status_with['status']
	
	purchase = get_purchase_order_with_status(start_date,end_date,status)
	return purchase
@frappe.whitelist()
def workflow_details(purchase_name):
	status = ""
	#print "purchase_name--------------",eval(purchase_name)
	for purchase in eval(purchase_name):
		status = purchase['status']
	#print "status--------------------",status
	#name = frappe.db.get_value("Customer", {"name": ("like Purchase Order%")})
	#print "name---------",name
	name1=frappe.db.sql("""select name from  `tabWorkflow` where name='Purchase Order' and is_active =1""",as_dict =1)
	#print "name---------",name1
	name2 = name1[0].name
	#print "name2-----------------",name2
	name = "Purchase Order"
	workflow = frappe.db.sql("""select * from `tabWorkflow Transition` where state = %s and parent = %s """,(status,name2), as_dict =1)
	#role =  frappe.get_roles(frappe.session.user)
	#print "role-----------",role
	
	#print "workflow--------------",workflow
	return workflow

@frappe.whitelist()
def user_details(user,role):
	user_data = frappe.db.sql("""select role from `tabHas Role` where parent = '"""+user+"""' AND role =%s """,role,as_dict=1)
	if user_data is not None:
		return user_data
	else:
		return None

@frappe.whitelist()
def ready_to_update_workflow_state(action,purchase_name):
	#print "action------------",action
	flag = 0
	#print "purchase_name-------------",purchase_name
	now = datetime.now()
 
	#print "now =", now
	# dd/mm/YY H:M:S
	dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
	#print "date and time =--------------", dt_string
	name1=frappe.db.sql("""select name from  `tabWorkflow` where name='Purchase Order' and is_active =1""",as_dict =1)
	#print "name---------",name1
	name2 = name1[0].name	
	for purchase in eval(purchase_name):
		current_status = purchase['status']
		current_purchase_name = purchase['name']
		get_next_state = frappe.db.sql("""select next_state from `tabWorkflow Transition` where state = %s and action = %s and parent=%s""",(current_status,action,name2),as_dict =1)
		next_state = get_next_state[0].next_state
		get_doc_status = frappe.db.sql("""select doc_status from `tabWorkflow Document State` where state = %s and parent=%s""",(get_next_state[0].next_state,name2), as_dict=1)
		doc_status = get_doc_status[0].doc_status
		#print "doc_status -----------",str(doc_status)
		if str(doc_status) == "0":
			flag = 1
			#print "zero status--------------------"
			doc = frappe.get_doc("Purchase Order",current_purchase_name)
			
			update_statues = frappe.db.sql("""update `tabPurchase Order`  set workflow_state = %s , docstatus = %s, modified = %s where name = %s """, (next_state,doc_status,dt_string,current_purchase_name))
			update_status_items = frappe.db.sql("""update `tabPurchase Order Item`  set docstatus = %s , modified = %s where parent = %s """, (doc_status,dt_string,current_purchase_name))
		elif str(doc_status) == "1":
			flag = 1
			status = "To Receive and Bill"
			update_status = frappe.db.sql("""update `tabPurchase Order`  set workflow_state = %s , docstatus = %s, status = %s, modified = %s where name = %s """, (next_state,doc_status,status,dt_string,current_purchase_name))
			update_status_items = frappe.db.sql("""update `tabPurchase Order Item`  set docstatus = %s , modified = %s where parent = %s """, (doc_status,dt_string,current_purchase_name))
			#doc = frappe.get_doc("Purchase Order",current_purchase_name)
			#doc.update()
	#print "flag --------------",flag
	return flag
