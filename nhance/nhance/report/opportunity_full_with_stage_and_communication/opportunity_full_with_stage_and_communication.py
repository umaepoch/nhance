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
        order_prev = "" 
        order_work = "" 
        item_prev = ""
        item_work = ""
        order_count = 0 
	item_count = 0
        tot_bal_qty = 0 
	tot_si_qty = 0
	tot_del_qty = 0
	tot_pend_qty = 0
	item_pend_qty = 0
	item_del_qty = 0
	temp_date = getdate("0001-01-01")
	diff_days = 0

        for (sales_order, item, delivery_date, del_note) in sorted(iwb_map):
                qty_dict = iwb_map[(sales_order, item, delivery_date, del_note)]
                data.append([
                        sales_order, qty_dict.so_date, qty_dict.so_del_date, delivery_date, qty_dict.customer, item, 
			item_map[item]["item_group"], item_map[item]["description"], item_map[item]["brand"],                    
                        qty_dict.si_qty, del_note, qty_dict.del_qty, qty_dict.pend_qty
                        
                    ])
	for rows in data: 
       		if order_count == 0: 
       			order_prev = rows[0] 
 			item_prev = rows[5]
			tot_si_qty = tot_si_qty + rows[9]
                        tot_del_qty = tot_del_qty + rows[11] 
			item_pend_qty = rows[9] - rows[11] 
			item_del_qty = rows[11]
			tot_pend_qty = tot_si_qty - tot_del_qty
			
			if rows[3] == temp_date:
				diff_days = 0
			else:
				diff_days = rows[3] - rows[2]
			summ_data.append([order_prev, rows[1], rows[2],
			 	rows[3], diff_days, rows[4], rows[5], rows[6], 
				rows[7], rows[8], rows[9], rows[10], rows[11], item_pend_qty
 				]) 
                else: 
			order_work = rows[0]
                        item_work = rows[5]
			
			if rows[3] == temp_date:
				diff_days = 0
			else:
				diff_days = rows[3] - rows[2]
			
			if order_prev == order_work: 
				tot_del_qty = tot_del_qty + rows[11]
				item_del_qty = item_del_qty + rows[11]
				
                                if item_prev == item_work:
					
					item_pend_qty = rows[9] - item_del_qty
								
				else:
					item_prev = item_work
					item_del_qty = rows[11]
					item_pend_qty = 0
					tot_si_qty = tot_si_qty + rows[9]
					item_pend_qty = rows[9] - item_del_qty	
				
				tot_pend_qty = tot_si_qty - tot_del_qty
				summ_data.append([order_prev, rows[1], rows[2],
			 	rows[3], diff_days, rows[4], rows[5], rows[6], 
				rows[7], rows[8], rows[9], rows[10], rows[11], item_pend_qty,
 				]) 
			else: 
				summ_data.append([order_prev, " ", 
			 	" ", " ", " ", " ", " ", " ", " ", " ", tot_si_qty, " ", tot_del_qty, tot_pend_qty
				
 				])	
				item_pend_qty = 0
				item_del_qty = rows[11]		 	 
				item_pend_qty = rows[9] - rows[11] - item_pend_qty

				summ_data.append([order_work, rows[1], rows[2],
			 	rows[3], diff_days, rows[4], rows[5], rows[6], 
				rows[7], rows[8], rows[9], rows[10], rows[11], item_pend_qty
 				]) 
                                
				tot_si_qty = 0
				tot_del_qty = 0
				tot_pend_qty = 0
                                tot_si_qty = tot_si_qty + rows[9]
                        	tot_del_qty = tot_del_qty + rows[11] 
				tot_pend_qty = tot_si_qty - tot_del_qty
				order_prev = order_work 
                                item_prev = item_work

		order_count = order_count + 1 
	summ_data.append([order_prev, " ", 
			 	" ", " ", " ", " ", " ", " ", " ", " ", tot_si_qty, " ", tot_del_qty, tot_pend_qty
 				])		 
	
		 
		 
						 
	return columns, summ_data 


def get_columns():
        """return columns"""
               
        columns = [
		_("SO Sales Order Number")+":Link/Sales Order:150",
		_("SO Posting Date")+":Date:150",
		_("SO Committed Delivery Date")+":Date:150",
		_("DN Actual Delivery Date")+":Date:100",
		_("Days Actual - Committed")+":Int:100",
                _("SO Customer")+"::150",
                _("SO Item")+":Link/Item:100",
		_("Item Group")+"::100",
	        _("Description")+"::140",
       	        _("Brand")+":Link/UOM:90",   
		_("SO Ordered Qty")+":Float:100",    
               	_("DN Delivery Note")+":Link/Delivery Note:100",
		_("DN Delivered Qty")+":Float:100",
		_("DN Balance Qty")+":Float:100"   
         ]

        return columns

