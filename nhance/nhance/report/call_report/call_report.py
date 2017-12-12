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

	

        for (inter_name, item) in sorted(iwb_map):
                qty_dict = iwb_map[(reference, item)]
                data.append([
                        qty_dict.date, inter_name, qty_dict.customer, qty_dict.short_description, qty_dict.first_name, qty_dict.last_name, qty_dict.city, qty_dict.mobile_no, qty_dict.email_id, qty_dict.doctype, qty_dict.reference, item, qty_dict.item_name, qty_dict.qty, qty_dict.complete_description
                        
                    ])
	
						 
	return columns, data 


def get_columns():
        """return columns"""
               
        columns = [

		_("Date of Interaction")+":Date:150",
		_("Interaction")+":Link/Customer:150",		
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
		_("Item Name")+"::100",
	        _("Qty")+":Float:100",
		_("Complete Description")+"::140"
       	       
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
		conditions += " and inter.user = '%s'" % filters.get("user")

        return conditions

def get_int_details_so(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.name as inter_name, inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.sales_order as reference, so.item_code as item, so.item_name as item_name, so.qty as qty, inter.short_description, inter.complete_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabSales Order Item` so where inter.customer = dy.link_name and inter.sales_order = so.parent and inter.reference_doctype = "Sales Order" %s """ % conditions, as_dict=1)

def get_int_details_si(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.name as inter_name, inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.sales_invoice as reference, si.item_code as item, si.item_name as item_name, si.qty as qty, inter.short_description, inter.complete_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabSales Invoice Item` si where inter.customer = dy.link_name and inter.sales_invoice = si.parent and inter.reference_doctype = "Sales Invoice" %s """ % conditions, as_dict=1)

def get_int_details_quo(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.name as inter_name, inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.quotation as reference, qi.item_code as item, qi.item_name as item_name, qi.qty as qty, inter.short_description, inter.complete_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabQuotation Item` qi where inter.customer = dy.link_name and inter.quotation = qi.parent and inter.reference_doctype = "Quotation" %s """ % conditions, as_dict=1)

def get_int_details_opp(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.name as inter_name, inter.date as date, inter.customer as customer, inter.city as city, first_name as first_name, last_name as last_name, mobile_no as mobile, inter.email_id as email, inter.opportunity as reference, op.item_code as item,  op.item_name as item_name, op.qty as qty, inter.short_description, inter.complete_description, inter.reference_doctype as doctype from `tabInteractions` inter, `tabDynamic Link` dy, `tabOpportunity Item` op where inter.customer = dy.link_name and inter.opportunity = op.parent and inter.reference_doctype = "Opportunity" %s """ % conditions, as_dict=1)

def get_int_details(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""Select inter.name as inter_name, inter.date, inter.customer, inter.city, first_name, last_name, mobile_no as mobile, inter.email_id as email, " " as reference, " " as item, " " as item_name, 0 as qty, inter.short_description, inter.complete_description, "" as doctype from `tabInteractions` inter, `tabDynamic Link` dy where inter.customer = dy.link_name and inter.opportunity is NULL and inter.quotation is NULL and inter.sales_order is NULL and inter.sales_invoice is NULL %s """ % conditions, as_dict=1)



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
                
        	        key = (d.inter_name, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.inter.name, d.item)]
			qty_dict.reference = d.reference
               		qty_dict.item_name = d.item_name
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.complete_description = d.complete_description
			qty_dict.doctype = d.doctype

	if sile:     	
	        for d in sile:
                
        	        key = (d.inter_name, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.inter.name, d.item)]
			qty_dict.reference = d.reference

             		qty_dict.item_name = d.item_name
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.complete_description = d.complete_description
			qty_dict.doctype = d.doctype

	if qle:     	
	        for d in qle:
                
        	        key = (d.inter_name, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.inter.name, d.item)]
			qty_dict.reference = d.reference

                        qty_dict.item_name = d.item_name
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.complete_description = d.complete_description
			qty_dict.doctype = d.doctype

 	if ole:     	
	        for d in ole:
                
        	        key = (d.inter_name, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.inter.name, d.item)]
			qty_dict.reference = d.reference

                        qty_dict.item_name = d.item_name        
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.complete_description = d.complete_description
			qty_dict.doctype = d.doctype

	if ile:     	
	        for d in ile:
                
        	        key = (d.inter_name, d.item)
        	        if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
				
        	                })

        	        qty_dict = iwb_map[(d.inter.name, d.item)]
			qty_dict.reference = d.reference

               		qty_dict.item_name = d.item_name               
        	        qty_dict.qty = d.qty
	                qty_dict.date = d.date
	                qty_dict.customer = d.customer
			qty_dict.city = d.city
			qty_dict.first_name = d.first_name
			qty_dict.last_name = d.last_name
			qty_dict.mobile_no = d.mobile
			qty_dict.email_id = d.email
			qty_dict.short_description = d.short_description
			qty_dict.complete_description = d.complete_description
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



