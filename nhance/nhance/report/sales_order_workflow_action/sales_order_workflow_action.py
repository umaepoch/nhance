# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint  #It is mandatory import to get the colums in report
from datetime import date,datetime
def execute(filters=None):
	start_date = filters.get("from_date")
	end_data = filters.get("to_date")
	status = filters.get("status")
	columns, data = [], []
	columns = get_columns()
	if status is None:
		sales_order = get_sales_order(start_date,end_data)
	if status:
		sales_order = get_sales_order_with_status(start_date,end_data,status)
	for sales in sales_order:
		posting_date = sales.creation
		posting_date = posting_date.strftime('%d-%m-%Y')
		#schedule_date = sales.schedule_date
		#schedule_date = schedule_date.strftime('%d-%m-%Y')
		data.append([sales.name,sales.customer,sales.workflow_state,posting_date,"",sales.grand_total])
	return columns, data


def get_columns():
	"""return columns"""
	columns = [
		_("Sales Order")+":Link/Sales Order:120",
		_("Customer Name")+"::120",
		_("Workflow State")+"::120",
		_("Posting Date")+"::120",
		_("Schedul Date")+"::120",
		_("Grand Total")+"::100"
		 ]
		
	return columns


def get_sales_order(start_date,end_data):
	start_date = str(start_date)+" 00:00:00:00"
	end_data = str(end_data)+" 23:59:59"
	
	sales = frappe.db.sql("""select * from `tabSales Order` where creation >= %s and creation <= %s""",(start_date,end_data), as_dict =1)

	return sales

@frappe.whitelist()
def sales_order_detials(start_date,end_date):
	sales = get_sales_order(start_date,end_date)
	return sales

def get_sales_order_with_status(start_date,end_data,status):
	start_date = str(start_date)+" 00:00:00:00"
	end_data = str(end_data)+" 23:59:59"
	
	sales = frappe.db.sql("""select * from `tabSales Order` where creation >= %s and creation <= %s and workflow_state = %s""",(start_date,end_data,status), as_dict =1)

	return sales

