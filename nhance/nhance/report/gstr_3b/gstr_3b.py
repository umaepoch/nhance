# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from datetime import datetime
import datetime
from datetime import date, timedelta

import calendar
import time
import math
import json
import ast
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def execute(filters=None):
	global summ_data
	global purchase_invoice_id 
	global end_date
	global columns
	global start_date
	start_date = ""
	columns = []
	summ_data = []
	end_date = ""
	purchase_invoice_id = ""
	columns, data = [], []
	company_address = ""
	company_gstin = ""
	current_year = ""
	current_month = ""
	current_date = ""
	month_filter = filters.get("month")
	month = month_filter.encode('utf8')
	short = datetime.datetime.strptime(month,'%B').strftime('%b')
	year_filter = filters.get("year")
	year =  year_filter.encode('utf8')
	year_con = int(year)
	abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
	months = abbr_to_num[short]
	date = datetime.date.today()
	start_date = datetime.datetime(year_con, months, 1)
	end_date = datetime.datetime(year_con, months, calendar.mdays[months])
	type_of_taxes = filters.get("type_of_taxes")
	if type_of_taxes == "Outward Supplies and inward supplies":
		columns=get_columns()
		total_net = 0.0
		igst_total = 0.0
		cgst_total = 0.0
		sgst_total = 0.0
		cess_total = 0.0
		purchase_invoice = purchase_invoice_details()
		for sales in purchase_invoice:
			net_total =sales.net_total
			total_net = total_net + net_total
			invoice_id = sales.name
			Puchase_atails = purchasse_taxes_and_details(invoice_id)
			for purchase in Puchase_atails:
				account_head = purchase.account_head
				if "IGST" in account_head:
					total = purchase.tax_amount
					igst_total = igst_total+total
				elif "CGST" in account_head:
					total = purchase.tax_amount
					cgst_total = cgst_total+total
				elif "SGST" in account_head:
					total = purchase.tax_amount
					sgst_total = sgst_total+total
				elif "CESS" in account_head:
					total = purchase.tax_amount
					cess_total = cess_total+total
	
		total_net_value = 0.0
		ex_cess_total = 0.0
		purchase_d = purchase_invoice_data()
		for data in purchase_d:
			net_total = data.net_total
			total_net_value = total_net_value +net_total
			invoice_id = data.name
			purchase_data = purchasse_taxes(invoice_id)
			for item in purchase_data:
				account_head = item.account_head
				if "CESS" in account_head:
					total = item.tax_amount
					ex_cess_total = ex_cess_total+total
		purchase_no_tax = not_taxes_charges()
		no_tax_total = 0.0
		nx_cess_total = 0.0
		for no_tax in purchase_no_tax:
			net_total = no_tax.net_total
			no_tax_total = no_tax_total +net_total
			name = no_tax.name
			no_taxes = no_taxes_gst(name)
			if no_taxes is not None:
				for no in no_taxes:
					account_head = no.account_head
					if "CESS" in account_head:
						total = no.tax_amount
						nx_cess_total = nx_cess_total+total
				
		reverse_net_total = 0.0
		tx_igst_total = 0.0
		tx_sgst_total = 0.0
		tx_cgst_total = 0.0
		tx_cess_total = 0.0
		reverse_charg = reverse_charges()
		for reverse in reverse_charg:
			net_total = reverse.net_total
			reverse_net_total = reverse_net_total + net_total
			invoice_id = reverse.name
			taxs_for = taxs_for_reverse(invoice_id)
			for taxs in taxs_for:
				account_head = taxs.account_head
				if "IGST" in account_head:
					total = taxs.tax_amount
					tx_igst_total = tx_igst_total+total
				elif "CGST" in account_head:
					total = taxs.tax_amount
					tx_cgst_total = tx_cgst_total+total
				elif "SGST" in account_head:
					total = taxs.tax_amount
					tx_sgst_total = tx_sgst_total+total
				elif "CESS" in account_head:
					total = taxs.tax_amount
					tx_cess_total = tx_cess_total+total
		p_revers = purchase_revers()
		reverse_total = 0.0
		rv_igst_total = 0.0
		rv_cgst_total = 0.0
		rv_sgst_total = 0.0
		rv_cess_total = 0.0
		for reverse in p_revers:
			net_total = reverse.net_total
			reverse_total = reverse_total + net_total
			name = reverse.name
			taxes = reverse_taxes_charges(name)
			for tax in taxes:
				account_head = tax.account_head
				if "IGST" in account_head:
					total = tax.tax_amount
					rv_igst_total = rv_igst_total+total
				elif "CGST" in account_head:
					total = tax.tax_amount
					rv_cgst_total = rv_cgst_total+total
				elif "SGST" in account_head:
					total = tax.tax_amount
					rv_sgst_total = rv_sgst_total+total
				elif "CESS" in account_head:
					total = tax.tax_amount
					rv_cess_total = tx_cess_total+total
		
		
		grand_total_net = total_net+reverse_total+reverse_net_total+no_tax_total+total_net_value
		grand_total_igst = igst_total+rv_igst_total+tx_igst_total+igst_total
		grand_total_cgst = cgst_total+rv_cgst_total+tx_cgst_total+cgst_total
		grand_total_sgst = sgst_total+rv_sgst_total+tx_sgst_total+sgst_total
		grand_total_cess = cess_total+rv_cess_total+tx_cess_total+cess_total
		summ_data.append([(" Outward Taxable  supplies\n(other than zero rated, nil rated and exempted)"), total_net , 				igst_total ,cgst_total ,sgst_total ,cess_total])

		summ_data.append([" Outward Taxable  supplies  (zero rated )",total_net_value, "0" , "0" , "0" ,ex_cess_total ])

	
		summ_data.append([" Other Outward Taxable  supplies (Nil rated, exempted)",no_tax_total, "0" , "0" , "0" ,nx_cess_total ])
	
		summ_data.append([" Inward supplies (liable to reverse charge) ",reverse_total,  rv_igst_total,rv_cgst_total,rv_sgst_total ,rv_cess_total,grand_total_cgst,grand_total_sgst,grand_total_cess])
	
	
		summ_data.append([" Non-GST Outward supplies",reverse_net_total, tx_igst_total,tx_cgst_total ,tx_sgst_total ,tx_cess_total])
		summ_data.append(["","",""])
		summ_data.append(["Total",grand_total_net,grand_total_igst,grand_total_cgst,grand_total_sgst,grand_total_cess])

	elif str(type_of_taxes) == "Eligible ITC":
		columns=get_columns1()
		purchase_detail = purchase_invoice_for()
		total_net = 0.0
		tx_igst_total = 0.0
		tx_cess_total = 0.0
		for purchase in purchase_detail:
			net_total = purchase.net_total
			total_net = total_net + net_total
			name = purchase.name
			purchase_tx = purchase_import(name)
			for tx in purchase_tx:
				account_head = tx.account_head
				if "IGST" in account_head:
					total = tx.tax_amount
					tx_igst_total = tx_igst_total+total
				elif "CESS" in account_head:
					total = tx.tax_amount
					tx_cess_total = tx_cess_total+total
		purchase_d = purchase_details_tx()
		sr_total = 0.0
		sr_igst_total = 0.0
		sr_cess_total = 0.0
		for purchase_data in purchase_d:
			net_total = purchase_data.net_total
			sr_total = sr_total + net_total
			name = purchase_data.name
			purchase_sr = purchase_import_sr(name)
			for service in purchase_sr:
				account_head = service.account_head
				if "IGST" in account_head:
					total = service.tax_amount
					sr_igst_total = sr_igst_total+total
				elif "CESS" in account_head:
					total = service.tax_amount
					sr_cess_total = sr_cess_total+total
		purchase_reverse = purchase_reverse_charge()
		reverse_total = 0.0
		rv_igst_total = 0.0
		rv_cgst_total = 0.0
		rv_sgst_total = 0.0
		rv_cess_total = 0.0
		for reverse in purchase_reverse:
			net_total = reverse.net_total
			reverse_total = reverse_total + net_total
			name = reverse.name
			purchase_rev = purchase_reverse_tx(name)
			for rev in purchase_rev:
				account_head = rev.account_head
				if "IGST" in account_head:
					total = rev.tax_amount
					rv_igst_total = rv_igst_total+total
				elif "CGST" in account_head:
					total = rev.tax_amount
					rv_cgst_total = rv_cgst_total+total
				elif "SGST" in account_head:
					total = rev.tax_amount
					rv_sgst_total = rv_sgst_total+total
				elif "CESS" in account_head:
					total = rev.tax_amount
					rv_cess_total = rv_cess_total+total
		no_compos_total = 0.0
		cm_igst_total = 0.0
		cm_cgst_total = 0.0
		cm_sgst_total = 0.0
		cm_cess_total = 0.0
		no_composit_dealer = purchase_not_composite()
		for no_compos in no_composit_dealer:
			net_total = no_compos.net_total
			no_compos_total = no_compos_total + net_total
			name = no_compos.name
			no_cmpos_item = no_composite(name)
			for item in no_cmpos_item:
				account_head = item.account_head
				if "IGST" in account_head:
					total = item.tax_amount
					cm_igst_total = cm_igst_total+total
				elif "CGST" in account_head:
					total = item.tax_amount
					cm_cgst_total = cm_cgst_total+total
				elif "SGST" in account_head:
					total = item.tax_amount
					cm_sgst_total = cm_sgst_total+total
				elif "CESS" in account_head:
					total = item.tax_amount
					cm_cess_total = cm_cess_total+total
		others_itc = other_itc()
		itc_net_total = 0.0
		cgst_itc_total = 0.0
		sgst_itc_total = 0.0
		igst_itc_total = 0.0
		itc_cess_total = 0.0
		for others in others_itc:
			invoice_id = others.name
			net_total = others.net_total
			itc_net_total = itc_net_total + net_total
			other_itc_tax = others_itc_taxs(invoice_id)
			for itc_tax in other_itc_tax:
				account_head = itc_tax.account_head
				if "CGST" in account_head:
					tax_amount = itc_tax.tax_amount
					cgst_itc_total = cgst_itc_total + tax_amount
				elif "SGST" in account_head:
					tax_amount = itc_tax.tax_amount
					sgst_itc_total = sgst_itc_total + tax_amount
				elif "IGST" in account_head:
					tax_amount = itc_tax.tax_amount
					igst_itc_total = igst_itc_total + tax_amount
				elif "CESS" in account_head:
					total = item.tax_amount
					itc_cess_total = itc_cess_total+total
		supplier_from_isd = supplier_isd()
		isd_net_total = 0.0
		cgst_isd_total = 0.0
		sgst_isd_total = 0.0
		igst_isd_total = 0.0
		cess_isd_total = 0.0
		for isd in supplier_from_isd:
			invoice_id = isd.name
			net_total = isd.net_total
			isd_net_total = isd_net_total + net_total
			tax_isd_details = isd_itc_taxs(invoice_id)
			#print "tax_isd_details----------",tax_isd_details
			for tax_isd in tax_isd_details:
				account_head = tax_isd.account_head
				if "CGST" in account_head:
					tax_amount = tax_isd.tax_amount
					cgst_isd_total = cgst_isd_total + tax_amount
				elif "SGST" in account_head:
					tax_amount = tax_isd.tax_amount
					sgst_isd_total = sgst_isd_total + tax_amount
				elif "IGST" in account_head:
					tax_amount = tax_isd.tax_amount
					igst_isd_total = igst_isd_total + tax_amount
				elif "CESS" in account_head:
					tax_amount = tax_isd.tax_amount
					cess_isd_total = cess_isd_total + tax_amount
		rule_gst = intrest_details()
		total_taxable_value = 0.0
		integrated_tax =0.0
		central_tax =0.0
		cess =0.0
		state_ut_tax = 0.0
		for rule in rule_gst:
			total_taxable_value = rule.taxable_value
			integrated_tax = rule.integrated_tax
			central_tax = rule.central_tax
			state_ut_tax = rule.state_ut_tax
			if rule.cess is not None:
				cess = rule.cess

		grand_total_value = float(total_taxable_value)+float(isd_net_total)+float(itc_net_total)+float(no_compos_total)+float(reverse_total)+float(sr_total+total_net)
		grand_total_igst = float(integrated_tax) + float(igst_isd_total) + float(igst_itc_total) + float(cm_igst_total) +float(rv_igst_total)+float(sr_igst_total)+float(tx_igst_total)
		grand_total_cgst = float(central_tax)+ float(cgst_isd_total) + float(cgst_itc_total) + float(cm_cgst_total) +float(rv_cgst_total) 
		grand_total_sgst = float(state_ut_tax) + float(sgst_isd_total) + float(sgst_itc_total) + float(cm_sgst_total) +float(rv_sgst_total)
		grand_total_cess = cess + cess_isd_total + itc_cess_total + cm_cess_total +rv_cess_total + sr_cess_total +tx_cess_total

		summ_data.append(["ITC Available (Whether in full or part)"])
		summ_data.append(["Import of goods ",total_net,tx_igst_total,0,0,tx_cess_total])
		summ_data.append([" Import of services ",sr_total,sr_igst_total,0,0,sr_cess_total])
		summ_data.append(["Inward supplies liable to reverse charge",reverse_total,rv_igst_total,rv_cgst_total,rv_sgst_total,rv_cess_total])
		summ_data.append([" Inward supplies from ISD",isd_net_total,igst_isd_total,cgst_isd_total,sgst_isd_total,cess_isd_total])
		summ_data.append([" All other ITC",itc_net_total,igst_itc_total,cgst_itc_total,sgst_itc_total,itc_cess_total])
		summ_data.append([" ITC Reversed","",""])
		summ_data.append(["As per Rule 42 & 43 of SGST/CGST rules",total_taxable_value,integrated_tax,central_tax,state_ut_tax,cess])
		summ_data.append(["Others",0,0,0,0])
		summ_data.append(["Net ITC Available ",grand_total_value,grand_total_igst,grand_total_cgst,grand_total_sgst,grand_total_cess])
		summ_data.append([" Ineligible ITC","",""])
		summ_data.append([" As per section 17(5) of CGST//SGST Act",no_compos_total,cm_igst_total,cm_cgst_total,cm_sgst_total,cm_cess_total])
		summ_data.append(["Others",0,0,0,0])
	
	elif type_of_taxes =="exempt, Nil-rated and non-GST":
		columns=get_columns2()
		gst_state_number = 0
		gst_state = 0
		inter_state = 0.0
		intra_state = 0.0
		purchase_details = purchase_invoice_tax()
		for invoice in purchase_details:
			supplier_address = invoice.supplier_address
			company_address = invoice.shipping_address
			address_details = address(supplier_address)
			company_name = shipping_address(company_address)
			for addr in address_details:
				gst_state = addr.gst_state_number
			for company in company_name:
				gst_state_number = company.gst_state_number
			if gst_state == gst_state_number:
				net_total = invoice.net_total
				intra_state = intra_state + net_total
			else:
				net_total = invoice.net_total
				inter_state = inter_state + net_total
		purchase_inv = purchase_detail_ex()
		gst_state_num = 0
		inter_total = 0.0
		intra_total = 0.0
		for invoice in purchase_inv:
			supplier_address = invoice.supplier_address
			addres = address_detail(supplier_address)
			for add in addres:
				gst_state_num = add.gst_state_number
			if gst_state_num == gst_state_number:
				net_total = invoice.net_total
				intra_total = intra_total + net_total
			else :
				net_total = invoice.net_total
				inter_total = inter_total + net_total
		grand_total_inter =0.0
		grand_total_intra = 0.0
		grand_total_inter = inter_total + inter_state
		grand_total_intra = intra_total + intra_state
		summ_data.append(["From a supplier under composition scheme, Exempt  and Nil rated supply",inter_state,intra_state])
		summ_data.append(["Non GST supply",inter_total,intra_total])
		summ_data.append(["Total",grand_total_inter,grand_total_intra])

	elif type_of_taxes == "Interest & late fee payable":
		columns=get_columns4()
		intrest = intrest_details()
		for int_details in intrest:
			integrated_tax = int_details.integrated_tax
			central_tax = int_details.central_tax
			state_ut_tax = int_details.state_ut_tax
			cess = int_details.cess
			summ_data.append(["Interest",integrated_tax,central_tax,state_ut_tax,cess])		

	elif type_of_taxes == "State Supplier Taxes":
		columns=get_columns3()
		invoice_id = ""
		invoice = sales_invoice()
		state = ""
		net_total = 0.0
		composit_amount = 0.0
		compo_tax_amount = 0.0
		uin_net_total = 0.0
		uin_tax_amount = 0.0
		tax_amount = 0.0
		customer_individual_net_total = 0.0
		customer_individual_tax_total = 0.0
		composite_net_total = 0.0
		composite_tax_total = 0.0
		customer_uin_net_total = 0.0
		customer_uin_tax_total = 0.0
		state_list = get_unique_state_list(invoice)
		if state_list is not None:
			for place in state_list:
				details = state_list[place]
				state = details.place_of_supply
				net_total = details.net_total
				customer_individual_net_total = customer_individual_net_total +net_total
				payment = sales_payment(state)
				payment_list = get_unique_tax_amount(payment)
				if payment_list is not None:
					for paymnt in payment_list:
						paymnet_data = payment_list[paymnt]
						tax_amount = paymnet_data.tax_amount
						customer_individual_tax_total = customer_individual_tax_total + tax_amount
				sale_composite = sale_invoice_composite(state)
		
				sales_amount = get_total_amount(sale_composite)
				if sales_amount is not None:
					for net_amount in sales_amount:
						net_detail = sales_amount[net_amount]
						composit_amount = net_detail.net_total
						composite_net_total = composite_net_total + composit_amount
				else:
					composit_amount = 0.0
					composite_net_total = composite_net_total + composit_amount
				composit_payment = payment_composite(state)
				comp_payment = get_tax_amount_com(composit_payment)
				if comp_payment is not None:
					for paym in comp_payment:
						paym_details = comp_payment[paym]
						compo_tax_amount = paym_details.tax_amount
						composite_tax_total = composite_tax_total +compo_tax_amount
				else: 
					compo_tax_amount = 0.0
					composite_tax_total = composite_tax_total +compo_tax_amount
				sales_uin = sales_uin_holder(state)
				sales_uin_net = get_uin_amount(sales_uin)
				if sales_uin_net is not None:
					for uin_d in sales_uin_net:
						uin_details = sales_uin_net[uin_d]
						uin_net_total = uin_details.net_total
						customer_uin_net_total = customer_uin_net_total+uin_net_total
				else:
					uin_net_total = 0.0
					customer_uin_net_total = customer_uin_net_total+uin_net_total
				payment_uin = payment_uin_holder(state)
				payment_uin_tax = get_tax_for_uin(payment_uin)
				if payment_uin_tax is not None:
					for uin in payment_uin_tax:
						uin_details = payment_uin_tax[uin]
						uin_tax_amount = uin_details.tax_amount
						customer_uin_tax_total = customer_uin_tax_total + uin_tax_amount
				else: 
					uin_tax_amount = 0.0
					customer_uin_tax_total = customer_uin_tax_total + uin_tax_amount
				summ_data.append([state,net_total,tax_amount,composit_amount,compo_tax_amount,uin_net_total,uin_tax_amount])
		summ_data.append(["","","","",""])
		summ_data.append(["Total",customer_individual_net_total,customer_individual_tax_total,composite_net_total,composite_tax_total,customer_uin_net_total,customer_uin_tax_total])
	return columns, summ_data


