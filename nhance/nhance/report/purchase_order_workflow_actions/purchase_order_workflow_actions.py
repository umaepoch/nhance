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

	purchase_order = get_purchase_order(start_date,end_data,status)
	for purchase in purchase_order:
		posting_date = purchase.creation
		posting_date = posting_date.strftime('%d-%m-%Y')
		schedule_date = purchase.schedule_date
		schedule_date = schedule_date.strftime('%d-%m-%Y')
		items_details = get_items_detials(purchase.name)
		tax_details = get_tax_detials(purchase.name)
		payment = get_payment_details(purchase.name)
		tax_amount = 0.0
		for tax in tax_details:
			tax_amount += tax.tax_amount
			tax_amount = round(tax_amount,2)
		data.append([posting_date,purchase.name,purchase.workflow_state,items_details[0].project,purchase.supplier,items_details[0].item_code,items_details[0].stock_qty,
		items_details[0].stock_uom,items_details[0].qty,items_details[0].uom,
		items_details[0].net_rate,items_details[0].net_amount,tax_amount,purchase.grand_total,payment[0].payment_term])
		total_net_amount = 0.0
		total_net_amount += items_details[0].net_amount
		for items in items_details:
				if items_details[0].item_code != items.item_code:
					data.append(["","","","","",items.item_code,items.stock_qty,items.stock_uom,items.qty,items.uom,items.net_rate,items.net_amount,"",""])
					total_net_amount += items.net_amount
		data.append(["Total","","","","","","","","","","",total_net_amount,tax_amount,purchase.grand_total])
	return columns, data


def get_columns():
	"""return columns"""
	columns = [
		_("Posting Date")+"::120",
		_("Purchase Order")+":Link/Purchase Order:120",
		_("Status")+"::120",
		_("Project")+"::120",
		_("Supplier")+"::120",
		_("Item Code")+"::120",
		_("Stock Qty")+"::120",
		_("Stock UOM")+"::120",
		_("Purchase Qty")+"::120",
		_("Purchase UOM")+"::120",
		_("Net Purchase Rate")+"::120",
		_("Total Net Value")+"::120",
		_("Total Tax")+"::120",
		_("Grand Total")+"::100",
		_("Payment Terms")+"::120"
		 ]
	return columns

def get_purchase_order(start_date,end_data,status):
	start_date = str(start_date)+" 00:00:00:00"
	end_data = str(end_data)+" 23:59:59"

	purchase = frappe.db.sql("""select * from `tabPurchase Order` where creation >= %s and creation <= %s and workflow_state = %s""",(start_date,end_data,status), as_dict =1)

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
	for purchase in eval(purchase_name):
		status = purchase['status']
	workflow = frappe.db.sql("""select * from `tabWorkflow Transition` where state = %s""",status, as_dict =1)
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
	flag = 0
	now = datetime.now()

	#print "now =", now
	# dd/mm/YY H:M:S
	dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
	for purchase in eval(purchase_name):
		current_status = purchase['status']
		current_purchase_name = purchase['name']
		get_next_state = frappe.db.sql("""select next_state from `tabWorkflow Transition` where state = %s and action = %s""",(current_status,action),as_dict =1)
		next_state = get_next_state[0].next_state
		get_doc_status = frappe.db.sql("""select doc_status from `tabWorkflow Document State` where state = %s""",get_next_state[0].next_state, as_dict=1)
		doc_status = get_doc_status[0].doc_status
		if str(doc_status) == "0":
			flag = 1
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
	return flag
def get_items_detials(name):
	items = frappe.db.sql("""select * from `tabPurchase Order Item` where parent = %s""",name,as_dict=1)
	return items
def get_tax_detials(name):
	taxes = frappe.db.sql("""select * from `tabPurchase Taxes and Charges` where parent = %s""",name, as_dict=1)
	return taxes
def get_payment_details(name):
	payment = frappe.db.sql("""select * from `tabPayment Schedule` where parent = %s""",name,as_dict=1)
	return payment
