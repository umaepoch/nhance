# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate
from frappe import _, msgprint
from datetime import datetime
import datetime
from datetime import date, timedelta
import calendar
import dateutil.parser
import time
import math
import json
import ast
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	columns, data = [], []
	from_date =""
	to_date =""
	if filters.fetch_days_data is not None:
		filters.from_date = filters.temp_from_date
		filters.to_date = filters.temp_to_date
	from_date = filters.from_date
	to_date = filters.to_date
	type_of_business = filters.get("type_of_business")
	if type_of_business == "B2B":
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_invoice_value = 0.0
		total_taxable_value = 0.0
		total_integrated_tax_paid = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid =0.0
		columns = get_columns_b2b()
		details_b2b = purchase_invoice_b2b(from_date,to_date)
		for b2b in details_b2b:
			india_gst_supplier_status = b2b.india_gst_supplier_status
			if india_gst_supplier_status != "Unregistered Dealer":
				purchase_invoice = b2b.name
				Purchase_gstin = b2b.supplier_gstin
				posting_date = b2b.posting_date
				posting_date = posting_date.strftime('%d-%m-%Y')
				place_of_supply = b2b.place_of_supply
				reverse_charge = b2b.reverse_charge
				invoice_type = b2b.invoice_type
				eligibility_for_itc = b2b.eligibility_for_itc
				itc_integrated_tax = b2b.itc_integrated_tax
				if itc_integrated_tax is not None:
					total_itc_integrated_tax += float(itc_integrated_tax)
				itc_central_tax = b2b.itc_central_tax
				itc_state_tax = b2b.itc_state_tax
				if itc_central_tax is not None:
					total_itc_central_tax = total_itc_central_tax+float(itc_central_tax)
					total_itc_state_tax = total_itc_state_tax+float(itc_state_tax)
				itc_cess_amount = b2b.itc_cess_amount
				if itc_cess_amount is not None:
					total_itc_cess_amount = total_itc_cess_amount+float(itc_cess_amount)
				supplier_address = b2b.supplier_address
				gst_state_number = ""
				state = ""
				gstin =""
				if supplier_address is not None:
					state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
					['state','gst_state_number','gstin'])
				net_total = 0.0
				tax_details = puchase_taxes(purchase_invoice)
				tax_rate = 0.0
				sgst_rate = 0.0
				cgst_rate = 0.0
				igst_rate= 0.0
				for tax in tax_details:
					account_head = tax.account_head
					charge_type = tax.charge_type
					if "On Net Total" in charge_type:
						net_total = b2b.net_total
					elif "On Previous Row Total" in charge_type:
						row_id = tax.row_id
						Previous_totla = previous_total_details(purchase_invoice,row_id)
						for previous in Previous_totla:
							net_total = previous.total
					if "SGST" in account_head:
						tax_rate = tax_rate + tax.rate
						sgst_rate = tax.rate
					elif "CGST" in account_head:
						tax_rate = tax_rate + tax.rate
						cgst_rate = tax.rate
					elif "IGST" in account_head:
						tax_rate = tax.rate
						igst_rate = tax.rate
				total_taxable_value +=net_total
				invoice_tax_value = net_total * tax_rate/100
				invoice_value = invoice_tax_value + net_total
				invoice_value = round(invoice_value,2)
				total_invoice_value += invoice_value
				integrated_tax_paid = net_total * igst_rate /100
				integrated_tax_paid = round(integrated_tax_paid,2)
				total_integrated_tax_paid += integrated_tax_paid
				central_tax_paid = net_total * cgst_rate /100
				central_tax_paid = round(central_tax_paid,2)
				state_tax_paid = net_total * sgst_rate /100
				state_tax_paid = round(state_tax_paid,2)
				total_central_tax_paid += central_tax_paid
				total_state_tax_paid += state_tax_paid
				data.append([gstin,purchase_invoice,posting_date,invoice_value,str(gst_state_number)+"-"+str(state),
						reverse_charge,invoice_type,tax_rate,net_total,integrated_tax_paid,central_tax_paid,
						state_tax_paid,"",eligibility_for_itc,itc_integrated_tax,itc_state_tax,itc_state_tax,
						itc_cess_amount])
		data.append(["","","","","","",""])
		data.append(["Total","","",total_invoice_value,"","","","",total_taxable_value,total_integrated_tax_paid,
			total_central_tax_paid,total_state_tax_paid,"","",total_itc_integrated_tax,total_itc_central_tax,total_itc_state_tax,
			total_itc_cess_amount])
	elif type_of_business == "B2BUR":
		columns = get_columns_b2bur()
		b2bur_details = purchase_invoice_bebur(from_date,to_date)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for b2b in b2bur_details:
			purchase_invoice = b2b.name
			Purchase_gstin = b2b.supplier_gstin
			posting_date = b2b.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			place_of_supply = b2b.place_of_supply
			reverse_charge = b2b.reverse_charge
			invoice_type = b2b.invoice_type
			eligibility_for_itc = b2b.eligibility_for_itc
			itc_integrated_tax = b2b.itc_integrated_tax
			if itc_integrated_tax is not None:
				total_itc_integrated_tax += float(itc_integrated_tax)
			itc_central_tax = b2b.itc_central_tax
			itc_state_tax = b2b.itc_state_tax
			if itc_central_tax is not None:
				total_itc_central_tax = total_itc_central_tax+float(itc_central_tax)
				total_itc_state_tax = total_itc_state_tax+float(itc_state_tax)
			itc_cess_amount = b2b.itc_cess_amount
			if itc_cess_amount is not None:
				total_itc_cess_amount = total_itc_cess_amount+float(itc_cess_amount)
			supplier_address = b2b.supplier_address
			company_name = b2b.company
			supplier_name = b2b.supplier_name
			supply_type = ""
			c_state = ""
			c_state_number = 0
			state =""
			gst_state_number =0
			gstin = ""
			if supplier_address is not None:
				state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
				['state','gst_state_number','gstin'])
				company_data = company_details(company_name)
				for company in company_data:
					c_state = company.state
					c_state_number = company.gst_state_number
				if state != c_state and gst_state_number != c_state_number:
					supply_type = "Inter State"
				elif  state == c_state and gst_state_number == c_state_number:
					supply_type = "Intra State"
			net_total = 0.0
			tax_details = puchase_taxes(purchase_invoice)
			tax_rate = 0.0
			sgst_rate = 0.0
			cgst_rate = 0.0
			igst_rate= 0.0
			for tax in tax_details:
				account_head = tax.account_head
				charge_type = tax.charge_type
				if "On Net Total" in charge_type:
					net_total = b2b.net_total
				elif "On Previous Row Total" in charge_type:
					row_id = tax.row_id
					Previous_totla = previous_total_details(purchase_invoice,row_id)
					for previous in Previous_totla:
						net_total = previous.total
				if "SGST" in account_head:
					tax_rate = tax_rate + tax.rate
					sgst_rate = tax.rate
				elif "CGST" in account_head:
					tax_rate = tax_rate + tax.rate
					cgst_rate = tax.rate
				elif "IGST" in account_head:
					tax_rate = tax.rate
					igst_rate = tax.rate
			invoice_tax_value = net_total * tax_rate/100
			invoice_value = invoice_tax_value + net_total
			invoice_value = round(invoice_value,2)
			integrated_tax_paid = net_total * igst_rate /100
			integrated_tax_paid = round(integrated_tax_paid,2)
			central_tax_paid = net_total * cgst_rate /100
			central_tax_paid = round(central_tax_paid,2)
			state_tax_paid = net_total * sgst_rate /100
			state_tax_paid = round(state_tax_paid,2)
			total_net_amount += net_total
			total_invoice_value += invoice_value
			total_integrated_tax_paid += integrated_tax_paid
			total_central_tax_paid += central_tax_paid
			total_state_tax_paid += state_tax_paid
			data.append([supplier_name,purchase_invoice,posting_date,invoice_value,str(gst_state_number)+"-"+str(state),supply_type,
					tax_rate,net_total,integrated_tax_paid,central_tax_paid,state_tax_paid,"",eligibility_for_itc,
					itc_integrated_tax,itc_state_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","","",""])
		data.append(["Total","","",total_invoice_value,"","","",total_net_amount,total_integrated_tax_paid,total_central_tax_paid,
				total_state_tax_paid,"","",total_itc_integrated_tax,total_itc_central_tax,total_itc_state_tax,
				total_itc_cess_amount])

	elif type_of_business == "IMPS":
		columns = get_columns_imps()
		imps_purchase = purchase_invoice_imps(from_date,to_date)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for b2b in imps_purchase:
			purchase_invoice = b2b.name
			posting_date = b2b.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			eligibility_for_itc = b2b.eligibility_for_itc
			itc_integrated_tax = b2b.itc_integrated_tax
			if itc_integrated_tax is not None:
				total_itc_integrated_tax += float(itc_integrated_tax)
			#itc_central_tax = b2b.itc_central_tax
			#itc_state_tax = b2b.itc_state_tax
			itc_cess_amount = b2b.itc_cess_amount
			if itc_cess_amount is not None:
				total_itc_cess_amount += float(itc_cess_amount)
			supplier_address = b2b.supplier_address
			company_name = b2b.company
			supplier_name = b2b.supplier_name
			state =""
			gst_state_number =0
			gstin = ""
			if supplier_address is not None:
				state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
				['state','gst_state_number','gstin'])
			net_total = 0.0
			tax_details = puchase_taxes(purchase_invoice)
			if len(tax_details) != 0:
				tax_rate = 0.0
				sgst_rate = 0.0
				cgst_rate = 0.0
				igst_rate= 0.0
				for tax in tax_details:
					account_head = tax.account_head
					charge_type = tax.charge_type
					if "On Net Total" in charge_type:
						net_total = b2b.net_total

					elif "On Previous Row Total" in charge_type:
						row_id = tax.row_id

						Previous_totla = previous_total_details(purchase_invoice,row_id)
						for previous in Previous_totla:
							net_total = previous.total
					if "SGST" in account_head:
						tax_rate = tax_rate + tax.rate
						sgst_rate = tax.rate
					elif "CGST" in account_head:
						tax_rate = tax_rate + tax.rate
						cgst_rate = tax.rate
					elif "IGST" in account_head:
						tax_rate = tax.rate
						igst_rate = tax.rate
				total_net_amount += net_total
				invoice_tax_value = net_total * tax_rate/100
				invoice_value = invoice_tax_value + net_total
				invoice_value = round(invoice_value,2)
				total_invoice_value += invoice_value
				integrated_tax_paid = net_total * igst_rate /100
				integrated_tax_paid = round(integrated_tax_paid,2)
				total_integrated_tax_paid += integrated_tax_paid
				central_tax_paid = net_total * cgst_rate /100
				central_tax_paid = round(central_tax_paid,2)
				total_central_tax_paid += central_tax_paid
				state_tax_paid = net_total * sgst_rate /100
				state_tax_paid = round(state_tax_paid,2)
				total_state_tax_paid += state_tax_paid
				data.append([purchase_invoice,posting_date,invoice_value,str(gst_state_number)+"-"+str(state),
						tax_rate,net_total,integrated_tax_paid,"",eligibility_for_itc,itc_integrated_tax,
						itc_cess_amount])
		data.append(["","","","","","",""])
		data.append(["Total","",total_invoice_value,"","",total_net_amount,total_integrated_tax_paid,"","",
				total_itc_integrated_tax,total_itc_cess_amount])


	elif type_of_business == "IMPG":
		columns = get_columns_impg()
		impg_purchase = purchase_invoice_impg(from_date,to_date)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for b2b in impg_purchase:
			purchase_invoice = b2b.name
			posting_date = b2b.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			eligibility_for_itc = b2b.eligibility_for_itc
			itc_integrated_tax = b2b.itc_integrated_tax
			if itc_integrated_tax is not None:
				total_itc_integrated_tax += float(itc_integrated_tax)
			#itc_central_tax = b2b.itc_central_tax
			#itc_state_tax = b2b.itc_state_tax
			itc_cess_amount = b2b.itc_cess_amount
			if itc_cess_amount is not None:
				total_itc_cess_amount += float(itc_cess_amount)
			supplier_address = b2b.supplier_address
			port_code = b2b.pch_port_code
			bill_of_entry_date = b2b.pch_bill_of_entry_date
			bill_of_entry_date = bill_of_entry_date.strftime('%d-%m-%Y')
			bill_of_entry_number = b2b.pch_bill_of_entry_number
			supplier_name = b2b.supplier_name
			invoice_type = b2b.invoice_type
			state = ""
			gst_state_number = 0
			gstin = ""
			if supplier_address is not None:
				state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
				['state','gst_state_number','gstin'])
			net_total = 0.0
			tax_details = puchase_taxes(purchase_invoice)
			if len(tax_details) != 0:
				tax_rate = 0.0
				sgst_rate = 0.0
				cgst_rate = 0.0
				igst_rate= 0.0
				for tax in tax_details:
					account_head = tax.account_head
					charge_type = tax.charge_type
					if "On Net Total" in charge_type:
						net_total = b2b.net_total
					elif "On Previous Row Total" in charge_type:
						row_id = tax.row_id
						Previous_totla = previous_total_details(purchase_invoice,row_id)
						for previous in Previous_totla:
							net_total = previous.total
					if "SGST" in account_head:
						tax_rate = tax_rate + tax.rate
						sgst_rate = tax.rate
					elif "CGST" in account_head:
						tax_rate = tax_rate + tax.rate
						cgst_rate = tax.rate
					elif "IGST" in account_head:
						tax_rate = tax.rate
						igst_rate = tax.rate
				total_net_amount += net_total
				invoice_tax_value = net_total * tax_rate/100
				invoice_value = invoice_tax_value + net_total
				invoice_value = round(invoice_value,2)
				total_invoice_value += invoice_value
				integrated_tax_paid = net_total * igst_rate /100
				integrated_tax_paid = round(integrated_tax_paid,2)
				total_integrated_tax_paid += integrated_tax_paid
				central_tax_paid = net_total * cgst_rate /100
				central_tax_paid = round(central_tax_paid,2)
				total_central_tax_paid += central_tax_paid
				state_tax_paid = net_total * sgst_rate /100
				state_tax_paid = round(state_tax_paid,2)
				total_state_tax_paid += state_tax_paid
				data.append([port_code,bill_of_entry_number,bill_of_entry_date,
						invoice_value,invoice_type,gstin,tax_rate,
						net_total,integrated_tax_paid,"",eligibility_for_itc,itc_integrated_tax,itc_cess_amount])
		data.append(["","","","","","",""])
		data.append(["Total","","",total_invoice_value,"","","",total_net_amount,total_integrated_tax_paid,"","",
				total_itc_integrated_tax,total_itc_cess_amount])

	elif type_of_business == "CDNR":
		columns = get_columns_cdnr()
		sdnr_purhcase = purchase_invoice_cdnr(from_date,to_date)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for b2b in sdnr_purhcase:
			india_gst_supplier_status = b2b.india_gst_supplier_status
			if india_gst_supplier_status != "Unregistered Dealer":
				purchase_invoice = b2b.name
				posting_date = b2b.posting_date
				eligibility_for_itc = b2b.eligibility_for_itc
				itc_integrated_tax = b2b.itc_integrated_tax
				if itc_integrated_tax is not None:
					total_itc_integrated_tax = total_itc_integrated_tax+float(itc_integrated_tax)
				itc_central_tax = b2b.itc_central_tax
				itc_state_tax = b2b.itc_state_tax
				if itc_central_tax is not None:
					total_itc_central_tax = total_itc_central_tax+float(itc_central_tax)
					total_itc_state_tax = total_itc_state_tax+float(itc_state_tax)
				itc_cess_amount = b2b.itc_cess_amount
				if itc_cess_amount is not None:
					total_itc_cess_amount = total_itc_cess_amount+float(itc_cess_amount)
				supplier_address = b2b.supplier_address
				port_code = b2b.pch_port_code
				bill_of_entry_date = b2b.pch_bill_of_entry_date
				bill_of_entry_number = b2b.pch_bill_of_entry_number
				supplier_name = b2b.supplier_name
				invoice_type = b2b.invoice_type
				reason_for_issuing_document = b2b.reason_for_issuing_document
				return_against = b2b.return_against
				company_name = b2b.company
				document_type = "C"
				return_posting_date = frappe.db.get_value("Purchase Invoice",return_against,"posting_date")
				return_posting_date = return_posting_date.strftime('%d-%m-%Y')
				c_state = ""
				c_state_number = 0
				state = ""
				gst_state_number = 0
				gstin = ""
				supply_type = ""
				#print "supplier_address----------",supplier_address
				if supplier_address is not None:
					state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
					['state','gst_state_number','gstin'])
					company_data = company_details(company_name)
					for company in company_data:
						c_state = company.state
						c_state_number = company.gst_state_number
					state = state.title()
					if state != c_state and gst_state_number != c_state_number:
						supply_type = "Inter State"
					elif  state == c_state and gst_state_number == c_state_number:
						supply_type = "Intra State"
				credit_invoice_id = ""
				credit_invoice_id = ""
				payment_date = ""
				creadit_return_date = ""
				payment_entry = get_Advance_Payment_details(purchase_invoice)
				if len(payment_entry) != 0:
					for payment in payment_entry:
						payment_number = payment.name
						payment_date = payment.posting_date
				else:
					payment_number = purchase_invoice
					payment_date = posting_date
				payment_date = payment_date.strftime('%d-%m-%Y')
				net_total = 0.0
				tax_details = puchase_taxes(purchase_invoice)
				if len(tax_details) != 0:
					tax_rate = 0.0
					sgst_rate = 0.0
					cgst_rate = 0.0
					igst_rate= 0.0
					for tax in tax_details:
						account_head = tax.account_head
						charge_type = tax.charge_type
						if "On Net Total" in charge_type:
							net_total = b2b.net_total

						elif "On Previous Row Total" in charge_type:
							row_id = tax.row_id

							Previous_totla = previous_total_details(purchase_invoice,row_id)
							for previous in Previous_totla:
								net_total = previous.total

						if "SGST" in account_head:
							tax_rate = tax_rate + tax.rate
							sgst_rate = tax.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + tax.rate
							cgst_rate = tax.rate
						elif "IGST" in account_head:
							tax_rate = tax.rate
							igst_rate = tax.rate
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					total_net_amount += net_total
					invoice_tax_value = net_total * tax_rate/100
					invoice_value = invoice_tax_value + net_total
					invoice_value = round(invoice_value,2)
					total_invoice_value += invoice_value
					integrated_tax_paid = net_total * igst_rate /100
					integrated_tax_paid = round(integrated_tax_paid,2)
					total_integrated_tax_paid += integrated_tax_paid
					central_tax_paid = net_total * cgst_rate /100
					central_tax_paid = round(central_tax_paid,2)
					total_central_tax_paid += central_tax_paid
					state_tax_paid = net_total * sgst_rate /100
					state_tax_paid = round(state_tax_paid,2)
					total_state_tax_paid += state_tax_paid
					data.append([gstin,return_against,return_posting_date,payment_number,payment_date,pre_gst,
					document_type,reason_for_issuing_document,supply_type,invoice_value,tax_rate,net_total,
					integrated_tax_paid,central_tax_paid,state_tax_paid,"",eligibility_for_itc,itc_integrated_tax
					,itc_central_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","",""])
		data.append(["Total","","","","","","","","",total_invoice_value,"",total_net_amount,
				total_integrated_tax_paid,total_central_tax_paid,total_state_tax_paid,"","",total_itc_integrated_tax,
				total_itc_central_tax,total_itc_state_tax,total_itc_cess_amount])

	elif type_of_business == "CDNUR":
		columns = get_columns_cdnur()
		sdnr_purhcase = purchase_invoice_cdnr(from_date,to_date)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for b2b in sdnr_purhcase:
			india_gst_supplier_status = b2b.india_gst_supplier_status
			if india_gst_supplier_status == "Unregistered Dealer":
				purchase_invoice = b2b.name
				posting_date = b2b.posting_date
				eligibility_for_itc = b2b.eligibility_for_itc
				itc_integrated_tax = b2b.itc_integrated_tax
				if itc_integrated_tax is not None:
					total_itc_integrated_tax = total_itc_integrated_tax+float(itc_integrated_tax)
				itc_central_tax = b2b.itc_central_tax
				if itc_central_tax is not None:
					total_itc_central_tax = total_itc_central_tax+float(itc_central_tax)
				itc_state_tax = b2b.itc_state_tax
				if itc_state_tax is not None:
					total_itc_state_tax = total_itc_state_tax+float(itc_state_tax)
				itc_cess_amount = b2b.itc_cess_amount
				if itc_cess_amount is not None:
					total_itc_cess_amount = total_itc_cess_amount+float(itc_cess_amount)
				supplier_address = b2b.supplier_address
				port_code = b2b.pch_port_code
				bill_of_entry_date = b2b.pch_bill_of_entry_date
				bill_of_entry_number = b2b.pch_bill_of_entry_number
				supplier_name = b2b.supplier_name
				invoice_type = b2b.invoice_type
				reason_for_issuing_document = b2b.reason_for_issuing_document
				return_against = b2b.return_against
				company_name = b2b.company
				document_type = "C"
				return_posting_date = frappe.db.get_value("Purchase Invoice",return_against,"posting_date")
				return_posting_date = return_posting_date.strftime('%d-%m-%Y')
				c_state = ""
				c_state_number = 0
				state = ""
				gst_state_number = 0
				gstin = ""
				supply_type = ""
				if supplier_address is not None:
					state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
					['state','gst_state_number','gstin'])
					company_data = company_details(company_name)
					for company in company_data:
						c_state = company.state
						c_state_number = company.gst_state_number
					state = state.title()
					if state != c_state and gst_state_number != c_state_number:
						supply_type = "Inter State"
					elif  state == c_state and gst_state_number == c_state_number:
						supply_type = "Intra State"

				credit_invoice_id = ""
				credit_invoice_id = ""
				payment_date = ""
				creadit_return_date = ""
				payment_entry = get_Advance_Payment_details(purchase_invoice)
				if len(payment_entry) != 0:
					for payment in payment_entry:
						payment_number = payment.name
						payment_date = payment.posting_date

				else:
					payment_number = purchase_invoice
					payment_date = posting_date
				payment_date = payment_date.strftime('%d-%m-%Y')
				net_total = 0.0
				tax_details = puchase_taxes(purchase_invoice)
				if len(tax_details) != 0:
					tax_rate = 0.0
					sgst_rate = 0.0
					cgst_rate = 0.0
					igst_rate= 0.0
					for tax in tax_details:
						account_head = tax.account_head
						charge_type = tax.charge_type
						if "On Net Total" in charge_type:
							net_total = b2b.net_total

						elif "On Previous Row Total" in charge_type:
							row_id = tax.row_id

							Previous_totla = previous_total_details(purchase_invoice,row_id)
							for previous in Previous_totla:
								net_total = previous.total
						if "SGST" in account_head:
							tax_rate = tax_rate + tax.rate
							sgst_rate = tax.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + tax.rate
							cgst_rate = tax.rate
						elif "IGST" in account_head:
							tax_rate = tax.rate
							igst_rate = tax.rate
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					total_net_amount += net_total
					invoice_tax_value = net_total * tax_rate/100
					invoice_value = invoice_tax_value + net_total
					total_invoice_value += invoice_value
					invoice_value = round(invoice_value,2)
					integrated_tax_paid = net_total * igst_rate /100
					integrated_tax_paid = round(integrated_tax_paid,2)
					total_integrated_tax_paid += integrated_tax_paid
					central_tax_paid = net_total * cgst_rate /100
					central_tax_paid = round(central_tax_paid,2)
					total_central_tax_paid += central_tax_paid
					state_tax_paid = net_total * sgst_rate /100
					state_tax_paid = round(state_tax_paid,2)
					total_state_tax_paid += state_tax_paid
					data.append([return_against,return_posting_date,payment_number,payment_date,pre_gst,
					document_type,reason_for_issuing_document,supply_type,invoice_value,tax_rate,net_total,
					integrated_tax_paid,central_tax_paid,state_tax_paid,"",eligibility_for_itc,itc_integrated_tax
					,itc_central_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","","","","","","","",""])
		data.append(["Total","","","","","","","",total_invoice_value,"",total_net_amount,total_integrated_tax_paid,
				total_central_tax_paid,total_state_tax_paid,"","",total_itc_integrated_tax,
				total_itc_central_tax,total_itc_state_tax])

	elif type_of_business == "AT":
		columns = get_columns_at()
		at_purchase = purchase_order_at(from_date,to_date)
		at_details = get_unique_state(at_purchase)
		total_taxable_value = 0.0
		total_invoice_value = 0.0
		for b2cs_data in at_details:
			b2cs_detail = at_details[b2cs_data]
			for b2cs_d in range(0,len(b2cs_detail["mapped_items"])):
				tax_rate = b2cs_detail["mapped_items"][b2cs_d]["tax_rate"]
				taxable_value = b2cs_detail["mapped_items"][b2cs_d]["allocated_amount"]
				total_taxable_value += taxable_value
				place_of_supply = b2cs_detail["mapped_items"][b2cs_d]["place_of_supply"]
				invoice_tax = taxable_value * tax_rate /100
				invoice_value = taxable_value + invoice_tax
				total_invoice_value += invoice_value
				data.append([place_of_supply,invoice_value,tax_rate,taxable_value,""])
		data.append(["","","","",""])
		data.append(["Total",total_invoice_value,"",total_taxable_value,""])

	elif type_of_business == "ATADJ":
		columns = get_columns_atadj()
		atadj_purchase = purchase_order_invoice_atadj(from_date,to_date)
		atadj_details = get_unique_atadj_state(atadj_purchase)
		total_taxable_value = 0.0
		total_invoice_value = 0.0
		for b2cs_data in atadj_details:
			b2cs_detail = atadj_details[b2cs_data]
			for b2cs_d in range(0,len(b2cs_detail["mapped_items"])):
				tax_rate = b2cs_detail["mapped_items"][b2cs_d]["tax_rate"]
				taxable_value = b2cs_detail["mapped_items"][b2cs_d]["allocated_amount"]
				total_taxable_value += taxable_value
				place_of_supply = b2cs_detail["mapped_items"][b2cs_d]["place_of_supply"]
				invoice_tax = taxable_value * tax_rate /100
				invoice_value = taxable_value + invoice_tax
				total_invoice_value += invoice_value
				data.append([place_of_supply,invoice_value,tax_rate,taxable_value,""])
		data.append(["","","","",""])
		data.append(["Total",total_invoice_value,"",total_taxable_value,""])

	elif type_of_business == "EXEMP":
		columns = get_columns_exemp()
		exemp_purchase = supplier_status(from_date,to_date)
		exempt_detail = sales_exepted_nill(exemp_purchase)
		grand_total_nill_net_amount = 0.0
		grand_total_non_net_amount =0.0
		grand_total_exempt_net_amount = 0.0
		grand_total_composition_net_amount = 0.0
		for exem in exempt_detail:
			exempt_details = exempt_detail[exem]
			supply_type = exempt_details.supply_type
			exempt_net_amount = exempt_details.exempt_net_amount
			grand_total_exempt_net_amount += exempt_net_amount
			nill_net_amount = exempt_details.nill_net_amount
			grand_total_nill_net_amount += nill_net_amount
			non_net_amount = exempt_details.non_net_amount
			grand_total_non_net_amount += non_net_amount
			composition_net_amount = exempt_details.composition_net_amount
			grand_total_composition_net_amount += composition_net_amount
			data.append([supply_type,composition_net_amount,nill_net_amount,exempt_net_amount,non_net_amount])
		data.append(["","","","",""])
		data.append(["Total",grand_total_composition_net_amount,grand_total_nill_net_amount,
				grand_total_exempt_net_amount,grand_total_non_net_amount])

	elif type_of_business == "ITCR":
		columns = get_columns_itcr()

	elif type_of_business == "HSNSUM":
		columns = get_columns_hsnsum()
		hsnsum_details = hsn_code_uqc_code(from_date,to_date)
		hsnsum_data = get_hsn_uqc_list(hsnsum_details)
		grand_total_value = 0.0
		grand_total_net_amount = 0.0
		grand_total_central = 0.0
		grand_total_integrated = 0.0
		grand_total_state = 0.0
		grand_total_cess = 0.0
		description = ""
		for unique_hsn in hsnsum_data:
			hsn_detials = hsnsum_data[unique_hsn]
			gst_hsn_code = hsn_detials.gst_hsn_code
			description_of_hsn = gst_hsn_doc(gst_hsn_code)
			for desc in description_of_hsn:
				if gst_hsn_code == desc.name:
					description =  desc.description
			uom = hsn_detials.uom
			uqc_details = gst_uqc_doc(uom)
			if uqc_details is not None:
				for uqc in uqc_details:
					uqc_code = uqc.uqc_code
					quantity = uqc.quantity
				uqc_name = uqc_code+"-"+quantity
			else:
				uqc_name = "OTH-OTHER"
			net_amount = hsn_detials.net_amount
			net_amount = round(net_amount,2)
			state_tax_amount = hsn_detials.state_tax_amount_total
			state_tax_amount = round(state_tax_amount,2)
			integrated_tax_amount = hsn_detials.integrated_tax_amount_total
			integrated_tax_amount = round(integrated_tax_amount,2)
			total_value_tax = net_amount*hsn_detials.tax_rate/100
			total_value = total_value_tax+net_amount
			total_value = round(total_value,2)
			grand_total_value = grand_total_value + total_value
			grand_total_net_amount = grand_total_net_amount + net_amount
			qty = hsn_detials.qty
			central_tax_amount = hsn_detials.central_tax_amount_total
			central_tax_amount = round(central_tax_amount,2)
			grand_total_central = grand_total_central + central_tax_amount
			grand_total_integrated = grand_total_integrated + integrated_tax_amount
			grand_total_state = grand_total_state + state_tax_amount
			data.append([gst_hsn_code,description,uqc_name,qty,total_value,
					net_amount,integrated_tax_amount,central_tax_amount,state_tax_amount])
		data.append(["","","","",""])
		data.append(["Total","","","",grand_total_value,grand_total_net_amount,grand_total_integrated,
				grand_total_central,grand_total_state])
	return columns, data

def get_columns_b2b():
	return [
		_("GSTIN of Supplier") + "::150",
		_("Invoice Number") + ":Link/Purchase Invoice:150",
		_("Invoice date") + "::150",
		_("Invoice Value") + ":Currency:150",
		_("Place Of Supply") + "::150",
		_("Reverse Charge") + "::180",
		_("Invoice Type") + "::150",
		_("Rate") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Paid") + ":Currency:150",
		_("Central Tax Paid") + ":Currency:150",
		_("State/UT Tax Paid") + ":Currency:150",
		_("Cess Paid") + ":Currency:160",
		_("Eligibility For ITC") + "::120",
		_("Availed ITC Integrated Tax") + ":Currency:150",
		_("Availed ITC Central Tax") + ":Currency:150",
		_("Availed ITC State/UT Tax") + ":Currency:160",
		_("Availed ITC Cess") + ":Currency:120"
	]
def get_columns_b2bur():
	return [
		_("Supplier Name") + "::150",
		_("Invoice Number") + ":Link/Purchase Invoice:150:150",
		_("Invoice date") + "::150",
		_("Invoice Value") + ":Currency:150",
		_("Place Of Supply") + "::150",
		_("Supply Type") + "::180",
		_("Rate") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Paid") + ":Currency:150",
		_("Central Tax Paid") + ":Currency:150",
		_("State/UT Tax Paid") + ":Currency:150",
		_("Cess Paid") + ":Currency:160",
		_("Eligibility For ITC") + "::120",
		_("Availed ITC Integrated Tax") + ":Currency:150",
		_("Availed ITC Central Tax") + ":Currency:150",
		_("Availed ITC State/UT Tax") + ":Currency:160",
		_("Availed ITC Cess") + ":Currency:120"
	]
def get_columns_imps():
	return [
		_("Invoice Number of Reg Recipient") + ":Link/Purchase Invoice:150",
		_("Invoice date") + "::150",
		_("Invoice Value") + ":Currency:150",
		_("Place Of Supply") + "::150",
		_("Rate") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Paid") + ":Currency:150",
		_("Cess Paid") + ":Currency:160",
		_("Eligibility For ITC") + "::120",
		_("Availed ITC Integrated Tax") + ":Currency:150",
		_("Availed ITC Cess") + ":Currency:120"
	]
def get_columns_impg():
	return [
		_("Port Code") + "::150",
		_("Bill Of Entry Number") + "::150",
		_("Bill Of Entry Date") + "::150",
		_("Bill Of Entry Value") + ":Currency:150",
		_("Document type") + "::180",
		_("GSTIN Of SEZ Supplier")+"::150",
		_("Rate") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Paid") + ":Currency:150",
		_("Cess Paid") + ":Currency:160",
		_("Eligibility For ITC") + "::120",
		_("Availed ITC Integrated Tax") + ":Currency:150",
		_("Availed ITC Cess") + ":Currency:120"
	]
def get_columns_cdnr():
	return [
		_("GSTIN of Supplier") + "::150",
		_("Note/Refund Voucher Number") + ":Link/Purchase Invoice:150",
		_("Note/Refund Voucher date") + "::150",
		_("Invoice/Advance Payment Voucher Number") + ":Link/Purchase Invoice:150",
		_("Invoice/Advance Payment Voucher date") + "::180",
		_("Pre GST")+"::150",
		_("Document Type") + "::150",
		_("Reason For Issuing document") + "::150",
		_("Supply Type") + "::180",
		_("Note/Refund Voucher Value")+":Currency:150",
		_("Rate") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Paid") + ":Currency:150",
		_("Central Tax Paid") + ":Currency:150",
		_("State/UT Tax Paid") + ":Currency:150",
		_("Cess Paid") + ":Currency:160",
		_("Eligibility For ITC") + "::120",
		_("Availed ITC Integrated Tax") + "::150",
		_("Availed ITC Central Tax") + ":Currency:150",
		_("Availed ITC State/UT Tax") + ":Currency:160",
		_("Availed ITC Cess") + ":Currency:120"
	]
def get_columns_cdnur():
	return [
		_("Note/Voucher Number") + ":Link/Purchase Invoice:150",
		_("Note/Voucher date") + "::150",
		_("Invoice/Advance Payment Voucher number") + ":Link/Purchase Invoice:150",
		_("Invoice/Advance Payment Voucher date") + "::150",
		_("Pre GST") + "::180",
		_("Document Type")+"::150",
		_("Reason For Issuing document") + "::150",
		_("Supply Type") + "::180",
		_("Note/Voucher Value")+":Currency:150",
		_("Rate") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Paid") + ":Currency:150",
		_("Central Tax Paid") + ":Currency:150",
		_("State/UT Tax Paid") + ":Currency:150",
		_("Cess Paid") + ":Currency:160",
		_("Eligibility For ITC") + "::120",
		_("Availed ITC Integrated Tax") + ":Currency:150",
		_("Availed ITC Central Tax") + ":Currency:150",
		_("Availed ITC State/UT Tax") + ":Currency:160",
		_("Availed ITC Cess") + ":Currency:120"
	]
def get_columns_at():
	return [
		_("Place Of Supply") + "::150",
		_("Invoice Value")+":Currency:120",
		_("Rate") + ":Currency:150",
		_("Gross Advance Paid") + ":Currency:150",
		_("Cess Amount") + "::150"
	]
def get_columns_atadj():
	return [
		_("Place Of Supply") + "::150",
		_("Invoice Value")+":Currency:120",
		_("Rate") + ":Currency:150",
		_("Gross Advance Paid to be adjusted") + ":Currency:150",
		_("Cess Amount") + ":Currency:150"
	]
def get_columns_exemp():
	return [
		_("Description") + "::150",
		_("Composition taxable person")+":Currency:150",
		_("Nil Rated Supplies") + ":Currency:150",
		_("Exempted (other than nil rated/non GST supply )") + ":Currency:180",
		_("Non-GST supplies") + ":Currency:150"
	]
def get_columns_itcr():
	return [
		_("Description for reversal of ITC") + "::150",
		_("To be added or reduced from output liability")+"::150",
		_("ITC Integrated Tax Amount") + "::150",
		_("ITC Central Tax Amount") + "::180",
		_("ITC State/UT Tax Amount") + "::150",
		_("ITC Cess Amount") + "::150"
	]
def get_columns_hsnsum():
	return [
		_("HSN") + "::150",
		_("Description")+"::150",
		_("UQC") + "::150",
		_("Total Quantity") + "::180",
		_("Total Value") + ":Currency:150",
		_("Taxable Value") + ":Currency:150",
		_("Integrated Tax Amount") + ":Currency:150",
		_("Central Tax Amount")+":Currency:150",
		_("State/UT Tax Amount") + ":Currency:150",
		_("Cess Amount") + ":Currency:180"
	]
def purchase_invoice_b2b(from_date,to_date):
	b2b_purchase = frappe.db.sql("""select
						pi.name,pi.supplier_gstin,pi.posting_date,pi.place_of_supply,pi.reverse_charge,
						pi.invoice_type,pi.net_total,pi.eligibility_for_itc,pi.itc_integrated_tax,pi.itc_central_tax,
						pi.itc_state_tax,pi.itc_cess_amount,s.india_gst_supplier_status,pi.supplier_address
				 	from `tabPurchase Invoice` pi, `tabSupplier` s
					where pi.supplier_name = s.name AND posting_date >= %s AND pi.posting_date <= %s
						AND pi.eligibility_for_itc NOT IN ("ineligible") AND pi.invoice_type = 'Regular'
						AND pi.docstatus =1 AND pi.is_return = 0""",
					(from_date,to_date), as_dict =1)
	return b2b_purchase
def puchase_taxes(purchase_invoice):
	purchase_tax = frappe.db.sql("""select
					account_head,rate,row_id,charge_type
					from `tabPurchase Taxes and Charges`
					where parent = %s
					order by idx""",
					(purchase_invoice), as_dict =1)
	return purchase_tax
def previous_total_details(purchase_invoice,row_id):
	previous = frappe.db.sql("""select
					idx,total
				from `tabPurchase Taxes and Charges`
				where idx = '"""+row_id+"""' AND parent = '"""+purchase_invoice+"""'""",
				as_dict =1)
	return previous
def purchase_invoice_bebur(from_date,to_date):
	b2bur_purhcase = frappe.db.sql("""select
						pi.name,pi.supplier_gstin,pi.posting_date,pi.place_of_supply,pi.reverse_charge,pi.invoice_type
						,pi.eligibility_for_itc,pi.itc_integrated_tax,pi.itc_central_tax,pi.itc_state_tax,
						pi.itc_cess_amount,pi.net_total,pi.supplier_address,pi.company,pi.supplier_name
					from `tabPurchase Invoice` pi, `tabSupplier` s
					where pi.supplier_name = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s
						AND pi.docstatus = 1 AND s.india_gst_supplier_status = 'Unregistered Dealer' AND
						pi.invoice_type = 'Regular' AND pi.docstatus =1 AND pi.is_return = 0""",
					(from_date,to_date), as_dict =1)
	return  b2bur_purhcase
def company_details(company_name):
	company_name = company_name + '%'
	company = frappe.db.sql("""select state,gst_state_number from `tabAddress` where name Like '"""+company_name+"""'""",as_dict=1)

	return company
def purchase_invoice_imps(from_date,to_date):
	imps_purchase = frappe.db.sql("""select
						pi.name,pi.posting_date,pi.supplier_address,pi.supplier_name,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.net_total,pi.itc_cess_amount
					from `tabPurchase Invoice` pi , `tabSupplier` s
					where pi.supplier_name = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s AND
						pi.invoice_type = 'Import - Service' AND pi.docstatus =1 AND pi.is_return = 0""",
					(from_date,to_date), as_dict =1)
	return imps_purchase
def purchase_invoice_impg(from_date,to_date):
	impg_purchase = frappe.db.sql("""select
						pi.name,pi.posting_date,pi.supplier_address,pi.supplier_name,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.net_total,pi.itc_cess_amount,pi.pch_port_code,
						pi.pch_bill_of_entry_date,pi.pch_bill_of_entry_number,pi.invoice_type
					from `tabPurchase Invoice` pi , `tabSupplier` s
					where pi.supplier_name = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s AND
						pi.invoice_type = 'Import - Goods' AND pi.docstatus =1 AND pi.is_return = 0""",
					(from_date,to_date), as_dict =1)
	return impg_purchase
def purchase_invoice_cdnr(from_date,to_date):
	cdnr_purchase = frappe.db.sql("""select
						pi.name,pi.posting_date,pi.supplier_address,pi.supplier_name,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.net_total,pi.itc_cess_amount,
						pi.pch_port_code,pi.pch_bill_of_entry_date
						,pi.pch_bill_of_entry_number,pi.invoice_type,s.india_gst_supplier_status,pi.return_against,
						pi.itc_central_tax,pi.itc_state_tax,pi.reason_for_issuing_document,pi.company
					from `tabPurchase Invoice` pi , `tabSupplier` s
					where pi.supplier_name = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s AND
						 pi.docstatus =1 AND pi.is_return = 1""",
					(from_date,to_date), as_dict =1)
	return cdnr_purchase
def get_Advance_Payment_details(invoice_id):
	payment_data = frappe.db.sql("""select pe.paid_amount,pe.name,pe.creation,pe.party_name,pe.posting_date
				 from `tabPayment Entry` pe , `tabPayment Entry Reference` per
				where pe.name = per.parent AND per.reference_name = %s""",(invoice_id),as_dict = 1)
	return payment_data
def purchase_order_at(from_date,to_date):
	temp_from_time = " 00:00:00"
	temp_to_time = " 23:59:59"
	tmp_from_date = str(from_date)+ (temp_from_time)
	tmp_to_date = str(to_date)+(temp_to_time)
	at_purchase = frappe.db.sql("""select
						po.name,po.supplier_address,per.reference_name,per.allocated_amount
					from `tabPurchase Order` po, `tabPayment Entry Reference` per , `tabPayment Entry` pe
					where po.name = per.reference_name AND pe.name = per.parent AND po.creation >= %s
						AND po.creation <=%s AND pe.docstatus =1 """,
					(tmp_from_date,tmp_to_date),as_dict =1)
	return at_purchase
def purchase_order_invoice_atadj(from_date,to_date):
	temp_from_time = " 00:00:00"
	temp_to_time = " 23:59:59"
	tmp_from_date = str(from_date)+ (temp_from_time)
	tmp_to_date = str(to_date)+(temp_to_time)
	atadj_purchase = frappe.db.sql("""select
						po.name as purchase_order,pi.name as purchase_invoice,pi.grand_total as
						invoice_total,po.grand_total as order_total,po.supplier_address,per.allocated_amount
					from `tabPurchase Order` po, `tabPurchase Invoice` pi, `tabPayment Entry Reference` per
					where po.name = pi.pch_purchase_order AND pi.name = per.reference_name AND po.creation >= %s AND
						 po.creation <= %s AND pi.docstatus =1""",
					(tmp_from_date,tmp_to_date), as_dict=1)
	return atadj_purchase
def supplier_status(from_date,to_date):
	status_purchase = frappe.db.sql("""select pi.name,pi.net_total,pi.supplier_address,s.india_gst_supplier_status,pi.company
						from `tabPurchase Invoice` pi, `tabSupplier` s
						where pi.supplier_name = s.name AND pi.docstatus =1 AND pi.posting_date >= %s
						AND pi.posting_date <= %s""",(from_date,to_date),as_dict=1)
	return status_purchase
def hsn_code_uqc_code(from_date,to_date):
	hsn_uqc = frappe.db.sql(""" select
					s.name,si.item_name,si.item_code,si.net_amount,si.uom,si.qty,si.gst_hsn_code
				from `tabPurchase Invoice` s, `tabPurchase Invoice Item` si
				where s.name = si.parent AND s.posting_date >= %s AND s.posting_date <= %s""",
					(from_date,to_date), as_dict = 1)
	return hsn_uqc
def sales_account_tax(invoice_id):
	if invoice_id:
		account_tax = frappe.db.sql("""select account_head,rate,item_wise_tax_detail,charge_type,row_id
						from `tabPurchase Taxes and Charges` where parent = %s """,(invoice_id),as_dict =1)
	return account_tax
def gst_uqc_doc(uom):
	uqc_doc = frappe.db.sql("""select uqc_code,quantity from `tabUQC Item` where erpnext_uom_link = %s""",(uom), as_dict = 1)
	return uqc_doc
def gst_hsn_doc(gst_hsn_code):
	hsn_doc = frappe.db.sql("""select name,description from `tabGST HSN Code` where  name = %s""",(gst_hsn_code), as_dict = 1)
	return hsn_doc

def get_unique_state(at_purchase):
	invoice_map = {}
	for at_data in at_purchase:
		purchase_order = at_data.name
		allocated_amount = at_data.allocated_amount
		supplier_address = at_data.supplier_address
		state = ""
		gst_state_number = 0
		gstin =""
		if supplier_address is not None:
			state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,['state','gst_state_number','gstin'])
		tax_details = puchase_taxes(purchase_order)
		place_of_supply = str(gst_state_number)+"-"+str(state)
		if len(tax_details) != 0:
			tax_rate = 0.0
			for tax in tax_details:
				account_head = tax.account_head
				if "SGST" in account_head:
					tax_rate = tax_rate + tax.rate
				elif "CGST" in account_head:
					tax_rate = tax_rate + tax.rate
				elif "IGST" in account_head:
					tax_rate = tax.rate
			tax_rate_list = []
			key = place_of_supply
			if key in invoice_map:
				item_entry = invoice_map[key]
				mapped_items_list = item_entry["mapped_items"]
				new_list = []
				for mapped_items in mapped_items_list:
			    		tax_rate_list.append(mapped_items["tax_rate"])
					data_rate = list(set(tax_rate_list))
				if tax_rate in data_rate:
				    	for items in mapped_items_list:
				   		if float(tax_rate) == float(items["tax_rate"]):
							amount_temp = items["allocated_amount"]
							items["allocated_amount"] = (amount_temp) + (allocated_amount)
				else :
					new_list.append({
							"tax_rate": tax_rate,
							"place_of_supply" : key,
							"allocated_amount":allocated_amount
							})
					item_entry["mapped_items"] = mapped_items_list + new_list
			else :
				item_list = []
				item_list.append({
						"tax_rate": tax_rate,
						"place_of_supply" : key,
						"allocated_amount":allocated_amount
						})
				invoice_map[key] = frappe._dict({
						   "mapped_items": item_list
						})

	return invoice_map

def get_unique_atadj_state(atadj_purchase):
	invoice_map = {}
	for at_data in atadj_purchase:
		invoice_total = at_data.invoice_total
		order_total = at_data.order_total
		if invoice_total < order_total:
			purchase_order = at_data.purchase_order
			purchase_invoice = at_data.purchase_invoice
			allocated_amount = at_data.allocated_amount
			supplier_address = at_data.supplier_address
			allocated_amount = at_data.allocated_amount
			state = ""
			gst_state_number = 0
			gstin =""
			if supplier_address is not None:
				state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,
				['state','gst_state_number','gstin'])
			tax_details = puchase_taxes(purchase_invoice)
			state = state.title()
			place_of_supply = str(gst_state_number)+"-"+str(state)
			if len(tax_details) != 0:
				tax_rate = 0.0
				for tax in tax_details:
					account_head = tax.account_head
					if "SGST" in account_head:
						tax_rate = tax_rate + tax.rate
					elif "CGST" in account_head:
						tax_rate = tax_rate + tax.rate
					elif "IGST" in account_head:
						tax_rate = tax.rate
				tax_rate_list = []
				key = place_of_supply
				if key in invoice_map:
					item_entry = invoice_map[key]
					mapped_items_list = item_entry["mapped_items"]
					new_list = []
					for mapped_items in mapped_items_list:
				    		tax_rate_list.append(mapped_items["tax_rate"])
						data_rate = list(set(tax_rate_list))
					if tax_rate in data_rate:
					    	for items in mapped_items_list:
					   		if float(tax_rate) == float(items["tax_rate"]):
								amount_temp = items["allocated_amount"]
								items["allocated_amount"] = (amount_temp) + (allocated_amount)
					else :
						new_list.append({
								"tax_rate": tax_rate,
								"place_of_supply" : key,
								"allocated_amount":allocated_amount
								})
						item_entry["mapped_items"] = mapped_items_list + new_list
				else :
					item_list = []
					item_list.append({
							"tax_rate": tax_rate,
							"place_of_supply" : key,
							"allocated_amount":allocated_amount
							})
					invoice_map[key] = frappe._dict({
							   "mapped_items": item_list
							})

	return invoice_map

def sales_exepted_nill(exemp_purchase):
	payment_tax = {}
	item_unieq_name1 = []
	item_unieq_name2 = []
	item_unieq_name3 = []
	item_unieq_name4 = []
	for exempt in exemp_purchase:
		supplier_address = exempt.supplier_address
		company_name = exempt.company
		supply_type = ""
		if supplier_address is not None:
			state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,['state','gst_state_number','gstin'])
			company_data = company_details(company_name)
			for company in company_data:
				c_state = company.state
				c_state_number = company.gst_state_number
			state = state.title()
			if state != c_state and gst_state_number != c_state_number:
				supply_type = "Inter-State Supplies"
			elif  state == c_state and gst_state_number == c_state_number:
				supply_type = "Intra-State Supplies"
			india_gst_supplier_status = exempt.india_gst_supplier_status
			if str(india_gst_supplier_status) == "Nil Rated":
				net_total = exempt.net_total
				exempt_net_amount = 0.0
				non_net_amount = 0.0
				composition_net_amount = 0.0
				key = supply_type
				if key in payment_tax:
					item_entry = payment_tax[key]
					item_unieq_name1.append(item_entry["supply_type"])
					uniue_name = list(set(item_unieq_name1))
					if supply_type in uniue_name:
						if supply_type == item_entry["supply_type"]:
							qty_temp = item_entry["nill_net_amount"]
							item_entry["nill_net_amount"] = (qty_temp) + (net_total)
					else:
						payment_tax[key] = frappe._dict({
							"supply_type": key,
							"nill_net_amount": net_total,
							"india_gst_supplier_status":india_gst_supplier_status,
							"non_net_amount":non_net_amount,
							"exempt_net_amount":exempt_net_amount,
							"composition_net_amount":composition_net_amount
							})
				else:
					payment_tax[key] = frappe._dict({
						"supply_type": key,
						"nill_net_amount": net_total,
						"india_gst_supplier_status":india_gst_supplier_status,
						"non_net_amount":non_net_amount,
						"exempt_net_amount":exempt_net_amount,
						"composition_net_amount":composition_net_amount
						})
			elif str(india_gst_supplier_status) == "Exempt":
				net_total = exempt.net_total
				non_net_amount = 0.0
				nill_net_amount = 0.0
				composition_net_amount = 0.0
				key = supply_type
				if key in payment_tax:
					item_entry = payment_tax[key]
					item_unieq_name2.append(item_entry["supply_type"])
					uniue_name = list(set(item_unieq_name2))
					if supply_type in uniue_name:
						if supply_type == item_entry["supply_type"]:
							qty_temp = item_entry["exempt_net_amount"]
							item_entry["exempt_net_amount"] = (qty_temp) + (net_total)
					else:
						payment_tax[key] = frappe._dict({
							"supply_type": key,
							"exempt_net_amount": net_total,
							"india_gst_supplier_status":india_gst_supplier_status,
							"non_net_amount":non_net_amount,
							"nill_net_amount":nill_net_amount,
							"composition_net_amount":composition_net_amount
							})
				else:
					payment_tax[key] = frappe._dict({
						"supply_type": key,
						"exempt_net_amount": net_total,
						"india_gst_supplier_status":india_gst_supplier_status,
						"non_net_amount":non_net_amount,
						"nill_net_amount":nill_net_amount,
						"composition_net_amount":composition_net_amount
						})

			elif str(india_gst_supplier_status) == "Non-GST":
				net_total = exempt.net_total
				exempt_net_amount = 0.0
				nill_net_amount = 0.0
				composition_net_amount = 0.0
				key = supply_type
				if key in payment_tax:
					item_entry = payment_tax[key]
					item_unieq_name3.append(item_entry["supply_type"])
					uniue_name = list(set(item_unieq_name3))
					if supply_type in uniue_name:
						if supply_type == item_entry["supply_type"]:
							qty_temp = item_entry["non_net_amount"]
							item_entry["non_net_amount"] = (qty_temp) + (net_total)
					else:
						payment_tax[key] = frappe._dict({
							"supply_type": key,
							"non_net_amount": net_total,
							"india_gst_supplier_status":india_gst_supplier_status,
							"exempt_net_amount":exempt_net_amount,
							"nill_net_amount":nill_net_amount,
							"composition_net_amount":composition_net_amount
							})
				else:
					payment_tax[key] = frappe._dict({
						"supply_type": key,
						"non_net_amount": net_total,
						"india_gst_supplier_status":india_gst_supplier_status,
						"exempt_net_amount":exempt_net_amount,
						"nill_net_amount":nill_net_amount,
						"composition_net_amount":composition_net_amount
						})
			elif str(india_gst_supplier_status) == "Composite Dealer":
				net_total = exempt.net_total
				exempt_net_amount = 0.0
				nill_net_amount = 0.0
				non_net_amount = 0.0
				key = supply_type
				if key in payment_tax:
					item_entry = payment_tax[key]
					item_unieq_name4.append(item_entry["supply_type"])
					uniue_name = list(set(item_unieq_name4))
					if supply_type in uniue_name:
						if supply_type == item_entry["supply_type"]:
							qty_temp = item_entry["composition_net_amount"]
							item_entry["composition_net_amount"] = (qty_temp) + (net_total)
					else:
						payment_tax[key] = frappe._dict({
							"supply_type": key,
							"non_net_amount": non_net_amount,
							"india_gst_supplier_status":india_gst_supplier_status,
							"exempt_net_amount":exempt_net_amount,
							"nill_net_amount":nill_net_amount,
							"composition_net_amount":net_total
							})
				else:
					payment_tax[key] = frappe._dict({
						"supply_type": key,
						"non_net_amount": non_net_amount,
						"india_gst_supplier_status":india_gst_supplier_status,
						"exempt_net_amount":exempt_net_amount,
						"nill_net_amount":nill_net_amount,
						"composition_net_amount":net_total
						})


	return payment_tax
