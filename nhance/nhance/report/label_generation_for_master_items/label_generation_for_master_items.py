# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _, msgprint, utils
from frappe.utils import flt, getdate, datetime,comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from datetime import datetime
import time
import math
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
	global data_summary
	global columns
	columns = []
	data_summary = []
	columns = get_columns()
	conditions = get_conditions(filters)
	items_list = get_master_items(conditions)
	#print "items_list--------", items_list
	if items_list is not None:
		for items_data in items_list:
			item_code = items_data['item_code']
			price_list = frappe.get_doc("Item Price", {"item_code": item_code, "price_list": "Standard Selling"}, "price_list_rate")
			data_summary.append([items_data['item_code'], items_data['item_name'], items_data['stock_uom'], price_list.price_list_rate])

	return columns, data_summary

def get_master_items(conditions):
	if conditions is not "":
		master_items_list = frappe.db.sql("""select item_code,item_name,stock_uom,item_group from `tabItem` where item_code is not NULL%s""" % conditions, as_dict=1)
		return master_items_list
	else:
		return None

def get_columns():
	"""return columns"""
	columns = [
	_("Item Code")+":Link/Item:100",
	_("Item Name")+"::150",
	_("Stock UOM")+":Link/UOM:90",
	_("MRP.")+"::100"
	 ]
	return columns

def get_conditions(filters):
	conditions = ""
    	if filters.get("item_group"):
        	conditions += " and item_group = '%s'" % frappe.db.escape(filters.get("item_group"), percent=False)
    	if filters.get("item_name"):
        	conditions += " and item_name = '%s'" % frappe.db.escape(filters.get("item_name"), percent=False)
	return conditions

@frappe.whitelist()
def make_prnfile(ncopies,label,date_of_import):
	#path = os.path.expanduser('~') +'/ERPNext_MASTER_ITEMS_PRN.PRN'
	#prn_file = open(path,'wb+')
	printer_details = frappe.get_doc("Label Printer", label)
	address = printer_details.address
	report_data_size = len(data_summary)
	#print "report_data_size-------", report_data_size
	split_address = address.split("\n")
	#print "len of address_details-----", len(split_address)

	curr_date = utils.today()
	fname = "ITEM_"+ str(curr_date) +".PRN"
	save_path = 'site1.local/private/files'
	file_name = os.path.join(save_path, fname)
	ferp = frappe.new_doc("File")
	ferp.file_name = fname
	ferp.folder = "Home/Labels"
	ferp.is_private = 1
	ferp.file_url = "/private/files/"+fname

	prn_file = open(file_name,"w+")
	
	for report_data in data_summary:
		qty = 1
		copies = 1
		item_code = report_data[0]
		item_name = report_data[1]
		stock_uom = report_data[2]
		mrp = report_data[3]

		#print "type of date_of_import-------", date_of_import, type(date_of_import)
		date_of_import1 = datetime.strptime(date_of_import, '%Y-%m-%d')
		month_and_year_of_import = (date_of_import1).strftime("%m/%y")
		#print "month_and_year_of_import-------", month_and_year_of_import

		for copies in xrange(int(ncopies)):
			prn_file.write("<xpml><page quantity='0' pitch='50.8 mm'></xpml>G0\015" +"\n")
			prn_file.write("n\015"+"\n") 
			prn_file.write("M0500\015"+"\n") 
			prn_file.write("MT\015"+"\n") 
			prn_file.write("O0214\015"+"\n") 
			prn_file.write("V0\015"+"\n") 
			prn_file.write("t1\015"+"\n") 
			prn_file.write("Kf0070\015"+"\n") 
			prn_file.write("SG\015"+"\n") 
			prn_file.write("c0000\015"+"\n") 
			prn_file.write("e\015"+"\n") 
			prn_file.write("<xpml></page></xpml><xpml><page quantity='1' pitch='50.8 mm'></xpml>L\015"+"\n") 
			prn_file.write("D11\015"+"\n"+"H14\015"+"\n"+"PG\015"+"\n"+"PG\015"+"\n"+"SG\015"+"\n"+"ySPM\015"+"\n"+"A2\015"+"\n") 
			prn_file.write("1911C1001760021" + str(item_name)+"\015"+"\n") #product-name
			prn_file.write("4911C0801000013" + str(item_code)+"\015"+"\n") #Barcode
			prn_file.write("1e8404201270018C0201&E0$2" + str(item_code)+"\015"+"\n") #ProductCode
			#prn_file.write("1911C1001570260" + "Black"+"\n") #item-color
			#prn_file.write("1911C1001570260" + "L" +"\n") #item-size
			prn_file.write("1911C1001050019Month & Yr of Import" +"\015"+ "\n") 
			prn_file.write("1911C10010501600" + str(month_and_year_of_import) + "\015"+ "\n") 
			prn_file.write("1911C1200800019M.R.P." +"\015"+ "\n") 
			prn_file.write("1911C1200800105" + str(mrp) +"\015"+"\n") #selling price
			prn_file.write("1911A0800670148Inclusive of all taxes" +"\015"+ "\n") 
			prn_file.write("1911A0800990227Qty" +"\015"+ "\n") 
			prn_file.write("1911A0800830227" + str(qty) + " " +str(stock_uom) +"\015"+ "\n") # Qty and UOM
			if len(split_address)!=0:
				if len(split_address) == 3:
					prn_file.write("1911C0800400012" + str(split_address[0]) +"\015"+ "\n") 
					prn_file.write("1911C08002500206,"+ str(split_address[1]) +"\015"+ "\n") 
					prn_file.write("1911C0800090005"+str(split_address[2]) +"\015"+ "\n") 
				else:
					prn_file.write("1911C0800400012" + str(split_address[0]) +"\015"+ "\n")
			prn_file.write("Q0001\015"+"\n") 
			prn_file.write("E\015"+"\n") 
			prn_file.write("<xpml></page></xpml><xpml><end/></xpml>\015"+"\n") 
				
	ferp.save()
	prn_file.close()
	frappe.msgprint(_("PRN File created - Please check File List to download the file"))