def purchase_invoice_details():
	sales_details = frappe.db.sql("""select name ,net_total from `tabPurchase Invoice` where invoice_type = 'Regular' AND posting_date >= %s AND posting_date <= %s AND docstatus=1 AND name IN (select parent from `tabPurchase Taxes and Charges` where account_head IN ('IGST - BBC','SGST - BBC','CGST - BBC'));""", (start_date, end_date), as_dict=1)
	return sales_details

def purchasse_taxes_and_details(id):

	sales_details = frappe.db.sql("""select parent,account_head,tax_amount from `tabPurchase Taxes and Charges` where parent = %s """, (id), as_dict=1)
	return sales_details

def purchase_invoice_data():
	sales_detail = frappe.db.sql("""select name ,net_total from `tabPurchase Invoice` where invoice_type IN('SEZ','Export','Deemed Export') AND posting_date >= %s AND posting_date <= %s AND docstatus=1;""", (start_date, end_date), as_dict=1)
	return sales_detail

def purchasse_taxes(ids):
	purchase_data = frappe.db.sql("""select parent,account_head,tax_amount from `tabPurchase Taxes and Charges` where parent = %s; """, (ids), as_dict=1)
	
	return purchase_data
def not_taxes_charges():
	taxes_charges = frappe.db.sql("""select name, net_total from `tabPurchase Invoice` where posting_date >= %s AND posting_date <= %s AND name NOT IN (select parent from `tabPurchase Taxes and Charges` where account_head IN ('IGST - BBC','SGST - BBC','CGST - BBC'));""",(start_date, end_date), as_dict=1)
	
	return taxes_charges

