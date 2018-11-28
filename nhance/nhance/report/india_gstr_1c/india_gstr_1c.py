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
	return IndiaGstr1C(filters).run()
class IndiaGstr1C(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.data = []
		self.columns = []
		self.invoice_id = ""
		self.item_code = ""
		self.tax_data = []
		self.tax_details = []
		self.customer_address = ""
		self.company_address = ""
		if self.filters.fetch_days_data is not None:
			self.filters.from_date = self.filters.temp_from_date
			self.filters.to_date = self.filters.temp_to_date
	def run(self):
		from_date = self.filters.from_date
		to_date = self.filters.to_date
		if self.filters.get("type_of_business") == "B2B":
			columns = self.get_columns_b2b()
			grand_total_taxable = 0.0
			grand_total_invoice = 0.0
			grand_total_cess = 0.0
			b2b_sales = sales_invoice_details(from_date,to_date)
			for sales in b2b_sales:
				amended_from = sales.amended_from
				if amended_from is None:
					billing_address_gstin = sales.billing_address_gstin
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = sales.place_of_supply
					reverse_charge = sales.reverse_charge
					invoice_type = sales.invoice_type
					customer_name = sales.customer_name
					ecommerce_gstin = sales.ecommerce_gstin
					posting_date = sales.posting_date
					posting_date = posting_date.strftime('%d-%m-%Y')
					grand_total = sales.grand_total
					company_address = sales.company_address
					customer_type = sales.customer_type
					port_code = sales.port_code
					shipping_bill_number = sales.shipping_bill_number
					shipping_bill_date = sales.shipping_bill_date
					if shipping_bill_date is not None:
						shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
					export_type = sales.export_type
					is_return = sales.is_return
					return_against = sales.return_against
					account_head = ""
					modified = sales.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					amended_from = sales.amended_from
					net_total = sales.net_total
					selas_taxes = sales_taxes_charges(invoice_id)
					taxable_value = 0.0
					tax_rate = 0.0
					cess_amount = 0.0
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					self.data.append([billing_address_gstin,customer_address,invoice_id,manual_serial_number,posting_date,
							invoice_value,place_of_supply,reverse_charge,"",invoice_type,
							ecommerce_gstin,tax_rate,taxable_value,cess_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","",grand_total_invoice,"","","","",
					"","",grand_total_taxable,grand_total_cess,""])
		elif self.filters.get("type_of_business") == "B2BA":
			columns = self.get_columns_b2ba()
			grand_total_taxable = 0.0
			grand_total_invoice = 0.0
			grand_total_cess = 0.0
			b2b_sales = sales_invoice_details(from_date,to_date)
			for sales in b2b_sales:
				amended_from = sales.amended_from
				if amended_from is not None:
					billing_address_gstin = sales.billing_address_gstin
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = sales.place_of_supply
					reverse_charge = sales.reverse_charge
					invoice_type = sales.invoice_type
					customer_name = sales.customer_name
					ecommerce_gstin = sales.ecommerce_gstin
					posting_date = sales.posting_date
					posting_date = posting_date.strftime('%d-%m-%Y')
					grand_total = sales.grand_total
					company_address = sales.company_address
					customer_type = sales.customer_type
					port_code = sales.port_code
					shipping_bill_number = sales.shipping_bill_number
					shipping_bill_date = sales.shipping_bill_date
					if shipping_bill_date is not None:
						shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
					export_type = sales.export_type
					is_return = sales.is_return
					return_against = sales.return_against
					account_head = ""
					modified = sales.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					amended_from = sales.amended_from
					net_total = sales.net_total
					selas_taxes = sales_taxes_charges(invoice_id)
					taxable_value = 0.0
					tax_rate = 0.0
					cess_amount = 0.0
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					self.data.append([billing_address_gstin,customer_address,amended_from,manual_serial_number,
							posting_date,invoice_id,modified,invoice_value,place_of_supply,
							reverse_charge,"",invoice_type,ecommerce_gstin,tax_rate,taxable_value,cess_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","","","",grand_total_invoice,"","","","",
					"","",grand_total_taxable,grand_total_cess,""])
		elif self.filters.get("type_of_business") == "B2CL":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_b2bl()
			b2cl_details = sales_invoice_b2bl(from_date,to_date)
			for sales in b2cl_details:
				amended_from = sales.amended_from
				if amended_from is None:
					billing_address_gstin = sales.billing_address_gstin
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = sales.place_of_supply
					reverse_charge = sales.reverse_charge
					invoice_type = sales.invoice_type
					customer_name = sales.customer_name
					ecommerce_gstin = sales.ecommerce_gstin
					posting_date = sales.posting_date
					posting_date = posting_date.strftime('%d-%m-%Y')
					grand_total = sales.grand_total
					company_address = sales.company_address
					customer_type = sales.customer_type
					port_code = sales.port_code
					shipping_bill_number = sales.shipping_bill_number
					shipping_bill_date = sales.shipping_bill_date
					if shipping_bill_date is not None:
						shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
					export_type = sales.export_type
					is_return = sales.is_return
					return_against = sales.return_against
					account_head = ""
					modified = sales.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					amended_from = sales.amended_from
					net_total = sales.net_total
					selas_taxes = sales_taxes_charges(invoice_id)
					taxable_value = 0.0
					tax_rate = 0.0
					cess_amount = 0.0
					b2c_limit = frappe.db.get_value('GST Settings',customer_address,'b2c_limit')
					gst_state_number = get_contact_details(customer_address)
					address_details = address_gst_number(company_address)
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					if grand_total > float(b2c_limit) and address_details != gst_state_number:
						self.data.append([invoice_id,
							posting_date,invoice_value,place_of_supply,"",
							tax_rate,taxable_value,cess_amount,ecommerce_gstin])
			self.data.append(["","","","",""])
			self.data.append(["Total","",grand_total_invoice,"",
					"","",grand_total_taxable,grand_total_cess,""])
		elif self.filters.get("type_of_business") == "B2CLA":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_b2bla()
			b2cl_details = sales_invoice_b2bl(from_date,to_date)
			for sales in b2cl_details:
				amended_from = sales.amended_from
				if amended_from is not None:
					original_place_of_supply = frappe.db.get_value('Sales Invoice',amended_from,'place_of_supply')
					billing_address_gstin = sales.billing_address_gstin
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = sales.place_of_supply
					reverse_charge = sales.reverse_charge
					invoice_type = sales.invoice_type
					customer_name = sales.customer_name
					ecommerce_gstin = sales.ecommerce_gstin
					posting_date = sales.posting_date
					posting_date = posting_date.strftime('%d-%m-%Y')
					grand_total = sales.grand_total
					company_address = sales.company_address
					customer_type = sales.customer_type
					port_code = sales.port_code
					shipping_bill_number = sales.shipping_bill_number
					shipping_bill_date = sales.shipping_bill_date
					if shipping_bill_date is not None:
						shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
					export_type = sales.export_type
					is_return = sales.is_return
					return_against = sales.return_against
					account_head = ""
					modified = sales.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					amended_from = sales.amended_from
					net_total = sales.net_total
					selas_taxes = sales_taxes_charges(invoice_id)
					taxable_value = 0.0
					tax_rate = 0.0
					cess_amount = 0.0
					b2c_limit = frappe.db.get_value('GST Settings',customer_address,'b2c_limit')
					gst_state_number = get_contact_details(customer_address)
					address_details = address_gst_number(company_address)
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					if grand_total > float(b2c_limit) and address_details != gst_state_number:
						self.data.append([amended_from,posting_date,original_place_of_supply,invoice_id,
								modified,invoice_value,"",tax_rate,taxable_value,cess_amount,ecommerce_gstin])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","",grand_total_invoice,
					"","",grand_total_taxable,grand_total_cess,""])

		elif self.filters.get("type_of_business") == "B2CS":
			invoice_map = {}
			grand_total_taxable = 0.0
			grand_total_invoice = 0.0
			grand_total_cess = 0.0
			cess_amount = 0.0
			columns = self.get_columns_b2bcs()
			b2cs_details = sales_invoice_b2bl(from_date,to_date)
			unique_state = get_unique_state_list(b2cs_details)
			for b2cs_data in unique_state:
				b2cs_detail = unique_state[b2cs_data]
				for b2cs_d in range(0,len(b2cs_detail["mapped_items"])):
					tax_rate = b2cs_detail["mapped_items"][b2cs_d]["tax_rate"]
					taxable_value = b2cs_detail["mapped_items"][b2cs_d]["taxable_value"]
					place_of_supply = b2cs_detail["mapped_items"][b2cs_d]["place_of_supply"]
					customer_type = b2cs_detail["mapped_items"][b2cs_d]["customer_type"]
					ecommerce_gstin = b2cs_detail["mapped_items"][b2cs_d]["ecommerce_gstin"]
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					self.data.append([customer_type,place_of_supply,invoice_value,"",tax_rate,taxable_value,
						cess_amount,ecommerce_gstin])

			self.data.append(["","","","",""])
			self.data.append(["Total","",grand_total_invoice,
					"","",grand_total_taxable,grand_total_cess,""])

		elif self.filters.get("type_of_business") == "B2CSA":
			columns = self.get_columns_b2bcsa()
			cess_amount = 0.0
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			now = datetime.datetime.now()
			current_year = now.year
			b2cs_details = sales_invoice_b2bl(from_date,to_date)
			unique_state = get_unique_state_list_amended(b2cs_details)
			for b2cs_data in unique_state:
				b2cs_detail = unique_state[b2cs_data]
				for b2cs_d in range(0,len(b2cs_detail["mapped_items"])):
					tax_rate = b2cs_detail["mapped_items"][b2cs_d]["tax_rate"]
					taxable_value = b2cs_detail["mapped_items"][b2cs_d]["taxable_value"]
					place_of_supply = b2cs_detail["mapped_items"][b2cs_d]["place_of_supply"]
					customer_type = b2cs_detail["mapped_items"][b2cs_d]["customer_type"]
					ecommerce_gstin = b2cs_detail["mapped_items"][b2cs_d]["ecommerce_gstin"]
					posting_date = b2cs_detail["mapped_items"][b2cs_d]["posting_date"]
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					self.data.append([str(current_year)+"-"+str(current_year+1),posting_date,place_of_supply,
					customer_type,invoice_value,"",tax_rate,taxable_value,cess_amount,ecommerce_gstin])

			self.data.append(["","","","",""])
			self.data.append(["Total","","","",grand_total_invoice,
					"","",grand_total_taxable,grand_total_cess,""])

		elif self.filters.get("type_of_business") == "CDNR":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_cdnr()
			cdnr_sales = sales_invoice_cdrn(from_date,to_date)
			for sales in cdnr_sales:
				amended_from = sales.amended_from
				if amended_from is None:
					billing_address_gstin = sales.billing_address_gstin
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = sales.place_of_supply
					reverse_charge = sales.reverse_charge
					invoice_type = sales.invoice_type
					customer_name = sales.customer_name
					ecommerce_gstin = sales.ecommerce_gstin
					posting_date = sales.posting_date
					posting_date = posting_date.strftime('%d-%m-%Y')
					grand_total = sales.grand_total
					company_address = sales.company_address
					customer_type = sales.customer_type
					port_code = sales.port_code
					shipping_bill_number = sales.shipping_bill_number
					shipping_bill_date = sales.shipping_bill_date
					if shipping_bill_date is not None:
						shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
					export_type = sales.export_type
					is_return = sales.is_return
					return_against = sales.return_against
					account_head = ""
					modified = sales.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					amended_from = sales.amended_from
					net_total = sales.net_total
					return_against = sales.return_against
					selas_taxes = sales_taxes_charges(invoice_id)
					taxable_value = 0.0
					tax_rate = 0.0
					cess_amount = 0.0
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					document_type = ""
					payment_entry = get_Advance_Payment_details(invoice_id)
					print "payment_entry--------",len(payment_entry)
					if len(payment_entry) != 0:
						for payment in payment_entry:
							payment_number = payment.name
							payment_date = payment.posting_date
							payment_date = payment_date.strftime('%d-%m-%Y')	
					else:
						payment_number = invoice_id
						payment_date = posting_date
					return_sales_details = sale_invoice_again_return(return_against)
					for return_sale in return_sales_details:
						credit_invoice_id = return_sale.name
						creadit_return_date = return_sale.posting_date
						creadit_return_date = creadit_return_date.strftime('%d-%m-%Y')
						document_type = "C"
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					self.data.append([billing_address_gstin,customer_address,payment_number,
							payment_date,credit_invoice_id,creadit_return_date,
							document_type,place_of_supply,invoice_value,""
							,tax_rate,taxable_value,cess_amount,pre_gst])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","","","","",grand_total_invoice,
					"","",grand_total_taxable,grand_total_cess,""])
		elif self.filters.get("type_of_business") == "CDNR-A":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_cdnra()
			cdnr_sales = sales_invoice_cdrn(from_date,to_date)
			for sales in cdnr_sales:
				amended_from = sales.amended_from
				if amended_from is not None:
					billing_address_gstin = sales.billing_address_gstin
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = sales.place_of_supply
					reverse_charge = sales.reverse_charge
					invoice_type = sales.invoice_type
					customer_name = sales.customer_name
					ecommerce_gstin = sales.ecommerce_gstin
					posting_date = sales.posting_date
					posting_date = posting_date.strftime('%d-%m-%Y')
					grand_total = sales.grand_total
					company_address = sales.company_address
					customer_type = sales.customer_type
					port_code = sales.port_code
					shipping_bill_number = sales.shipping_bill_number
					shipping_bill_date = sales.shipping_bill_date
					if shipping_bill_date is not None:
						shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
					export_type = sales.export_type
					is_return = sales.is_return
					return_against = sales.return_against
					account_head = ""
					modified = sales.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					amended_from = sales.amended_from
					net_total = sales.net_total
					return_against = sales.return_against
					selas_taxes = sales_taxes_charges(invoice_id)
					taxable_value = 0.0
					tax_rate = 0.0
					cess_amount = 0.0
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					document_type = ""
					payment_entry = get_Advance_Payment_details(invoice_id)
					print "payment_entry--------",len(payment_entry)
					if len(payment_entry) != 0:
						for payment in payment_entry:
							payment_number = payment.name
							payment_date = payment.posting_date
							payment_date = payment_date.strftime('%d-%m-%Y')	
					else:
						payment_number = invoice_id
						payment_date = posting_date
					return_sales_details = sale_invoice_again_return(return_against)
					for return_sale in return_sales_details:
						credit_invoice_id = return_sale.name
						creadit_return_date = return_sale.posting_date
						creadit_return_date = creadit_return_date.strftime('%d-%m-%Y')
						document_type = "C"
					pre_gst = ""
					if str(posting_date) < "01-07-2017":
						pre_gst = "Y"
					else:
						pre_gst = "N"
					self.data.append([billing_address_gstin,customer_address,amended_from,
							modified,payment_number,
							payment_date,credit_invoice_id,creadit_return_date,
							document_type,place_of_supply,invoice_value,""
							,tax_rate,taxable_value,cess_amount,pre_gst])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","","","","","","",grand_total_invoice,
					"","",grand_total_taxable,grand_total_cess,""])

		elif self.filters.get("type_of_business") == "EXPORT":
			invoice_map = {}
			grand_total_invoice = 0.0
			grand_total_taxable = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_exp()
			export_sales = sales_invoice_exp(from_date,to_date)
			for sales in export_sales:
				amended_from = sales.amended_from
				billing_address_gstin = sales.billing_address_gstin
				invoice_id = sales.name
				manual_serial_number = sales.manual_serial_number
				customer_address = sales.customer_address
				place_of_supply = sales.place_of_supply
				reverse_charge = sales.reverse_charge
				invoice_type = sales.invoice_type
				customer_name = sales.customer_name
				ecommerce_gstin = sales.ecommerce_gstin
				posting_date = sales.posting_date
				posting_date = posting_date.strftime('%d-%m-%Y')
				grand_total = sales.grand_total
				company_address = sales.company_address
				customer_type = sales.customer_type
				port_code = sales.port_code
				shipping_bill_number = sales.shipping_bill_number
				shipping_bill_date = sales.shipping_bill_date
				if shipping_bill_date is not None:
					shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
				export_type = sales.export_type
				is_return = sales.is_return
				return_against = sales.return_against
				account_head = ""
				modified = sales.modified
				modified = modified.date()
				modified = modified.strftime('%d-%m-%Y')
				amended_from = sales.amended_from
				net_total = sales.net_total
				return_against = sales.return_against
				selas_taxes = sales_taxes_charges(invoice_id)
				taxable_value = 0.0
				tax_rate = 0.0
				cess_amount = 0.0
				for taxes in selas_taxes:
					charge_type = taxes.charge_type
					if "On Net Total" in charge_type:
						taxable_value = net_total
					elif "On Previous Row Total" in charge_type:
						row_id = taxes.row_id
						get_amount_tax = sales_tax_amount(row_id,invoice_id)
						for amount in get_amount_tax:
							taxable_value = amount.total
					account_head = taxes.account_head
					if "SGST" in account_head:
						tax_rate = tax_rate + taxes.rate
					elif "CGST" in account_head:
						tax_rate = tax_rate + taxes.rate
					elif "IGST" in account_head:
						tax_rate = taxes.rate
				amount_by_gst =  taxable_value * tax_rate/100
				invoice_value = amount_by_gst + taxable_value
				grand_total_taxable = grand_total_taxable + taxable_value
				grand_total_invoice = grand_total_invoice + invoice_value
				self.data.append([export_type,invoice_id,posting_date,invoice_value,
						port_code,shipping_bill_number,shipping_bill_date,""
						,tax_rate,taxable_value,cess_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","","",grand_total_invoice,"","","","","",grand_total_taxable,grand_total_cess])
		elif self.filters.get("type_of_business") == "EXEMP":
			invoice_map = {}
			grand_total_nill = 0.0
			grand_total_non = 0.0
			grand_total_exmp = 0.0
			columns = self.get_columns_exemp()

		elif self.filters.get("type_of_business") == "HSN":
			grand_total_value = 0.0
			grand_total_net_amount = 0.0
			grand_total_central = 0.0
			grand_total_integrated = 0.0
			grand_total_state = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_hsn()

		elif self.filters.get("type_of_business") == "AT":
			columns = self.get_columns_at()

		elif self.filters.get("type_of_business") == "ATA":
			columns = self.get_columns_ata()

		elif self.filters.get("type_of_business") == "ATADJ":
			columns = self.get_columns_at()

		elif self.filters.get("type_of_business") == "ATADJA":
			columns = self.get_columns_ata()

		return columns, self.data


	def get_columns_b2b(self):
		return [
			_("GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Manual Serial Number") + "::150",
			_("Invoice date") + "::150",
			_("Invoice Value") + "::180",
			_("Place Of Supply") + "::150",
			_("Reverse Charge") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Invoice Type") + "::150",
			_("E-Commerce GSTIN") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::160", 
			_("Cess Amount") + "::120"
		
			]
	def get_columns_b2ba(self):
		return [
			_("GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Original Invoice Number") + ":Link/Sales Invoice:150",
			_("Manual Serial Number") + "::150",
			_("Original Invoice date") + "::150",
			_("Revised Invoice Number") + ":Link/Sales Invoice:150",
			_("Revised Invoice date") + "::150",
			_("Invoice Value") + "::180",
			_("Place Of Supply") + "::150",
			_("Reverse Charge") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Invoice Type") + "::150",
			_("E-Commerce GSTIN") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::160", 
			_("Cess Amount") + "::120"
	
			]
	def get_columns_b2bl(self):
		return [
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Invoice date") + "::150",
			_("Invoice Value") + "::150",
			_("Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::180",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
	
		]
	def get_columns_b2bla(self):
		return [
			_("Original Invoice Number") + ":Link/Sales Invoice:150",
			_("Original Invoice date") + "::150",
			_("Original Place Of Supply") + "::150",
			_("Revised Invoice Number") + ":Link/Sales Invoice:150",
			_("Revised Invoice date") + "::150",
			_("Invoice Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::180",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]
	def get_columns_b2bcs(self):
		return [
			_("Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Invoice Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"

		]
	def get_columns_b2bcsa(self):
		return [
			_("Financial Year") + "::150",
			_("Original Month") + "::150",
			_("Type ") + "::150",
			_("Place Of Supply") + "::150",
			_("Invoice Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
	
		]
	def get_columns_exp(self):
		return [
			_(" Export Type") + "::150",
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Invoice date ") + "::150",
			_("Invoice Value ") + "::150",
			_("Port Code") + "::150",
			_("Shipping Bill Number") + "::150",
			_("Shipping Bill Date") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150"
		
	
		]
	def get_columns_cdnr(self):
		return [
			_(" GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Invoice/Advance Receipt Number") + "::150",
			_("Invoice/Advance Receipt date") + "::150",
			_("Note/Refund Voucher Number ") + ":Link/Sales Invoice:150",
			_("Note/Refund Voucher date") + "::150",
			_("Document Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Note/Refund Voucher Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("Pre GST") + "::150"
	
	
		]
	def get_columns_cdnra(self):
		return [
			_(" GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Original Note/Refund Voucher Number ") + ":Link/Sales Invoice:150",
			_("Original Note/Refund Voucher date") + "::150",
			_("Original Invoice/Advance Receipt Number") + "::150",
			_("Original Invoice/Advance Receipt date") + "::150",
			_("Revised Note/Refund Voucher Number ") + ":Link/Sales Invoice:150",
			_("Revised Note/Refund Voucher date") + "::150",
			_("Document Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Note/Refund Voucher Value") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("Pre GST") + "::150"
	
	
		]
	def get_columns_exemp(self):
		return [
			_("Description") + ":Link/Item:250",
			_("Nil Rated Supplies") + "::150",
			_("Exempted(other than nil rated/non GST supply)") + "::250",
			_("Non-GST Supplies") + "::150"
		]
	def get_columns_hsn(self):
		return [
			_("HSN") + "::150",
			_("Description") + "::250",
			_("UQC ") + "::150",
			_("Total Quantity") + "::150",
			_("Total Value") + "::150",
			_("Taxable Value") + "::150",
			_("Integrated Tax Amount") + "::150",
			_("Central Tax Amount") + "::150",
			_("State/UT Tax Amount") + "::150",
			_("Cess Amount") + "::150"
		
		]
	def get_columns_at(self):
		return [
			_("Sales Order Number") + ":Link/Sales Order:150",
			_("Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::250",
			_("Rate ") + "::150",
			_("Gross Advance Received") + "::150",
			_("Cess Amount") + "::150"
		
		]
	def get_columns_ata(self):
		return [
			_("Sales Order Number") + ":Link/Sales Order:150",
			_("Financial Year") + "::150",
			_("Original Month") + "::250",
			_("Original Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::250",
			_("Rate ") + "::150",
			_("Gross Advance Received") + "::150",
			_("Cess Amount") + "::150"
		
		]

def sales_invoice_details(from_date,to_date):
	sales_invoice = frappe.db.sql("""select si.billing_address_gstin,si.customer_address,si.name,si.customer_name,
					si.posting_date,si.place_of_supply,si.is_return,si.return_against,si.manual_serial_number,
					si.reverse_charge,si.invoice_type,si.ecommerce_gstin,si.posting_date,si.amended_from,
					si.modified,si.grand_total,si.company_address,c.customer_type,si.net_total
					from `tabSales Invoice` si, `tabCustomer` c
					where si.posting_date >= %s AND si.posting_date <= %s AND si.invoice_type = "Regular"
			 		AND c.customer_type = "Company" AND si.customer_name = c.customer_name
					AND si.docstatus = 1""",(from_date,to_date), as_dict = 1)

	return sales_invoice

def sales_taxes_charges(invoice_id):
	taxes_and_charges = frappe.db.sql(""" select charge_type,account_head,row_id,total,rate 
						from `tabSales Taxes and Charges` where parent = %s
						""",(invoice_id) , as_dict = 1)
	return taxes_and_charges

def sales_tax_amount(row_id,invoice_id):
	tax_amount = frappe.db.sql("""select total 
				from `tabSales Taxes and Charges` 
				where parent = %s AND idx = %s
				""",(invoice_id,row_id), as_dict =1)
	return tax_amount

def sales_invoice_b2bl(from_date,to_date):
	sales_invoice_b = frappe.db.sql("""select si.billing_address_gstin,si.customer_address,si.name,si.customer_name,si.net_total,
					si.posting_date,si.place_of_supply,si.is_return,si.return_against,si.manual_serial_number,
					si.reverse_charge,si.invoice_type,si.ecommerce_gstin,si.posting_date,si.amended_from,
					si.modified,si.grand_total,si.company_address,c.customer_type
					from `tabSales Invoice` si, `tabCustomer` c
					where si.posting_date >= %s AND si.posting_date <= %s AND si.invoice_type = "Regular"
			 		AND c.customer_type = "Individual" AND si.customer_name = c.customer_name AND si.is_return = 0
					AND si.docstatus = 1""",(from_date,to_date), as_dict = 1)
	
	return sales_invoice_b

def get_contact_details(customer_address):
	gst_state_number =""
	if customer_address:
		gst_state_number = frappe.db.get_value('Address',customer_address,
		['gst_state_number'])
	return gst_state_number

def address_gst_number(company_address):
	company_gst_state_number = ""
	address_detail = frappe.get_list("Address",["address_type","gst_state_number","name"])
	for itrate_address in address_detail:
		name = itrate_address.name
		if name == company_address:
			company_gst_state_number  = itrate_address.gst_state_number
	return company_gst_state_number

def sales_invoice_cdrn(from_date,to_date):
	sales_invoice_cd = frappe.db.sql("""select billing_address_gstin,customer_address,name,customer_name,net_total,
					posting_date,place_of_supply,port_code,shipping_bill_number,shipping_bill_date,
					export_type,reverse_charge,invoice_type,ecommerce_gstin,posting_date,amended_from,
					modified,grand_total,company_address,is_return,return_against
					from `tabSales Invoice`
					where posting_date >= %s AND posting_date <= %s AND is_return = 1
					AND docstatus = 1""",(from_date,to_date), as_dict = 1)
	return sales_invoice_cd

def sale_invoice_again_return(return_against):
	return_sales = frappe.db.sql("""select name,posting_date from `tabSales Invoice` where name = %s""",(return_against), as_dict = 1)
	return return_sales

def get_Advance_Payment_details(invoice_id):
	payment_data = frappe.db.sql("""select pe.paid_amount,pe.name,pe.creation,pe.party_name,pe.posting_date
				 from `tabPayment Entry` pe , `tabPayment Entry Reference` per 
				where pe.name = per.parent AND per.reference_name = %s""",(invoice_id),as_dict = 1)
	return payment_data

def sales_invoice_exp(from_date,to_date):
	sales_invoice_ex = frappe.db.sql("""select billing_address_gstin,customer_address,name,customer_name,net_total,
					posting_date,place_of_supply,port_code,shipping_bill_number,shipping_bill_date,
					export_type,reverse_charge,invoice_type,ecommerce_gstin,posting_date,amended_from,
					modified,grand_total,company_address,is_return,return_against
					from `tabSales Invoice`
					where posting_date >= %s AND posting_date <= %s AND invoice_type = "Export"
					AND docstatus = 1""",(from_date,to_date), as_dict = 1)
	return sales_invoice_ex

def get_unique_state_list(sales):
	invoice_map = {}
	for seles_data in sales:
		amended_from = seles_data.amended_from
		if amended_from is None:
			billing_address_gstin = seles_data.billing_address_gstin
			invoice_id = seles_data.name
			manual_serial_number = seles_data.manual_serial_number
			customer_address = seles_data.customer_address
			place_of_supply = seles_data.place_of_supply
			reverse_charge = seles_data.reverse_charge
			invoice_type = seles_data.invoice_type
			customer_name = seles_data.customer_name
			ecommerce_gstin = seles_data.ecommerce_gstin
			posting_date = seles_data.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			grand_total = seles_data.grand_total
			company_address = seles_data.company_address
			customer_type = seles_data.customer_type
			port_code = seles_data.port_code
			shipping_bill_number = seles_data.shipping_bill_number
			shipping_bill_date = seles_data.shipping_bill_date
			if shipping_bill_date is not None:
				shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
			export_type = seles_data.export_type
			is_return = seles_data.is_return
			return_against = seles_data.return_against
			account_head = ""
			modified = seles_data.modified
			modified = modified.date()
			modified = modified.strftime('%d-%m-%Y')
			amended_from = seles_data.amended_from
			net_total = seles_data.net_total
			cess_amount = 0.0
			b2c_limit = frappe.db.get_value('GST Settings',customer_address,'b2c_limit')
			gst_state_number = get_contact_details(customer_address)
			address_details = address_gst_number(company_address)
			if (grand_total <= float(b2c_limit) and address_details != gst_state_number)\
			or (grand_total <= float(b2c_limit) and address_details == gst_state_number) \
			or (grand_total >= float(b2c_limit) and address_details == gst_state_number): 
				
				selas_taxes = sales_taxes_charges(invoice_id)
				if len(selas_taxes) != 0:
					taxable_value = 0.0
					tax_rate = 0.0
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
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
						   			qty_temp = items["taxable_value"]
									items["taxable_value"] = (qty_temp) + (taxable_value)
						else :
							new_list.append({
											"tax_rate": tax_rate,
											"taxable_value": taxable_value,
											"billing_address_gstin": billing_address_gstin,
											"customer_address": customer_address,
											"place_of_supply": key,
											"reverse_charge": reverse_charge,
											"invoice_type": invoice_type,
											"posting_date": posting_date,
											"ecommerce_gstin": ecommerce_gstin,
											"modified":modified,
											"amended_from":amended_from,
											"grand_total":grand_total,
											"company_address":company_address,
											"customer_type":customer_type,
											"port_code":port_code,
											"shipping_bill_number":shipping_bill_number,
											"shipping_bill_date":shipping_bill_date,
											"export_type":export_type,
											"customer_name":customer_name,
											"is_return":is_return,
											"return_against":return_against
								
									    })
							item_entry["mapped_items"] = mapped_items_list + new_list
					else :
						item_list = []
						item_list.append({
									"tax_rate": tax_rate,
									"taxable_value": taxable_value,
									"billing_address_gstin": billing_address_gstin,
									"customer_address": customer_address,
									"place_of_supply": key,
									"reverse_charge": reverse_charge,
									"invoice_type": invoice_type,
									"posting_date": posting_date,
									"ecommerce_gstin": ecommerce_gstin,
									"modified":modified,
									"amended_from":amended_from,
									"grand_total":grand_total,
									"company_address":company_address,
									"customer_type":customer_type,
									"port_code":port_code,
									"shipping_bill_number":shipping_bill_number,
									"shipping_bill_date":shipping_bill_date,
									"export_type":export_type,
									"customer_name":customer_name,
									"is_return":is_return,
										"return_against":return_against
							})
						invoice_map[key] = frappe._dict({
							    "mapped_items": item_list
								})
	return invoice_map

def get_unique_state_list_amended(sales):
	invoice_map = {}
	for seles_data in sales:
		amended_from = seles_data.amended_from
		if amended_from is not None:
			billing_address_gstin = seles_data.billing_address_gstin
			invoice_id = seles_data.name
			manual_serial_number = seles_data.manual_serial_number
			customer_address = seles_data.customer_address
			place_of_supply = seles_data.place_of_supply
			reverse_charge = seles_data.reverse_charge
			invoice_type = seles_data.invoice_type
			customer_name = seles_data.customer_name
			ecommerce_gstin = seles_data.ecommerce_gstin
			posting_date = seles_data.posting_date
			posting_date = posting_date.strftime('%d-%m-%Y')
			grand_total = seles_data.grand_total
			company_address = seles_data.company_address
			customer_type = seles_data.customer_type
			port_code = seles_data.port_code
			shipping_bill_number = seles_data.shipping_bill_number
			shipping_bill_date = seles_data.shipping_bill_date
			if shipping_bill_date is not None:
				shipping_bill_date = shipping_bill_date.strftime('%d-%m-%Y')
			export_type = seles_data.export_type
			is_return = seles_data.is_return
			return_against = seles_data.return_against
			account_head = ""
			modified = seles_data.modified
			modified = modified.date()
			modified = modified.strftime('%d-%m-%Y')
			amended_from = seles_data.amended_from
			net_total = seles_data.net_total
			cess_amount = 0.0
			b2c_limit = frappe.db.get_value('GST Settings',customer_address,'b2c_limit')
			gst_state_number = get_contact_details(customer_address)
			address_details = address_gst_number(company_address)
			if (grand_total <= float(b2c_limit) and address_details != gst_state_number)\
			or (grand_total <= float(b2c_limit) and address_details == gst_state_number) \
			or (grand_total >= float(b2c_limit) and address_details == gst_state_number): 
				
				selas_taxes = sales_taxes_charges(invoice_id)
				if len(selas_taxes) != 0:
					print "invoice_id-----------",invoice_id
					taxable_value = 0.0
					tax_rate = 0.0
					for taxes in selas_taxes:
						charge_type = taxes.charge_type
						if "On Net Total" in charge_type:
							taxable_value = net_total
						elif "On Previous Row Total" in charge_type:
							row_id = taxes.row_id
							get_amount_tax = sales_tax_amount(row_id,invoice_id)
							for amount in get_amount_tax:
								taxable_value = amount.total
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
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
						   			qty_temp = items["taxable_value"]
									items["taxable_value"] = (qty_temp) + (taxable_value)
						else :
							new_list.append({
											"tax_rate": tax_rate,
											"taxable_value": taxable_value,
											"billing_address_gstin": billing_address_gstin,
											"customer_address": customer_address,
											"place_of_supply": key,
											"reverse_charge": reverse_charge,
											"invoice_type": invoice_type,
											"posting_date": posting_date,
											"ecommerce_gstin": ecommerce_gstin,
											"modified":modified,
											"amended_from":amended_from,
											"grand_total":grand_total,
											"company_address":company_address,
											"customer_type":customer_type,
											"port_code":port_code,
											"shipping_bill_number":shipping_bill_number,
											"shipping_bill_date":shipping_bill_date,
											"export_type":export_type,
											"customer_name":customer_name,
											"is_return":is_return,
											"return_against":return_against
								
									    })
							item_entry["mapped_items"] = mapped_items_list + new_list
					else :
						item_list = []
						item_list.append({
									"tax_rate": tax_rate,
									"taxable_value": taxable_value,
									"billing_address_gstin": billing_address_gstin,
									"customer_address": customer_address,
									"place_of_supply": key,
									"reverse_charge": reverse_charge,
									"invoice_type": invoice_type,
									"posting_date": posting_date,
									"ecommerce_gstin": ecommerce_gstin,
									"modified":modified,
									"amended_from":amended_from,
									"grand_total":grand_total,
									"company_address":company_address,
									"customer_type":customer_type,
									"port_code":port_code,
									"shipping_bill_number":shipping_bill_number,
									"shipping_bill_date":shipping_bill_date,
									"export_type":export_type,
									"customer_name":customer_name,
									"is_return":is_return,
										"return_against":return_against
							})
						invoice_map[key] = frappe._dict({
							    "mapped_items": item_list
								})
	return invoice_map
	