def get_conditions(filters):
        conditions = ""
        if not filters.get("from_date"):
                frappe.throw(_("'From Date' is required"))

        if filters.get("to_date"):
                conditions += " and so.transaction_date <= '%s'" % frappe.db.escape(filters["to_date"])
        else:
                frappe.throw(_("'To Date' is required"))

        if filters.get("item_code"):
                conditions += " and si.item_code = '%s'" % frappe.db.escape(filters.get("item_code"), percent=False)
     
        if filters.get("name"):
                conditions += " and si.parent = '%s'" % frappe.db.escape(filters.get("name"), percent=False)

        if filters.get("warehouse"):
                conditions += " and si.warehouse = '%s'" % frappe.db.escape(filters.get("warehouse"), percent=False)
        return conditions

def get_sales_details(filters):
        conditions = get_conditions(filters)
	
        return frappe.db.sql("""select so.name as sales_order, so.transaction_date as date, so.customer, so.delivery_date as sodel_date, si.item_code, si.warehouse, si.qty as si_qty, si.delivered_qty as delivered_qty, dni.qty as del_qty, dn.posting_date as delivery_date, dni.parent as del_note
                from `tabDelivery Note Item` dni, `tabDelivery Note` dn, `tabSales Order Item` si, `tabSales Order` so
                where dni.item_code = si.item_code and so.status != "Cancelled" and dn.status in ("Completed", "To Bill") and so.name = si.parent and dn.name = dni.parent and dni.against_sales_order = so.name %s order by so.name, si.item_code, dn.posting_date asc, si.warehouse""" % conditions, as_dict=1)

def get_sales_details_wn_dn(filters):
        conditions = get_conditions(filters)
		
        return frappe.db.sql("""select so.name as sales_order, so.transaction_date as date, so.customer, so.delivery_date as sodel_date, si.item_code, si.warehouse, si.qty as si_qty, si.delivered_qty as delivered_qty, 0 as del_qty, date("2001-01-01") as delivery_date, " " as del_note
                from `tabSales Order Item` si, `tabSales Order` so where so.name = si.parent and so.status != "Cancelled" and not exists (
                select 1 from `tabDelivery Note Item` dni where dni.against_sales_order = so.name) order by so.name, si.item_code""", as_dict=1)

def get_item_map(filters):
        iwb_map = {}
        from_date = getdate(filters["from_date"])
        to_date = getdate(filters["to_date"])
	
        sle = get_sales_details(filters)
        
	dle = get_sales_details_wn_dn(filters)
        
             	
        for d in sle:
                
                key = (d.sales_order, d.item_code, d.delivery_date, d.del_note)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                "si_qty": 0.0, "del_qty": 0.0,
				"pend_qty": 0.0,
                                "val_rate": 0.0, "uom": None
                        })

                qty_dict = iwb_map[(d.sales_order, d.item_code, d.delivery_date, d.del_note)]

                
                qty_dict.si_qty = d.si_qty
                qty_dict.del_qty = d.del_qty
                qty_dict.delivered_qty = d.delivered_qty
                qty_dict.so_date = d.date
		qty_dict.so_del_date = d.sodel_date
        #        qty_dict.del_date = d.delivery_date
                qty_dict.customer = d.customer
                if qty_dict.si_qty > qty_dict.del_qty:
              		qty_dict.pend_qty = qty_dict.si_qty - qty_dict.del_qty - qty_dict.delivered_qty

	for d in dle:

                key = (d.sales_order, d.item_code, d.delivery_date, d.del_note)
                if key not in iwb_map:
                        iwb_map[key] = frappe._dict({
                                "si_qty": 0.0, "del_qty": 0.0,
				"pend_qty": 0.0,
                                "val_rate": 0.0, "uom": None
                        })

                qty_dict = iwb_map[(d.sales_order, d.item_code, d.delivery_date, d.del_note)]

                
                qty_dict.si_qty = d.si_qty
                qty_dict.del_qty = d.del_qty
                qty_dict.delivered_qty = d.delivered_qty
                qty_dict.so_date = d.date
		qty_dict.so_del_date = d.sodel_date
        #        qty_dict.del_date = d.delivery_date
                qty_dict.customer = d.customer
                if qty_dict.si_qty > qty_dict.del_qty:
              		qty_dict.pend_qty = qty_dict.si_qty - qty_dict.del_qty - qty_dict.delivered_qty


               
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