def no_taxes_gst(name):
	no_taxes_charges = frappe.db.sql("""select parent,account_head,tax_amount from `tabPurchase Taxes and Charges` where parent = %s; """, (name), as_dict=1)
	return no_taxes_charges

def reverse_charges():
	reverse_data = frappe.db.sql("""select name,net_total from `tabPurchase Invoice` where reverse_charge = 'Y' AND posting_date >= %s AND posting_date <= %s AND docstatus = 1;""", (start_date, end_date), as_dict=1)
	return reverse_data

def taxs_for_reverse(ids):
	taxes_for = frappe.db.sql("""select parent,account_head,tax_amount from `tabPurchase Taxes and Charges` where parent = %s; """, (ids), as_dict=1)
	return taxes_for
		
def purchase_revers():
	taxes_and_charge = frappe.db.sql("""select name, net_total from `tabPurchase Invoice` where reverse_charge = 'Y' AND posting_date >= %s AND posting_date <= %s;""", (start_date, end_date), as_dict=1)
	return taxes_and_charge

def reverse_taxes_charges(ids):
	taxs_charges = frappe.db.sql("""select parent,account_head,tax_amount from `tabPurchase Taxes and Charges` where parent = %s; """, (ids), as_dict=1)
	return taxs_charges
	
def get_columns():
	return [
		_("Nature of Supplies") + "::350", 
		_("Total Taxable value ") + "::180",
		_("Integrated Tax ") + "::120",
		_("Central Tax") + "::120", 
		_("State/UT Tax ") + "::120",
		_("Cess ") + "::120"
	]
