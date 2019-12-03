# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.utils import flt
from datetime import date
from frappe import _, throw, msgprint, utils
from frappe.model.mapper import get_mapped_doc
import ast
import datetime

def execute(filters=None):
	return Gstr1Report(filters).run()

class Gstr1Report(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.columns = []
		self.invoice_ID = ""
		self.docstatus = ""
		self.amended_from=""
		self.sales_Invoice_iD = ""
		self.item_name = ""
		self.item_code = ""
		self.invoice_type = ""
		self.billing_address_gstin =""
		self.company_address = ""
		self.customer_address = ""
		self.customer_address_bill = ""
		self.data = []
		self.value_of_invoice_data=""
		self.details_tax=""
		self.gst_state_number = 0
		self.company_gst_state_number = 0
		self.doctype = "Sales Invoice"
		self.tax_doctype = "Sales Taxes and Charges"
		self.Sales_invoice_item = "Sales Invoice Item"
		self.select_columns = """
			name as invoice_number,
			manual_serial_number,
			customer_name,
			posting_date,
			base_grand_total,
			base_rounded_total,
			customer_gstin,
			place_of_supply,
			company_gstin,
			billing_address_gstin,
			customer_address,
			reverse_charge,
			invoice_type,
			return_against,
			is_return,
			invoice_type,
			export_type,
			port_code,
			shipping_bill_number,
			shipping_bill_date,
			reason_for_issuing_document,
			grand_total,
			ecommerce_gstin,
			docstatus,
			amended_from,
			name
		"""
		self.customer_type = "Company" if self.filters.get("type_of_business") ==  "B2B" else "Individual"
		if self.filters.fetch_days_data is not None:
			self.filters.from_date = self.filters.temp_from_date
			self.filters.to_date = self.filters.temp_to_date
	def run(self):
		self.get_columns()
		self.get_gst_accounts()
		self.get_invoice_data()
		summ_data = []
		if self.invoices:
			self.get_invoice_items()
			self.get_items_based_on_tax_rate()
			self.invoice_fields = [d["fieldname"] for d in self.invoice_columns]
			self.get_data()
			sales_in = ""
			for item_list in self.data:
				sales_in = item_list[1]
				if sales_in != self.sales_Invoice_iD:
					self.sales_Invoice_iD = sales_in
					self.invoice_ID = self.sales_Invoice_iD
					self.customer_address_bill = item_list[3]
					self.docstatus = item_list[46]
					self.amended_from = item_list[47]
					self.invoice_type = item_list[48]
					self.billing_address_gstin = item_list[4]
					advance_payment_detais = self.get_Advance_Payment_details()
					now = datetime.datetime.now()
					current_year = now.year
					current_month = now.month
					invoice_items_data = self.get_invoice_items_details()
					for items in invoice_items_data:
						self.item_name = items.item_name
						self.item_code = items.item_code
						gst_hsn_code = items.gst_hsn_code
						qty = items.qty
						uom = items.uom
						rate = items.rate
						price_list_rate = items.price_list_rate
						total_disc = price_list_rate-rate
						if total_disc == 0:
							total_disc = "0"
						bill_of_supply = ""
						check_bill_of_supply=""
						docstatus = ""
						is_cancelled=""
						dealer_registered=""
						check_for_registed =""
						amended_from = ""
						original_invoice_date = ""
						original_invoice_id = ""
						Return_Filing_Quarter = ""
						original_customer_gstin = ""
						advance_reciept_date = ""
						voucher_number = ""
						advance_amount = ""
						shipping_bill_date = ""
						port_code = ""
						export_type = ""
						grand_total = 0
						shipping_bill_number = ""
						address_type = ""
						cgst_tax_rate =0
						cgst_tax_amount = 0
						sgst_tax_amount = 0
						sgst_tax_rate = 0
						igst_tax_rate = 0
						igst_tax_amount = 0
						cess_tax_amount = 0
						cess_tax_rate = 0
						customer_type = ""
						customer_gst = ""
						if len(advance_payment_detais ) != 0:
							for ad_payment in advance_payment_detais:
								party_name = ad_payment.party_name
								if str(self.customer_address_bill) == str(party_name):
									advance_reciept_date = ad_payment.creation
									voucher_number = ad_payment.name
									advance_amount = ad_payment.paid_amount
								else:
									advance_reciept_date = "--"
									advance_amount = "--"
									voucher_number = "--"
						else:
							advance_reciept_date ="--"
							advance_amount = "--"
							voucher_number = "--"
						
						if self.filters.get("type_of_business") ==  "EXPORT":
							export_Details = self.value_of_invoice_data
							if self.invoice_type == "Export":
								for export_items in export_Details:
									customer_gst = export_items.customer_gstin
									bil_gstin = export_items.billing_address_gstin
									invoice_id = export_items.invoice_number
									if str(self.invoice_ID) == str(invoice_id):
										export_type = export_items.export_type
										port_code = export_items.port_code
										shipping_bill_number = export_items.shipping_bill_number
										shipping_bill_date = export_items.shipping_bill_date
										
							else:
								export_type = "--"
								port_code = "--"
								shipping_bill_number = "--"
								shipping_bill_date = "--"
							
						for invoice_value in self.value_of_invoice_data:
							self.company_address = invoice_value.company_address
							sales_invoice_id = invoice_value.invoice_number
							if self.invoice_ID in sales_invoice_id:
								grand_total = invoice_value.grand_total
								if self.amended_from is not None:
									original_invoice_date = invoice_value.posting_date
									original_invoice_id = self.amended_from
									original_customer_gstin = invoice_value.customer_gstin
								else:
									original_invoice_date = "--"
									original_invoice_id = "--"
									original_customer_gstin = "--"
								if current_month >= 1 and current_month <=3:
									Return_Filing_Quarter = "Jan - March  "+str(current_year)
								if current_month >= 4 and current_month <=6:
									Return_Filing_Quarter = "April - Jun  "+str(current_year)
								if current_month >= 7 and current_month <=9:
									Return_Filing_Quarter = "Jul - Sep  "+str(current_year)
								if current_month >= 10 and current_month <=12:
									Return_Filing_Quarter = "Oct - Dec  "+str(current_year)
								if self.docstatus == 2:
									is_cancelled = "Yes"
								elif self.docstatus == 1:
									is_cancelled = "No"
								bill_of_supply = invoice_value.bill_of_supply
								self.customer_address =invoice_value.customer_address
								docstatus = invoice_value. status
								if bill_of_supply == 1:
									check_bill_of_supply = "Yes"
								else:
									check_bill_of_supply = "No"					
						tax_data_details = self.get_tax_details()
						for items_data in tax_data_details:
							if "cgst_rate" in items_data:
								cgst_tax_rate = items_data["cgst_rate"]
							else:
								cgst_tax_rate = "--"
							if "cgst_amount" in items_data:
								cgst_tax_amount = items_data["cgst_amount"]
							else:
								cgst_tax_amount = "--"
							if "sgst_rate" in items_data:
								sgst_tax_rate = items_data["cgst_rate"]
							else:
								sgst_tax_rate = "--"
							if "sgst_amount" in items_data:
								sgst_tax_amount = items_data["sgst_amount"]
							else:
								sgst_tax_amount = "--"
							if "igst_rate" in items_data:
								igst_tax_rate = items_data["igst_rate"]
							else:
								igst_tax_rate = "--"
							if "igst_amount" in items_data:
								igst_tax_amount = items_data["igst_amount"]
							else:
								igst_tax_amount = "--"
							if "cess_rate" in items_data:
								cess_tax_rate = items_data["cess_rate"]
							else:
								cess_tax_rate = "--"
							if "cess_amount" in items_data:
								cess_tax_amount = items_data["cess_amount"]
							else:
								cess_tax_amount = "--"
						item_good_service =""
						gst_item_status = ""
						item_code,is_the_item_is_good_or_serivce,item_status = self.get_Item_details()
						if item_code:
							if is_the_item_is_good_or_serivce != None:
								if "Service" == str(is_the_item_is_good_or_serivce):
									item_good_service = is_the_item_is_good_or_serivce
								elif "Goods" == str(is_the_item_is_good_or_serivce):
									item_good_service = is_the_item_is_good_or_serivce
							else :
								item_good_service ="--"
							if item_status is not None:
								if "Nil Rated Item" == str(item_status):
									gst_item_status = item_status
								elif "Exempt Item" == str(item_status):
									gst_item_status = item_status
								elif "Non-GST Item" == str(item_status):
									gst_item_status = item_status
								elif "Composition Dealer " == str(item_status):
									gst_item_status = item_status
								elif "UIN Restration changes " == str(item_status):
									gst_item_status = item_status
							else :
								gst_item_status = "--"
						city = ""
						state =""
						gst_state_number = ""
						name,city,state,gst_state_number = self.get_contact_details()
						if name:
							if str(name) == self.customer_address:
								if city is None:
									city = "--"
								if state is None:
									state = "--"
						else:
							city = "--"
							state = "--"
						has_gst_or_idt = ""
						for taxs_name in self.details_tax:
							invoice_id = taxs_name[0]
							if invoice_id in self.invoice_ID:
								acount_head = taxs_name[1]
								if "CGST" in acount_head or "SGST" in acount_head or "IGST" in acount_head:
									has_gst_or_idt = "YES"
								else:
									has_gst_or_idt = "NO"
						b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
						address_details = self.address_gst_number()
						customer_gst = self.customer_gst_Status()
						gst_status = ""
						composition = ""
						for custum in customer_gst:
							customer_status = custum.gst_status
							if self.billing_address_gstin is None:
								
								if custum.gst_status:
									gst_status = custum.gst_status
								else:
									gst_status = "--"
							if "Composite Dealer" == str(customer_status) or "UIN Holder" == str(customer_status):
								composition = "Yes"
							else :
								composition = "No"
						gst_bill_state_number = 0
						if self.customer_type == "Company":
							if self.filters.get("type_of_business") ==  "B2B":
								summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
								item_list[4],gst_status,item_list[6],
								item_good_service, self.item_name,gst_hsn_code, 
								qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
								cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
								igst_tax_amount,cess_tax_rate,cess_tax_amount,check_bill_of_supply,
								gst_item_status,item_list[25],export_type,port_code,
								shipping_bill_number,shipping_bill_date,has_gst_or_idt,
								item_list[31], item_list[32],city,state,is_cancelled,composition,
								Return_Filing_Quarter,original_invoice_date,original_invoice_id,
								original_customer_gstin,item_list[41],advance_reciept_date,
								voucher_number,advance_amount, item_list[45],
								item_list[46], item_list[47], item_list[48]])
						elif self.customer_type == "Individual":
							if self.filters.get("type_of_business") ==  "B2C Large":
								if grand_total > float(b2c_limit) and address_details != gst_state_number:
									summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
									item_list[4],gst_status,item_list[6],
									item_good_service, self.item_name,gst_hsn_code, 
									qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
									cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
									igst_tax_amount,cess_tax_rate,cess_tax_amount,check_bill_of_supply,
									gst_item_status,item_list[25],export_type,port_code,
									shipping_bill_number,shipping_bill_date,has_gst_or_idt,
									item_list[31], item_list[32],city,state,is_cancelled,composition,
									Return_Filing_Quarter,original_invoice_date,original_invoice_id,
									original_customer_gstin,item_list[41],advance_reciept_date,
									voucher_number,advance_amount, item_list[45],
									item_list[46], item_list[47], item_list[48]])
							elif self.filters.get("type_of_business") ==  "B2C Small":
								if grand_total <= float(b2c_limit) and address_details != gst_state_number:
									summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
									item_list[4],gst_status,item_list[6],
									item_good_service, self.item_name,gst_hsn_code, 
									qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
									cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
									igst_tax_amount,cess_tax_rate,cess_tax_amount,check_bill_of_supply,
									gst_item_status,item_list[25],export_type,port_code,
									shipping_bill_number,shipping_bill_date,has_gst_or_idt,
									item_list[31], item_list[32],city,state,is_cancelled,composition,
									Return_Filing_Quarter,original_invoice_date,original_invoice_id,
									original_customer_gstin,item_list[41],advance_reciept_date,
									voucher_number,advance_amount, item_list[45],
									item_list[46], item_list[47], item_list[48]])
								elif grand_total <= float(b2c_limit) and address_details == gst_state_number:
									summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
									item_list[4],gst_status,item_list[6],
									item_good_service, self.item_name,gst_hsn_code, 
									qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
									cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
									igst_tax_amount,cess_tax_rate,cess_tax_amount,check_bill_of_supply,
									gst_item_status,item_list[25],export_type,port_code,
									shipping_bill_number,shipping_bill_date,has_gst_or_idt,
									item_list[31], item_list[32],city,state,is_cancelled,composition,
									Return_Filing_Quarter,original_invoice_date,original_invoice_id,
									original_customer_gstin,item_list[41],advance_reciept_date,
									voucher_number,advance_amount, item_list[45],
									item_list[46], item_list[47], item_list[48]])
								elif grand_total >= float(b2c_limit) and address_details == gst_state_number:
									summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
									item_list[4],gst_status,item_list[6],
									item_good_service, self.item_name,gst_hsn_code, 
									qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
									cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
									igst_tax_amount,cess_tax_rate,cess_tax_amount,check_bill_of_supply,
									gst_item_status,item_list[25],export_type,port_code,
									shipping_bill_number,shipping_bill_date,has_gst_or_idt,
									item_list[31], item_list[32],city,state,is_cancelled,composition,
									Return_Filing_Quarter,original_invoice_date,original_invoice_id,
									original_customer_gstin,item_list[41],advance_reciept_date,
									voucher_number,advance_amount, item_list[45],
									item_list[46], item_list[47], item_list[48]])
						if self.filters.get("type_of_business") ==  "EXPORT":
							summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
							item_list[4],gst_status,item_list[6],
							item_good_service, self.item_name,gst_hsn_code, 
							qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
							cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
							igst_tax_amount,cess_tax_rate,cess_tax_amount,check_bill_of_supply,
							gst_item_status,item_list[25],export_type,port_code,
							shipping_bill_number,shipping_bill_date,has_gst_or_idt,
							item_list[31], item_list[32],city,state,is_cancelled,composition,
							Return_Filing_Quarter,original_invoice_date,original_invoice_id,
							original_customer_gstin,item_list[41],advance_reciept_date,
							voucher_number,advance_amount, item_list[45],
							item_list[46], item_list[47], item_list[48]])
							#summ_data.append(["","","","","",""])
						if self.filters.get("type_of_business") ==  "CDNR":
							summ_data.append([item_list[0], item_list[1], item_list[2],item_list[3],
							item_list[4],gst_status,item_list[6],
							item_good_service, self.item_name,gst_hsn_code, 
							qty, uom, rate,total_disc,price_list_rate,cgst_tax_rate ,
							cgst_tax_amount,sgst_tax_rate,sgst_tax_amount,igst_tax_rate,
							igst_tax_amount,cess_tax_rate,cess_tax_amount,composition,
							gst_item_status,item_list[25],export_type,port_code,
							shipping_bill_number,shipping_bill_date,has_gst_or_idt,
							item_list[31], item_list[32],city,state,is_cancelled,check_for_registed,
							Return_Filing_Quarter,original_invoice_date,original_invoice_id,
							original_customer_gstin,item_list[41],advance_reciept_date,
							voucher_number,advance_amount, item_list[45],
							item_list[46], item_list[47], item_list[48]])
		return self.columns, summ_data

	def get_data(self):
		for inv, items_based_on_rate in self.items_based_on_tax_rate.items():
			invoice_details = self.invoices.get(inv)
			for rate, items in items_based_on_rate.items():
				row, taxable_value = self.get_row_data_for_invoice(inv, invoice_details, rate, items)
				if self.filters.get("type_of_business") ==  "B2C Small":
					row.append("E" if invoice_details.ecommerce_gstin else "OE")
				if self.filters.get("type_of_business") ==  "CDNR":
					row.append("Y" if invoice_details.posting_date <= date(2017, 7, 1) else "N")
					row.append("C" if invoice_details.return_against else "R")
				self.data.append(row)

	def get_row_data_for_invoice(self, invoice, invoice_details, tax_rate, items):
		row = []
		for fieldname in self.invoice_fields:
			if self.filters.get("type_of_business") ==  "CDNR" and fieldname == "invoice_value":
				row.append(abs(invoice_details.base_rounded_total) or abs(invoice_details.base_grand_total))
			elif fieldname == "invoice_value":
				row.append(invoice_details.base_rounded_total or invoice_details.base_grand_total)
			else:
				row.append(invoice_details.get(fieldname))
		taxable_value = sum([abs(net_amount)
			for item_code, net_amount in self.invoice_items.get(invoice).items() if item_code in items])
		row += [tax_rate, taxable_value]
		return row, taxable_value

	def get_invoice_data(self):
		self.invoices = frappe._dict()
		conditions = self.get_conditions()
		invoice_data = frappe.db.sql("""
			select
				{select_columns},bill_of_supply,customer_address,status,
				posting_date,docstatus,shipping_bill_number,
				shipping_bill_date,port_code,export_type,grand_total,company_address,name,customer_gstin,
				billing_address_gstin
			from `tab{doctype}`
			where docstatus NOT IN (0) {where_conditions}
			order by posting_date desc
			""".format(select_columns=self.select_columns, doctype=self.doctype,
				where_conditions=conditions), self.filters, as_dict=1)
		self.value_of_invoice_data = invoice_data
		for d in invoice_data:
			self.invoices.setdefault(d.invoice_number, d)
			
	def get_conditions(self):
		conditions = ""
		for opts in (("company", " and company=%(company)s"),
			("from_date", " and posting_date>=%(from_date)s"),
			("to_date", " and posting_date<=%(to_date)s")):
				if self.filters.get(opts[0]):
					conditions += opts[1]
		customers = frappe.get_all("Customer", filters={"customer_type": self.customer_type})
		if self.filters.get("type_of_business") ==  "B2B":
			conditions += """ and ifnull(invoice_type, '') != 'Export' and is_return != 1
				and customer in ('{0}')""".format("', '".join([frappe.db.escape(c.name) for c in customers]))
		if self.filters.get("type_of_business") in ("B2C Large", "B2C Small"):
			b2c_limit = frappe.db.get_single_value('GSt Settings', 'b2c_limit')
			if not b2c_limit:
				frappe.throw(_("Please set B2C Limit in GST Settings."))
		if self.filters.get("type_of_business") ==  "B2C Large":
			conditions += """ and SUBSTR(place_of_supply, 1, 2) != SUBSTR(company_gstin, 1, 2)
				and grand_total > {0} and is_return != 1 and customer in ('{1}')""".\
					format(flt(b2c_limit), "', '".join([frappe.db.escape(c.name) for c in customers])	)
		elif self.filters.get("type_of_business") ==  "B2C Small":
			conditions += """ and (
				SUBSTR(place_of_supply, 1, 2) = SUBSTR(company_gstin, 1, 2)
					or grand_total <= {0}) and is_return != 1 and customer in ('{1}')""".\
						format(flt(b2c_limit), "', '".join([frappe.db.escape(c.name) for c in customers]))
		elif self.filters.get("type_of_business") ==  "CDNR":
			conditions += """ and is_return = 1 """
		elif self.filters.get("type_of_business") ==  "EXPORT":
			conditions += """ and is_return !=1 and invoice_type = 'Export' """
		return conditions

	def get_invoice_items(self):
		self.invoice_items = frappe._dict()
		items = frappe.db.sql("""
			select item_code, parent, base_net_amount
			from `tab%s Item`
			where parent in (%s)
		""" % (self.doctype, ', '.join(['%s']*len(self.invoices))), tuple(self.invoices), as_dict=1)
		for d in items:
			self.invoice_items.setdefault(d.parent, {}).setdefault(d.item_code, d.base_net_amount)

	def get_invoice_items_details(self):
		sales_invoice_items = []
		if self.invoice_ID:
			sales_invoice_id = str(self.invoice_ID)
			doc = frappe.get_doc("Sales Invoice",sales_invoice_id)
			sales_invoice_items = doc.items
		return sales_invoice_items

	def get_items_based_on_tax_rate(self):
		self.tax_details = frappe.db.sql("""
			select
				parent, account_head, item_wise_tax_detail,
				base_tax_amount_after_discount_amount
			from `tab%s`
			where
				parenttype = %s and parent in (%s)
			order by account_head
		""" % (self.tax_doctype, '%s', ', '.join(['%s']*len(self.invoices.keys()))),
			tuple([self.doctype] + self.invoices.keys()))
		self.details_tax =self.tax_details
		self.items_based_on_tax_rate = {}
		self.invoice_cess = frappe._dict()
		unidentified_gst_accounts = []
		for parent, account, item_wise_tax_detail, tax_amount in self.tax_details:
			if account in self.gst_accounts.cess_account:
				self.invoice_cess.setdefault(parent, tax_amount)
			else:
				if item_wise_tax_detail:
					try:
						item_wise_tax_detail = json.loads(item_wise_tax_detail)
						cgst_or_sgst = False
						if account in self.gst_accounts.cgst_account \
							or account in self.gst_accounts.sgst_account:
							cgst_or_sgst = True
						if not (cgst_or_sgst or account in self.gst_accounts.igst_account):
							if "gst" in account.lower() and account not in unidentified_gst_accounts:
								unidentified_gst_accounts.append(account)
							continue
						for item_code, tax_amounts in item_wise_tax_detail.items():
							tax_rate = tax_amounts[0]
							if cgst_or_sgst:
								tax_rate *= 2
							rate_based_dict = self.items_based_on_tax_rate\
								.setdefault(parent, {}).setdefault(tax_rate, [])
							if item_code not in rate_based_dict:
								rate_based_dict.append(item_code)
					except ValueError:
						continue
		if unidentified_gst_accounts:
			frappe.msgprint(_("Following accounts might be selected in GST Settings:")
				+ "<br>" + "<br>".join(unidentified_gst_accounts), alert=True)

	def get_tax_details(self):
		tax_data = []
		tax_data_json = {}
		for tax_list in self.tax_details:
			tax_invoice_id = tax_list[0]
			gst_rate = tax_list[2]
			account_head = tax_list[1]
			cgst_rate = 0
			cgst_amount = 0
			sgst_rate = 0
			sgst_amount = 0
			igst_rate = 0
			igst_amount = 0
			convert_dict = ast.literal_eval(gst_rate)
			if tax_invoice_id == self.invoice_ID:
				if self.item_code in convert_dict:
					tax_rate = convert_dict.get(self.item_code)
					if "CGST" in account_head:
						cgst_rate = tax_rate[0]
						cgst_amount = tax_rate[1]
						tax_data_json['cgst_rate'] = cgst_rate
						tax_data_json['cgst_amount'] = cgst_amount
						tax_data.append(tax_data_json)
					elif "SGST" in account_head:
						sgst_rate = tax_rate[0]
						sgst_amount = tax_rate[1]
						tax_data_json['sgst_rate'] = sgst_rate
						tax_data_json['sgst_amount'] = sgst_amount
						tax_data.append(tax_data_json)
					elif "IGST" in account_head:
						igst_rate = tax_rate[0]
						igst_amount = tax_rate[1]
						tax_data_json['igst_rate'] = igst_rate
						tax_data_json['igst_amount'] = igst_amount
						tax_data.append(tax_data_json)
					elif "CESS" in account_head:
						cess_rate = tax_rate[0]
						cess_amount = tax_rate[1]
						tax_data_json['cess_rate'] = cess_rate
						tax_data_json['cess_amount'] = cess_amount
						tax_data.append(tax_data_json)
		return tax_data

	def get_contact_details(self):
		name = ""
		city = ""
		state = ""
		address_type = ""
		gst_state_number =""
		if self.customer_address:
			name,city,state,gst_state_number = frappe.db.get_value('Address',self.customer_address,
			['name','city','state','gst_state_number'])
		return name,city,state,gst_state_number

	def get_Advance_Payment_details(self):
		if self.customer_address_bill:
			payment_data = frappe.get_list("Payment Entry", {"party_name":self.customer_address_bill},
			["paid_amount","name","creation","party_name"])
			return payment_data
		else:
			return None

	def get_Item_details(self):
		item_code = ""
		is_the_item_is_good_or_serivce = ""
		item_status = ""
		if self.item_code:
			item_code,is_the_item_is_good_or_serivce,item_status = frappe.db.get_value('Item',self.item_code,
			['item_code',"item_goods_or_service","india_gst_item_status"])
		return item_code,is_the_item_is_good_or_serivce,item_status

	def address_gst_number(self):
		address_detail = frappe.get_list("Address",["address_type","gst_state_number","name"])
		for itrate_address in address_detail:
			name = itrate_address.name
			if name == self.company_address:
				self.company_gst_state_number  = itrate_address.gst_state_number
		return self.company_gst_state_number
	def customer_gst_Status(self):
		customer_details = ""
		if self.customer_address_bill:
			customer_details = frappe.get_list("Customer", {"name":self.customer_address_bill},
			["gst_status"])
		return customer_details

	def get_gst_accounts(self):
		self.gst_accounts = frappe._dict()
		gst_settings_accounts = frappe.get_list("GST Account",
			filters={"parent": "GST Settings", "company": self.filters.company},
			fields=["cgst_account", "sgst_account", "igst_account", "cess_account"])
		if not gst_settings_accounts:
			frappe.throw(_("Please set GST Accounts in GST Settings"))
		for d in gst_settings_accounts:
			for acc, val in d.items():
				self.gst_accounts.setdefault(acc, []).append(val)

	def get_columns(self):
		self.tax_columns = [
		]
		self.other_columns = []
		if self.filters.get("type_of_business") ==  "B2B":
			self.invoice_columns = [
				{
					"fieldname": "posting_date",
					"label": "Invoice date",
					"fieldtype": "Date",
					"width":80
				},
				{
					"fieldname": "invoice_number",
					"label": "Invoice Number",
					"fieldtype": "Link",
					"options": "Sales Invoice",
					"width":100
				},
				{
					"fieldname": "manual_serial_number",
					"label": "Manual Serial Number",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_name",
					"label": "Customer Billing Name",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "billing_address_gstin",
					"label": "Customer Billing GSTIN",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"fieldname": "gst_status",
					"label": "GST Status",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "place_of_supply",
					"label": "State Place of Supply",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "item_good_service",
					"label": "Is the item a GOOD (G) or SERVICE (S)",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "item_name",
					"label": "Item Description",
					"fieldtype": "Data",
					"width":200
				},
				{
					"fieldname": "gst_hsn_code",
					"label": "HSN or SAC code",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "qty",
					"label": "Item Quantity",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "uom",
					"label": "Item Unit of Measurement",
					"fieldtype": "Link",
					"options": "UOM",
					"width":180
				},
				{
					"fieldname": "rate",
					"label": "Item Rate",
					"fieldtype": "Currency",
					"width":90
				},
				{
					"fieldname": "total_disc",
					"label": "Total Item Discount Amount",
					"fieldtype": "Currency",
					"width":180
				},
				{
					"fieldname": "price_list_rate",
					"label": "Item Taxable Value",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cgst_tax_rate",
					"label": "CGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cgst_tax_amount",
					"label": "CGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "sgst_tax_rate",
					"label": "SGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "sgst_tax_amount",
					"label": "SGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "igst_tax_rate",
					"label": "IGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "igst_tax_amount",
					"label": "IGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cess_tax_rate",
					"label": "CESS Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cess_tax_amount",
					"label": "CESS Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "check_bill_of_supply",
					"label": "Is this a Bill of Supply?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "nil_rate_non_gst",
					"label": "Is this a Nil Rated/Exempt/NonGST item?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "reverse_charge",
					"label": "Reverse Charge",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "export_type",
					"label": "Type of Export",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "port_code",
					"label": "Shipping Port Code - Export",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "shipping_bill_number",
					"label": "Shipping Bill Number - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "shipping_bill_date",
					"label": "Shipping Bill Date - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "has_gst_or_idt",
					"label": "Has GST/IDT TDS been deducted",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "company_gstin",
					"label": "MY GSTIN",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_address",
					"label": "Customer Billing Address",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "city",
					"label": "Customer Billing City",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "state",
					"label": "Customer Billing State",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "is_cancelled",
					"label": "Is this document cancelled?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "check_for_registed",
					"label": "Is the customer a Composition dealer or UIN registered?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "Return_Filing_Quarter",
					"label": "Return Filing Quarter",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "original_invoice_date",
					"label": "Original Invoice Date (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_invoice_id",
					"label": "Original Invoice Number (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_customer_gstin",
					"label": "Original Customer Billing GSTIN (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "ecommerce_gstin",
					"label": "GSTIN of Ecommerce Marketplace",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_reciept_date",
					"label": "Date of Linked Advance Receipt",
					"fieldtype": "Date",
					"width":180
				},
				{
					"fieldname": "voucher_number",
					"label": "Voucher Number of Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_amount",
					"label": "Adjustment Amount of the Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "grand_total",
					"label": "Total Transaction Value",
					"fieldtype": "Currency",
					"width":140
				},
				{
					"fieldname": "docstatus",
					"label": "Docstatus",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "amended_from",
					"label": "amended_from",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "invoice_type",
					"label": "invoice_type",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				}
			]
				
			self.other_columns = [
				]
		elif self.filters.get("type_of_business") ==  "B2C Large":
			self.invoice_columns = [
				{
					"fieldname": "posting_date",
					"label": "Invoice date",
					"fieldtype": "Date",
					"width":80
				},
				{
					"fieldname": "invoice_number",
					"label": "Invoice Number",
					"fieldtype": "Link",
					"options": "Sales Invoice",
					"width":100
				},
				{
					"fieldname": "manual_serial_number",
					"label": "Manual Serial Number",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_name",
					"label": "Customer Billing Name",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "billing_address_gstin",
					"label": "Customer Billing GSTIN",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"fieldname": "gst_status",
					"label": "GST Status",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "place_of_supply",
					"label": "State Place of Supply",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "item_good_service",
					"label": "Is the item a GOOD (G) or SERVICE (S)",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "item_name",
					"label": "Item Description",
					"fieldtype": "Data",
					"width":200
				},
				{
					"fieldname": "gst_hsn_code",
					"label": "HSN or SAC code",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "qty",
					"label": "Item Quantity",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "uom",
					"label": "Item Unit of Measurement",
					"fieldtype": "Link",
					"options": "UOM",
					"width":180
				},
				{
					"fieldname": "rate",
					"label": "Item Rate",
					"fieldtype": "Currency",
					"width":90
				},
				{
					"fieldname": "total_disc",
					"label": "Total Item Discount Amount",
					"fieldtype": "Currency",
					"width":180
				},
				{
					"fieldname": "price_list_rate",
					"label": "Item Taxable Value",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cgst_tax_rate",
					"label": "CGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cgst_tax_amount",
					"label": "CGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "sgst_tax_rate",
					"label": "SGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "sgst_tax_amount",
					"label": "SGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "igst_tax_rate",
					"label": "IGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "igst_tax_amount",
					"label": "IGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cess_tax_rate",
					"label": "CESS Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cess_tax_amount",
					"label": "CESS Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "check_bill_of_supply",
					"label": "Is this a Bill of Supply?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "nil_rate_non_gst",
					"label": "Is this a Nil Rated/Exempt/NonGST item?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "reverse_charge",
					"label": "Reverse Charge",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "export_type",
					"label": "Type of Export",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "port_code",
					"label": "Shipping Port Code - Export",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "shipping_bill_number",
					"label": "Shipping Bill Number - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "shipping_bill_date",
					"label": "Shipping Bill Date - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "has_gst_or_idt",
					"label": "Has GST/IDT TDS been deducted",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "company_gstin",
					"label": "MY GSTIN",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_address",
					"label": "Customer Billing Address",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "city",
					"label": "Customer Billing City",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "state",
					"label": "Customer Billing State",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "is_cancelled",
					"label": "Is this document cancelled?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "check_for_registed",
					"label": "Is the customer a Composition dealer or UIN registered?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "Return_Filing_Quarter",
					"label": "Return Filing Quarter",
					"fieldtype": "Data",
					"width":150
				},	
				{
					"fieldname": "original_invoice_date",
					"label": "Original Invoice Date (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_invoice_id",
					"label": "Original Invoice Number (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_customer_gstin",
					"label": "Original Customer Billing GSTIN (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "ecommerce_gstin",
					"label": "GSTIN of Ecommerce Marketplace",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_reciept_date",
					"label": "Date of Linked Advance Receipt",
					"fieldtype": "Date",
					"width":180
				},
				{
					"fieldname": "voucher_number",
					"label": "Voucher Number of Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_amount",
					"label": "Adjustment Amount of the Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "grand_total",
					"label": "Total Transaction Value",
					"fieldtype": "Currency",
					"width":140
				},
				{
					"fieldname": "docstatus",
					"label": "Docstatus",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "amended_from",
					"label": "amended_from",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "invoice_type",
					"label": "invoice_type",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				}
			]
			self.other_columns = [
				]
		elif self.filters.get("type_of_business") ==  "CDNR":
			self.invoice_columns = [
				{
					"fieldname": "posting_date",
					"label": "Invoice date",
					"fieldtype": "Date",
					"width":80
				},
				{
					"fieldname": "invoice_number",
					"label": "Invoice Number",
					"fieldtype": "Link",
					"options": "Sales Invoice",
					"width":100
				},
				{
					"fieldname": "manual_serial_number",
					"label": "Manual Serial Number",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_name",
					"label": "Customer Billing Name",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "billing_address_gstin",
					"label": "Customer Billing GSTIN",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"fieldname": "gst_status",
					"label": "GST Status",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "place_of_supply",
					"label": "State Place of Supply",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "item_good_service",
					"label": "Is the item a GOOD (G) or SERVICE (S)",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "item_name",
					"label": "Item Description",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "gst_hsn_code",
					"label": "HSN or SAC code",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "qty",
					"label": "Item Quantity",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "uom",
					"label": "Item Unit of Measurement",
					"fieldtype": "Link",
					"options": "UOM",
					"width":180
				},
				{
					"fieldname": "rate",
					"label": "Item Rate",
					"fieldtype": "Currency",
					"width":90
				},
				{
					"fieldname": "total_disc",
					"label": "Total Item Discount Amount",
					"fieldtype": "Currency",
					"width":180
				},
				{
					"fieldname": "price_list_rate",
					"label": "Item Taxable Value",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cgst_tax_rate",
					"label": "CGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cgst_tax_amount",
					"label": "CGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "sgst_tax_rate",
					"label": "SGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "sgst_tax_amount",
					"label": "SGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "igst_tax_rate",
					"label": "IGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "igst_tax_amount",
					"label": "IGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cess_tax_rate",
					"label": "CESS Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cess_tax_amount",
					"label": "CESS Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "check_bill_of_supply",
					"label": "Is this a Bill of Supply?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "nil_rate_non_gst",
					"label": "Is this a Nil Rated/Exempt/NonGST item?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "reverse_charge",
					"label": "Reverse Charge",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "export_type",
					"label": "Type of Export",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "port_code",
					"label": "Shipping Port Code - Export",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "shipping_bill_number",
					"label": "Shipping Bill Number - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "shipping_bill_date",
					"label": "Shipping Bill Date - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "has_gst_or_idt",
					"label": "Has GST/IDT TDS been deducted",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "company_gstin",
					"label": "MY GSTIN",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_address",
					"label": "Customer Billing Address",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "city",
					"label": "Customer Billing City",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "state",
					"label": "Customer Billing State",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "is_cancelled",
					"label": "Is this document cancelled?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "check_for_registed",
					"label": "Is the customer a Composition dealer or UIN registered?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "Return_Filing_Quarter",
					"label": "Return Filing Quarter",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "original_invoice_date",
					"label": "Original Invoice Date (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_invoice_id",
					"label": "Original Invoice Number (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_customer_gstin",
					"label": "Original Customer Billing GSTIN (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "ecommerce_gstin",
					"label": "GSTIN of Ecommerce Marketplace",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_reciept_date",
					"label": "Date of Linked Advance Receipt",
					"fieldtype": "Date",
					"width":180
				},
				{
					"fieldname": "voucher_number",
					"label": "Voucher Number of Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_amount",
					"label": "Adjustment Amount of the Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "grand_total",
					"label": "Total Transaction Value",
					"fieldtype": "Currency",
					"width":140
				},
				{
					"fieldname": "docstatus",
					"label": "Docstatus",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "amended_from",
					"label": "amended_from",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "invoice_type",
					"label": "invoice_type",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				}
			]
			self.other_columns = [
			]
		elif self.filters.get("type_of_business") ==  "B2C Small":
			self.invoice_columns = [
				{
					"fieldname": "posting_date",
					"label": "Invoice date",
					"fieldtype": "Date",
					"width":80
				},
				{
					"fieldname": "invoice_number",
					"label": "Invoice Number",
					"fieldtype": "Link",
					"options": "Sales Invoice",
					"width":100
				},
				{
					"fieldname": "manual_serial_number",
					"label": "Manual Serial Number",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_name",
					"label": "Customer Billing Name",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "billing_address_gstin",
					"label": "Customer Billing GSTIN",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"fieldname": "gst_status",
					"label": "GST Status",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "place_of_supply",
					"label": "State Place of Supply",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "item_good_service",
					"label": "Is the item a GOOD (G) or SERVICE (S)",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "item_name",
					"label": "Item Description",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "gst_hsn_code",
					"label": "HSN or SAC code",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "qty",
					"label": "Item Quantity",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "uom",
					"label": "Item Unit of Measurement",
					"fieldtype": "Link",
					"options": "UOM",
					"width":180
				},
				{
					"fieldname": "rate",
					"label": "Item Rate",
					"fieldtype": "Currency",
					"width":90
				},
				{
					"fieldname": "total_disc",
					"label": "Total Item Discount Amount",
					"fieldtype": "Currency",
					"width":180
				},
				{
					"fieldname": "price_list_rate",
					"label": "Item Taxable Value",
					"fieldtype": "Currency",
					"width":120
				},
				{		
					"fieldname": "cgst_tax_rate",
					"label": "CGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cgst_tax_amount",
					"label": "CGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "sgst_tax_rate",
					"label": "SGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "sgst_tax_amount",
					"label": "SGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "igst_tax_rate",
					"label": "IGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "igst_tax_amount",
					"label": "IGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cess_tax_rate",
					"label": "CESS Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cess_tax_amount",
					"label": "CESS Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "check_bill_of_supply",
					"label": "Is this a Bill of Supply?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "nil_rate_non_gst",
					"label": "Is this a Nil Rated/Exempt/NonGST item?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "reverse_charge",
					"label": "Reverse Charge",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "export_type",
					"label": "Type of Export",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "port_code",
					"label": "Shipping Port Code - Export",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "shipping_bill_number",
					"label": "Shipping Bill Number - Export",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "shipping_bill_date",
					"label": "Shipping Bill Date - Export",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "has_gst_or_idt",
					"label": "Has GST/IDT TDS been deducted",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "company_gstin",
					"label": "MY GSTIN",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_address",
					"label": "Customer Billing Address",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "city",
					"label": "Customer Billing City",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "state",
					"label": "Customer Billing State",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "is_cancelled",
					"label": "Is this document cancelled?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "check_for_registed",
					"label": "Is the customer a Composition dealer or UIN registered?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "Return_Filing_Quarter",
					"label": "Return Filing Quarter",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "original_invoice_date",
					"label": "Original Invoice Date (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_invoice_id",
					"label": "Original Invoice Number (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_customer_gstin",
					"label": "Original Customer Billing GSTIN (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "ecommerce_gstin",
					"label": "GSTIN of Ecommerce Marketplace",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_reciept_date",
					"label": "Date of Linked Advance Receipt",
					"fieldtype": "Date",
					"width":180
				},
				{
					"fieldname": "voucher_number",
					"label": "Voucher Number of Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_amount",
					"label": "Adjustment Amount of the Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "grand_total",
					"label": "Total Transaction Value",
					"fieldtype": "Currency",
					"width":140
				},
				{
					"fieldname": "docstatus",
					"label": "Docstatus",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "amended_from",
					"label": "amended_from",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "invoice_type",
					"label": "invoice_type",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				}
			]
			self.other_columns = [
			]
		elif self.filters.get("type_of_business") ==  "EXPORT":
			self.invoice_columns = [
				{
					"fieldname": "posting_date",
					"label": "Invoice date",
					"fieldtype": "Date",
					"width":80
				},
				{
					"fieldname": "invoice_number",
					"label": "Invoice Number",
					"fieldtype": "Link",
					"options": "Sales Invoice",
					"width":100
				},
				{
					"fieldname": "manual_serial_number",
					"label": "Manual Serial Number",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_name",
					"label": "Customer Billing Name",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "billing_address_gstin",
					"label": "Customer Billing GSTIN",
					"fieldtype": "Data",
					"width": 150
				},
				{
					"fieldname": "gst_status",
					"label": "GST Status",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "place_of_supply",
					"label": "State Place of Supply",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "item_good_service",
					"label": "Is the item a GOOD (G) or SERVICE (S)",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "item_name",
					"label": "Item Description",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "gst_hsn_code",
					"label": "HSN or SAC code",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "qty",
					"label": "Item Quantity",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "uom",
					"label": "Item Unit of Measurement",
					"fieldtype": "Link",
					"options": "UOM",
					"width":180
				},
				{
					"fieldname": "rate",
					"label": "Item Rate",
					"fieldtype": "Currency",
					"width":90
				},
				{
					"fieldname": "total_disc",
					"label": "Total Item Discount Amount",
					"fieldtype": "Currency",
					"width":180
				},
				{
					"fieldname": "price_list_rate",
					"label": "Item Taxable Value",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cgst_tax_rate",
					"label": "CGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cgst_tax_amount",
					"label": "CGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "sgst_tax_rate",
					"label": "SGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "sgst_tax_amount",
					"label": "SGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "igst_tax_rate",
					"label": "IGST Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "igst_tax_amount",
					"label": "IGST Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "cess_tax_rate",
					"label": "CESS Rate",
					"fieldtype": "Data",
					"width":120
				},
				{
					"fieldname": "cess_tax_amount",
					"label": "CESS Amount",
					"fieldtype": "Currency",
					"width":120
				},
				{
					"fieldname": "check_bill_of_supply",
					"label": "Is this a Bill of Supply?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "nil_rate_non_gst",
					"label": "Is this a Nil Rated/Exempt/NonGST item?",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "reverse_charge",
					"label": "Reverse Charge",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "export_type",
					"label": "Type of Export",
					"fieldtype": "Data",
					"width":140
				},
				{
					"fieldname": "port_code",
					"label": "Shipping Port Code - Export",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "shipping_bill_number",
					"label": "Shipping Bill Number - Export",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "shipping_bill_date",
					"label": "Shipping Bill Date - Export",
					"fieldtype": "Data",
					"width":160
				},
				{
					"fieldname": "has_gst_or_idt",
					"label": "Has GST/IDT TDS been deducted",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "company_gstin",
					"label": "MY GSTIN",
					"fieldtype": "Data",
					"width":100
				},
				{
					"fieldname": "customer_address",
					"label": "Customer Billing Address",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "city",
					"label": "Customer Billing City",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "state",
					"label": "Customer Billing State",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "is_cancelled",
					"label": "Is this document cancelled?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "check_for_registed",
					"label": "Is the customer a Composition dealer or UIN registered?",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "Return_Filing_Quarter",
					"label": "Return Filing Quarter",
					"fieldtype": "Data",
					"width":150
				},
				{
					"fieldname": "original_invoice_date",
					"label": "Original Invoice Date (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_invoice_id",
					"label": "Original Invoice Number (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "original_customer_gstin",
					"label": "Original Customer Billing GSTIN (In case of amendment)",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "ecommerce_gstin",
					"label": "GSTIN of Ecommerce Marketplace",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_reciept_date",
					"label": "Date of Linked Advance Receipt",
					"fieldtype": "Date",
					"width":180
				},
				{
					"fieldname": "voucher_number",
					"label": "Voucher Number of Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "advance_amount",
					"label": "Adjustment Amount of the Linked Advance Receipt",
					"fieldtype": "Data",
					"width":180
				},
				{
					"fieldname": "grand_total",
					"label": "Total Transaction Value",
					"fieldtype": "Currency",
					"width":140
				},
				{
					"fieldname": "docstatus",
					"label": "Docstatus",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "amended_from",
					"label": "amended_from",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				},
				{
					"fieldname": "invoice_type",
					"label": "invoice_type",
					"fieldtype": "Data",
					"width":140,
					"hidden": 1
				}
			]
		self.columns = self.invoice_columns +self.tax_columns + self.other_columns
