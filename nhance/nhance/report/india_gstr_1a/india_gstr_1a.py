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
import time
import math
import json
import ast
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	return IndiaGstr1A(filters).run()
class IndiaGstr1A(object):
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
		if self.filters.get("type_of_business") == "B2B":
			sales = self.sales_invoice_details()
			columns = self.get_columns_b2b()
			sales_count = self.sales_invoice_counts()
			total_bill_gstin = 0
			total_customer = 0
			total_taxable_vlaue = 0.0
			total_invoice_value = 0.0
			total_cess_amount = 0.0
			invoice_map = {}
			for sale in sales_count:
				total_bill_gstin = sale.bill_gstin
				total_customer = sale.customer
			for seles_data in sales:
				amended_from = seles_data.amended_from
				if amended_from == None:
					self.invoice_id = seles_data.name
					print "self.invoice_id----------",self.invoice_id
					billing_address_gstin = seles_data.billing_address_gstin
					customer_address = seles_data.customer_address
					place_of_supply = seles_data.place_of_supply
					reverse_charge = seles_data.reverse_charge
					invoice_type = seles_data.invoice_type
					ecommerce_gstin = seles_data.ecommerce_gstin
					posting_date = seles_data.posting_date
					account_head = ""
					sales_item = self.sales_item_details()
					for item in sales_item:
						self.item_code = item.item_code
						item_net_amount = item.net_amount
						tax_data = self.sales_tax()
						#print "tax_data----------",tax_data
						sales_invoice_tax_data = self.sales_account_tax()
						tax_rate_list = []
						if len(tax_data) != 0:
							for data in tax_data:
								tax_rate = data.tax_rate
								net_amount = data.net_amount
								#print "net_amount----------",net_amount
								key = self.invoice_id
								if key in invoice_map:
									item_entry = invoice_map[key]
									mapped_items_list = item_entry["mapped_items"]
									print "type of mapped_items_list-------------", (mapped_items_list,net_amount)
									new_list = []
									for mapped_items in mapped_items_list:
										tax_rate_list.append(mapped_items["tax_rate"])
										data_rate = list(set(tax_rate_list))
										print "data_rate---------",data_rate
									if tax_rate in data_rate:
										for items in mapped_items_list:
											if float(tax_rate) == float(items["tax_rate"]):
												qty_temp = items["net_amount"]
												items["net_amount"] = (qty_temp) + (net_amount)
									else:
										
										new_list.append({
												"tax_rate": tax_rate, 
										  		"net_amount": net_amount,
									                        "invoice_id": key,
												"billing_address_gstin":billing_address_gstin,
												"customer_address":customer_address,
												"place_of_supply":place_of_supply,
												"reverse_charge":reverse_charge,
												"invoice_type":invoice_type,
												"posting_date":posting_date,
												"ecommerce_gstin":ecommerce_gstin
												})
									
										item_entry["mapped_items"] = mapped_items_list + new_list
									#print "new_list--------",item_entry["mapped_items"]
								else:
									item_list = []
									item_list.append({
											"tax_rate": tax_rate, 
											"net_amount": net_amount,
										        "invoice_id": key,
											"billing_address_gstin":billing_address_gstin,
											"customer_address":customer_address,
											"place_of_supply":place_of_supply,
											"reverse_charge":reverse_charge,
											"invoice_type":invoice_type,
											"posting_date":posting_date,
											"ecommerce_gstin":ecommerce_gstin		
											})
									invoice_map[key] = frappe._dict({"mapped_items": item_list})
								
						else:
							#print "else part enter ---------"
							#print "item_net_amount----------",item_net_amount
							sales_tax_rate = 0
							total_amount = 0.0
							if len(sales_invoice_tax_data) != 0:
								for invoice_tax_data in sales_invoice_tax_data:
									account_head = invoice_tax_data.account_head
									#print "account_head----------",account_head
									item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
									#print "type of -----------",type(item_wise_tax_detail)
									converted = ast.literal_eval(item_wise_tax_detail)
									#print "else----item_code--------",self.item_code
									if self.item_code in converted:
										details = converted[self.item_code]
										if "SGST" in account_head or "CGST" in account_head:
											sales_tax_rate = sales_tax_rate + details[0]
											#print "rate ---------",addition
										elif "IGST" in account_head:
											sales_tax_rate = details[0]
											
								if self.invoice_id in invoice_map:
									item_entry = invoice_map[self.invoice_id]
									mapped_items_list = item_entry["mapped_items"]

									for mapped_items in mapped_items_list:
										tax_rate_list.append(mapped_items["tax_rate"])
										data_rate = list(set(tax_rate_list))
										#print "data_rate---------",data_rate
									if sales_tax_rate in data_rate:
										for items in mapped_items_list:
											if float(sales_tax_rate) == float(items["tax_rate"]):
												qty_temp = items["net_amount"]
												items["net_amount"] = (qty_temp) + (item_net_amount)
									else:
										mapped_items_list.append({
												"tax_rate": sales_tax_rate, 
										  		"net_amount": item_net_amount,
									                        "invoice_id": self.invoice_id,
												"billing_address_gstin":billing_address_gstin,
												"customer_address":customer_address,
												"place_of_supply":place_of_supply,
												"reverse_charge":reverse_charge,
												"invoice_type":invoice_type,
												"posting_date":posting_date,
												"ecommerce_gstin":ecommerce_gstin
												})
										item_entry["mapped_items"] = mapped_items_list
								else:
									item_list = []
									item_list.append({
											"tax_rate": sales_tax_rate, 
											"net_amount": item_net_amount,
										        "invoice_id": self.invoice_id,
											"billing_address_gstin":billing_address_gstin,
											"customer_address":customer_address,
											"place_of_supply":place_of_supply,
											"reverse_charge":reverse_charge,
											"invoice_type":invoice_type,
											"posting_date":posting_date,
											"ecommerce_gstin":ecommerce_gstin
											})
									invoice_map[self.invoice_id] = frappe._dict({"mapped_items": item_list})
			print "	invoice_map-------------",invoice_map
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					billing_address_gstin = map_data["mapped_items"][map_d]["billing_address_gstin"]
					customer_address = map_data["mapped_items"][map_d]["customer_address"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					reverse_charge = map_data["mapped_items"][map_d]["reverse_charge"]
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					self.data.append([billing_address_gstin,customer_address,invoice_no,
						posting_date,grand_total,place_of_supply,reverse_charge,"",
						invoice_type,ecommerce_gstin,rate_of_tax,tot_net_amount,""])	
			#print "self.data------out side loop----",self.data
		
		elif self.filters.get("type_of_business") == "B2BA":
			invoice_map = {}
			columns = self.get_columns_b2ba()
			sales_detail = self.sales_invoice_details()
			for sale in sales_detail:
				amended_from = sale.amended_from
				#print "amended_from----------",amended_from
				if amended_from is not None:
					self.invoice_id = sale.name
					#print "self.invoice_id----------",self.invoice_id
					billing_address_gstin = sale.billing_address_gstin
					customer_address = sale.customer_address
					place_of_supply = sale.place_of_supply
					reverse_charge = sale.reverse_charge
					invoice_type = sale.invoice_type
					ecommerce_gstin = sale.ecommerce_gstin
					posting_date = sale.posting_date
					modified_from = sale.modified
					modified = getdate(modified_from.strftime('%Y-%m-%d'))
					sales_item = self.sales_item_details()
					for item in sales_item:
						self.item_code = item.item_code
						item_net_amount = item.net_amount
						#print "self.item_code----------",self.item_code
						tax_data = self.sales_tax()
						#print "tax_data----------",tax_data
						sales_invoice_tax_data = self.sales_account_tax()
						tax_rate_list = []
						if len(tax_data) != 0:
							for data in tax_data:
								tax_rate = data.tax_rate
								net_amount = data.net_amount
								#print "net_amount----------",net_amount
								key = self.invoice_id
								if key in invoice_map:
									item_entry = invoice_map[key]
									mapped_items_list = item_entry["mapped_items"]
									#print "type of mapped_items_list-------------", (mapped_items_list,net_amount)
									new_list = []
									for mapped_items in mapped_items_list:
										tax_rate_list.append(mapped_items["tax_rate"])
										data_rate = list(set(tax_rate_list))
										#print "data_rate---------",data_rate
									if tax_rate in data_rate:
										for items in mapped_items_list:
											if float(tax_rate) == float(items["tax_rate"]):
												qty_temp = items["net_amount"]
												items["net_amount"] = (qty_temp) + (net_amount)
									else:
										
										new_list.append({
												"tax_rate": tax_rate, 
										  		"net_amount": net_amount,
									                        "invoice_id": key,
												"billing_address_gstin":billing_address_gstin,
												"customer_address":customer_address,
												"place_of_supply":place_of_supply,
												"reverse_charge":reverse_charge,
												"invoice_type":invoice_type,
												"posting_date":posting_date,
												"modified":modified,
												"amended_from":amended_from,
												"ecommerce_gstin":ecommerce_gstin
												})
									
										item_entry["mapped_items"] = mapped_items_list + new_list
									#print "new_list--------",item_entry["mapped_items"]
								else:
									item_list = []
									item_list.append({
											"tax_rate": tax_rate, 
											"net_amount": net_amount,
										        "invoice_id": key,
											"billing_address_gstin":billing_address_gstin,
											"customer_address":customer_address,
											"place_of_supply":place_of_supply,
											"reverse_charge":reverse_charge,
											"invoice_type":invoice_type,
											"posting_date":posting_date,
											"modified":modified,
											"amended_from":amended_from,
											"ecommerce_gstin":ecommerce_gstin
											})
									invoice_map[key] = frappe._dict({"mapped_items": item_list})
								
									
						else:
							#print "else part enter ---------"
							print "invoice_map----------",invoice_map
							sales_tax_rate = 0
							total_amount = 0.0
							if len(sales_invoice_tax_data) != 0:
								for invoice_tax_data in sales_invoice_tax_data:
									account_head = invoice_tax_data.account_head
									print "account_head----------",account_head
									item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
									#print "type of -----------",type(item_wise_tax_detail)
									converted = ast.literal_eval(item_wise_tax_detail)
									print "else----item_code--------",self.item_code
									if self.item_code in converted:
										details = converted[self.item_code]
										if "SGST" in account_head or "CGST" in account_head:
											sales_tax_rate = sales_tax_rate + details[0]
											#print "rate ---------",addition
										elif "IGST" in account_head:
											sales_tax_rate = details[0]
											
								if self.invoice_id in invoice_map:
									item_entry = invoice_map[self.invoice_id]
									mapped_items_list = item_entry["mapped_items"]
									

									for mapped_items in mapped_items_list:
										tax_rate_list.append(mapped_items["tax_rate"])
										data_rate = list(set(tax_rate_list))
										#print "data_rate---------",data_rate
									if sales_tax_rate in data_rate:
										for items in mapped_items_list:
											if float(sales_tax_rate) == float(items["tax_rate"]):
												qty_temp = items["net_amount"]
												items["net_amount"] = (qty_temp) + (item_net_amount)

									else:
										mapped_items_list.append({
												"tax_rate": sales_tax_rate, 
											  	"net_amount": item_net_amount,
										                "invoice_id": self.invoice_id,
												"billing_address_gstin":billing_address_gstin,
												"customer_address":customer_address,
												"place_of_supply":place_of_supply,
												"reverse_charge":reverse_charge,
												"invoice_type":invoice_type,
												"posting_date":posting_date,
												"modified":modified,
												"amended_from":amended_from,
												"ecommerce_gstin":ecommerce_gstin
												})
										item_entry["mapped_items"] = mapped_items_list
								else:
									item_list = []
									item_list.append({
											"tax_rate": sales_tax_rate, 
											"net_amount": item_net_amount,
										        "invoice_id": self.invoice_id,
											"billing_address_gstin":billing_address_gstin,
											"customer_address":customer_address,
											"place_of_supply":place_of_supply,
											"reverse_charge":reverse_charge,
											"invoice_type":invoice_type,
											"posting_date":posting_date,
											"modified":modified,
											"amended_from":amended_from,
											"ecommerce_gstin":ecommerce_gstin
											})
									invoice_map[self.invoice_id] = frappe._dict({"mapped_items": item_list})
			print "	invoice_map-------------",invoice_map
			#print "amended_from----------",amended_from
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					billing_address_gstin = map_data["mapped_items"][map_d]["billing_address_gstin"]
					customer_address = map_data["mapped_items"][map_d]["customer_address"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					reverse_charge = map_data["mapped_items"][map_d]["reverse_charge"]
					invoice_type = map_data["mapped_items"][map_d]["invoice_type"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					modified = map_data["mapped_items"][map_d]["modified"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					invoice_value = tot_net_amount * rate_of_tax /100
					grand_total = invoice_value + tot_net_amount
					self.data.append([billing_address_gstin,customer_address,amended_from,
						posting_date,invoice_no,modified,grand_total,place_of_supply,reverse_charge,"",
						invoice_type,ecommerce_gstin,rate_of_tax,tot_net_amount,""])	
			#print "self.data------out side loop----",self.data
		
		elif self.filters.get("type_of_business") == "B2CL":
			invoice_map = {}
			columns = self.get_columns_b2bl()
			sales_b = self.sales_invoice_b2bl()
			for sales_datas in sales_b:
				amended_from = sales_datas.amended_from
				if amended_from == None:
					self.invoice_id = sales_datas.name
					print "self.invoice_id--------",self.invoice_id
					posting_date = sales_datas.posting_date
					place_of_supply = sales_datas.place_of_supply
					print "place_of_supply------",place_of_supply
					ecommerce_gstin = sales_datas.ecommerce_gstin
					self.customer_address = sales_datas.customer_address
					grand_total = sales_datas.grand_total
					print "grand_total--------",grand_total
					self.company_address = sales_datas.company_address
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					if grand_total > float(b2c_limit) and address_details != gst_state_number:
						sales_item = self.sales_item_details()
						for item in sales_item:
							self.item_code = item.item_code
							item_net_amount = item.net_amount
							#print "self.item_code----------",self.item_code
							tax_data = self.sales_tax()
							#print "tax_data----------",tax_data
							sales_invoice_tax_data = self.sales_account_tax()
							tax_rate_list = []
							if len(tax_data) != 0:
								for data in tax_data:
									tax_rate = data.tax_rate
									net_amount = data.net_amount
									#print "net_amount----------",net_amount
									key = self.invoice_id
									if key in invoice_map:
										item_entry = invoice_map[key]
										mapped_items_list = item_entry["mapped_items"]
										#print "type of mapped_items_list-------------", (mapped_items_list,net_amount)
										new_list = []
										for mapped_items in mapped_items_list:
											tax_rate_list.append(mapped_items["tax_rate"])
											data_rate = list(set(tax_rate_list))
											#print "data_rate---------",data_rate
										if tax_rate in data_rate:
											for items in mapped_items_list:
												if float(tax_rate) == float(items["tax_rate"]):
													qty_temp = items["net_amount"]
													items["net_amount"] = (qty_temp) + (net_amount)
										else:
										
											new_list.append({
												"tax_rate": tax_rate, 
											  	"net_amount": net_amount,
											        "invoice_id": key,
												"posting_date":posting_date,
												 "place_of_supply":place_of_supply,	
												 "ecommerce_gstin":ecommerce_gstin
															})
									
											item_entry["mapped_items"] = mapped_items_list + new_list
										#print "new_list--------",item_entry["mapped_items"]
									else:
										item_list = []
										item_list.append({"tax_rate": tax_rate, 
												  "net_amount": net_amount,
												  "invoice_id": key,
												  "posting_date":posting_date,
												  "place_of_supply":place_of_supply,	
												  "ecommerce_gstin":ecommerce_gstin 																									
													})
										invoice_map[key] = frappe._dict({"mapped_items": item_list})
								
									
							else:
								#print "else part enter ---------"
								print "invoice_map----------",invoice_map
								sales_tax_rate = 0
								total_amount = 0.0
								if len(sales_invoice_tax_data) != 0:
									for invoice_tax_data in sales_invoice_tax_data:
										account_head = invoice_tax_data.account_head
										print "account_head----------",account_head
										item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
										#print "type of -----------",type(item_wise_tax_detail)
										converted = ast.literal_eval(item_wise_tax_detail)
										print "else----item_code--------",self.item_code
										if self.item_code in converted:
											details = converted[self.item_code]
											if "SGST" in account_head or "CGST" in account_head:
												sales_tax_rate = sales_tax_rate + details[0]
												#print "rate ---------",addition
											elif "IGST" in account_head:
												sales_tax_rate = details[0]
											
									if self.invoice_id in invoice_map:
										item_entry = invoice_map[self.invoice_id]
										mapped_items_list = item_entry["mapped_items"]
									

										for mapped_items in mapped_items_list:
											tax_rate_list.append(mapped_items["tax_rate"])
											data_rate = list(set(tax_rate_list))
											#print "data_rate---------",data_rate
										if sales_tax_rate in data_rate:
											for items in mapped_items_list:
												if float(sales_tax_rate) == float(items["tax_rate"]):
													qty_temp = items["net_amount"]
													items["net_amount"] = (qty_temp) + (item_net_amount)

										else:
											mapped_items_list.append({
												"tax_rate": sales_tax_rate, 
												"net_amount": item_net_amount,
												"invoice_id": self.invoice_id,
												"posting_date":posting_date,
												"place_of_supply":place_of_supply,	
												"ecommerce_gstin":ecommerce_gstin
														})
											item_entry["mapped_items"] = mapped_items_list
									else:
										item_list = []
										item_list.append({
												 "tax_rate": sales_tax_rate, 
												 "net_amount": item_net_amount,
												 "invoice_id": self.invoice_id,
												 "posting_date":posting_date,
												 "place_of_supply":place_of_supply,	  													"ecommerce_gstin":ecommerce_gstin				
													})
										invoice_map[self.invoice_id] = frappe._dict({"mapped_items": item_list})
			#print "	invoice_map-------------",invoice_map
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					self.data.append([invoice_no,
						posting_date,invoice_grand_total,place_of_supply,""
						,rate_of_tax,tot_net_amount,"",ecommerce_gstin])	
			#print "self.data------out side loop----",self.data
		elif self.filters.get("type_of_business") == "B2CLA":
			invoice_map = {}
			columns = self.get_columns_b2bla()
			sales_b = self.sales_invoice_b2bl()
			for sales_datas in sales_b:
				amended_from = sales_datas.amended_from
				if amended_from is not None:
					self.invoice_id = sales_datas.name
					posting_date = sales_datas.posting_date
					place_of_supply = sales_datas.place_of_supply
					ecommerce_gstin = sales_datas.ecommerce_gstin
					self.customer_address = sales_datas.customer_address
					grand_total = sales_datas.grand_total
					modified = sales_datas.modified
					modified_date = getdate(modified.strftime('%Y-%m-%d'))
					self.company_address = sales_datas.company_address
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					if grand_total > float(b2c_limit) and address_details != gst_state_number:
						sales_item = self.sales_item_details()
						for item in sales_item:
							self.item_code = item.item_code
							item_net_amount = item.net_amount
							tax_data = self.sales_tax()
							sales_invoice_tax_data = self.sales_account_tax()
							tax_rate_list = []
							if len(tax_data) != 0:
								for data in tax_data:
									tax_rate = data.tax_rate
									net_amount = data.net_amount
									key = self.invoice_id
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
													qty_temp = items["net_amount"]
													items["net_amount"] = (qty_temp) + (net_amount)
										else:
										
											new_list.append({
												"tax_rate": tax_rate, 
											  	"net_amount": net_amount,
											        "invoice_id": key,
												 "posting_date":posting_date,
												 "place_of_supply":place_of_supply,	
												 "ecommerce_gstin":ecommerce_gstin,
												 "modified_date":modified_date,
												 "amended_from":amended_from
															})
									
											item_entry["mapped_items"] = mapped_items_list + new_list
									else:
										item_list = []
										item_list.append({
												"tax_rate": tax_rate, 
												 "net_amount": net_amount,
												 "invoice_id": key,
												 "posting_date":posting_date,
												 "place_of_supply":place_of_supply,	
												 "ecommerce_gstin":ecommerce_gstin,
												 "modified_date":modified_date,
												 "amended_from":amended_from 																									
													})
										invoice_map[key] = frappe._dict({"mapped_items": item_list})
								
									
							else:
								sales_tax_rate = 0
								total_amount = 0.0
								if len(sales_invoice_tax_data) != 0:
									for invoice_tax_data in sales_invoice_tax_data:
										account_head = invoice_tax_data.account_head
										item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
										converted = ast.literal_eval(item_wise_tax_detail)
										if self.item_code in converted:
											details = converted[self.item_code]
											if "SGST" in account_head or "CGST" in account_head:
												sales_tax_rate = sales_tax_rate + details[0]
											elif "IGST" in account_head:
												sales_tax_rate = details[0]
											
									if self.invoice_id in invoice_map:
										item_entry = invoice_map[self.invoice_id]
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
												"net_amount": item_net_amount,
												"invoice_id": self.invoice_id,
												 "posting_date":posting_date,
												 "place_of_supply":place_of_supply,	
												 "ecommerce_gstin":ecommerce_gstin,
												 "modified_date":modified_date,
												 "amended_from":amended_from
														})
											item_entry["mapped_items"] = mapped_items_list
									else:
										item_list = []
										item_list.append({
												 "tax_rate": sales_tax_rate, 
												 "net_amount": item_net_amount,
												 "invoice_id": self.invoice_id,
												 "posting_date":posting_date,
												 "place_of_supply":place_of_supply,	
												 "ecommerce_gstin":ecommerce_gstin,
												 "modified_date":modified_date,
												 "amended_from":amended_from
													})
										invoice_map[self.invoice_id] = frappe._dict({"mapped_items": item_list})
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					posting_date = map_data["mapped_items"][map_d]["posting_date"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					modified_date = map_data["mapped_items"][map_d]["modified_date"]
					amended_from = map_data["mapped_items"][map_d]["amended_from"]
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					self.data.append([amended_from,posting_date,place_of_supply,invoice_no,
						modified_date,invoice_grand_total,""
						,rate_of_tax,tot_net_amount,"",ecommerce_gstin])	
		elif self.filters.get("type_of_business") == "B2CS":
			invoice_map = {}
			columns = self.get_columns_b2bcs()
			sales_b = self.sales_invoice_b2bl()
			for sales_datas in sales_b:
				amended_from = sales_datas.amended_from
				if amended_from == None:
					self.invoice_id = sales_datas.name
					posting_date = sales_datas.posting_date
					place_of_supply = sales_datas.place_of_supply
					ecommerce_gstin = sales_datas.ecommerce_gstin
					customer_address = sales_datas.customer_address
					grand_total = sales_datas.grand_total
					invoice_type = sales_datas.invoice_type
					company_address = sales_datas.company_address
					customer_type = sales_datas.customer_type
					sales_item = self.sales_item_details()
					for item in sales_item:
						self.item_code = item.item_code
						item_net_amount = item.net_amount
						tax_data = self.sales_tax()
						sales_invoice_tax_data = self.sales_account_tax()
						tax_rate_list = []
						if len(tax_data) != 0:
							for data in tax_data:
								tax_rate = data.tax_rate
								net_amount = data.net_amount
								key = self.invoice_id
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
												qty_temp = items["net_amount"]
												items["net_amount"] = (qty_temp) + (net_amount)
									else:
									
										new_list.append({
											"tax_rate": tax_rate, 
										  	"net_amount": net_amount,
										        "invoice_id": key,
											 "customer_type":customer_type,
											 "place_of_supply":place_of_supply,	
											 "ecommerce_gstin":ecommerce_gstin,
											"grand_total":grand_total,
											"customer_address":customer_address,
											"company_address":company_address
														})
								
										item_entry["mapped_items"] = mapped_items_list + new_list
								else:
									item_list = []
									item_list.append({
											"tax_rate": tax_rate, 
										  	"net_amount": net_amount,
										        "invoice_id": key,
											 "customer_type":customer_type,
											 "place_of_supply":place_of_supply,	
											 "ecommerce_gstin":ecommerce_gstin,
											"grand_total":grand_total,
											"customer_address":customer_address,
											"company_address":company_address 																									
													})
									invoice_map[key] = frappe._dict({"mapped_items": item_list})
								
									
						else:
							sales_tax_rate = 0
							total_amount = 0.0
							if len(sales_invoice_tax_data) != 0:
								for invoice_tax_data in sales_invoice_tax_data:
									account_head = invoice_tax_data.account_head
									item_wise_tax_detail = invoice_tax_data.item_wise_tax_detail
									converted = ast.literal_eval(item_wise_tax_detail)
									if self.item_code in converted:
										details = converted[self.item_code]
										if "SGST" in account_head or "CGST" in account_head:
											sales_tax_rate = sales_tax_rate + details[0]
										elif "IGST" in account_head:
											sales_tax_rate = details[0]
										
								if self.invoice_id in invoice_map:
									item_entry = invoice_map[self.invoice_id]
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
										  	"net_amount": net_amount,
										        "invoice_id": key,
											 "customer_type":customer_type,
											 "place_of_supply":place_of_supply,	
											 "ecommerce_gstin":ecommerce_gstin,
											"grand_total":grand_total,
											"customer_address":customer_address,
											"company_address":company_address
													})
										item_entry["mapped_items"] = mapped_items_list
								else:
									item_list = []
									item_list.append({
											"tax_rate": sales_tax_rate, 
										  	"net_amount": net_amount,
										        "invoice_id": key,
											 "customer_type":customer_type,
											 "place_of_supply":place_of_supply,	
											 "ecommerce_gstin":ecommerce_gstin,
											"grand_total":grand_total,
											"customer_address":customer_address,
											"company_address":company_address
												})
									invoice_map[self.invoice_id] = frappe._dict({"mapped_items": item_list})
			for invoice_map_data in invoice_map:
				map_data = invoice_map[invoice_map_data]
				for map_d in range(0,len(map_data["mapped_items"])):
					invoice_no = map_data["mapped_items"][map_d]["invoice_id"]
					rate_of_tax = map_data["mapped_items"][map_d]["tax_rate"]
					tot_net_amount = map_data["mapped_items"][map_d]["net_amount"]
					place_of_supply = map_data["mapped_items"][map_d]["place_of_supply"]
					customer_type = map_data["mapped_items"][map_d]["customer_type"]
					ecommerce_gstin = map_data["mapped_items"][map_d]["ecommerce_gstin"]
					self.customer_address = map_data["mapped_items"][map_d]["customer_address"]
					self.company_address = map_data["mapped_items"][map_d]["company_address"]
					b2c_limit = frappe.db.get_value('GST Settings',self.customer_address,'b2c_limit')
					gst_state_number = self.get_contact_details()
					address_details = self.address_gst_number()
					invoice_value = tot_net_amount * rate_of_tax /100
					invoice_grand_total = invoice_value + tot_net_amount
					if grand_total <= float(b2c_limit) and address_details != gst_state_number:
						self.data.append([customer_type,place_of_supply,""
							,rate_of_tax,tot_net_amount,"",ecommerce_gstin])
					elif grand_total <= float(b2c_limit) and address_details == gst_state_number:
						self.data.append([customer_type,place_of_supply,""
							,rate_of_tax,tot_net_amount,"",ecommerce_gstin])
					elif grand_total >= float(b2c_limit) and address_details == gst_state_number:
						self.data.append([customer_type,place_of_supply,""
							,rate_of_tax,tot_net_amount,"",ecommerce_gstin])
			#print "self.data------out side loop----",self.data
		return columns, self.data
	
	def get_columns_b2b(self):
		return [
			_("GSTIN/UIN of Recipient") + "::150",
			_("Receiver Name") + "::150",
			_("Invoice Number") + "::150",
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
			_("Original Invoice Number") + "::150",
			_("Original Invoice date") + "::150",
			_("Revised Invoice Number") + "::150",
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
			_("Invoice Number") + "::150",
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
			_("Original Invoice Number") + "::150",
			_("Original Invoice date") + "::150",
			_("Original Place Of Supply") + "::150",
			_("Revised Invoice Number") + "::150",
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
			_("Applicable % of Tax Rate") + "::150",
			_("Rate") + "::150",
			_("Taxable Value") + "::150",
			_("Cess Amount") + "::150",
			_("E-Commerce GSTIN") + "::150"
		
		]

	def sales_invoice_details(self):
		sales_invoice = frappe.db.sql("""select billing_address_gstin,customer_address,name,posting_date,place_of_supply,
						reverse_charge,invoice_type,ecommerce_gstin,posting_date,amended_from,modified
 						from `tabSales Invoice` 
						where posting_date >= %s AND posting_date <= %s 
						AND customer_name IN (select customer_name from `tabCustomer` where customer_type = "Company")
						 AND docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)

		
		return sales_invoice

	def sales_invoice_b2bl(self):
		sales_invoice_b = frappe.db.sql("""select si.billing_address_gstin,si.customer_address,si.name,si.posting_date,si.place_of_supply,
					si.reverse_charge,si.invoice_type,si.ecommerce_gstin,si.posting_date,si.amended_from,
					si.modified,si.grand_total,si.company_address,c.customer_type
					from `tabSales Invoice` si, `tabCustomer` c
					where si.posting_date >= %s AND si.posting_date <= %s
			 		AND c.customer_type = "Individual" AND si.customer_name = c.customer_name 
					AND si.docstatus = 1""",(self.filters.from_date,self.filters.to_date), as_dict = 1)
		#print "sales_invoice_b-----------",sales_invoice_b
		return sales_invoice_b

	def sales_invoice_counts(self):
		sales_in = frappe.db.sql("""select count(billing_address_gstin) as bill_gstin, count(name) as customer,amended_from 
					from `tabSales Invoice` 
					where posting_date >= %s AND posting_date <= %s AND amended_from is NULL
 					AND customer_name IN (select customer_name from `tabCustomer` where customer_type = "Company")""",(self.filters.from_date,self.filters.to_date), as_dict = 1)

		
		return sales_in
	def sales_item_details(self):
		if self.invoice_id:
			invoice_item = frappe.db.sql("""select item_code,net_amount,qty,rate from `tabSales Invoice Item` where parent = %s""",(self.invoice_id), as_dict = 1)
			
		return invoice_item

	def sales_tax(self):
		#rint " self.item_code-------------", self.item_code
		if self.item_code:
			items = frappe.db.sql("""select distinct si.parent,si.item_code,si.item_name,si.net_amount,it.tax_rate,it.tax_type from `tabSales Invoice Item` si, `tabItem Tax` it where si.item_code = '"""+ str(self.item_code)+"""' AND it.parent = si.item_code AND it.tax_type like '%IGST%' AND si.parent = '"""+ str(self.invoice_id)+"""'""", as_dict = 1)
		#print "items-----------",items
		return items		
	def sales_account_tax(self):
		if self.invoice_id:
			account_tax = frappe.db.sql("""select account_head,rate,item_wise_tax_detail from `tabSales Taxes and Charges` where parent = %s""",(self.invoice_id),as_dict =1)
		return account_tax

	def get_contact_details(self):
		
		gst_state_number =""
		if self.customer_address:
			gst_state_number = frappe.db.get_value('Address',self.customer_address,
			['gst_state_number'])
		return gst_state_number

	def address_gst_number(self):
		company_gst_state_number = ""
		address_detail = frappe.get_list("Address",["address_type","gst_state_number","name"])
		for itrate_address in address_detail:
			name = itrate_address.name
			if name == self.company_address:
				company_gst_state_number  = itrate_address.gst_state_number
		return company_gst_state_number