'''
@frappe.whitelist()
def for_gstin():
	purchase_invoice = frappe.db.sql ("""select company_gstin from `tabPurchase Invoice""",as_dict = 1)
	
	return purchase_invoice
'''
def purchase_invoice_for():
	purchase_details = frappe.db.sql("""select name , net_total from `tabPurchase Invoice` where invoice_type = 'Import' AND eligibility_for_itc = 'input' AND posting_date >= %s AND posting_date <= %s""",(start_date, end_date), as_dict=1)
	return purchase_details

def  purchase_import(name):
	taxes = frappe.db.sql("""select account_head, tax_amount from `tabPurchase Taxes and Charges` where parent = %s""",(name),as_dict = 1)
	return taxes

def purchase_details_tx():
	purchase_detail = frappe.db.sql("""select name , net_total from `tabPurchase Invoice` where invoice_type = 'Import ' AND eligibility_for_itc = 'input service' AND posting_date >= %s AND posting_date <= %s""",(start_date, end_date), as_dict=1)
	return purchase_detail

def  purchase_import_sr(name):
	tax_serv = frappe.db.sql("""select account_head, tax_amount from `tabPurchase Taxes and Charges` where parent = %s""",(name),as_dict = 1)
	return tax_serv
def purchase_reverse_charge():
	reverse_charge = frappe.db.sql("""select name, net_total from `tabPurchase Invoice` where reverse_charge = 'Y' AND posting_date >= %s AND posting_date <= %s""",(start_date, end_date), as_dict=1)
	return reverse_charge

