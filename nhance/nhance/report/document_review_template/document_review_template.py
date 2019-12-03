# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
import datetime
from datetime import date, timedelta
import calendar
from frappe import _, msgprint

def execute(filters=None):
	global columns
	global data
	columns, data = [], []
	month_filter = filters.get("document_type")
	doctype = filters.get("document_type")
	docIds = filters.get("docIds")
	doc_filter = filters.get("details")
	#print "doctype----",doctype
	#print "docids-----",docIds
	review_outcome = filters.get("review_outcome")
	if review_outcome == "Information/Read Only":
		if doctype is not None and docIds is not None:
			doc_details = frappe.get_doc(doctype, docIds)
			if doctype == "Sales Order":
				if doc_filter == "Parent":
					columns=get_columns_sales()
					name = doc_details.name
					supplier_name = doc_details.customer_name
					delivery_date = doc_details.delivery_date
					doc_type = doc_details.order_type
					creation_date = doc_details.transaction_date
					company = doc_details.company
					total_qty = doc_details.total_qty
					grand_total = doc_details.grand_total
					docstatus = doc_details.status
					data.append([name , supplier_name,doc_type,company,creation_date,creation_date,total_qty,
					grand_total,docstatus])
					
				elif doc_filter == "Items":
					columns=get_columns_sales_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_items = doc_details.items
					for items in sales_items:
						item_code = items.item_code
						item_name = items.item_name
						item_qty = items.qty
						stock_uom = items.stock_uom
						delivery_warehouse = items.warehouse
						rate = items.net_rate
						amount = items.net_amount
						delivery_date = items.delivery_date
						data.append([item_code,item_name,item_qty,stock_uom,rate,
						amount,delivery_warehouse,delivery_date])
				elif doc_filter == "Taxes and Charges":
					columns=get_columns_sales_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_taxes = doc_details.taxes
					if sales_taxes is not None:
						for taxes in sales_taxes:
							account_head = items.account_head
							charge_type = items.charge_type
							tax_amount = items.tax_amount
							rate = items.net_rate
							cost_center = items.cost_center
							data.append([account_head,charge_type,tax_amount,rate,
							cost_center])
			if doctype == "Purchase Order":
				if doc_filter == "Parent":
					columns=get_columns_purchase()
					#name =  frappe.db.sql("""select name from `tabSales Order` where amended_from = %s""",(docIds))
					name = doc_details.name
					supplier_name = doc_details.supplier_name
					schedule_date = doc_details.schedule_date
					#doc_type = doc_details.order_type
					transaction_date = doc_details.transaction_date
					company = doc_details.company
					docstatus = doc_details.status
					total_qty = doc_details.total_qty
					grand_total = doc_details.grand_total
					data.append([name , supplier_name,company,transaction_date,schedule_date,total_qty,
					grand_total,docstatus])
					
				elif doc_filter == "Items":
					columns=get_columns_purchase_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_items = doc_details.items
					for items in sales_items:
						item_code = items.item_code
						item_name = items.item_name
						item_qty = items.qty
						stock_uom = items.stock_uom
						delivery_warehouse = items.warehouse
						rate = items.net_rate
						amount = items.net_amount
						delivery_date = items.schedule_date
						data.append([item_code,item_name,item_qty,stock_uom,rate,
						amount,delivery_warehouse,delivery_date])
				elif doc_filter == "Taxes and Charges":
					columns=get_columns_sales_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_taxes = doc_details.taxes
					if sales_taxes is not None:
						for taxes in sales_taxes:
							account_head = items.account_head
							charge_type = items.charge_type
							tax_amount = items.tax_amount
							rate = items.net_rate
							cost_center = items.cost_center
							data.append([account_head,charge_type,tax_amount,rate,
							cost_center])
	elif review_outcome == "Accept/Reject/Enter New Value":
		if doctype is not None and docIds is not None:
			doc_details = frappe.get_doc(doctype, docIds)
			if doctype == "Sales Order":
				if doc_filter == "Parent":
					columns=get_columns_sales()
					#name =  frappe.db.sql("""select name from `tabSales Order` where amended_from = %s""",(docIds))
					name = doc_details.name
					supplier_name = doc_details.customer_name
					delivery_date = doc_details.delivery_date
					doc_type = doc_details.order_type
					creation_date = doc_details.transaction_date
					company = doc_details.company
					docstatus = doc_details.status
					total_qty = doc_details.total_qty
					grand_total = doc_details.grand_total
					data.append([name , supplier_name,doc_type,company,creation_date,delivery_date,total_qty,
					grand_total,docstatus])
					
				elif doc_filter == "Items":
					columns=get_columns_sales_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_items = doc_details.items
					for items in sales_items:
						item_code = items.item_code
						item_name = items.item_name
						item_qty = items.qty
						stock_uom = items.stock_uom
						delivery_warehouse = items.warehouse
						rate = items.net_rate
						amount = items.net_amount
						delivery_date = items.delivery_date
						data.append([item_code,item_name,item_qty,stock_uom,rate,
						amount,delivery_warehouse,delivery_date])
				elif doc_filter == "Taxes and Charges":
					columns=get_columns_sales_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_taxes = doc_details.taxes
					if sales_taxes is not None:
						for taxes in sales_taxes:
							account_head = items.account_head
							charge_type = items.charge_type
							tax_amount = items.tax_amount
							rate = items.net_rate
							cost_center = items.cost_center
							data.append([account_head,charge_type,tax_amount,rate,
							cost_center])
			if doctype == "Purchase Order":
				if doc_filter == "Parent":
					columns=get_columns_purchase()
					#name =  frappe.db.sql("""select name from `tabSales Order` where amended_from = %s""",(docIds))
					name = doc_details.name
					supplier_name = doc_details.supplier_name
					schedule_date = doc_details.schedule_date
					#doc_type = doc_details.order_type
					transaction_date = doc_details.transaction_date
					company = doc_details.company
					docstatus = doc_details.status
					total_qty = doc_details.total_qty
					grand_total = doc_details.grand_total
					data.append([name , supplier_name,company,transaction_date,schedule_date,total_qty,
					grand_total,docstatus])
					
				elif doc_filter == "Items":
					columns=get_columns_purchase_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_items = doc_details.items
					for items in sales_items:
						item_code = items.item_code
						item_name = items.item_name
						item_qty = items.qty
						stock_uom = items.stock_uom
						delivery_warehouse = items.warehouse
						rate = items.net_rate
						amount = items.net_amount
						delivery_date = items.schedule_date
						data.append([item_code,item_name,item_qty,stock_uom,rate,
						amount,delivery_warehouse,delivery_date])
				elif doc_filter == "Taxes and Charges":
					columns=get_columns_sales_items()
					#doc_details = frappe.get_doc(doctype, docIds)
					sales_taxes = doc_details.taxes
					if sales_taxes is not None:
						for taxes in sales_taxes:
							account_head = items.account_head
							charge_type = items.charge_type
							tax_amount = items.tax_amount
							rate = items.net_rate
							cost_center = items.cost_center
							data.append([account_head,charge_type,tax_amount,rate,
							cost_center])
	return columns, data



