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
reload(sys)
sys.setdefaultencoding('utf-8')

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
	#print "doctype=============",doctype
	#print "stock_entry=============",document_no

	
	#print "entering under execute method----"

	columns = get_columns()
	serial_details = fetching_details(doctype,document_no)

	
	for serial_data in serial_details:
		item_name = serial_data['item_name'],
		item_code = serial_data['item_code'],
		serial_no=serial_data['serial_no'],
                qr_code=serial_data['serial_no']
		sum_data.append([ serial_data['item_name'] ,serial_data['item_code'],serial_data['serial_no'],serial_data['serial_no']
					
                        ])
			 					     					    	
	
			 					     					    	
			
	return columns, sum_data

def fetching_details(doctype,document_no):
	serial_data = frappe.db.sql("""select item_name,item_code,serial_no
			from 
				`tabSerial No` 
			where 
				purchase_document_type='"""+str(doctype)+"""' and  purchase_document_no='"""+str(document_no)+"""' """, 
			 as_dict=1)

	#print "serial_data",serial_data
	return serial_data



def get_columns():
	"""return columns"""
	columns = [
		_("Description")+"::100",
		_("Part No")+"::100",
		_("Serial No")+":Link/Serial No:100",
		_("QR Code")+"::100"
		 ]
	return columns