def purchase_reverse_tx(name):
	tax_servce = frappe.db.sql("""select account_head, tax_amount from `tabPurchase Taxes and Charges` where parent = %s""",(name),as_dict = 1)
	return tax_servce

def purchase_not_composite():
	no_composite = frappe.db.sql(""" select pi.name, pi.net_total from `tabPurchase Invoice` pi , `tabSupplier` su where pi.supplier = su.supplier_name AND  pi.invoice_type = "Regular" AND pi.eligibility_for_itc = "ineligible" AND pi.posting_date >= %s AND pi.posting_date <= %s AND su.india_gst_supplier_status  NOT IN( "Composite Dealer")""",(start_date, end_date), as_dict=1)
	return no_composite

def no_composite(name):
	tax_servce = frappe.db.sql("""select account_head, tax_amount from `tabPurchase Taxes and Charges` where parent = %s""",(name),as_dict = 1)
	return tax_servce

def other_itc():
	other = frappe.db.sql(""" select net_total,name from `tabPurchase Invoice` where eligibility_for_itc IN ("ineligible","capital goods") AND posting_date >=%s AND posting_date <= %s AND docstatus = 1""",(start_date, end_date), as_dict = 1)
	return other

def others_itc_taxs(invoice_id):
	if invoice_id:
		other_tax_servce = frappe.db.sql("""select account_head, tax_amount from `tabPurchase Taxes and Charges` where parent = %s""",(invoice_id),as_dict = 1)
	return other_tax_servce
