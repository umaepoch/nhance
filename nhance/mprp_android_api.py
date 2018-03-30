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

@frappe.whitelist()
def set_requested_items_details(loggedInUser, reqdByDate, reqdItemsList=[]):

	
	record = frappe.db.sql("""select usr.role_profile_name from `tabUser` usr where usr.name = %s""",(loggedInUser))
	if record:
		
		cdrecord = frappe.db.sql("""select cd.name, cd.warehouse, cd.upstream_warehouse, cd.downstream_warehouse from `tabControlDocument` cd where cd.user =%s and cd.docstatus = 1 and cd.is_active = 1 and cd.is_default = 1""",(record[0]))
		if cdrecord:
			company = frappe.defaults.get_user_default("Company")
				
			purposeType = "Material Transfer"
			transaction_date = reqdByDate
					
			warehouse = cdrecord[0][1]
			upstream_warehouse = cdrecord[0][2]
			downstream_warehouse = cdrecord[0][3]
			newJson =	{
					  "company": company,
					  "doctype": "Material Request",
					  "title": "Material Transfer",
					  "material_request_type": purposeType,
					  "schedule_date":reqdByDate,
					  "items":[
						  ]
					}
			data = json.loads(reqdItemsList)
			for jsonobject in data['requiredItems']:
				item_code= jsonobject['item_code']
				reqd_qty = jsonobject['reqd_qnty']
				stock_uom = jsonobject['uom']
				itemRecord = frappe.get_doc("Item",item_code)
				innerJson = {}
				itemdescription = ""
				conversion_factor = "dummy"
				if itemRecord:
					itemdescription = itemRecord.description
					for itemUOM in itemRecord.uoms:
						if itemUOM.uom == stock_uom:
							conversion_factor = itemUOM.conversion_factor
							break
				else:
					return """Error: Couldnt find the Item doctype for the item code {it}. Could not create the Material Request Document""".format(it = item_code).encode('ascii')
				if conversion_factor == "dummy":
					return """Error: Couldnt find the conversion factor for the item code {it} with stock UOM {stuom}. Could not create the Material Request Document""".format(it = item_code, stuom = stock_uom).encode('ascii')
								
				print reqd_qty
				
				innerJson = {
						"doctype": "Material Request Item",
						"item_code": item_code,
						"description": itemdescription,
						"qty":reqd_qty,
						"warehouse": warehouse,
						"uom":stock_uom,
						"stock_uom" : stock_uom,
						"conversion_factor": conversion_factor,
						"schedule_date":reqdByDate
						
					    }
				newJson["items"].append(innerJson)
			doc = frappe.new_doc("Material Request")
			doc.update(newJson)
			doc.save()
			frappe.db.commit()
			docname = doc.name
			return """Success: Succesfully created a Material Request {mreq} document. Click on Submit to submit it!""".format(mreq=docname).encode('ascii')
		else:
			return """Error: Could not find the Control Document for the user {user}""".format(user = loggedInUser).encode('ascii')
	else:
		return """Error: Could not find the role profile for the user {user}""".format(user = loggedInUser).encode('ascii')


