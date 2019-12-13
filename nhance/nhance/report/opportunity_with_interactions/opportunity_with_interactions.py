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


        for (opportunity, item_code, interaction, in_date) in sorted(iwb_map):
                qty_dict = iwb_map[(opportunity, item_code, interaction, in_date)]
                data.append([
                        opportunity, qty_dict.customer, item_code, qty_dict.item_group, qty_dict.qty, interaction, in_date, qty_dict.mode, qty_dict.inbound, qty_dict.short_desc, qty_dict.comp_desc, qty_dict.todo
                        
                    ])
	for rows in data: 
       		if opp_count == 0: 
       			opp_prev = rows[0] 
 			item_prev = rows[2]
			tot_qty = tot_qty + rows[4]
                      			
			summ_data.append([opp_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], 
				rows[8], rows[9], rows[10], rows[11]
 				]) 
                else: 
			opp_work = rows[0]
                        item_work = rows[2]
			
					
			if opp_prev == opp_work: 
				tot_qty = tot_qty + rows[4]

                                summ_data.append([opp_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8], rows[9], rows[10], rows[11]
 				]) 
			else: 
				summ_data.append([opp_prev, " ", " ", " ", tot_qty, " ",  " ", " ", " ", " "
					" ", " "
				
 				])	
				
				summ_data.append([opp_work, rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], 
				rows[8], rows[9], rows[10], rows[11]
 				]) 
		
				tot_qty = 0
                                
				tot_qty = tot_qty + rows[4] 

				opp_prev = opp_work 
                                item_prev = item_work

		opp_count = opp_count + 1 
	summ_data.append([opp_prev, " ", " ", " ", tot_qty, " ", " ", " ",
					" ", " ", " ", " "
 				])		 
	
		 
		 
						 
	return columns, summ_data 


def get_columns():
        """return columns"""
               
        columns = [

		_("Opportunity")+":Link/Opportunity:150",
		_("Customer")+":Link/Customer:150",
		_("Item Code")+":Link/Item:150",
		_("Item Group")+":Link/Item Group:100",
		_("Qty")+":Float:100", 
		_("Interaction")+"::100",
                _("Interaction Date")+":Date:100",
		_("Mode")+"::100",
		_("Inbound Outboud")+"::100",
	        _("Short Description")+"::140",
       	        _("Complete Description")+"::90",   
		_("To Do")+"::90"


          ]

        return columns

def get_conditions(filters):
        conditions = ""
        if filters.get("from_date"):

          	conditions += " and op.transaction_date >= '%s'" % frappe.db.escape(filters["from_date"])
	
        if filters.get("to_date"):

                conditions += " and op.transaction_date <= '%s'" % frappe.db.escape(filters["to_date"])
        else:
                frappe.throw(_("'To Date' is required"))

        if filters.get("item_code"):
                conditions += " and opi.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)
     
        if filters.get("name"):
                conditions += " and op.name = '%s'" % frappe.db.escape(filters.get("name"), percent=False)

        return conditions

def get_opp_details(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select op.name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, intr.name as interaction, intr.date as in_date, intr.mode as mode, intr.inbound_or_outbound as inbound, intr.short_description as short_desc, intr.complete_description as comp_desc, intr.todo as todo 
from `tabOpportunity` op, `tabOpportunity Item` opi, `tabInteractions` intr 
where op.name = opi.parent and op.name = intr.opportunity %s """ % conditions, as_dict=1)

def get_opp_details_1(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select op.name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, " " as interaction, " " as in_date, " " as mode, " " as inbound, " " as short_desc, " " as comp_desc, " " as todo

from `tabOpportunity` op, `tabOpportunity Item` opi
where op.name = opi.parent %s and not exists (select 1 from `tabInteractions` intr where op.name = intr.opportunity)""" % conditions, as_dict=1)



def get_item_map(filters):
        iwb_map = {}
#        from_date = getdate(filters["from_date"])
#        to_date = getdate(filters["to_date"])
	
        sle = get_opp_details(filters)

	dle = get_opp_details_1(filters)
	
             	
        for d in sle:
                
                key = (d.opportunity, d.item_code, d.interaction, d.in_date)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                "qty": 0.0, "value": 0.0,
				
                        })

                qty_dict = iwb_map[(d.opportunity, d.item_code, d.interaction, d.in_date)]

                
                qty_dict.qty = d.qty
                qty_dict.customer = d.customer
		qty_dict.mode = d.mode
		qty_dict.item_group = d.item_group
		qty_dict.inbound = d.inbound
		qty_dict.short_desc = d.short_desc
		qty_dict.comp_desc = d.comp_desc
		qty_dict.todo = d.todo
		
        if dle:      
		for d in dle:

 			key = (d.opportunity, d.item_code, d.interaction, d.in_date)
	                if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
					
        	                })

                	qty_dict = iwb_map[(d.opportunity, d.item_code, d.interaction, d.in_date)]

                
			qty_dict.qty = d.qty
	                qty_dict.customer = d.customer
			qty_dict.mode = d.mode
			qty_dict.item_group = d.item_group
			qty_dict.inbound = d.inbound
			qty_dict.short_desc = d.short_desc
			qty_dict.comp_desc = d.comp_desc
			qty_dict.todo = d.todo              
 	
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