def supplier_isd():
	isd_supplier = frappe.db.sql("""select net_total,name from `tabPurchase Invoice` where eligibility_for_itc = "input service distributor" AND posting_date >= %s AND posting_date <= %s AND docstatus = 1""",(start_date, end_date), as_dict = 1)
	return isd_supplier

def isd_itc_taxs(invoice_id):
	if invoice_id:
		isd_tax_servce = frappe.db.sql("""select account_head, tax_amount from `tabPurchase Taxes and Charges` where parent = %s""",(invoice_id),as_dict = 1)
	return isd_tax_servce

def get_columns1():
	return [
		_("Details") + "::350", 
		_("Total Taxable value ") + "::180",
		_("Integrated Tax ") + "::120",
		_("Central Tax") + "::120", 
		_("State/UT Tax ") + "::120",
		_("Cess ") + "::120"
	]

def purchase_invoice_tax():
	purchase = frappe.db.sql("""select name,net_total,supplier_address,shipping_address,posting_date from `tabPurchase Invoice` where supplier IN (select name from `tabSupplier` where india_gst_supplier_status IN ("Composite Dealer","Exempt","Nil Rated")) AND invoice_type = "Regular"AND eligibility_for_itc = "ineligible" AND posting_date >= %s AND posting_date <= %s
""", (start_date, end_date), as_dict=1)
	
	return purchase
