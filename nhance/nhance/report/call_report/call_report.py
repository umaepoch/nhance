# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate

def execute(filters=None):
        if not filters: filters = {}

        validate_filters(filters)

        columns = get_columns()
       
        item_map = get_item_details(filters)
        iwb_map = get_item_map(filters)

        data = []
        summ_data = [] 
        opp_prev = "" 
        opp_work = "" 
        item_prev = ""
        item_work = ""
        opp_count = 0 
	item_count = 0
        tot_qty = 0 
	tot_val = 0
	temp_date = getdate("0001-01-01")
	diff_days = 0

	

        for (reference, item) in sorted(iwb_map):
                qty_dict = iwb_map[(reference, item)]
                data.append([
                        qty_dict.date, qty_dict.customer, qty_dict.short_description, qty_dict.first_name, qty_dict.last_name, qty_dict.city, qty_dict.mobile_no, qty_dict.email_id, qty_dict.doctype, reference, item, qty_dict.qty
                        
                    ])
	
#	for rows in data: 
 #     		if opp_count == 0: 
  #    			opp_prev = rows[0] 
# 			item_prev = rows[2]
#			tot_qty = tot_qty + rows[4]
                      			
#			summ_data.append([opp_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], 
#				rows[8], rows[9], rows[10], rows[11]
 #				]) 
#                else: 
#			opp_work = rows[0]
 #                       item_work = rows[2]
			
					
#			if opp_prev == opp_work: 
#				tot_qty = tot_qty + rows[4]

#                                summ_data.append([opp_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8], rows[9], rows[10], rows[11]
 #				]) 
#			else: 
#				summ_data.append([opp_prev, " ", " ", " ", tot_qty, " ",  " ", " ", " ", " "
#					" ", " "
				
 #				])	
				
#				summ_data.append([opp_work, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], 
#				rows[8], rows[9], rows[10], rows[11]
 #				]) 
		
#				tot_qty = 0
                                
#				tot_qty = tot_qty + rows[4] 

#				opp_prev = opp_work 
 #                               item_prev = item_work

#		opp_count = opp_count + 1 
#	summ_data.append([opp_prev, " ", " ", " ", tot_qty, " ", " ", " ",
#					" ", " ", " ", " "
 #				])		  
						 
	return columns, data 


def get_columns():
        """return columns"""
               
        columns = [

		_("Date of Interaction")+":Date:150",
		_("Customer")+":Link/Customer:150",
		_("Short Description")+"::140",
		_("First Name")+"::100",
		_("Last Name")+"::100",
		_("City")+"::150",
		_("Mobile Number")+"::100",
		_("Email ID")+"::100",
		_("Reference Document")+"::100",
                _("Reference Number")+"::100",
		_("Item Code")+"::100",
	        _("Qty")+":Float:100"
       	       
          ]

        return columns

def get_conditions(filters):
        conditions = ""
        if filters.get("from_date"):

          	conditions += " and inter.date >= '%s'" % frappe.db.escape(filters["from_date"])
	
        if filters.get("to_date"):

                conditions += " and inter.date <= '%s'" % frappe.db.escape(filters["to_date"])
        else:
                frappe.throw(_("'To Date' is required"))

        if filters.get("user"):
#		pre_ass = '["'
#		suf_ass = '"]'
#		assign_to = pre_ass + filters.get("owner") + suf_ass 
		conditions += " and inter.user = '%s'" % filters.get("user")

        return conditions

def get_int_details_so(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.sales_order as reference, so.item_code as item, so.qty as qty, inter.short_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabSales Order Item` so where inter.customer = dy.link_name and inter.sales_order = so.parent and inter.reference_doctype = "Sales Order" %s """ % conditions, as_dict=1)

def get_int_details_si(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.sales_invoice as reference, si.item_code as item, si.qty as qty, inter.short_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabSales Invoice Item` si where inter.customer = dy.link_name and inter.sales_invoice = si.parent and inter.reference_doctype = "Sales Invoice" %s """ % conditions, as_dict=1)

def get_int_details_quo(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.quotation as reference, qi.item_code as item, qi.qty as qty, inter.short_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabQuotation Item` qi where inter.customer = dy.link_name and inter.quotation = qi.parent and inter.reference_doctype = "Quotation" %s """ % conditions, as_dict=1)

def get_int_details_opp(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.opportunity as reference, op.item_code as item, op.qty as qty, inter.short_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabOpportunity Item` op where inter.customer = dy.link_name and inter.opportunity = op.parent and inter.reference_doctype = "Opportunity" %s """ % conditions, as_dict=1)

def get_int_details(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.date, inter.customer, inter.city, first_name, last_name, mobile_no as mobile, inter.email_id as email, " " as reference, " " as item, 0 as qty, inter.short_description, "" as doctype from `tabInteractions` inter, `tabDynamic Link` dy	 where inter.customer = dy.link_name and inter.reference_doctype = "" %s """ % conditions, as_dict=1)



def get_item_map(filters):
        iwb_map = {}
#        from_date = getdate(filters["from_date"])
#        to_date = getdate(filters["to_date"])
	
        sle = get_int_details_so(filters)
	sile = get_int_details_si(filters)
	qle = get_int_details_quo(filters)
	ole = get_int_details_opp(filters)
	ile = get_int_details(filters)
	
        if sle:     	
	        for d in sle:
                
        	        key = (d.reference, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.reference, d.item)]
               
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.doctype = d.doctype

	if sile:     	
	        for d in sile:
                
        	        key = (d.reference, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.reference, d.item)]
               
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.doctype = d.doctype

	if qle:     	
	        for d in qle:
                
        	        key = (d.reference, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.reference, d.item)]
               
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.doctype = d.doctype

 	if ole:     	
	        for d in ole:
                
        	        key = (d.reference, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.reference, d.item)]
               
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.doctype = d.doctype

	if ile:     	
	        for d in ile:
                
        	        key = (d.reference, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.reference, d.item)]
               
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.doctype = d.doctype


        return iwb_map

def get_item_details(filters):
        condition = ''
        value = ()
        if filters.get("item_code"):
                condition = "where item_code=%s"
                value = (filters["item_code"],)
	
        items = frappe.db.sql("""select item_group, item_name, stock_uom, name, brand, description
                from tabItem {condition}""".format(condition=condition), value, as_dict=1)

        return dict((d.name, d) for d in items)

def validate_filters(filters):
        if not (filters.get("item_code") or filters.get("warehouse")):
                sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
                if sle_count > 500000:
                        frappe.throw(_("Please set filter based on Item or Warehouse"))