def get_columns_sales():
	return [
		_("Sales Order Number") + "::150", 
		_("Customer name ") + "::180",
		_("Order Type") + "::120",
		_("Company")+"::130",
		_("Creation Date") + "::150", 
		_("Delivery Date") + "::180",
		_("Total Quantity") + "::120",
		_("Grand Total (INR)")+"::130",
		_("Status")+"::130"
		
	]
def get_columns_purchase():
	return [
		_("Sales Order Number") + "::150", 
		_("Customer name ") + "::180",
		_("Company")+"::130",
		_("Creation Date") + "::150", 
		_("Schedule Date") + "::180",
		_("Total Quantity") + "::120",
		_("Grand Total (INR)")+"::130",
		_("Status")+"::130"
		
	]
def get_columns_sales_items():
	return [
		_("Item Code") + "::150", 
		_("Item Name") + "::180",
		_("Quantity") + "::120",
		_("Stock UOM")+"::130",
		_("Rate (INR)") + "::150", 
		_("Amount (INR)") + "::180",
		_("Delivery Warehouse") + "::120",
		_("Delivery Date")+"::130"
		
	]
def get_columns_purchase_items():
	return [
		_("Item Code") + "::150", 
		_("Item Name") + "::180",
		_("Quantity") + "::120",
		_("Stock UOM")+"::130",
		_("Rate (INR)") + "::150", 
		_("Amount (INR)") + "::180",
		_("Warehouse") + "::120",
		_("Schedule Date")+"::130"
		
	]
