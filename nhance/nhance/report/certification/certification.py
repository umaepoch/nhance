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


def execute(filters=None):
	columns, data = [], []
	serial_no = filters.get("item_serial_no")
	columns = get_columns()
	serial_no_details = fetching_serial_no_details(serial_no)

	
	for serial_data in serial_no_details:
		coc=serial_data['pch1_coc'],
		pressure_test=serial_data['pch1_pressure_test'],
		build_sheet=serial_data['pch1_build_sheet'],
		supplier=serial_data[''],
		company=serial_data[''],
		purchase_document_no=serial_data['purchase_document_no'],
		purchase_date=serial_data['purchase_date'],
		delivery_document_no=serial_data['delivery_document_no'],
		delivery_date=serial_data['delivery_date'],
		item_code = serial_data['item_code'],
		item_name = serial_data['item_name'],
		serial_no=serial_data['serial_no']
		data.append([serial_data['pch1_coc'], serial_data['pch1_pressure_test'],serial_data['pch1_build_sheet'],serial_data[''],serial_data[''],serial_data['purchase_document_no'],serial_data['purchase_date'],serial_data['delivery_document_no'],serial_data['delivery_date'],serial_data['item_code'],serial_data['item_name'],serial_data['serial_no']
					
                        ])
			 					     					    	
	
			 					     					   
	return columns, data
def fetching_serial_no_details(serial_no):
	serial_details = frappe.db.sql("""select pch1_coc,pch1_pressure_test,pch1_build_sheet,"","",purchase_document_no,purchase_date,delivery_document_no,delivery_date,item_code,item_name,serial_no
			from 
				`tabSerial No` 
			where 
				serial_no='"""+serial_no+"""' """, 
			 as_dict=1)

	
	return serial_details



def get_columns():
	"""return columns"""
	columns = [
		_("CoC")+"::100",
		_("Pressure Test")+"::100",
		_("Assembly build sheet")+"::100",
		_("DNV-GL Product Certification")+"::100",
		_("CE Approval")+"::100",
		_("Customer PO")+"::100",
		_("Date (customer PO)")+"::100",
		_("Delivery Note ")+"::100",
		_("Date ( Delivery note)")+"::100",
		_("Item Code")+"::100",
		_("Item Name")+"::100",
		_("Item Serial No")+":Link/Serial No:100"
		 ]
	return columns
