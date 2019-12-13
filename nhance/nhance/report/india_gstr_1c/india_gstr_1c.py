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
			invoice_no = ""
			for sales in b2b_sales:
				amended_from = sales.amended_from
				if amended_from is None:
					invoice_id = sales.name
					selas_taxes = sales_taxes_charges(invoice_id)
					if invoice_id != invoice_no and len(selas_taxes)!= 0:
						invoice_no = invoice_id
						gstin_and_place_of_supply = sales.gstin_and_place_of_supply
						place_of_supply = ""
						billing_address_gstin = ""
						customer_address = sales.customer_address
						shipping_address_name = sales.shipping_address_name
						gst_state_number = ""
						gst_state = ""
						party_gsstin = ""
						if shipping_address_name:
							if gstin_and_place_of_supply == 1:
								billing_address = get_address_details(customer_address)
								for bill in billing_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
							elif gstin_and_place_of_supply == 0:
								shipping_address = get_address_details(shipping_address_name)
								for bill in shipping_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
						else:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
						manual_serial_number = sales.manual_serial_number
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
						
						grand_total_taxable = grand_total_taxable + taxable_value
						grand_total_invoice = grand_total_invoice + grand_total
						self.data.append([party_gsstin,customer_address,invoice_id,manual_serial_number,
								posting_date,grand_total,str(gst_state_number)+"-"+str(gst_state),
								reverse_charge,"",invoice_type,ecommerce_gstin,tax_rate,
								taxable_value,cess_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","","",grand_total_invoice,"","","","",
					"","",grand_total_taxable,grand_total_cess,""])
		elif self.filters.get("type_of_business") == "B2BA":
			columns = self.get_columns_b2ba()
			grand_total_taxable = 0.0
			grand_total_invoice = 0.0
			grand_total_cess = 0.0
			b2b_sales = sales_invoice_details(from_date,to_date)
			invoice_no = ""
			for sales in b2b_sales:
				amended_from = sales.amended_from
				if amended_from is not None:
					invoice_id = sales.name
					
					selas_taxes = sales_taxes_charges(invoice_id)
					if invoice_id != invoice_no and len(selas_taxes)!= 0:
						invoice_no = invoice_id
						billing_address_gstin = sales.billing_address_gstin
						manual_serial_number = sales.manual_serial_number
						customer_address = sales.customer_address
						place_of_supply = ""
						gstin_and_place_of_supply = sales.gstin_and_place_of_supply
						place_of_supply = ""
						customer_address = sales.customer_address
						shipping_address_name = sales.shipping_address_name
						gst_state_number = ""
						gst_state = ""
						party_gsstin = ""
						if shipping_address_name:
							if gstin_and_place_of_supply == 1:
								billing_address = get_address_details(customer_address)
								for bill in billing_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
							elif gstin_and_place_of_supply == 0:
								shipping_address = get_address_details(shipping_address_name)
								for bill in shipping_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
						else:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
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
						invoice_value = round(invoice_value)
						grand_total_taxable = grand_total_taxable + taxable_value
						grand_total_invoice = grand_total_invoice + grand_total
						self.data.append([party_gsstin,customer_address,amended_from,manual_serial_number,
							posting_date,invoice_id,modified,grand_total,str(gst_state_number)+"-"+str(gst_state),
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
					invoice_id = sales.name
					invoice_no = ""
					selas_taxes = sales_taxes_charges(invoice_id)
					if invoice_id != invoice_no and len(selas_taxes)!= 0:
						invoice_no = invoice_id
						billing_address_gstin = sales.billing_address_gstin
						invoice_id = sales.name
						manual_serial_number = sales.manual_serial_number
						customer_address = sales.customer_address
						place_of_supply = ""
						billing_address_gstin = ""
						gstin_and_place_of_supply = sales.gstin_and_place_of_supply
						customer_address = sales.customer_address
						shipping_address_name = sales.shipping_address_name
						gst_state_number = ""
						gst_state = ""
						party_gsstin = ""
						if shipping_address_name:
							if gstin_and_place_of_supply == 1:
								billing_address = get_address_details(customer_address)
								for bill in billing_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
							elif gstin_and_place_of_supply == 0:
								shipping_address = get_address_details(shipping_address_name)
								for bill in shipping_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
						else:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
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
						if grand_total > float(b2c_limit) and address_details != gst_state_number:
							amount_by_gst =  taxable_value * tax_rate/100
							invoice_value = amount_by_gst + taxable_value
							invoice_value = round(invoice_value)
							grand_total_taxable = grand_total_taxable + taxable_value
							grand_total_invoice = grand_total_invoice + grand_total
							self.data.append([invoice_id,
								posting_date,grand_total,str(gst_state_number)+"-"+str(gst_state),"",
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
					invoice_id = sales.name
					invoice_no = ""
					selas_taxes = sales_taxes_charges(invoice_id)
					if invoice_id != invoice_no and len(selas_taxes)!= 0:
						invoice_no = invoice_id
						original_place_of_supply =""
						billing_address_gstin = sales.billing_address_gstin
						invoice_id = sales.name
						customer_address = sales.customer_address
						place_of_supply = ""
						billing_address_gstin = ""
						gstin_and_place_of_supply,shipping_address_name,customer_address = frappe.db.get_value('Sales Invoice',amended_from,['gstin_and_place_of_supply','shipping_address_name','customer_address'])
						print "amended_from----------",amended_from
						print "gstin_and_place_of_supply----------",gstin_and_place_of_supply
						print "shipping_address_name-----------",shipping_address_name
						print "customer_address----------",customer_address
						gst_state_number = ""
						gst_state = ""
						party_gsstin = ""
						if shipping_address_name:
							if gstin_and_place_of_supply == 1:
								billing_address = get_address_details(customer_address)
								for bill in billing_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
							elif gstin_and_place_of_supply == 0:
								shipping_address = get_address_details(shipping_address_name)
								for bill in shipping_address:
									gst_state_number = bill.gst_state_number
									gst_state = bill.gst_state
									party_gsstin = bill.gstin
						else:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
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
					
						if grand_total > float(b2c_limit) and address_details != gst_state_number:
							amount_by_gst =  taxable_value * tax_rate/100
							invoice_value = amount_by_gst + taxable_value
							invoice_value = round(invoice_value)
							grand_total_taxable = grand_total_taxable + taxable_value
							grand_total_invoice = grand_total_invoice + grand_total
							self.data.append([amended_from,posting_date,str(gst_state_number)+"-"+str(gst_state),
							invoice_id,modified,grand_total,"",tax_rate,taxable_value,cess_amount,ecommerce_gstin])
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
					grand_total = b2cs_detail["mapped_items"][b2cs_d]["grand_total"]
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					invoice_value = round(invoice_value,2)
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
					fiscal_year = frappe.defaults.get_user_default("fiscal_year")
					amount_by_gst =  taxable_value * tax_rate/100
					invoice_value = amount_by_gst + taxable_value
					grand_total_taxable = grand_total_taxable + taxable_value
					grand_total_invoice = grand_total_invoice + invoice_value
					self.data.append([str(fiscal_year),posting_date,place_of_supply,
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
					place_of_supply = ""
					billing_address_gstin = ""
					gstin_and_place_of_supply = sales.gstin_and_place_of_supply
					customer_address = sales.customer_address
					shipping_address_name = sales.shipping_address_name
					gst_state_number = ""
					gst_state = ""
					party_gsstin = ""
					if shipping_address_name:
						if gstin_and_place_of_supply == 1:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
						elif gstin_and_place_of_supply == 0:
							shipping_address = get_address_details(shipping_address_name)
							for bill in shipping_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
					else:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
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
					grand_total_invoice = grand_total_invoice + grand_total
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					document_type = ""
					payment_entry = get_Advance_Payment_details(invoice_id)
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
							document_type,str(gst_state_number)+"-"+str(gst_state),grand_total,""
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
					billing_address_gstin = ""
					invoice_id = sales.name
					manual_serial_number = sales.manual_serial_number
					customer_address = sales.customer_address
					place_of_supply = ""
					billing_address_gstin = ""
					gstin_and_place_of_supply = sales.gstin_and_place_of_supply
					customer_address = sales.customer_address
					shipping_address_name = sales.shipping_address_name
					gst_state_number = ""
					gst_state = ""
					party_gsstin = ""
					if shipping_address_name:
						if gstin_and_place_of_supply == 1:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
						elif gstin_and_place_of_supply == 0:
							shipping_address = get_address_details(shipping_address_name)
							for bill in shipping_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
					else:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
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
					grand_total_invoice = grand_total_invoice + grand_total
					credit_invoice_id = ""
					credit_invoice_id = ""
					payment_date = ""
					creadit_return_date = ""
					document_type = ""
					payment_entry = get_Advance_Payment_details(invoice_id)
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
							document_type,str(gst_state_number)+"-"+str(gst_state),grand_total,""
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
				billing_address_gstin = ""
				invoice_id = sales.name
				manual_serial_number = sales.manual_serial_number
				customer_address = sales.customer_address
				place_of_supply = ""
				billing_address_gstin = ""
				gstin_and_place_of_supply = sales.gstin_and_place_of_supply
				customer_address = sales.customer_address
				shipping_address_name = sales.shipping_address_name
				gst_state_number = ""
				gst_state = ""
				party_gsstin = ""
				if shipping_address_name:
					if gstin_and_place_of_supply == 1:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
					elif gstin_and_place_of_supply == 0:
						shipping_address = get_address_details(shipping_address_name)
						for bill in shipping_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
				else:
					billing_address = get_address_details(customer_address)
					for bill in billing_address:
						gst_state_number = bill.gst_state_number
						gst_state = bill.gst_state
						party_gsstin = bill.gstin
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
				invoice_value = round(invoice_value)
				grand_total_taxable = grand_total_taxable + taxable_value
				grand_total_invoice = grand_total_invoice + grand_total
				self.data.append([export_type,invoice_id,posting_date,grand_total,
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
			exempt_items = sales_invoice_item_expem(from_date,to_date)
			exempt_item_data = sales_exepted_nill(exempt_items)
			for exem in exempt_item_data:
				exempt_details = exempt_item_data[exem]
				item_name = exempt_details.item_name
				non_net_amount = exempt_details.non_net_amount
				non_net_amount = round(non_net_amount)
				exempt_net_amount = exempt_details.exempt_net_amount
				exempt_net_amount = round(exempt_net_amount)
				nill_net_amount = exempt_details.nill_net_amount
				nill_net_amount = round(nill_net_amount)
				india_gst_item_status = exempt_details.india_gst_item_status
				grand_total_nill = grand_total_nill + nill_net_amount
				grand_total_non = grand_total_non + non_net_amount
				grand_total_exmp = grand_total_exmp + exempt_net_amount
				self.data.append([item_name,nill_net_amount,exempt_net_amount,non_net_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total",grand_total_nill,grand_total_exmp,grand_total_non])

		elif self.filters.get("type_of_business") == "HSN":
			grand_total_value = 0.0
			grand_total_net_amount = 0.0
			grand_total_central = 0.0
			grand_total_integrated = 0.0
			grand_total_state = 0.0
			grand_total_cess = 0.0
			columns = self.get_columns_hsn()
			hsn_code_uqc_details = hsn_code_uqc_code(from_date,to_date)
			hsn_uqc_unique = get_hsn_uqc_list(hsn_code_uqc_details)
			description = ""
			for unique_hsn in hsn_uqc_unique:
				hsn_detials = hsn_uqc_unique[unique_hsn]
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
				net_amount = round(net_amount)
				state_tax_amount = hsn_detials.state_tax_amount
				state_tax_amount = round(state_tax_amount)
				integrated_tax_amount = hsn_detials.integrated_tax_amount
				integrated_tax_amount = round(integrated_tax_amount)
				total_value_tax = net_amount*hsn_detials.tax_rate/100
				total_value = total_value_tax+net_amount
				total_value = round(total_value)
				grand_total_value = grand_total_value + total_value
				grand_total_net_amount = grand_total_net_amount + net_amount
				qty = hsn_detials.qty
				central_tax_amount = hsn_detials.central_tax_amount
				central_tax_amount = round(central_tax_amount)
				grand_total_central = grand_total_central + central_tax_amount
				grand_total_integrated = grand_total_integrated + integrated_tax_amount
				grand_total_state = grand_total_state + state_tax_amount
				self.data.append([gst_hsn_code,description,uqc_name,qty,total_value,
					net_amount,integrated_tax_amount,central_tax_amount,state_tax_amount])
			self.data.append(["","","","",""])
			self.data.append(["Total","","","",grand_total_value,grand_total_net_amount,grand_total_integrated,grand_total_central,
						grand_total_state,grand_total_cess])

		elif self.filters.get("type_of_business") == "AT":
			columns = self.get_columns_at()
			at_sales = payment_and_sales(from_date,to_date)
			total_ad_recieve = 0.0
			total_ad_adjusted = 0.0
			totla_pending = 0.0
			total_taxable = 0.0
			total_isgt = 0.0
			total_ssgt = 0.0
			total_csgt = 0.0
			for seles_data in at_sales:
				invoice_id = seles_data.name
				allocated_amount = seles_data.allocated_amount
				advance_paid = seles_data.advance_paid
				grand_total = seles_data.grand_total
				place_of_supply = seles_data.place_of_supply
				net_total = seles_data.net_total
				additional_discount_percentage = seles_data.additional_discount_percentage
				selas_taxes = sales_taxes_charges(invoice_id)
				payment_entry_id = seles_data.entry_id
				creation = seles_data.creation
				creation = creation.date()
				creation = creation.strftime('%d-%m-%Y')
				gstin = seles_data.gstin
				customer_address = seles_data.customer_address
				shipping_address_name = seles_data.shipping_address_name
				gstin_and_place_of_supply = seles_data.gstin_and_place_of_supply
				gst_state_number = ""
				gst_state = ""
				party_gsstin = ""
				if shipping_address_name:
					if gstin_and_place_of_supply == 1:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
					elif gstin_and_place_of_supply == 0:
						shipping_address = get_address_details(shipping_address_name)
						for bill in shipping_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
				else:
					billing_address = get_address_details(customer_address)
					for bill in billing_address:
						gst_state_number = bill.gst_state_number
						gst_state = bill.gst_state
						party_gsstin = bill.gstin
				taxable_value = 0.0
				tax_rate = 0.0
				tax_rate_sgst = 0.0
				tax_rate_cgst = 0.0
				tax_rate_igst = 0.0
				cess_amount = 0.0
				advance_adjust = 0.0
				total_ad_recieve = total_ad_recieve + allocated_amount
				total_ad_adjusted = total_ad_adjusted + advance_adjust
				advance_pending = allocated_amount - advance_adjust
				totla_pending = totla_pending + advance_pending
				for taxes in selas_taxes:
					account_head = taxes.account_head
					if "SGST" in account_head:
						tax_rate = tax_rate + taxes.rate
						tax_rate_sgst = taxes.rate	
					elif "CGST" in account_head:
						tax_rate = tax_rate + taxes.rate
						tax_rate_cgst = taxes.rate
					elif "IGST" in account_head:
						tax_rate = taxes.rate
						tax_rate_igst = taxes.rate
				taxable_value = advance_pending/(1 + tax_rate/100)
				taxable_value = round(taxable_value)
				total_taxable = total_taxable + taxable_value
				igst_amount = (taxable_value * tax_rate_igst)/100
				igst_amount = round(igst_amount)
				sgst_amount = (taxable_value * tax_rate_sgst)/100
				sgst_amount = round(sgst_amount)
				cgst_amount = (taxable_value * tax_rate_cgst)/100
				cgst_amount = round(cgst_amount)
				total_isgt = total_isgt + igst_amount
				total_ssgt = total_ssgt + sgst_amount
				total_csgt = total_csgt + cgst_amount
				self.data.append([creation,payment_entry_id,party_gsstin,customer_address,
						str(gst_state_number)+"-"+str(gst_state),invoice_id,
						tax_rate,allocated_amount,advance_adjust,advance_pending,taxable_value,igst_amount,
						cgst_amount,sgst_amount])
			self.data.append(["","","","","","","",""])
			self.data.append(["","","","","","","Total",total_ad_recieve,total_ad_adjusted,
					totla_pending,total_taxable,total_isgt,total_csgt,total_ssgt])
		elif self.filters.get("type_of_business") == "ATA":
			columns = self.get_columns_ata()
			ata_sales = payment_and_sales_amended(from_date,to_date)
			total_ad_recieve = 0.0
			total_ad_adjusted = 0.0
			totla_pending = 0.0
			total_taxable = 0.0
			total_isgt = 0.0
			total_ssgt = 0.0
			total_csgt = 0.0
			for seles_data in ata_sales:
				sales_doc = seles_data.sales_doc
				payment_doc = seles_data.payment_doc
				payment_amended_from = seles_data.payment_amended
				if payment_amended_from is not None:
					payment_entry_details = payment_entry_amended(payment_amended_from)
					original_voucher_no = ""
					original_date = ""
					original_state = ""
					for pay in payment_entry_details:
						original_voucher_no = pay.name
						original_date = pay.creation
						original_date = original_date.date()
						financial_year = original_date.year
						finalcial_month = original_date.strftime("%b")
						original_date = original_date.strftime('%d-%m-%Y')
					invoice_id = seles_data.sales_id
					sales_amended_from = seles_data.sales_amended
					sales_id = seles_data.sales_id
					customer_address = seles_data.customer_address
					gstin_and_place_of_supply = seles_data.gstin_and_place_of_supply
					shipping_address_name = seles_data.shipping_address_name
					gst_state_number = ""
					gst_state = ""
					party_gsstin = ""
					if shipping_address_name:
						if gstin_and_place_of_supply == 1:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
						elif gstin_and_place_of_supply == 0:
							shipping_address = get_address_details(shipping_address_name)
							for bill in shipping_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
					else:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
					original_gst_state_number = ""
					original_gst_state = ""
					original_party_gsstin = ""
					if sales_amended_from is not None:
						gstin_and_place_of_supply,shipping_address_name,customer_address = frappe.db.get_value('Sales Order',sales_amended_from,['gstin_and_place_of_supply','shipping_address_name','customer_address'])
						
						if shipping_address_name:
							if gstin_and_place_of_supply == 1:
								billing_address = get_address_details(customer_address)
								for bill in billing_address:
									original_gst_state_number = bill.gst_state_number
									original_gst_state = bill.gst_state
									original_party_gsstin = bill.gstin
							elif gstin_and_place_of_supply == 0:
								shipping_address = get_address_details(shipping_address_name)
								for bill in shipping_address:
									original_gst_state_number = bill.gst_state_number
									original_gst_state = bill.gst_state
									original_party_gsstin = bill.gstin
						else:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								original_gst_state_number = bill.gst_state_number
								original_gst_state = bill.gst_state
								original_party_gsstin = bill.gstin
					else:
						original_gst_state_number = gst_state_number
						original_gst_state = gst_state
						original_party_gsstin = party_gsstin
					allocated_amount = seles_data.allocated_amount
					advance_paid = seles_data.advance_paid
					grand_total = seles_data.grand_total
					place_of_supply = seles_data.state
					net_total = seles_data.net_total
					additional_discount_percentage = seles_data.additional_discount_percentage
					selas_taxes = sales_taxes_charges(invoice_id)
					payment_entry_id = seles_data.entry_id
					creation = seles_data.creation
					creation = creation.date()
					fiscal_year = frappe.defaults.get_user_default("fiscal_year")
					creation = creation.strftime('%d-%m-%Y')
					modified = seles_data.modified
					modified = modified.date()
					modified = modified.strftime('%d-%m-%Y')
					gstin = seles_data.gstin
					taxable_value = 0.0
					tax_rate = 0.0
					tax_rate_sgst = 0.0
					tax_rate_cgst = 0.0
					tax_rate_igst = 0.0
					cess_amount = 0.0
					advance_adjust = 0.0
					total_ad_recieve = total_ad_recieve + allocated_amount
					total_ad_adjusted = total_ad_adjusted + advance_adjust
					advance_pending = allocated_amount - advance_adjust
					totla_pending = totla_pending + advance_pending
					for taxes in selas_taxes:
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
							tax_rate_sgst = taxes.rate	
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
							tax_rate_cgst = taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
							tax_rate_igst = taxes.rate
					taxable_value = advance_pending/(1 + tax_rate/100)
					total_taxable = total_taxable + taxable_value
					igst_amount = (taxable_value * tax_rate_igst)/100
					sgst_amount = (taxable_value * tax_rate_sgst)/100
					cgst_amount = (taxable_value * tax_rate_cgst)/100
					total_isgt = total_isgt + igst_amount
					total_ssgt = total_ssgt + sgst_amount
					total_csgt = total_csgt + cgst_amount

					self.data.append([str(fiscal_year),str(finalcial_month)+"-"+str(financial_year),
							str(original_gst_state_number)+"-"+str(original_gst_state),str(original_date)
							,str(original_voucher_no),str(creation),str(payment_entry_id),str(party_gsstin),
							str(customer_address),str(gst_state_number)+"-"+str(gst_state),str(invoice_id),
							str(tax_rate),str(allocated_amount),str(advance_adjust),
							str(advance_pending),str(taxable_value),str(igst_amount),
							str(sgst_amount),str(cgst_amount)])
			self.data.append(["","","","","","","",""])
			self.data.append(["","","","","","","","","","","","Total",total_ad_recieve,total_ad_adjusted,
					totla_pending,total_taxable,total_isgt,total_ssgt,total_csgt])

		elif self.filters.get("type_of_business") == "ATADJ":
			cess_amount = 0.0
			total_ad_recieve = 0.0
			total_ad_adjusted = 0.0
			totla_pending = 0.0
			total_taxable = 0.0
			total_isgt = 0.0
			total_ssgt = 0.0
			total_csgt = 0.0
			pending_amount = 0.0
			columns = self.get_columns_atadj()
			atadj_sales = order_invoice_sales(from_date,to_date)
			for atadj in atadj_sales:
				order_total = atadj.order_total
				invoice_total = atadj.invoice_total
				if order_total > invoice_total:
					order_id = atadj.order_id
					invoice_id = atadj.invoice_id
					grand_total = atadj.grand_total
					allocated_amount = atadj.allocated_amount
					payment_entry = atadj.parent
					customer_address = atadj.customer_address
					shipping_address_name = atadj.shipping_address_name
					gstin_and_place_of_supply = atadj.gstin_and_place_of_supply
					gst_state_number = ""
					gst_state = ""
					party_gsstin = ""
					if shipping_address_name:
						if gstin_and_place_of_supply == 1:
							billing_address = get_address_details(customer_address)
							for bill in billing_address:
								gst_state_number = bill.gst_state_number
								gst_statse = bill.gst_state
								party_gsstin = bill.gstin
						elif gstin_and_place_of_supply == 0:
							shipping_address = get_address_details(shipping_address_name)
							for bill in shipping_address:
								gst_state_number = bill.gst_state_number
								gst_state = bill.gst_state
								party_gsstin = bill.gstin
					else:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
					selas_taxes = sales_taxes_charges(invoice_id)
					tax_rate = 0.0
					tax_rate_sgst = 0.0
					tax_rate_cgst = 0.0
					tax_rate_igst = 0.0
					for taxes in selas_taxes:
						account_head = taxes.account_head
						if "SGST" in account_head:
							tax_rate = tax_rate + taxes.rate
							tax_rate_sgst = taxes.rate	
						elif "CGST" in account_head:
							tax_rate = tax_rate + taxes.rate
							tax_rate_cgst = taxes.rate
						elif "IGST" in account_head:
							tax_rate = taxes.rate
							tax_rate_igst = taxes.rate
					state = atadj.state
					gstin = atadj.gstin
					creation = atadj.creation
					creation = creation.date()
					creation = creation.strftime('%d-%m-%Y')
					igst_amount = (grand_total * tax_rate_igst)/100
					igst_amount = round(igst_amount)
					sgst_amount = (grand_total * tax_rate_sgst)/100
					sgst_amount = round(sgst_amount)
					cgst_amount = (grand_total * tax_rate_cgst)/100
					cgst_amount = round(cgst_amount)
					total_ad_adjusted = total_ad_adjusted + grand_total
					total_ad_recieve = total_ad_recieve + allocated_amount
					total_isgt = total_isgt + igst_amount
					total_ssgt = total_ssgt + sgst_amount
					total_csgt = total_csgt + cgst_amount
					self.data.append([creation,payment_entry,party_gsstin,customer_address,
							str(gst_state_number)+"-"+str(gst_state),order_id,tax_rate,
							allocated_amount,pending_amount,grand_total,igst_amount,cgst_amount,sgst_amount])
			self.data.append(["","","","","","","",""])
			self.data.append(["","","","","","","Total",total_ad_recieve,
					totla_pending,total_ad_adjusted,total_isgt,total_ssgt,total_csgt])

		return columns, self.data


	def get_columns_b2b(self):
		return [
			_("GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Manual Serial Number") + "::150",
			_("Invoice date") + "::150",
			_("Invoice Value") + ":Currency:180",
			_("Place Of Supply") + "::150",
			_("Reverse Charge") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Invoice Type") + "::150",
			_("E-Commerce GSTIN") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:160", 
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
			_("Invoice Value") + ":Currency:180",
			_("Place Of Supply") + "::150",
			_("Reverse Charge") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Invoice Type") + "::150",
			_("E-Commerce GSTIN") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:160", 
			_("Cess Amount") + "::120"
	
			]
	def get_columns_b2bl(self):
		return [
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Invoice date") + "::150",
			_("Invoice Value") + ":Currency:150",
			_("Place Of Supply") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:180",
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
			_("Invoice Value") + ":Currency:150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:180",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]
	def get_columns_b2bcs(self):
		return [
			_("Type") + "::150",
			_("Place Of Supply") + "::150",
			_("Invoice Value") + ":Currency:150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"

		]
	def get_columns_b2bcsa(self):
		return [
			_("Financial Year") + "::150",
			_("Original Month") + "::150",
			_("Type ") + "::150",
			_("Place Of Supply") + "::150",
			_("Invoice Value") + ":Currency:150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
	
		]
	def get_columns_exp(self):
		return [
			_(" Export Type") + "::150",
			_("Invoice Number") + ":Link/Sales Invoice:150",
			_("Invoice date ") + "::150",
			_("Invoice Value ") + ":Currency:150",
			_("Port Code") + "::150",
			_("Shipping Bill Number") + "::150",
			_("Shipping Bill Date") + "::150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:150",
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
			_("Note/Refund Voucher Value") + ":Currency:150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:150",
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
			_("Note/Refund Voucher Value") + ":Currency:150",
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + ":Currency:150",
			_("Cess Amount") + "::150",
			_("Pre GST") + "::150"
	
	
		]
	def get_columns_exemp(self):
		return [
			_("Description") + ":Link/Item:250",
			_("Nil Rated Supplies") + ":Currency:150",
			_("Exempted(other than nil rated/non GST supply)") + ":Currency:250",
			_("Non-GST Supplies") + ":Currency:150"
		]
	def get_columns_hsn(self):
		return [
			_("HSN") + "::150",
			_("Description") + "::250",
			_("UQC ") + "::150",
			_("Total Quantity") + "::150",
			_("Total Value") + "::150",
			_("Taxable Value") + ":Currency:150",
			_("Integrated Tax Amount") + ":Currency:150",
			_("Central Tax Amount") + ":Currency:150",
			_("State/UT Tax Amount") + ":Currency:150",
			_("Cess Amount") + "::150"
		
		]
	def get_columns_at(self):
		return [
			_("Date") + "::150",
			_("Voucher No.") + ":Link/Payment Entry:150",
			_("GSTIN No.") + "::250",
			_("Party ") + "::150",
			_("Place of Supply") + "::150",
			_("Reference No.") + ":Link/Sales Order:150",
			_("Rate") + "::150",
			_("Advance Received") + ":Currency:150",
			_("Advance Adjusted") + ":Currency:250",
			_("Advance Pending ") + ":Currency:150",
			_("Taxable Amount") + ":Currency:150",
			_("IGST Amt") + ":Currency:150",
			_("CGST Amt") + ":Currency:150",
			_("SGST Amt") + ":Currency:150"
		
		]
	def get_columns_ata(self):
		return [
			_("financial Year") + "::150",
			_("Original Month") + "::150",
			_("Original Place Of Supply") + "::150",
			_("Original Date") + "::150",
			_("Original Voucher Number") +":Link/Payment Entry:150",
			_("Date")+"::150",
			_("Voucherch No")+":Link/Payment Entry:150",
			_("GSTIN No.") + "::250",
			_("Party ") + "::150",
			_("Place of Supply") + "::150",
			_("Reference No.") + "::150",
			_("Rate") + "::150",
			_("Advance Received") + ":Currency:150",
			_("Advance Adjusted") + ":Currency:250",
			_("Advance Pending ") + ":Currency:150",
			_("Taxable Amount") + ":Currency:150",
			_("IGST Amt") + ":Currency:150",
			_("CGST Amt") + ":Currency:150",
			_("SGST Amt") + ":Currency:150"
		]
	def get_columns_atadj(self):
		return [
			_("Date") + "::150",
			_("Voucher No.") + ":Link/Payment Entry:150",
			_("GSTIN No.") + "::250",
			_("Party ") + "::150",
			_("Place of Supply") + "::150",
			_("Reference No.") + ":Link/Sales Order:150",
			_("Rate") + "::150",
			_("Advance Received") + ":Currency:150",
			_("Advance Pending ") + ":Currency:150",
			_("Advance Adjusted") + ":Currency:150",
			_("IGST Amt") + ":Currency:150",
			_("CGST Amt") + ":Currency:150",
			_("SGST Amt") + ":Currency:150"
		
		]

def sales_invoice_details(from_date,to_date):
	sales_invoice = frappe.db.sql("""select si.billing_address_gstin,si.customer_address,si.name,si.customer_name,
					si.posting_date,si.place_of_supply,si.is_return,si.return_against,si.shipping_address_name
					,si.manual_serial_number,si.reverse_charge,si.invoice_type,si.ecommerce_gstin,
					si.posting_date,si.amended_from,si.modified,si.grand_total,si.company_address,
					c.customer_type,si.net_total,si.gstin_and_place_of_supply,si.customer_gstin
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
					si.modified,si.grand_total,si.company_address,c.customer_type,si.shipping_address_name
					,si.gstin_and_place_of_supply,si.customer_gstin
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
def get_address_details(address_name):
	address_details = frappe.db.sql("""select gst_state_number,gst_state,gstin 
					from `tabAddress`
					where name  = %s""",(address_name), as_dict=1)
	return address_details

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
					modified,grand_total,company_address,is_return,return_against,gstin_and_place_of_supply,customer_gstin
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
					,gstin_and_place_of_supply,customer_gstin
					from `tabSales Invoice`
					where posting_date >= %s AND posting_date <= %s AND invoice_type = "Export"
					AND docstatus = 1""",(from_date,to_date), as_dict = 1)
	return sales_invoice_ex

def sales_invoice_item_expem(from_date,to_date):
	exempt_item = frappe.db.sql(""" select sii.name,si.parent,si.item_name,si.item_code,si.net_amount,i.india_gst_item_status 
					from `tabSales Invoice` sii, `tabSales Invoice Item` si , `tabItem` i 
					where sii.name = si.parent AND si.item_code = i.name 
					AND i.india_gst_item_status IN ("Nil Rated Item","Exempt Item","Non-GST Item") 
					AND sii.posting_date >= %s AND sii.posting_date <=%s
				 	AND sii.docstatus = 1""",(from_date,to_date), as_dict = 1)
		
	return exempt_item

def hsn_code_uqc_code(from_date,to_date):
	hsn_uqc = frappe.db.sql(""" select s.name,si.item_name,si.item_code,si.net_amount,si.uom,si.qty,si.gst_hsn_code
					from `tabSales Invoice` s, `tabSales Invoice Item` si
					where s.name = si.parent AND s.posting_date >= %s AND s.posting_date <= %s""",
					(from_date,to_date), as_dict = 1)
	return hsn_uqc
def sales_tax_hsn(item_code,invoice_id):
	if item_code:
		items_hsn = frappe.db.sql("""select si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type 
					from `tabSales Invoice Item` si, `tabItem Tax` it
					where si.item_code = %s AND si.parent = %s AND it.parent = si.item_code 
					""",(item_code,invoice_id), as_dict = 1)
	return items_hsn
def sales_account_tax(invoice_id):
	if invoice_id:
		account_tax = frappe.db.sql("""select account_head,rate,item_wise_tax_detail
						from `tabSales Taxes and Charges` where parent = %s """,(invoice_id),as_dict =1)
	return account_tax

def gst_hsn_doc(gst_hsn_code):
	hsn_doc = frappe.db.sql("""select name,description from `tabGST HSN Code` where  name = %s""",(gst_hsn_code), as_dict = 1)
	return hsn_doc

def gst_uqc_doc(uom):
	uqc_doc = frappe.db.sql("""select uqc_code,quantity from `tabUQC Item` where erpnext_uom_link = %s""",(uom), as_dict = 1)
	return uqc_doc

def payment_and_sales(from_date,to_date):
	temp_from_time = " 00:00:00"
	temp_to_time = " 23:59:59"
	tmp_from_date = str(from_date)+ (temp_from_time)
	tmp_to_date = str(to_date)+(temp_to_time)
	payment_sale = frappe.db.sql(""" select so.name,so.advance_paid,pr.parent,pr.allocated_amount,ad.state,so.amended_from,so.net_total
					,so.additional_discount_percentage,so.grand_total,so.creation,
					pe.name as entry_id,ad.gstin,so.customer_address,so.gstin_and_place_of_supply,so.shipping_address_name
					from `tabSales Order` so, `tabPayment Entry Reference` pr, `tabAddress` ad,
					`tabPayment Entry` pe
					where so.name = pr.reference_name AND so.customer_address = ad.name AND 
					pe.name = pr.parent AND pe.amended_from is NULL
					AND so.creation >= %s AND so.creation <= %s AND so.amended_from is NULL AND so.docstatus = 1 AND 						pe.docstatus = 1
					""",(tmp_from_date,tmp_to_date), as_dict = 1)
	return payment_sale

def payment_and_sales_amended(from_date,to_date):
	temp_from_time = " 00:00:00"
	temp_to_time = " 23:59:59"
	tmp_from_date = str(from_date)+ (temp_from_time)
	tmp_to_date = str(to_date)+(temp_to_time)
	payment_sale_amend = frappe.db.sql(""" select pe.name,per.parent,per.allocated_amount,so.name as sales_id,so.amended_from
						as sales_amended,pe.amended_from as payment_amended,so.advance_paid,pe.creation,pe.modified,
						so.docstatus as sales_doc,pe.docstatus as payment_doc,pe.creation,ad.gstin,so.customer_address,
						so.additional_discount_percentage,so.grand_total,ad.state,pe.name as entry_id,
						so.gstin_and_place_of_supply,so.shipping_address_name
						from `tabPayment Entry` pe , `tabPayment Entry Reference` per, `tabSales Order` so 
						, `tabAddress` ad
						where pe.name = per.parent AND so.name = per.reference_name  AND
						 so.customer_address = ad.name AND pe.amended_from is not NULL AND
						so.docstatus IN (1) AND pe.docstatus IN (1) AND so.creation >= %s AND so.creation <= %s
						""",(tmp_from_date,tmp_to_date), as_dict = 1)
	return payment_sale_amend

def payment_entry_amended(payment_amended_from):
	payment = frappe.db.sql("""select name,creation from `tabPayment Entry` where name = %s""",(payment_amended_from), as_dict =1)
	return payment

def amended_sales_order(customer_address):
	original_state = frappe.db.get_value('Address',customer_address,['state'])
	return original_state
def order_invoice_sales(from_date,to_date):
	temp_from_time = " 00:00:00"
	temp_to_time = " 23:59:59"
	tmp_from_date = str(from_date)+ (temp_from_time)
	tmp_to_date = str(to_date)+(temp_to_time)
	partially = frappe.db.sql("""select so.name as order_id,si.name as invoice_id,so.net_total as order_total,
				si.net_total as invoice_total,pr.allocated_amount,ad.state,ad.gstin,
				pr.parent,si.grand_total,so.creation,so.customer_address,so.gstin_and_place_of_supply,so.shipping_address_name
				from `tabSales Order` so, `tabSales Invoice` si, `tabPayment Entry Reference` pr,`tabAddress` ad
				where so.name = si.sales_order AND si.name = pr.reference_name AND so.customer_address = ad.name AND
				so.creation >= %s AND so.creation <= %s AND so.docstatus = 1 AND si.docstatus = 1""",
				(tmp_from_date,tmp_to_date), as_dict=1)
	return partially

def get_unique_state_list(sales):
	invoice_map = {}
	invoice_no = ""
	for seles_data in sales:
		amended_from = seles_data.amended_from
		if amended_from is None:
			billing_address_gstin = seles_data.billing_address_gstin
			invoice_id = seles_data.name
			if invoice_id != invoice_no:
				invoice_no = invoice_id
				manual_serial_number = seles_data.manual_serial_number
				customer_address = seles_data.customer_address
				billing_address_gstin = ""
				gstin_and_place_of_supply = seles_data.gstin_and_place_of_supply
				customer_address = seles_data.customer_address
				shipping_address_name = seles_data.shipping_address_name
				gst_state_number = ""
				gst_state = ""
				party_gsstin = ""
				if shipping_address_name:
					if gstin_and_place_of_supply == 1:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
					elif gstin_and_place_of_supply == 0:
						shipping_address = get_address_details(shipping_address_name)
						for bill in shipping_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
				else:
					billing_address = get_address_details(customer_address)
					for bill in billing_address:
						gst_state_number = bill.gst_state_number
						gst_state = bill.gst_state
						party_gsstin = bill.gstin
				place_of_supply = str(gst_state_number)+"-"+str(gst_state)
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
				or (grand_total <= float(b2c_limit) and address_details == gst_state_number)\
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
										amount_temp = items["taxable_value"]
										items["taxable_value"] = (amount_temp) + (taxable_value)
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
	invoice_no = ""
	for seles_data in sales:
		amended_from = seles_data.amended_from
		if amended_from is not None:
			invoice_id = seles_data.name
			if invoice_id != invoice_no:
				invoice_no = invoice_id
				billing_address_gstin = seles_data.billing_address_gstin
				manual_serial_number = seles_data.manual_serial_number
				customer_address = seles_data.customer_address
				billing_address_gstin = ""
				gstin_and_place_of_supply = seles_data.gstin_and_place_of_supply
				customer_address = seles_data.customer_address
				shipping_address_name = seles_data.shipping_address_name
				gst_state_number = ""
				gst_state = ""
				party_gsstin = ""
				if shipping_address_name:
					if gstin_and_place_of_supply == 1:
						billing_address = get_address_details(customer_address)
						for bill in billing_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
					elif gstin_and_place_of_supply == 0:
						shipping_address = get_address_details(shipping_address_name)
						for bill in shipping_address:
							gst_state_number = bill.gst_state_number
							gst_state = bill.gst_state
							party_gsstin = bill.gstin
				else:
					billing_address = get_address_details(customer_address)
					for bill in billing_address:
						gst_state_number = bill.gst_state_number
						gst_state = bill.gst_state
						party_gsstin = bill.gstin
				place_of_supply = str(gst_state_number)+"-"+str(gst_state)
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
										amount_temp = items["taxable_value"]
										items["taxable_value"] = (amount_temp) + (taxable_value)
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
def sales_exepted_nill(exempted_items):
	payment_tax = {}
	item_unieq_name1 = []
	item_unieq_name2 = []
	item_unieq_name3 = []
	for exempt in exempted_items:
		india_gst_item_status = exempt.india_gst_item_status
		if str(india_gst_item_status) == "Nil Rated Item":
			item_name = exempt.item_name
			net_amount = exempt.net_amount
			exempt_net_amount = 0.0
			non_net_amount = 0.0
			key = item_name
			if key in payment_tax:						
				item_entry = payment_tax[key]
				item_unieq_name1.append(item_entry["item_name"])
				uniue_name = list(set(item_unieq_name1))
				if item_name in uniue_name:
					if item_name == item_entry["item_name"]:
						qty_temp = item_entry["nill_net_amount"]
						item_entry["nill_net_amount"] = (qty_temp) + (net_amount)
				else:
					payment_tax[key] = frappe._dict({
						"item_name": key, 
						"nill_net_amount": net_amount,
						"india_gst_item_status":india_gst_item_status,
						"non_net_amount":non_net_amount,
						"exempt_net_amount":exempt_net_amount
						})
			else:
				payment_tax[key] = frappe._dict({
					"item_name": key, 
					"nill_net_amount": net_amount,
					"india_gst_item_status":india_gst_item_status,
					"non_net_amount":non_net_amount,
					"exempt_net_amount":exempt_net_amount
					})		
		elif str(india_gst_item_status) == "Exempt Item":
			item_name = exempt.item_name
			net_amount = exempt.net_amount
			non_net_amount = 0.0
			nill_net_amount = 0.0
			key = item_name
			if key in payment_tax:						
				item_entry = payment_tax[key]
				item_unieq_name2.append(item_entry["item_name"])
				uniue_name = list(set(item_unieq_name2))
				if item_name in uniue_name:
					if item_name == item_entry["item_name"]:
						qty_temp = item_entry["exempt_net_amount"]
						item_entry["exempt_net_amount"] = (qty_temp) + (net_amount)
				else:
					payment_tax[key] = frappe._dict({
						"item_name": key, 
						"exempt_net_amount": net_amount,
						"india_gst_item_status":india_gst_item_status,
						"non_net_amount":non_net_amount,
						"nill_net_amount":nill_net_amount
						})
			else:
				payment_tax[key] = frappe._dict({
					"item_name": key, 
					"exempt_net_amount": net_amount,
					"india_gst_item_status":india_gst_item_status,
					"non_net_amount":non_net_amount,
					"nill_net_amount":nill_net_amount
					})
			
		elif str(india_gst_item_status) == "Non-GST Item":
			item_name = exempt.item_name
			net_amount = exempt.net_amount
			exempt_net_amount = 0.0
			nill_net_amount = 0.0
			key = item_name
			if key in payment_tax:						
				item_entry = payment_tax[key]
				item_unieq_name3.append(item_entry["item_name"])
				uniue_name = list(set(item_unieq_name3))
				if item_name in uniue_name:
					if item_name == item_entry["item_name"]:
						qty_temp = item_entry["non_net_amount"]
						item_entry["non_net_amount"] = (qty_temp) + (net_amount)
				else:
					payment_tax[key] = frappe._dict({
						"item_name": key, 
						"non_net_amount": net_amount,
						"india_gst_item_status":india_gst_item_status,
						"exempt_net_amount":exempt_net_amount,
						"non_net_amount":non_net_amount
						})
			else:
				payment_tax[key] = frappe._dict({
					"item_name": key, 
					"non_net_amount": net_amount,
					"india_gst_item_status":india_gst_item_status,
					"exempt_net_amount":exempt_net_amount,
					"nill_net_amount":nill_net_amount
					})

	
	return payment_tax
def get_hsn_uqc_list(sales):
	invoice_map = {}
	item_tax_rate = 0.0
	integrated_tax_amount = 0.0
	central_tax_amount = 0.0
	state_tax_amount = 0.0
	total_value = 0.0
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
		if gst_hsn_code is not None:
			if len(tax_data) != 0:
				for data in tax_data:
					tax_rate = data.tax_rate
					tax_type = data.tax_type
					key = gst_hsn_code
					if "SGST" in tax_type or "CGST" in tax_type:
						if  "SGST" in tax_type:
							state_tax_amount = net_amount * data.tax_rate/100
						elif "CGST" in tax_type:
							central_tax_amount = net_amount * data.tax_rate/100
					elif "IGST" in tax_type:
						
						item_tax_rate = data.tax_rate
						integrated_tax_amount = net_amount * data.tax_rate/100
				if key in invoice_map:
				    	item_entry = invoice_map[key]
					qty_temp = item_entry["net_amount"]
					qty_count = item_entry["qty"]
					item_entry["net_amount"] = (qty_temp) + (net_amount)
					item_entry["qty"] = (qty_count) + (qty)
				else :
				
					invoice_map[key] = frappe._dict({
							"tax_rate": item_tax_rate,
							"net_amount": net_amount,
							"gst_hsn_code": key,
							"state_tax_amount":state_tax_amount,
							"central_tax_amount":central_tax_amount,
							"integrated_tax_amount":integrated_tax_amount,
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
							if "SGST" in account_head or "CGST" in account_head:
								if "SGST" in account_head:
									sales_tax_rate = sales_tax_rate + details[0]
									state_tax_amount = state_tax_amount * details[0]/100
								elif  "CGST" in account_head:
									sales_tax_rate = sales_tax_rate + details[0]
									central_tax_amount = central_tax_amount * details[0]/100
							elif "IGST" in account_head:
								sales_tax_rate = details[0]
								integrated_tax_amount = net_amount * details[0]/100
							
					if gst_hsn_code in invoice_map:
						item_entry = invoice_map[gst_hsn_code]
					
						qty_temp = item_entry["net_amount"]
						qty_count = item_entry["qty"]
						item_entry["net_amount"] = (qty_temp) + (net_amount)
						item_entry["qty"] = (qty_count) + (qty)
					else:
						invoice_map[gst_hsn_code] = frappe._dict({
							"tax_rate": sales_tax_rate,
							"net_amount": net_amount,
							"gst_hsn_code": gst_hsn_code,
							"state_tax_amount":state_tax_amount,
							"central_tax_amount":central_tax_amount,
							"integrated_tax_amount":integrated_tax_amount,
							"uom":uom,
							"qty":qty,
							"item_code":item_code
							})	
	return invoice_map
	