def get_columns_sales_taxes():
	return [
		_("Account Head") + "::150", 
		_("Charge Type") + "::180",
		_("Tax Amount") + "::120",
		_("Rate")+"::130",
		_("Cost Center") + "::150"
		
	]
@frappe.whitelist()
def cancel_doc(doctype,docIdss):
	stock_requisition = frappe.get_doc(doctype, docIdss)
	stock_requisition.cancel()
	frappe.msgprint("The doctype "+doctype +" and docId "+docIdss+" is cancelled successfully!!")
	return 1
@frappe.whitelist()
def date_details(doctype,docIdss):
	stock_requisition = ""
	if doctype == "Sales Order":
		stock_requisition =  frappe.db.get_value(doctype,docIdss,'delivery_date')
		#stock_requisition = frappe.get_doc(doctype, docIdss,"delivery_date")
		#date = stock_requisition.delivery_date
		#date = date.strftime('%d-%m-%Y')
		#print "stock_requisition-----------",stock_requisition.delivery_date
	elif doctype == "Purchase Order":
		stock_requisition =  frappe.db.get_value(doctype,docIdss,'schedule_date')
	return stock_requisition

@frappe.whitelist()
def cancel_and_amend_doc(doctype,docIdss,newdate):
	stock_requisition = frappe.get_doc(doctype, docIdss)
	#print "stock_requisition------------",stock_requisition
	#stock_requisition.cancel()
	#date = str(date).strftime('%Y-%m-%d')
	#print "date-----",newdate
	#date = datetime(date)
	#date = datetime.datetime.strptime(date,"%Y-%m-%d")
	#stock_requisition.delivery_date = date
	
	stock_requisition.cancel() 
	frappe.msgprint("The doctype "+doctype +" and docId "+docIdss+" is cancelled successfully!!")
	new_pr = frappe.copy_doc(stock_requisition) 
	new_pr.amended_from = stock_requisition.name 
	new_pr.status = "Draft" 
	new_pr.insert()
	#new_pr.delivery_date = ""
	#new_pr.delivery_date = newdate
	#print "new_doc--------",new_pr.delivery_date
	new_pr.save()
	sales_name = new_pr.name
	#print "name------------",sales_name
	new_pr.submit()
	frappe.msgprint(" Successfully created new Doc "+doctype+" as Amended "+sales_name+" !!")
	if doctype == "Sales Order":
		frappe.db.sql("""UPDATE `tabSales Order` SET delivery_date = '"""+str(newdate)+"""' where name = '"""+sales_name+"""'""")
		frappe.db.sql("""UPDATE `tabSales Order Item` SET delivery_date = '"""+str(newdate)+"""' where parent = '"""+sales_name+"""'""")
	elif doctype == "Purchase Order":
		frappe.db.sql("""UPDATE `tabPurchase Order` SET schedule_date = '"""+str(newdate)+"""' where name = '"""+sales_name+"""'""")
		frappe.db.sql("""UPDATE `tabPurchase Order Item` SET schedule_date = '"""+str(newdate)+"""' where parent = '"""+sales_name+"""'
		""")
	
	return sales_name