def address(supplier_address):
	addrs = frappe.db.sql("""select gst_state_number,name from `tabAddress` where name = %s""",(supplier_address), as_dict = 1)
	
	return addrs
	
def shipping_address(company_address):
	company = frappe.db.sql("""select gst_state_number,name from `tabAddress` where name = %s""",(company_address), as_dict = 1)
	
	return company
def purchase_detail_ex():
	purchase_de = frappe.db.sql("""select name,net_total,supplier_address from `tabPurchase Invoice` where supplier IN (select name from `tabSupplier` where india_gst_supplier_status IN ("Non-GST"))AND invoice_type = "Regular"AND eligibility_for_itc = "ineligible" AND posting_date >= %s AND posting_date <= %s
""", (start_date, end_date), as_dict=1)
	return purchase_de
def address_detail(supplier_address):
	add = frappe.db.sql("""select gst_state_number,name from `tabAddress` where name = %s""",(supplier_address), as_dict = 1)
	return add


def get_columns2():
	return [
		_("Nature of Supplies") + "::550", 
		_("Inter-State supplies ") + "::180",
		_("Intra-state supplies ") + "::120"
		
	]

def sales_invoice():
	invoices = frappe.db.sql("""select si.place_of_supply,si.customer_address,si.name,si.net_total,si.posting_date from `tabSales Invoice` si , `tabCustomer` c where si.customer = c.name AND si.posting_date >= %s AND si.posting_date <= %s AND c.customer_type = 'Individual'""",(start_date, end_date), as_dict = 1)
	return invoices
def sales_payment(state):
	payment = frappe.db.sql(""" select st.account_head,st.tax_amount,si.name,si.place_of_supply from `tabSales Invoice` si, `tabSales Taxes and Charges` st where si.name = st.parent AND si.place_of_supply = %s AND si.posting_date >= %s AND si.posting_date <= %s AND customer IN(select name from `tabCustomer` where customer_type = "Individual")  """,(state,start_date, end_date), as_dict = 1)
	return payment

def sale_invoice_composite(state):
	sales = frappe.db.sql ("""select name,place_of_supply,net_total from `tabSales Invoice` where customer IN(select name from `tabCustomer` where gst_status = "Composite Dealer") AND place_of_supply = %s AND posting_date >=%s AND posting_date <= %s""",(state,start_date, end_date), as_dict = 1)
	return sales

def payment_composite(state):
	payment_com = frappe.db.sql("""select st.account_head,st.tax_amount,si.name,si.place_of_supply from `tabSales Invoice` si, `tabSales Taxes and Charges` st where si.name = st.parent AND si.place_of_supply = %s AND si.posting_date >= %s AND si.posting_date <= %s AND customer IN(select name from `tabCustomer` where gst_status = "Composite Dealer") """,(state,start_date, end_date), as_dict = 1)
	return payment_com

def sales_uin_holder(state):
	uin_holder = frappe.db.sql("""select name,place_of_supply,net_total,customer,posting_date from `tabSales Invoice` where customer IN(select name from `tabCustomer` where gst_status = "UIN Holder") AND place_of_supply = %s AND posting_date >= %s AND posting_date <= %s""",(state,start_date, end_date), as_dict = 1)
	return uin_holder

def payment_uin_holder(state):
	payment_uin = frappe.db.sql("""select st.account_head,st.tax_amount,si.name,si.place_of_supply from `tabSales Invoice` si, `tabSales Taxes and Charges` st where si.name = st.parent AND si.place_of_supply = %s AND si.posting_date >= %s AND si.posting_date <= %s AND customer IN(select name from `tabCustomer` where gst_status = "UIN Holder") """,(state,start_date, end_date), as_dict = 1)
	return payment_uin

