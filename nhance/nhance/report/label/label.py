# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
import time
import math
import json
import ast
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []
	purchase_document_type = ""
	purchase_document_no=""
	doctype=""
	document_no=""
	doctype = filters.get("document_type")
	document_no = filters.get("document_no_value")
	##print "doctype=============",doctype
	##print "stock_entry=============",document_no
	
	##print "entering under execute method----"

	columns = get_columns()
	if doctype=="Purchase Receipt":
		#print ("Purchase Receipt")
		serial_details = fetching_details(document_no)
	
	
		for serial_data in serial_details:
			item_name = serial_data['item_name'],
			item_code = serial_data['item_code'],
			serial_no = serial_data['serial_no'],
			batch_no  = serial_data['batch_no']
			##print "batch_no",batch_no
			if batch_no == None: 
    				#print ("Yes")
				#print "serial_no",type(serial_no)
				serial_list=serial_no[0];
				#print "serial_list",serial_list
				serial_list1=serial_list.split('\n');
				#print "serial_list1",str(serial_list1)
				serial=str(serial_list1[0]);
				#print "serial",serial
				for serial_list2 in serial_list1:
					#print serial_list2
		
               		
		
					sum_data.append([ serial_data['item_name'] ,serial_data['item_code'],serial_list2,serial_list2
					
                        ])
			
			else : 
    				#print ("No")
				expiry_date=fetching_expiry_date(batch_no)
				#print "expiry_date",expiry_date[0].get("DATE_FORMAT(expiry_date,'%d/%m/%Y')") 
				expiry=expiry_date[0].get("DATE_FORMAT(expiry_date,'%d/%m/%Y')") 
				sum_data.append([ serial_data['item_name'] ,serial_data['item_code'],"","",serial_data['batch_no'],expiry
					
                        ]) 
		
			 					     					    	
	
	elif doctype=="Stock Entry":
		#print ("stock entry")		 					     					    	
		serial_details_stock = fetching_details_stock_entry(document_no)
		#print "serial_details_stock",serial_details_stock
	
		for serial_data in serial_details_stock:
			item_name = serial_data['item_name'],
			item_code = serial_data['item_code'],
			serial_no = serial_data['serial_no'],
			batch_no  = serial_data['batch_no']
			#print "batch_no",batch_no
			if batch_no == None: 
    				#print ("Yes")
				#print "serial_no",type(serial_no)
				serial_list=serial_no[0];
				#print "serial_list",serial_list
				serial_list1=serial_list.split('\n');
				#print "serial_list1",str(serial_list1)
				serial=str(serial_list1[0]);
				#print "serial",serial
				for serial_list2 in serial_list1:
					#print serial_list2
		
               		
		
					sum_data.append([ serial_data['item_name'] ,serial_data['item_code'],serial_list2,serial_list2
					
                        ])
			
			elif batch_no != None : 
    				#print ("No") 
				expiry_date=fetching_expiry_date(batch_no)
				#print expiry_date[0]
				#print "expiry_date",expiry_date[0].get("DATE_FORMAT(expiry_date,'%d/%m/%Y')")
				expiry=expiry_date[0].get("DATE_FORMAT(expiry_date,'%d/%m/%Y')") 
				sum_data.append([ serial_data['item_name'] ,serial_data['item_code'],"","",serial_data['batch_no'],expiry
					
                        ]) 
			
	return columns, sum_data

def fetching_details(document_no):
	serial_data = frappe.db.sql("""select item_name,item_code,serial_no,batch_no
			from 
				`tabPurchase Receipt Item` 
			where 
				 parent='"""+str(document_no)+"""' """, 
			 as_dict=1)

	##print "serial_data",serial_data
	return serial_data

def fetching_details_stock_entry(document_no):
	stock_entry_list= frappe.db.sql("""select item_name,item_code,serial_no,batch_no
			from 
				`tabStock Entry Detail` 
			where 
				 parent='"""+str(document_no)+"""' """, 
			 as_dict=1)

	
	return stock_entry_list

def fetching_expiry_date(batch_no):
	expiry_date= frappe.db.sql("""select  DATE_FORMAT(expiry_date,'%d/%m/%Y')
			from 
				`tabBatch` 
			where 
				 name='"""+str(batch_no)+"""' """, 
			 as_dict=1)

	
	return expiry_date


def convert(expiry_date): 
    return tuple(i for i in expiry_date)

def get_columns():
	"""return columns"""
	columns = [
		_("Item Name")+"::100",
		_("Item Code")+"::100",
		_("Serial No")+"::100",
		_("QR Code")+"::100",
		_("Batch No")+"::100",
		_("Expiry Date")+"::100"
		 ]
	return columns
