from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
import json


@frappe.whitelist()
def hellosub(loggedInUser):
	return 'pong'

@frappe.whitelist()
def get_requested_items_details(loggedInUser):

	
	outerJson = []
		
	record = frappe.db.sql("""select usr.role_profile_name from `tabUser` usr where usr.name = %s""",(loggedInUser))
	if record:
		cdrecord = frappe.db.sql("""select cd.name, cd.warehouse, cd.upstream_warehouse, cd.downstream_warehouse from `tabControlDocument` cd where cd.user =%s and cd.docstatus = 1 and cd.is_active = 1 and cd.is_default = 1""",(record[0]))
		if cdrecord:
			requestedItemRecords = frappe.db.sql(""" select ritms.item_code from `tabControlDocument Item` ritms where ritms.parent = %s""",(cdrecord[0][0]))
			warehouse = cdrecord[0][1]
			upstream_warehouse = cdrecord[0][2]
			print(upstream_warehouse)
			downstream_warehouse = cdrecord[0][3]
			
			if requestedItemRecords:
				for item in requestedItemRecords:
					itemDetails = frappe.db.sql("""select sle.item_code, sle.stock_uom, sle.qty_after_transaction from `tabStock Ledger Entry` sle where sle.item_code = %(itemCode)s and sle.warehouse = %(fromwh)s""",{'itemCode': item[0],'fromwh': upstream_warehouse})
								
					constructedJson = {}
					constructedJson ['item_code'] =  itemDetails[0][0]
					constructedJson['uom'] = itemDetails[0][1]
					constructedJson['available_qnty'] = get_latest_stock_qty(itemDetails[0][0],upstream_warehouse)
					constructedJson['reqd_qnty'] = 0.0
					
							   
					outerJson.append(constructedJson)
				return outerJson

	
		