def get_hsn_uqc_list(sales):
	invoice_map = {}
	item_tax_rate = 0.0
	total_value = 0.0
	integrated_tax_amount_total = 0.0
	central_tax_amount_total = 0.0
	state_tax_amount_total = 0.0
	total_integrated_tax_amount = 0.0
	total_central_tax_amount = 0.0
	total_state_tax_amount = 0.0
	for seles_data in sales:
		invoice_id = seles_data.name
		item_name = seles_data.itme_name
		item_code = seles_data.item_code
		net_amount = seles_data.net_amount
		gst_hsn_code = seles_data.gst_hsn_code
		uom = seles_data.uom
		qty = seles_data.qty
		#tax_data = sales_tax_hsn(item_code,invoice_id)
		sales_invoice_tax_data = sales_account_tax(invoice_id)
		#print "sales_invoice_tax_data-----------",sales_invoice_tax_data
		tax_rate_list = []
		if gst_hsn_code is not None:
			if len(sales_invoice_tax_data) != 0:
				integrated_tax_amount = 0.0
				central_tax_amount = 0.0
				state_tax_amount = 0.0
				for tax_data in sales_invoice_tax_data:
					#tax_rate = data.rate
					tax_type = tax_data.account_head
					key = gst_hsn_code
					if "SGST" in tax_type or "CGST" in tax_type:
						if  "SGST" in tax_type:
							state_tax_amount = net_amount * tax_data.rate/100
							item_tax_rate = item_tax_rate + tax_data.rate
						elif "CGST" in tax_type:
							central_tax_amount = net_amount * tax_data.rate/100
							item_tax_rate  = item_tax_rate + tax_data.rate
					elif "IGST" in tax_type:
						item_tax_rate = tax_data.rate
						integrated_tax_amount = net_amount * tax_data.rate/100
				if key in invoice_map:
				    	item_entry = invoice_map[key]
					qty_temp = item_entry["net_amount"]
					integrated_tmp = item_entry["integrated_tax_amount_total"]
					central_tmp = item_entry["central_tax_amount_total"]
					state_tmp = item_entry["state_tax_amount_total"]
					integrated_tmp = item_entry["integrated_tax_amount_total"]
					qty_count = item_entry["qty"]
					item_entry["net_amount"] = (qty_temp) + (net_amount)
					item_entry["qty"] = (qty_count) + (qty)
					item_entry["integrated_tax_amount_total"] = (integrated_tmp) + (integrated_tax_amount)
					item_entry["central_tax_amount_total"] = (central_tmp) + (central_tax_amount)
					item_entry["state_tax_amount_total"] = (state_tmp) + (state_tax_amount)
				else :

					invoice_map[key] = frappe._dict({
							"tax_rate": item_tax_rate,
							"net_amount": net_amount,
							"gst_hsn_code": key,
							"state_tax_amount_total":state_tax_amount,
							"central_tax_amount_total":central_tax_amount,
							"integrated_tax_amount_total":integrated_tax_amount,
							"uom":uom,
							"qty":qty,
							"item_code":item_code
							})
	return invoice_map
