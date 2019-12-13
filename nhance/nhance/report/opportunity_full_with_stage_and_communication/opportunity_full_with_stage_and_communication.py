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


        for (opportunity, item, sales_cycle, communication_date) in sorted(iwb_map):
                qty_dict = iwb_map[(opportunity, item, sales_cycle, communication_date)]
                data.append([
                        opportunity, qty_dict.customer, item, qty_dict.item_group, qty_dict.qty, sales_cycle, qty_dict.stage_date, qty_dict.value, qty_dict.closing_date, qty_dict.stage, qty_dict.opportunity_purpose, qty_dict.buying_status, qty_dict.support_needed, qty_dict.subject, communication_date, qty_dict.reference_name, qty_dict.recipients, qty_dict.phone, qty_dict.content
                        
                    ])
	for rows in data: 
       		if opp_count == 0: 
       			opp_prev = rows[0] 
 			item_prev = rows[2]
			tot_qty = tot_qty + rows[4]
			tot_val = tot_val + rows[7]
                        			
			
			summ_data.append([opp_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[7], 
				rows[8], rows[9], rows[10], rows[11], rows[12], rows[13], rows[14], rows[15], rows[16], rows[17], rows[18]
 				]) 
                else: 
			opp_work = rows[0]
                        item_work = rows[2]
			
					
			if opp_prev == opp_work: 
				tot_qty = tot_qty + rows[4]
				tot_val = tot_val + rows[7]
		
                                summ_data.append([opp_prev, rows[1], rows[2], rows[3], rows[4], rows[5], rows[7], rows[8], rows[9], rows[10], rows[11], rows[12], rows[13], rows[14], rows[15], rows[16], rows[17], rows[18]
 				]) 
			else: 
				summ_data.append([opp_prev, " ", " ", " ", tot_qty, " ", tot_val, " ", " ", " ", " "
					" ", " ", " ", " ", " ", " ", " " 
				
 				])	
				

				summ_data.append([opp_work,  rows[1], rows[2], rows[3], rows[4], rows[5], rows[7], 
				rows[8], rows[9], rows[10], rows[11], rows[12], rows[13], rows[14], rows[15], rows[16], rows[17], rows[18]
 				]) 
		
				tot_qty = 0
				tot_val = 0
                                
				tot_qty = tot_qty + rows[4] 
				tot_val = tot_val + rows[7]

				opp_prev = opp_work 
                                item_prev = item_work

		opp_count = opp_count + 1 
	summ_data.append([opp_prev, " ", " ", " ", tot_qty, " ", tot_val, " ", " ",
					" ", " ", " ", " ", " ", " ", " ", " ", " "
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
		_("Sales Cycle")+"::100",
 #               _("Stage Date")+":Date:100",
		_("Value")+":Float:100",
		_("Closing Date")+":Date:100",
	        _("Stage")+"::140",
       	        _("Opportunity Purpose")+"::90",   
		_("Buying Status")+"::90", 
               	_("Support Needed")+"::100",
		_("Subject")+"::100",
		_("Communication Date")+":Date:100",
		_("Reference Name")+"::100",
		_("Contact")+"::100",
		_("Phone")+"::100",
		_("Message")+"::150"


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
	
        return frappe.db.sql("""select sc.reference_name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, sc.name as sales_cycle, sc.stage_date as stage_date, sc.value as value, sc.closing_date as closing_date, sc.stage as stage, sc.opportunity_purpose as opportunity_purpose, sc.buying_status as buying_status, sc.support_needed as support_needed, co.subject as subject, co.communication_date as communication_date, co.reference_name as reference_name, co.recipients as recipients, co.phone_no as phone, co.content as content

from `tabOpportunity` op, `tabOpportunity Item` opi, `tabProposal Stage` sc, `tabCommunication` co
where op.name = opi.parent and op.name = sc.reference_name and op.name = co.reference_name %s 
and sc.stage_date in (select co1.communication_date from `tabCommunication` co1, `tabProposal Stage` sc1 where co1.reference_name = sc1.reference_name and sc1.reference_name = sc.reference_name)
""" % conditions, as_dict=1)

def get_opp_details_1(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select op.name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, " " as sales_cycle, " " as stage_date, 0 as value, " " as closing_date, " " as stage, " " as opportunity_purpose, " " as buying_status, " " as support_needed, " " as subject, " " as communication_date, " " as reference_name, " " as recipients, " " as phone, " " as content

from `tabOpportunity` op, `tabOpportunity Item` opi
where op.name = opi.parent %s and not exists (select 1 from `tabCommunication` co where op.name = co.reference_name)
and not exists (select 1 from `tabProposal Stage` sc where op.name = sc.reference_name)
""" % conditions, as_dict=1)

def get_opp_details_2(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select sc.reference_name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, sc.name as sales_cycle, sc.stage_date as stage_date, sc.value as value, sc.closing_date as closing_date, sc.stage as stage, sc.opportunity_purpose as opportunity_purpose, sc.buying_status as buying_status, sc.support_needed as support_needed, " " as subject, " " as communication_date, " " as reference_name, " " as recipients, " " as phone, " " as content

from `tabOpportunity` op, `tabOpportunity Item` opi, `tabProposal Stage` sc
where op.name = opi.parent and  op.name = sc.reference_name %s and not exists (select 1 from `tabCommunication` co where op.name = co.reference_name)
""" % conditions, as_dict=1)


def get_opp_details_3(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select op.name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, " " as sales_cycle, " " as stage_date, 0 as value, " " as closing_date, " " as stage, " " as opportunity_purpose, " " as buying_status, " " as support_needed, co.subject as subject, co.communication_date as communication_date, co.reference_name as reference_name, co.recipients as recipients, co.phone_no as phone, co.content as content

from `tabOpportunity` op, `tabOpportunity Item` opi, `tabCommunication` co
where op.name = opi.parent and op.name = co.reference_name %s
and not exists (select 1 from `tabProposal Stage` sc where op.name = sc.reference_name)
""" % conditions, as_dict=1)

def get_opp_details_4(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select sc.reference_name as opportunity, op.customer as customer, opi.item_code as item_code, opi.item_group as item_group, opi.qty as qty, sc.name as sales_cycle, sc.stage_date as stage_date, sc.value as value, sc.closing_date as closing_date, sc.stage as stage, sc.opportunity_purpose as opportunity_purpose, sc.buying_status as buying_status, sc.support_needed as support_needed, co.subject as subject, co.communication_date as communication_date, co.reference_name as reference_name, co.recipients as recipients, co.phone_no as phone, co.content as content

from `tabOpportunity` op, `tabOpportunity Item` opi, `tabProposal Stage` sc, `tabCommunication` co
where op.name = opi.parent and op.name = sc.reference_name and op.name = co.reference_name %s 
and sc.stage_date not in (select co1.communication_date from `tabCommunication` co1, `tabProposal Stage` sc1 where co1.reference_name = sc1.reference_name and sc1.reference_name = sc.reference_name)
""" % conditions, as_dict=1)




def get_item_map(filters):
        iwb_map = {}
        from_date = getdate(filters["from_date"])
        to_date = getdate(filters["to_date"])
	
        sle = get_opp_details(filters)

	dle = get_opp_details_1(filters)
	kle = get_opp_details_2(filters)
	mle = []
	mle = get_opp_details_3(filters)
	ple = []
	ple = get_opp_details_4(filters)
        
             	
        for d in sle:
                
                key = (d.opportunity, d.item_code, d.sales_cycle, d.communication_date)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                "qty": 0.0, "value": 0.0,
				
                        })

                qty_dict = iwb_map[(d.opportunity, d.item_code, d.sales_cycle, d.communication_date)]

                
                qty_dict.qty = d.qty
                qty_dict.value = d.value
                qty_dict.customer = d.customer
		qty_dict.stage_date = d.stage_date
		qty_dict.stage = d.stage
		qty_dict.item_group = d.item_group
		qty_dict.closing_date = d.closing_date
		qty_dict.opportunity_purpose = d.opportunity_purpose
		qty_dict.buying_status = d.buying_status
		qty_dict.support_needed = d.support_needed
		qty_dict.subject = d.subject
	        qty_dict.communication_date = d.communication_date
		qty_dict.reference_name = d.reference_name
		qty_dict.recipients = d.recipients
		qty_dict.phone_no = d.phone
		qty_dict.content = d.content

        if dle:      
		for d in dle:

 			key = (d.opportunity, d.item_code, d.sales_cycle, d.communication_date)
	                if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
					
        	                })

                	qty_dict = iwb_map[(d.opportunity, d.item_code, d.sales_cycle, d.communication_date)]

                
	                qty_dict.qty = d.qty
        	        qty_dict.value = d.value
        	        qty_dict.customer = d.customer
			qty_dict.stage_date = d.stage_date
			qty_dict.stage = d.stage
			qty_dict.item_group = d.item_group
			qty_dict.closing_date = d.closing_date
			qty_dict.opportunity_purpose = d.opportunity_purpose
			qty_dict.buying_status = d.buying_status
			qty_dict.support_needed = d.support_needed
			qty_dict.subject = d.subject
		        qty_dict.communication_date = d.communication_date
			qty_dict.reference_name = d.reference_name
			qty_dict.recipients = d.recipients
			qty_dict.phone_no = d.phone
			qty_dict.content = d.content
              
 	if kle:      
		for d in kle:

			key = (d.opportunity, d.item_code, d.sales_cycle, d.communication_date)
	                if key not in iwb_map:
	      	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
					
        	                })

                	qty_dict = iwb_map[(d.opportunity, d.item_code, d.sales_cycle, d.communication_date)]

                
	                qty_dict.qty = d.qty
        	        qty_dict.value = d.value
        	        qty_dict.customer = d.customer
			qty_dict.stage_date = d.stage_date
			qty_dict.stage = d.stage
			qty_dict.item_group = d.item_group
			qty_dict.closing_date = d.closing_date
			qty_dict.opportunity_purpose = d.opportunity_purpose
			qty_dict.buying_status = d.buying_status
			qty_dict.support_needed = d.support_needed
			qty_dict.subject = d.subject
		        qty_dict.communication_date = d.communication_date
			qty_dict.reference_name = d.reference_name
			qty_dict.recipients = d.recipients
			qty_dict.phone_no = d.phone
			qty_dict.content = d.content

	if mle:      
		for d in mle:

 			key = (d.opportunity, d.item_code, d.sales_cycle, d.communication_date)
	                if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
					
        	                })

                	qty_dict = iwb_map[(d.opportunity, d.item_code, d.sales_cycle, d.communication_date)]

                
	                qty_dict.qty = d.qty
        	        qty_dict.value = d.value
        	        qty_dict.customer = d.customer
			qty_dict.stage_date = d.stage_date
			qty_dict.stage = d.stage
			qty_dict.item_group = d.item_group
			qty_dict.closing_date = d.closing_date
			qty_dict.opportunity_purpose = d.opportunity_purpose
			qty_dict.buying_status = d.buying_status
			qty_dict.support_needed = d.support_needed
			qty_dict.subject = d.subject
		        qty_dict.communication_date = d.communication_date
			qty_dict.reference_name = d.reference_name
			qty_dict.recipients = d.recipients
			qty_dict.phone_no = d.phone
			qty_dict.content = d.content
               
	if ple:      
		for d in ple:

 			key = (d.opportunity, d.item_code, d.sales_cycle, d.communication_date)
	                if key not in iwb_map:
        	                iwb_map[key] = frappe._dict({
        	                        "qty": 0.0, "value": 0.0,
					
        	                })

                	qty_dict = iwb_map[(d.opportunity, d.item_code, d.sales_cycle, d.communication_date)]

                
	                qty_dict.qty = d.qty
        	        qty_dict.value = d.value
        	        qty_dict.customer = d.customer
			qty_dict.stage_date = d.stage_date
			qty_dict.stage = d.stage
			qty_dict.item_group = d.item_group
			qty_dict.closing_date = d.closing_date
			qty_dict.opportunity_purpose = d.opportunity_purpose
			qty_dict.buying_status = d.buying_status
			qty_dict.support_needed = d.support_needed
			qty_dict.subject = d.subject
		        qty_dict.communication_date = d.communication_date
			qty_dict.reference_name = d.reference_name
			qty_dict.recipients = d.recipients
			qty_dict.phone_no = d.phone
			qty_dict.content = d.content

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



