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
		columns = get_columns_b2b()
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
	#	print "gst_hsn_code----------",gst_hsn_code
		total_invoice_value = 0.0
		total_taxable_value = 0.0
		total_integrated_tax_paid = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid =0.0
		b2b_purchase = purchase_invoice_b2b(from_date,to_date)
		b2b_item_vise = get_business_type_details(b2b_purchase)
		#print "b2b_item_vise-----------",b2b_item_vise
		for invoice_map_data in b2b_item_vise:
			map_data = b2b_item_vise[invoice_map_data]
			for map_d in range(0,len(map_data["mapped_items"])):
				india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
				if india_gst_supplier_status != "Unregistered Dealer":
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					tot_net_amount = round(tot_net_amount,2)
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					itc_state_tax = map_data["mapped_items"][map_d]["itc_state_tax"]
					reverse_charge = map_data["mapped_items"][map_d]["reverse_charge"]
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					eligibility_for_itc = map_data["mapped_items"][map_d]["eligibility_for_itc"]
					itc_integrated_tax = map_data["mapped_items"][map_d]["itc_integrated_tax"]
					itc_central_tax =map_data["mapped_items"][map_d]["itc_central_tax"]
					itc_cess_amount = map_data["mapped_items"][map_d]["itc_cess_amount"]
					igst_tax_rate = map_data["mapped_items"][map_d]["igst_tax_rate"]
					sgst_tax_rate = map_data["mapped_items"][map_d]["sgst_tax_rate"]
					cgst_tax_rate = map_data["mapped_items"][map_d]["cgst_tax_rate"]
					gstin = map_data["mapped_items"][map_d]["gstin"]
					supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
					supplier_invoice_no = map_data["mapped_items"][map_d]["supplier_invoice_no"]
					supplier_invoice_date = map_data["mapped_items"][map_d]["supplier_invoice_date"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					igst_tax_amount = tot_net_amount * igst_tax_rate /100
					sgst_tax_amount = tot_net_amount * sgst_tax_rate /100
					cgst_tax_amount = tot_net_amount * cgst_tax_rate /100
					igst_tax_amount = round(igst_tax_amount,2)
					sgst_tax_amount = round(sgst_tax_amount,2)
					cgst_tax_amount = round(cgst_tax_amount,2)
					total_integrated_tax_paid += igst_tax_amount
					total_central_tax_paid += cgst_tax_amount
					total_state_tax_paid += sgst_tax_amount
					total_taxable_value += tot_net_amount
					total_invoice_value += grand_total
					if itc_integrated_tax is not None:
						total_itc_integrated_tax += float(itc_integrated_tax)
					if itc_state_tax is not None:
						total_itc_state_tax += float(itc_state_tax)
						total_itc_central_tax += float(itc_central_tax)
					if itc_cess_amount is not None:
						total_itc_cess_amount += float(itc_cess_amount)
					data.append([gstin,invoice_no,posting_date,supplier_name,supplier_invoice_no,supplier_invoice_date,grand_total,place_of_supply,reverse_charge,invoice_type,
						rate_of_tax,tot_net_amount,igst_tax_amount,cgst_tax_amount,sgst_tax_amount
						,"",eligibility_for_itc,itc_integrated_tax,itc_central_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","","",""])
		data.append(["Total","","","","","",total_invoice_value,"","","","",total_taxable_value,total_integrated_tax_paid,
			total_central_tax_paid,total_state_tax_paid,"","",total_itc_integrated_tax,total_itc_central_tax,total_itc_state_tax,
			total_itc_cess_amount])
	elif type_of_business == "B2BUR":
		columns = get_columns_b2bur()
		b2bur_purchase = purchase_invoice_b2bur(from_date,to_date)
		b2bur_item_vise = get_business_type_details(b2bur_purchase)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for invoice_map_data in b2bur_item_vise:
			map_data = b2bur_item_vise[invoice_map_data]
			for map_d in range(0,len(map_data["mapped_items"])):
				invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
				rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
				tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
				tot_net_amount = round(tot_net_amount,2)
				place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
				itc_state_tax = map_data["mapped_items"][map_d]["itc_state_tax"]
				supply_type = map_data["mapped_items"][map_d]["supply_type"]
				supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
				posting_date = map_data["mapped_items"][map_d]["posting_date"]
				eligibility_for_itc = map_data["mapped_items"][map_d]["eligibility_for_itc"]
				itc_integrated_tax = map_data["mapped_items"][map_d]["itc_integrated_tax"]
				itc_central_tax =map_data["mapped_items"][map_d]["itc_central_tax"]
				itc_cess_amount = map_data["mapped_items"][map_d]["itc_cess_amount"]
				igst_tax_rate = map_data["mapped_items"][map_d]["igst_tax_rate"]
				sgst_tax_rate = map_data["mapped_items"][map_d]["sgst_tax_rate"]
				cgst_tax_rate = map_data["mapped_items"][map_d]["cgst_tax_rate"]
				india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
				gstin = map_data["mapped_items"][map_d]["gstin"]
				supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
				supplier_invoice_no = map_data["mapped_items"][map_d]["supplier_invoice_no"]
				supplier_invoice_date = map_data["mapped_items"][map_d]["supplier_invoice_date"]
				invoice_value = tot_net_amount * rate_of_tax /100
				grand_total = invoice_value + tot_net_amount
				igst_tax_amount = tot_net_amount * igst_tax_rate /100
				sgst_tax_amount = tot_net_amount * sgst_tax_rate /100
				cgst_tax_amount = tot_net_amount * cgst_tax_rate /100
				igst_tax_amount = round(igst_tax_amount,2)
				sgst_tax_amount = round(sgst_tax_amount,2)
				cgst_tax_amount = round(cgst_tax_amount,2)
				total_integrated_tax_paid += igst_tax_amount
				total_central_tax_paid += cgst_tax_amount
				total_state_tax_paid += sgst_tax_amount
				total_net_amount += tot_net_amount
				total_invoice_value += grand_total
				if itc_integrated_tax is not None:
					total_itc_integrated_tax += float(itc_integrated_tax)
				if itc_state_tax is not None:
					total_itc_state_tax += float(itc_state_tax)
					total_itc_central_tax += float(itc_central_tax)
				if itc_cess_amount is not None:
					total_itc_cess_amount += float(itc_cess_amount)
				data.append([supplier_name,invoice_no,posting_date,supplier_invoice_no,supplier_invoice_date,grand_total,place_of_supply,supply_type,
					rate_of_tax,tot_net_amount,igst_tax_amount,cgst_tax_amount,sgst_tax_amount
					,"",eligibility_for_itc,itc_integrated_tax,itc_central_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","","",""])
		data.append(["Total","","","","",total_invoice_value,"","","",total_net_amount,total_integrated_tax_paid,total_central_tax_paid,
				total_state_tax_paid,"","",total_itc_integrated_tax,total_itc_central_tax,total_itc_state_tax,
				total_itc_cess_amount])
	elif type_of_business == "IMPS":
		columns = get_columns_imps()
		imps_purchase = purchase_invoice_imps(from_date,to_date)
		imps_invoice = get_business_type_details(imps_purchase)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for invoice_map_data in imps_invoice:
			map_data = imps_invoice[invoice_map_data]
			for map_d in range(0,len(map_data["mapped_items"])):
				igst_tax_rate = map_data["mapped_items"][map_d]["igst_tax_rate"]
				if igst_tax_rate is not None:
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					tot_net_amount = round(tot_net_amount,2)
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					itc_state_tax = map_data["mapped_items"][map_d]["itc_state_tax"]
					supply_type = map_data["mapped_items"][map_d]["supply_type"]
					supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					eligibility_for_itc = map_data["mapped_items"][map_d]["eligibility_for_itc"]
					itc_integrated_tax = map_data["mapped_items"][map_d]["itc_integrated_tax"]
					itc_central_tax =map_data["mapped_items"][map_d]["itc_central_tax"]
					itc_cess_amount = map_data["mapped_items"][map_d]["itc_cess_amount"]
					sgst_tax_rate = map_data["mapped_items"][map_d]["sgst_tax_rate"]
					cgst_tax_rate = map_data["mapped_items"][map_d]["cgst_tax_rate"]
					india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
					gstin = map_data["mapped_items"][map_d]["gstin"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					igst_tax_amount = tot_net_amount * igst_tax_rate /100
					sgst_tax_amount = tot_net_amount * sgst_tax_rate /100
					cgst_tax_amount = tot_net_amount * cgst_tax_rate /100
					igst_tax_amount = round(igst_tax_amount,2)
					sgst_tax_amount = round(sgst_tax_amount,2)
					cgst_tax_amount = round(cgst_tax_amount,2)
					total_integrated_tax_paid += igst_tax_amount
					total_central_tax_paid += cgst_tax_amount
					total_state_tax_paid += sgst_tax_amount
					total_net_amount += tot_net_amount
					total_invoice_value += grand_total
					if itc_integrated_tax is not None:
						total_itc_integrated_tax += float(itc_integrated_tax)
					if itc_cess_amount is not None:
						total_itc_cess_amount += float(itc_cess_amount)
					data.append([invoice_no,posting_date,grand_total,place_of_supply,rate_of_tax,tot_net_amount,
							igst_tax_amount,"",eligibility_for_itc,itc_integrated_tax,itc_cess_amount])
		data.append(["","","","","",""])
		data.append(["Total","",total_invoice_value,"","",total_net_amount,
				total_integrated_tax_paid,"","",total_itc_integrated_tax,total_itc_cess_amount])
	elif type_of_business == "IMPG":
		columns = get_columns_impg()
		impg_purchase = purchase_invoice_impg(from_date,to_date)
		impg_invoice = get_business_type_details(impg_purchase)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for invoice_map_data in impg_invoice:
			map_data = impg_invoice[invoice_map_data]
			for map_d in range(0,len(map_data["mapped_items"])):
				igst_tax_rate = map_data["mapped_items"][map_d]["igst_tax_rate"]
				if igst_tax_rate is not None:
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					tot_net_amount = round(tot_net_amount,2)
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					itc_state_tax = map_data["mapped_items"][map_d]["itc_state_tax"]
					supply_type = map_data["mapped_items"][map_d]["supply_type"]
					supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					eligibility_for_itc = map_data["mapped_items"][map_d]["eligibility_for_itc"]
					itc_integrated_tax = map_data["mapped_items"][map_d]["itc_integrated_tax"]
					itc_central_tax =map_data["mapped_items"][map_d]["itc_central_tax"]
					itc_cess_amount = map_data["mapped_items"][map_d]["itc_cess_amount"]
					sgst_tax_rate = map_data["mapped_items"][map_d]["sgst_tax_rate"]
					cgst_tax_rate = map_data["mapped_items"][map_d]["cgst_tax_rate"]
					india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
					gstin = map_data["mapped_items"][map_d]["gstin"]
					port_code = map_data["mapped_items"][map_d]["port_code"]
					bill_of_entry_number = map_data["mapped_items"][map_d]["bill_of_entry_number"]
					bill_of_entry_date = map_data["mapped_items"][map_d]["bill_of_entry_date"]
					bill_of_entry_date = bill_of_entry_date.strftime('%d-%m-%Y')
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					igst_tax_amount = tot_net_amount * igst_tax_rate /100
					sgst_tax_amount = tot_net_amount * sgst_tax_rate /100
					cgst_tax_amount = tot_net_amount * cgst_tax_rate /100
					igst_tax_amount = round(igst_tax_amount,2)
					sgst_tax_amount = round(sgst_tax_amount,2)
					cgst_tax_amount = round(cgst_tax_amount,2)
					total_integrated_tax_paid += igst_tax_amount
					total_central_tax_paid += cgst_tax_amount
					total_state_tax_paid += sgst_tax_amount
					total_net_amount += tot_net_amount
					total_invoice_value += grand_total
					if itc_integrated_tax is not None:
						total_itc_integrated_tax += float(itc_integrated_tax)
					if itc_cess_amount is not None:
						total_itc_cess_amount += float(itc_cess_amount)
					data.append([port_code,bill_of_entry_number,bill_of_entry_date,grand_total,invoice_type,gstin,
							rate_of_tax,tot_net_amount,
							igst_tax_amount,"",eligibility_for_itc,itc_integrated_tax,itc_cess_amount])
		data.append(["","","","","",""])
		data.append(["Total","","",total_invoice_value,"","","",total_net_amount,
				total_integrated_tax_paid,"","",total_itc_integrated_tax,total_itc_cess_amount])
	elif type_of_business == "CDNR":
		columns = get_columns_cdnr()
		cdnr_invoice = purchase_invoice_cdnr(from_date,to_date)
		cdrn_purchase = get_business_type_details(cdnr_invoice)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for invoice_map_data in cdrn_purchase:
			map_data = cdrn_purchase[invoice_map_data]
			for map_d in range(0,len(map_data["mapped_items"])):
				igst_tax_rate = map_data["mapped_items"][map_d]["igst_tax_rate"]
				india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
				if india_gst_supplier_status != "Unregistered Dealer":
					document_type = "C"
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					tot_net_amount = round(tot_net_amount,2)
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					itc_state_tax = map_data["mapped_items"][map_d]["itc_state_tax"]
					supply_type = map_data["mapped_items"][map_d]["supply_type"]
					supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					eligibility_for_itc = map_data["mapped_items"][map_d]["eligibility_for_itc"]
					itc_integrated_tax = map_data["mapped_items"][map_d]["itc_integrated_tax"]
					itc_central_tax =map_data["mapped_items"][map_d]["itc_central_tax"]
					itc_cess_amount = map_data["mapped_items"][map_d]["itc_cess_amount"]
					sgst_tax_rate = map_data["mapped_items"][map_d]["sgst_tax_rate"]
					cgst_tax_rate = map_data["mapped_items"][map_d]["cgst_tax_rate"]
					india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
					gstin = map_data["mapped_items"][map_d]["gstin"]
					port_code = map_data["mapped_items"][map_d]["port_code"]
					bill_of_entry_number = map_data["mapped_items"][map_d]["bill_of_entry_number"]
					bill_of_entry_date = map_data["mapped_items"][map_d]["bill_of_entry_date"]
					return_against = map_data["mapped_items"][map_d]["return_against"]
					reason_for_issuing_document = map_data["mapped_items"][map_d]["reason_for_issuing_document"]
					return_posting_date = frappe.db.get_value("Purchase Invoice",return_against,"posting_date")
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					payment_entry = get_Advance_Payment_details(invoice_no)
					if len(payment_entry) != 0:
						for payment in payment_entry:
							payment_number = payment.name
							payment_date = payment.posting_date
					else:
						payment_number = invoice_no
						payment_date = posting_date
					#payment_date = payment_date.strftime('%d-%m-%Y')
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					return_posting_date = return_posting_date.strftime('%d-%m-%Y')
					#bill_of_entry_date = bill_of_entry_date.strftime('%d-%m-%Y')
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					igst_tax_amount = tot_net_amount * igst_tax_rate /100
					sgst_tax_amount = tot_net_amount * sgst_tax_rate /100
					cgst_tax_amount = tot_net_amount * cgst_tax_rate /100
					igst_tax_amount = round(igst_tax_amount,2)
					sgst_tax_amount = round(sgst_tax_amount,2)
					cgst_tax_amount = round(cgst_tax_amount,2)
					total_integrated_tax_paid += igst_tax_amount
					total_central_tax_paid += cgst_tax_amount
					total_state_tax_paid += sgst_tax_amount
					total_net_amount += tot_net_amount
					total_invoice_value += grand_total
					if itc_integrated_tax is not None:
						total_itc_integrated_tax += float(itc_integrated_tax)
					if itc_state_tax is not None:
						total_itc_state_tax += float(itc_state_tax)
						total_itc_central_tax += float(itc_central_tax)
					if itc_cess_amount is not None:
						total_itc_cess_amount += float(itc_cess_amount)
					data.append([gstin,return_against,return_posting_date,payment_number,payment_date,pre_gst,
					document_type,reason_for_issuing_document,supply_type,grand_total,rate_of_tax,tot_net_amount,
					igst_tax_amount,cgst_tax_amount,sgst_tax_amount,"",eligibility_for_itc,itc_integrated_tax
					,itc_central_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","",""])
		data.append(["Total","","","","","","","","",total_invoice_value,"",total_net_amount,
				total_integrated_tax_paid,total_central_tax_paid,total_state_tax_paid,"","",total_itc_integrated_tax,
				total_itc_central_tax,total_itc_state_tax,total_itc_cess_amount])
	elif type_of_business == "CDNUR":
		columns = get_columns_cdnur()
		cdnr_invoice = purchase_invoice_cdnr(from_date,to_date)
		cdrn_purchase = get_business_type_details(cdnr_invoice)
		total_itc_integrated_tax = 0.0
		total_itc_central_tax = 0.0
		total_itc_state_tax = 0.0
		total_itc_cess_amount = 0.0
		total_net_amount = 0.0
		total_invoice_value = 0.0
		total_central_tax_paid = 0.0
		total_state_tax_paid = 0.0
		total_integrated_tax_paid = 0.0
		for invoice_map_data in cdrn_purchase:
			map_data = cdrn_purchase[invoice_map_data]
			for map_d in range(0,len(map_data["mapped_items"])):
				igst_tax_rate = map_data["mapped_items"][map_d]["igst_tax_rate"]
				india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
				if india_gst_supplier_status == "Unregistered Dealer":
					document_type = "C"
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					tot_net_amount = round(tot_net_amount,2)
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					itc_state_tax = map_data["mapped_items"][map_d]["itc_state_tax"]
					supply_type = map_data["mapped_items"][map_d]["supply_type"]
					supplier_name = map_data["mapped_items"][map_d]["supplier_name"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					eligibility_for_itc = map_data["mapped_items"][map_d]["eligibility_for_itc"]
					itc_integrated_tax = map_data["mapped_items"][map_d]["itc_integrated_tax"]
					itc_central_tax =map_data["mapped_items"][map_d]["itc_central_tax"]
					itc_cess_amount = map_data["mapped_items"][map_d]["itc_cess_amount"]
					sgst_tax_rate = map_data["mapped_items"][map_d]["sgst_tax_rate"]
					cgst_tax_rate = map_data["mapped_items"][map_d]["cgst_tax_rate"]
					india_gst_supplier_status = map_data["mapped_items"][map_d]["india_gst_supplier_status"]
					gstin = map_data["mapped_items"][map_d]["gstin"]
					port_code = map_data["mapped_items"][map_d]["port_code"]
					bill_of_entry_number = map_data["mapped_items"][map_d]["bill_of_entry_number"]
					bill_of_entry_date = map_data["mapped_items"][map_d]["bill_of_entry_date"]
					return_against = map_data["mapped_items"][map_d]["return_against"]
					reason_for_issuing_document = map_data["mapped_items"][map_d]["reason_for_issuing_document"]
					return_posting_date = frappe.db.get_value("Purchase Invoice",return_against,"posting_date")
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					payment_entry = get_Advance_Payment_details(invoice_no)
					if len(payment_entry) != 0:
						for payment in payment_entry:
							payment_number = payment.name
							payment_date = payment.posting_date
					else:
						payment_number = invoice_no
						payment_date = posting_date
					#payment_date = payment_date.strftime('%d-%m-%Y')
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					return_posting_date = return_posting_date.strftime('%d-%m-%Y')
					#bill_of_entry_date = bill_of_entry_date.strftime('%d-%m-%Y')
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					igst_tax_amount = tot_net_amount * igst_tax_rate /100
					sgst_tax_amount = tot_net_amount * sgst_tax_rate /100
					cgst_tax_amount = tot_net_amount * cgst_tax_rate /100
					igst_tax_amount = round(igst_tax_amount,2)
					sgst_tax_amount = round(sgst_tax_amount,2)
					cgst_tax_amount = round(cgst_tax_amount,2)
					total_integrated_tax_paid += igst_tax_amount
					total_central_tax_paid += cgst_tax_amount
					total_state_tax_paid += sgst_tax_amount
					total_net_amount += tot_net_amount
					total_invoice_value += grand_total
					if itc_integrated_tax is not None:
						total_itc_integrated_tax += float(itc_integrated_tax)
					if itc_state_tax is not None:
						total_itc_state_tax += float(itc_state_tax)
						total_itc_central_tax += float(itc_central_tax)
					if itc_cess_amount is not None:
						total_itc_cess_amount += float(itc_cess_amount)
					data.append([return_against,return_posting_date,payment_number,payment_date,pre_gst,
					document_type,reason_for_issuing_document,supply_type,grand_total,rate_of_tax,tot_net_amount,
					igst_tax_amount,cgst_tax_amount,sgst_tax_amount,"",eligibility_for_itc,itc_integrated_tax
					,itc_central_tax,itc_state_tax,itc_cess_amount])
		data.append(["","","","","",""])
		data.append(["Total","","","","","","","",total_invoice_value,"",total_net_amount,
				total_integrated_tax_paid,total_central_tax_paid,total_state_tax_paid,"","",total_itc_integrated_tax,
				total_itc_central_tax,total_itc_state_tax,total_itc_cess_amount])

	elif type_of_business == "EXEMP":
		columns = get_columns_exemp()
		expemted_items_details = sales_invoice_item_expem(from_date,to_date)
		exempt_detail = sales_exepted_nill(expemted_items_details)
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

	elif type_of_business == "HSNSUM":
		columns = get_columns_hsnsum()
		grand_total_value = 0.0
		grand_total_net_amount = 0.0
		grand_total_central = 0.0
		grand_total_integrated = 0.0
		grand_total_state = 0.0
		grand_total_cess = 0.0
		hsn_details = hsn_code_uqc_code(from_date,to_date)
		hsn_listed = get_hsn_uqc_list(hsn_details)
		description = ""
		for unique_hsn in hsn_listed:
			hsn_detials = hsn_listed[unique_hsn]
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
			#print "gst_hsn_code----------",gst_hsn_code
			#print "tax_rate-------------",hsn_detials.tax_rate
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
				net_amount,integrated_tax_amount,central_tax_amount,state_tax_amount,""])
		data.append(["","","","",""])
		data.append(["Total","","","",grand_total_value,grand_total_net_amount,grand_total_integrated,grand_total_central,
						grand_total_state,grand_total_cess])
	return columns, data

def get_columns_b2b():
	return [
		_("GSTIN of Supplier") + "::150",
		_("Invoice Number") + ":Link/Purchase Invoice:150",
		_("Invoice date") + "::150",
		_("Supplier Name")+"::150",
		_("Supplier Invoice no")+"::150",
		_("Supplier Invoice Date")+"::150",
		_("Invoice Value") + ":Currency:150",
		_("Place Of Supply") + "::150",
		_("Reverse Charge") + "::180",
		_("Invoice Type") + "::150",
		_("Rate") + "::150",
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
		_("Invoice Number") + ":Link/Purchase Invoice:150",
		_("Invoice date") + "::150",
		_("Supplier Invoice no")+"::150",
		_("Supplier Invoice Date")+"::150",
		_("Invoice Value") + ":Currency:150",
		_("Place Of Supply") + "::150",
		_("Supply Type") + "::180",
		_("Rate") + "::150",
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
		_("Rate") + "::150",
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
		_("Rate") + "::150",
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
		_("Rate") + "::150",
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
		_("Rate") + "::150",
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
						pi.name,pi.invoice_type,pi.reverse_charge,pi.posting_date,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.itc_central_tax,pi.itc_state_tax,pi.supplier_address,
						pi.itc_cess_amount,pi.supplier_name,pi.company,s.india_gst_supplier_status,pi.bill_no,pi.bill_date
					from
						`tabPurchase Invoice` pi , `tabSupplier` s
					where
						pi.posting_date >= %s AND pi.posting_date <= %s AND
						pi.eligibility_for_itc NOT IN ("ineligible") AND pi.supplier = s.name
						AND pi.invoice_type = 'Regular' AND pi.docstatus = 1 AND pi.is_return = 0""",
					(from_date,to_date), as_dict = 1)
	return b2b_purchase
def purchase_invoice_b2bur(from_date,to_date):
	b2b_purchase = frappe.db.sql("""select
						pi.name,pi.invoice_type,pi.reverse_charge,pi.posting_date,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.itc_central_tax,pi.itc_state_tax,pi.supplier_address,
						pi.itc_cess_amount,pi.supplier_name,pi.company,s.india_gst_supplier_status,pi.bill_no,pi.bill_date
					from
						`tabPurchase Invoice` pi , `tabSupplier` s
					where
						pi.posting_date >= %s AND pi.posting_date <= %s AND pi.supplier = s.name AND
						pi.eligibility_for_itc NOT IN ("ineligible") AND pi.invoice_type = 'Regular'
						AND pi.docstatus = 1 AND pi.is_return = 0 AND
						s.india_gst_supplier_status = 'Unregistered Dealer'
					""",(from_date,to_date), as_dict = 1)
	return b2b_purchase
def purchase_invoice_imps(from_date,to_date):
	imps_purchase = frappe.db.sql("""select
						pi.name,pi.invoice_type,pi.reverse_charge,pi.posting_date,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.itc_central_tax,pi.itc_state_tax,pi.supplier_address,
						pi.itc_cess_amount,pi.supplier_name,pi.company,s.india_gst_supplier_status,pi.bill_no,pi.bill_date
					from
						`tabPurchase Invoice` pi , `tabSupplier` s
					where
						pi.supplier = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s AND
						pi.invoice_type = 'Import - Service' AND pi.docstatus =1 AND pi.is_return = 0
					""",(from_date,to_date), as_dict =1)
	return imps_purchase
def purchase_invoice_impg(from_date,to_date):
	impg_purchase = frappe.db.sql("""select
						pi.name,pi.invoice_type,pi.reverse_charge,pi.posting_date,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.itc_central_tax,pi.itc_state_tax,pi.supplier_address,
						pi.itc_cess_amount,pi.supplier_name,pi.company,s.india_gst_supplier_status
						,pi.pch_port_code,pi.pch_bill_of_entry_date,pi.pch_bill_of_entry_number,pi.invoice_type,pi.bill_no,pi.bill_date
					from
						`tabPurchase Invoice` pi , `tabSupplier` s
					where
						pi.supplier = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s AND
						pi.invoice_type = 'Import - Goods' AND pi.docstatus =1 AND pi.is_return = 0
					""",(from_date,to_date), as_dict =1)
	return impg_purchase
def purchase_invoice_cdnr(from_date,to_date):
	cdnr_purchase = frappe.db.sql("""select
						pi.name,pi.posting_date,pi.supplier_address,pi.supplier_name,pi.eligibility_for_itc,
						pi.itc_integrated_tax,pi.itc_cess_amount
						,pi.invoice_type,s.india_gst_supplier_status,pi.return_against,
						pi.itc_central_tax,pi.itc_state_tax,pi.reason_for_issuing_document,pi.company,pi.bill_no,pi.bill_date
					from
						`tabPurchase Invoice` pi , `tabSupplier` s
					where
						pi.supplier = s.name AND pi.posting_date >= %s AND pi.posting_date <= %s AND
						pi.docstatus =1 AND pi.is_return = 1
					""",(from_date,to_date), as_dict =1)
	return cdnr_purchase
def sales_invoice_item_expem(from_date,to_date):
	exempt_item = frappe.db.sql(""" select
						sii.name,si.parent,si.item_name,si.item_code,si.net_amount,i.india_gst_item_status,
						sii.supplier_address,sii.company
					from
						`tabPurchase Invoice` sii, `tabPurchase Invoice Item` si , `tabItem` i
					where
						sii.name = si.parent AND si.item_code = i.name
						AND i.india_gst_item_status IN ("Nil Rated Item","Exempt Item","Non-GST Item",
						"Composite Dealer ")
						AND sii.posting_date >= %s AND sii.posting_date <=%s AND sii.docstatus = 1
					""",(from_date,to_date), as_dict = 1)

	return exempt_item
def hsn_code_uqc_code(from_date,to_date):
	hsn_uqc = frappe.db.sql(""" select
						s.name,si.item_name,si.item_code,si.net_amount,si.uom,si.qty,si.gst_hsn_code
				    from
						`tabPurchase Invoice` s, `tabPurchase Invoice Item` si
				   where
						s.name = si.parent AND s.posting_date >= %s AND s.posting_date <= %s""",
					(from_date,to_date), as_dict = 1)
	return hsn_uqc
def gst_hsn_doc(gst_hsn_code):
	hsn_doc = frappe.db.sql("""select
					name,description
				from
					`tabGST HSN Code`
				where  name = %s
				""",(gst_hsn_code), as_dict = 1)
	return hsn_doc
def gst_uqc_doc(uom):
	uqc_doc = frappe.db.sql("""select
					uqc_code,quantity
				from
					`tabUQC Item`
				where
					erpnext_uom_link = %s
				""",(uom), as_dict = 1)
	return uqc_doc
def sales_item_details(invoice_id):
	if invoice_id:
		invoice_item = frappe.db.sql("""select
							item_code,net_amount,qty,rate
						from
							`tabPurchase Invoice Item`
						where
							parent = %s"""
						,(invoice_id), as_dict = 1)
	return invoice_item

def sales_taxe_rate_details(invoice_id):
	taxe_rate_data = frappe.db.sql("""select
						parent,rate,account_head
					from
						`tabPurchase Taxes and Charges`
					where
						parent = %s"""
					,(invoice_id), as_dict = 1)
	return taxe_rate_data
def sales_tax(item_code,invoice_id):
	items = frappe.db.sql("""select
					si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type
				from
					`tabPurchase Invoice Item` si, `tabItem Tax` it , `tabPurchase Taxes and Charges` st
				where
					si.item_code = %s AND si.parent = %s AND it.parent = si.item_code AND
					st.parent = si.parent AND it.tax_type = st.account_head
					order by it.idx
				""",(item_code,invoice_id), as_dict = 1)
	return items
def sales_account_tax(invoice_id):
	account_tax = ""
	if invoice_id:
		account_tax = frappe.db.sql("""select
							account_head,rate,item_wise_tax_detail
						from
							`tabPurchase Taxes and Charges`
						where
							parent = %s """
						,(invoice_id),as_dict =1)
	return account_tax
def company_details(company_name):
	company_name = company_name + '%'
	company = frappe.db.sql("""select
					state,gst_state_number
				from
					`tabAddress`
				where
					name Like '"""+company_name+"""'
				""",as_dict=1)

	return company
def get_Advance_Payment_details(invoice_id):
	payment_data = frappe.db.sql("""select
						pe.paid_amount,pe.name,pe.creation,pe.party_name,pe.posting_date
					from
						`tabPayment Entry` pe , `tabPayment Entry Reference` per
					where
						pe.name = per.parent AND per.reference_name = %s
					""",(invoice_id),as_dict = 1)
	return payment_data
def sales_tax_hsn(item_code,invoice_id):
	items_hsn = ""
	if item_code:
		items_hsn = frappe.db.sql("""select
							si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type
					     from
							`tabPurchase Invoice Item` si, `tabItem Tax` it, `tabPurchase Taxes and Charges` ptc
					     where
							si.item_code = %s AND si.parent = %s AND it.parent = si.item_code
							AND si.parent = ptc.parent AND it.tax_type = ptc.account_head
					   """,(item_code,invoice_id), as_dict = 1)
	return items_hsn

def get_business_type_details(sales):
	invoice_map = {}
	for seles_data in sales:
		invoice_id = seles_data.name
		supplier_address = seles_data.supplier_address
		company_name = seles_data.company
		supply_type = ""
		c_state = ""
		c_state_number = 0
		state =""
		gst_state_number =0
		gstin = ""
		if supplier_address is not None:
			state,gst_state_number,gstin = frappe.db.get_value("Address",supplier_address,['state','gst_state_number','gstin'])
			company_data = company_details(company_name)
			for company in company_data:
				c_state = company.state
				c_state_number = company.gst_state_number
			if state != c_state and gst_state_number != c_state_number:
				supply_type = "Inter State"
			elif  state == c_state and gst_state_number == c_state_number:
				supply_type = "Intra State"
		place_of_supply = ""
		if state is not None:
			place_of_supply = str(gst_state_number)+"-"+str(state)
		reverse_charge = seles_data.reverse_charge
		invoice_type = seles_data.invoice_type
		supplier_name = seles_data.supplier_name
		supplier_invoice_no = seles_data.bill_no
		supplier_invoice_date = seles_data.bill_date
		india_gst_supplier_status = seles_data.india_gst_supplier_status
		posting_date = seles_data.posting_date
		eligibility_for_itc = seles_data.eligibility_for_itc
		itc_integrated_tax = seles_data.itc_integrated_tax
		itc_central_tax = seles_data.itc_central_tax
		itc_state_tax = seles_data.itc_state_tax
		itc_cess_amount = seles_data.itc_cess_amount
		port_code = seles_data.pch_port_code
		bill_of_entry_date = seles_data.pch_bill_of_entry_date
		bill_of_entry_number = seles_data.pch_bill_of_entry_number
		return_against = seles_data.return_against
		reason_for_issuing_document = seles_data.reason_for_issuing_document
		posting_date = posting_date.strftime('%d-%m-%Y')
		sales_item = sales_item_details(invoice_id)
		sales_account_head = ""
		for item in sales_item:
			item_code = item.item_code
			item_net_amount = item.net_amount
			#print "item_code---------",item_code
			tax_data = sales_tax(item_code,invoice_id)
			igst_tax_rate = 0
			sgst_tax_rate = 0
			cgst_tax_rate = 0
			tax_rate = 0
			if len(tax_data) != 0:
				for data in tax_data:
					tax_type = data.tax_type
					if "IGST" in tax_type:
						igst_tax_rate = data.tax_rate
						tax_rate = data.tax_rate
					elif "SGST" in tax_type:
						sgst_tax_rate = data.tax_rate
						tax_rate += data.tax_rate
					elif "CGST" in tax_type:
						cgst_tax_rate = data.tax_rate
						tax_rate += data.tax_rate
					net_amount = data.net_amount

			sales_invoice_tax_data = sales_account_tax(invoice_id)
			tax_rate_list = []
			if len(tax_data) != 0:
				key = invoice_id
				if key in invoice_map:
					item_entry = invoice_map[key]
					#print "item_entry------------",item_entry
					mapped_items_list = item_entry["mapped_items"]
					new_list = []
					for mapped_items in mapped_items_list:
				    		tax_rate_list.append(mapped_items["tax_rate"])
						data_rate = list(set(tax_rate_list))
					if tax_rate in data_rate:
					    	for items in mapped_items_list:
					   		 if float(tax_rate) == float(items["tax_rate"]):
					    			qty_temp = items["net_amount"]
								items["net_amount"] = (qty_temp) + (net_amount)
					else :
						new_list.append({
									"tax_rate": tax_rate,
									"igst_tax_rate":igst_tax_rate,
									"sgst_tax_rate":sgst_tax_rate,
									"cgst_tax_rate":cgst_tax_rate,
									"net_amount": net_amount,
									"invoice_id": key,
									"eligibility_for_itc": eligibility_for_itc,
									"place_of_supply": place_of_supply,
									"reverse_charge": reverse_charge,
									"invoice_type": invoice_type,
									"posting_date": posting_date,
									"itc_integrated_tax": itc_integrated_tax,
									"itc_central_tax":itc_central_tax,
									"itc_state_tax":itc_state_tax,
									"itc_cess_amount":itc_cess_amount,
									"gstin":gstin,
									"supplier_name":supplier_name,
									"supply_type":supply_type,
									"india_gst_supplier_status":india_gst_supplier_status,
									"port_code":port_code,
									"bill_of_entry_date":bill_of_entry_date,
									"bill_of_entry_number":bill_of_entry_number,
									"return_against":return_against,
									"reason_for_issuing_document":reason_for_issuing_document,
									"supplier_invoice_no":supplier_invoice_no,
									"supplier_invoice_date":supplier_invoice_date
								    })
						item_entry["mapped_items"] = mapped_items_list + new_list
				else :
					item_list = []
					item_list.append({
							"tax_rate": tax_rate,
							"igst_tax_rate":igst_tax_rate,
							"sgst_tax_rate":sgst_tax_rate,
							"cgst_tax_rate":cgst_tax_rate,
							"net_amount": net_amount,
							"invoice_id": key,
							"eligibility_for_itc": eligibility_for_itc,
							"place_of_supply": place_of_supply,
							"reverse_charge": reverse_charge,
							"invoice_type": invoice_type,
							"posting_date": posting_date,
							"itc_integrated_tax": itc_integrated_tax,
							"itc_central_tax":itc_central_tax,
							"itc_state_tax":itc_state_tax,
							"itc_cess_amount":itc_cess_amount,
							"gstin":gstin,
							"supplier_name":supplier_name,
							"supply_type":supply_type,
							"india_gst_supplier_status":india_gst_supplier_status,
							"port_code":port_code,
							"bill_of_entry_date":bill_of_entry_date,
							"bill_of_entry_number":bill_of_entry_number,
							"return_against":return_against,
							"reason_for_issuing_document":reason_for_issuing_document,
							"supplier_invoice_no":supplier_invoice_no,
							"supplier_invoice_date":supplier_invoice_date
						})
					invoice_map[key] = frappe._dict({
						    "mapped_items": item_list
					})
			else:
				sales_tax_rate = 0
				total_amount = 0.0
				igst_tax_rate = 0
				sgst_tax_rate = 0
				cgst_tax_rate = 0
				if len(sales_invoice_tax_data) != 0:
					for invoice_tax_data in sales_invoice_tax_data:
						account_head = invoice_tax_data.account_head
						item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
						converted = ast.literal_eval(item_wise_tax_detail)
						if item_code in converted:
							details = converted[item_code]
							if "SGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
								sgst_tax_rate = details[0]
							elif "CGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
								cgst_tax_rate = details[0]
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
								igst_tax_rate = details[0]
					if invoice_id in invoice_map:
						item_entry = invoice_map[invoice_id]
						#print "item_entry sales---------",item_entry
						mapped_items_list = item_entry["mapped_items"]
						for mapped_items in mapped_items_list:
							tax_rate_list.append(mapped_items["tax_rate"])
							data_rate = list(set(tax_rate_list))
						if sales_tax_rate in data_rate:
							for items in mapped_items_list:
								if float(sales_tax_rate) == float(items["tax_rate"]):
									qty_temp = items["net_amount"]
									items["net_amount"] = (qty_temp) + (item_net_amount)
						else:
							mapped_items_list.append({
										"tax_rate": sales_tax_rate,
										"igst_tax_rate":igst_tax_rate,
										"sgst_tax_rate":sgst_tax_rate,
										"cgst_tax_rate":cgst_tax_rate,
										"net_amount": item_net_amount,
										"invoice_id": invoice_id,
										"eligibility_for_itc": eligibility_for_itc,
										"place_of_supply": place_of_supply,
										"reverse_charge": reverse_charge,
										"invoice_type": invoice_type,
										"posting_date": posting_date,
										"itc_integrated_tax": itc_integrated_tax,
										"itc_central_tax":itc_central_tax,
										"itc_state_tax":itc_state_tax,
										"itc_cess_amount":itc_cess_amount,
										"gstin":gstin,
										"supplier_name":supplier_name,
										"supply_type":supply_type,
										"india_gst_supplier_status":india_gst_supplier_status,
										"port_code":port_code,
										"bill_of_entry_date":bill_of_entry_date,
										"bill_of_entry_number":bill_of_entry_number,
										"return_against":return_against,
										"reason_for_issuing_document":reason_for_issuing_document,
										"supplier_invoice_no":supplier_invoice_no,
										"supplier_invoice_date":supplier_invoice_date
									})
							item_entry["mapped_items"] = mapped_items_list
					else:
						item_list = []
						item_list.append({
								"tax_rate": sales_tax_rate,
								"igst_tax_rate":igst_tax_rate,
								"sgst_tax_rate":sgst_tax_rate,
								"cgst_tax_rate":cgst_tax_rate,
								"net_amount": item_net_amount,
								"invoice_id": invoice_id,
								"eligibility_for_itc": eligibility_for_itc,
								"place_of_supply": place_of_supply,
								"reverse_charge": reverse_charge,
								"invoice_type": invoice_type,
								"posting_date": posting_date,
								"itc_integrated_tax": itc_integrated_tax,
								"itc_central_tax":itc_central_tax,
								"itc_state_tax":itc_state_tax,
								"itc_cess_amount":itc_cess_amount,
								"gstin":gstin,
								"supplier_name":supplier_name,
								"supply_type":supply_type,
								"india_gst_supplier_status":india_gst_supplier_status,
								"port_code":port_code,
								"bill_of_entry_date":bill_of_entry_date,
								"bill_of_entry_number":bill_of_entry_number,
								"return_against":return_against,
								"reason_for_issuing_document":reason_for_issuing_document,
								"supplier_invoice_no":supplier_invoice_no,
								"supplier_invoice_date":supplier_invoice_date
								})
						invoice_map[invoice_id] = frappe._dict({"mapped_items": item_list})
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
			india_gst_supplier_status = exempt.india_gst_item_status
			if str(india_gst_supplier_status) == "Nil Rated Item":
				net_total = exempt.net_amount
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
			elif str(india_gst_supplier_status) == "Exempt Item":
				net_total = exempt.net_amount
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

			elif str(india_gst_supplier_status) == "Non-GST Item":
				net_total = exempt.net_amount
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
				net_total = exempt.net_amount
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
	total_value = 0.0
	integrated_tax_amount_total = 0.0
	central_tax_amount_total = 0.0
	state_tax_amount_total = 0.0
	for seles_data in sales:
		invoice_id = seles_data.name
		item_name = seles_data.itme_name
		item_code = seles_data.item_code
		net_amount = seles_data.net_amount
		gst_hsn_code = seles_data.gst_hsn_code
		uom = seles_data.uom
		qty = seles_data.qty
		tax_data = sales_tax_hsn(item_code,invoice_id)
		sales_invoice_tax_data = sales_account_tax(invoice_id)
		tax_rate_list = []
		integrated_tax_amount = 0.0
		central_tax_amount = 0.0
		state_tax_amount = 0.0
		if gst_hsn_code is not None:
			if len(tax_data) != 0:
				item_tax_rate = 0.0
				for data in tax_data:
					#tax_rate = data.tax_rate
					tax_type = data.tax_type
					key = gst_hsn_code
					if  "SGST" in tax_type:
						item_tax_rate = item_tax_rate + data.tax_rate
						state_tax_amount = net_amount * data.tax_rate/100
					elif "CGST" in tax_type:
						item_tax_rate = item_tax_rate + data.tax_rate
						central_tax_amount = net_amount * data.tax_rate/100
					elif "IGST" in tax_type:

						item_tax_rate = data.tax_rate
						integrated_tax_amount = net_amount * data.tax_rate/100
				if key in invoice_map:
				    	item_entry = invoice_map[key]
					qty_temp = item_entry["net_amount"]
					qty_count = item_entry["qty"]
					integrated_tmp = item_entry["integrated_tax_amount_total"]
					central_tmp = item_entry["central_tax_amount_total"]
					state_tmp = item_entry["state_tax_amount_total"]
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
			else:
				sales_tax_rate = 0
				total_amount = 0.0
				if len(sales_invoice_tax_data) != 0:
					for invoice_tax_data in sales_invoice_tax_data:
						account_head = invoice_tax_data.account_head
						item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
						converted = ast.literal_eval(item_wise_tax_detail)
						if item_code in converted:
							details = converted[item_code]
							if "SGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
								state_tax_amount = net_amount * details[0]/100
							elif "CGST" in account_head:
								sales_tax_rate = sales_tax_rate + details[0]
								central_tax_amount = net_amount * details[0]/100
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
								integrated_tax_amount = net_amount * details[0]/100

					if gst_hsn_code in invoice_map:
						item_entry = invoice_map[gst_hsn_code]

						qty_temp = item_entry["net_amount"]
						qty_count = item_entry["qty"]
						integrated_tmp = item_entry["integrated_tax_amount_total"]
						central_tmp = item_entry["central_tax_amount_total"]
						state_tmp = item_entry["state_tax_amount_total"]
						item_entry["net_amount"] = (qty_temp) + (net_amount)
						item_entry["qty"] = (qty_count) + (qty)
						item_entry["integrated_tax_amount_total"] = (integrated_tmp) + (integrated_tax_amount)
						item_entry["central_tax_amount_total"] = (central_tmp) + (central_tax_amount)
						item_entry["state_tax_amount_total"] = (state_tmp) + (state_tax_amount)
					else:
						invoice_map[gst_hsn_code] = frappe._dict({
							"tax_rate": sales_tax_rate,
							"net_amount": net_amount,
							"gst_hsn_code": gst_hsn_code,
							"state_tax_amount_total":state_tax_amount,
							"central_tax_amount_total":central_tax_amount,
							"integrated_tax_amount_total":integrated_tax_amount,
							"uom":uom,
							"qty":qty,
							"item_code":item_code
							})
	return invoice_map