def get_unique_state_list(items_list):
	if len(items_list)!=0:
		items_state = {}
		for data in items_list:
			place_of_supply = data.place_of_supply
			net_total = data.net_total
			key = place_of_supply
			if key in items_state:
				item_entry = items_state[key]
				qty_temp = item_entry["net_total"]
				item_entry["net_total"] = (qty_temp) + (net_total)

			else:
				items_state[key] = frappe._dict({
						"place_of_supply": place_of_supply, 
						"net_total": net_total, 
						})
		return items_state
def get_unique_tax_amount(payment):
	if len(payment)!=0:
		payment_tax = {}
		for data in payment:
			place_of_supply = data.place_of_supply
			tax_amount = data.tax_amount
			key = place_of_supply
			if key in payment_tax:
				item_entry = payment_tax[key]
				qty_temp = item_entry["tax_amount"]
				item_entry["tax_amount"] = (qty_temp) + (tax_amount)

			else:
				payment_tax[key] = frappe._dict({
						"place_of_supply": place_of_supply, 
						"tax_amount": tax_amount, 
						})
		
		return payment_tax

def get_total_amount(sale_composite):
	if len(sale_composite)!=0:
		composite_map = {}
		for data in sale_composite:
			place_of_supply = data.place_of_supply
			net_total = data.net_total
			key = place_of_supply
			if key in composite_map:
				item_entry = composite_map[key]
				qty_temp = item_entry["net_total"]
				item_entry["net_total"] = (qty_temp) + (net_total)

			else:
				composite_map[key] = frappe._dict({
						"place_of_supply": place_of_supply, 
						"net_total": net_total, 
						})
		return composite_map

def get_tax_amount_com(composit_payment):
	if len(composit_payment)!=0:
		composite_tax = {}
		for data in composit_payment:
			place_of_supply = data.place_of_supply
			tax_amount = data.tax_amount
			key = place_of_supply
			if key in composite_tax:
				item_entry = composite_tax[key]
				qty_temp = item_entry["tax_amount"]
				item_entry["tax_amount"] = (qty_temp) + (tax_amount)

			else:
				composite_tax[key] = frappe._dict({
						"place_of_supply": place_of_supply, 
						"tax_amount": tax_amount, 
						})
		
		return composite_tax

def get_uin_amount(sales_uin):
	if len(sales_uin)!=0:
		uin_map = {}
		for data in sales_uin:
			place_of_supply = data.place_of_supply
			net_total = data.net_total
			key = place_of_supply
			if key in uin_map:
				item_entry = uin_map[key]
				qty_temp = item_entry["net_total"]
				item_entry["net_total"] = (qty_temp) + (net_total)

			else:
				uin_map[key] = frappe._dict({
						"place_of_supply": place_of_supply, 
						"net_total": net_total, 
						})
		
		return uin_map

def get_tax_for_uin(payment_uin):
	if len(payment_uin)!=0:
		uin_tax_map = {}
		for data in payment_uin:
			place_of_supply = data.place_of_supply
			tax_amount = data.tax_amount
			key = place_of_supply
			if key in uin_tax_map:
				item_entry = uin_tax_map[key]
				qty_temp = item_entry["tax_amount"]
				item_entry["tax_amount"] = (qty_temp) + (tax_amount)

			else:
				uin_tax_map[key] = frappe._dict({
						"place_of_supply": place_of_supply, 
						"tax_amount": tax_amount, 
						})
		return uin_tax_map

def get_columns3():
	return [
		_("Place of Supply(State/UT)") + "::250",
		_("Taxable value(Unregistered Persons)") + "::250",
		_("Integrated Tax(Unregistered Persons) ") + "::250",
		_("Taxable value(Composition Persons)") + "::250",
		_("Integrated Tax(Composition Persons) ") + "::250",
		_("Total Taxable value(UIN holders)") + "::250",
		_("Integrated Tax(UIN holders) ") + "::230"
		
	]
def get_columns4():
	return [
		_("Description") + "::150", 
		_("Integrated Tax ") + "::120",
		_("Central Tax") + "::120", 
		_("State/UT Tax ") + "::120",
		_("Cess ") + "::120"
	]
def intrest_details():
	intrest_data = frappe.db.sql("""select taxable_value,integrated_tax,central_tax,state_ut_tax,cess from `tabGSTR 3B INTEREST AND RULES`""",as_dict = 1)
	return intrest_data
