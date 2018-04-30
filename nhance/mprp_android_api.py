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
					itemDetails = frappe.db.sql("""select itmtable.item_code, itmtable.stock_uom from `tabItem` itmtable where itmtable.item_code = %(itemCode)s""",{'itemCode': item[0]})
								
					if itemDetails:
						constructedJson = {}
						availQnty = 0.0
						constructedJson ['item_code'] =  itemDetails[0][0]
						constructedJson['uom'] = itemDetails[0][1]
						if get_latest_stock_qty(itemDetails[0][0],upstream_warehouse):
							availQnty = get_latest_stock_qty(itemDetails[0][0],upstream_warehouse)
						constructedJson['available_qnty'] = availQnty
						constructedJson['reqd_qnty'] = 0.0
						outerJson.append(constructedJson)
					else:
						continue
				if len(outerJson) == 0:
					return None
				else:
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
			doc.submit()
			frappe.db.commit()
			docname = doc.name
			return """Success: Succesfully submitted a Material Request {mreq} document for the requested items. """.format(mreq=docname).encode('ascii')
		else:
			return """Error: Could not find the Control Document for the user {user}""".format(user = loggedInUser).encode('ascii')
	else:
		return """Error: Could not find the role profile for the user {user}""".format(user = loggedInUser).encode('ascii')

@frappe.whitelist()
def get_transformed_items_details(loggedInUser):
	outerJson = []
		
	record = frappe.db.sql("""select usr.role_profile_name from `tabUser` usr where usr.name = %s""",(loggedInUser))
	if record:
		cdrecord = frappe.db.sql("""select cd.name, cd.warehouse, cd.upstream_warehouse, cd.downstream_warehouse from `tabControlDocument` cd where cd.user =%s and cd.docstatus = 1 and cd.is_active = 1 and cd.is_default = 1""",(record[0]))
		if cdrecord:
			transformedItemMaterials = frappe.db.sql(""" select trsmditms.transformed_materials, trsmditms.pass_manufacturing_entries_based_on from `tabControlDocument Transformed Item` trsmditms where trsmditms.parent = %s""",(cdrecord[0][0]))
			warehouse = cdrecord[0][1]
			upstream_warehouse = cdrecord[0][2]
			downstream_warehouse = cdrecord[0][3]
			for itemRecord in transformedItemMaterials:
				if itemRecord:
					passBasedOn = itemRecord[1]
					transformedMaterialItemCode = itemRecord[0]
					print transformedMaterialItemCode
					bomRecord = frappe.db.sql("""select it.default_bom from `tabItem` it where it.item_code = %s""",(transformedMaterialItemCode))
					if bomRecord:
						bomDoc = frappe.get_doc("BOM", bomRecord[0][0])
						if bomDoc:
							bomquantity = bomDoc.quantity
						else:
							bomquantity = 1
					detailsOfItemToBeTransformed = frappe.db.sql("""select it.has_batch_no, it.has_serial_no, it.stock_uom from `tabItem` it where it.item_code = %(itemCode)s""",{'itemCode':transformedMaterialItemCode})
					if detailsOfItemToBeTransformed:
						
						#do something here
						hasBatchNumber = detailsOfItemToBeTransformed[0][0]
						hasSerialNumber = detailsOfItemToBeTransformed[0][1]
						item_stock_uom = detailsOfItemToBeTransformed[0][2]
						should_uom_be_whole_number = True
						#get whether the UOM can have fractions
						uomRecord = frappe.db.sql("""select uom.must_be_whole_number from `tabUOM` uom where uom.name = %s""",(item_stock_uom))
						if uomRecord:
							should_uom_be_whole_number = uomRecord[0][0]
						else:
							return """Error: Could not fetch UOM details for the item {item}""".format(item = transformedMaterialItemCode).encode('ascii')
						#now construct the inner json for each of the items to be transformed
						itemsJson = {}
						itemsJson['item_code'] = transformedMaterialItemCode
						itemsJson['stock_uom'] = item_stock_uom
						itemsJson['whole_number'] = should_uom_be_whole_number
						itemsJson['has_batch_no'] = hasBatchNumber
						itemsJson['has_serial_no'] = hasSerialNumber
						itemsJson['pass_based_on'] = passBasedOn
						itemsJson['quantity'] = bomquantity
						itemsJson['items_consumed'] = fetchItemsConsumedListFromBom(transformedMaterialItemCode)
						outerJson.append(itemsJson)
					else:
						return """Error: Could not find the details of the Item to be transformed from the Item Table""".encode('ascii')
				else:
					continue
			return outerJson

		else:
			return """Error: Could not find the control document for the user {usr}""".format(usr = loggedInUser).encode('ascii')
	else:
		return """Error: Could not find the user profile details for the user {usr}""".format(usr = loggedInUser).encode('ascii')

def fetchItemsConsumedListFromBom(transformedMaterialItemCode):
	outerJson = []
	
	bomRecord = frappe.db.sql("""select it.default_bom from `tabItem` it where it.item_code = %s""",(transformedMaterialItemCode))
	if bomRecord:
		bomDoc = frappe.get_doc("BOM", bomRecord[0][0])
		if bomDoc:
			bomItemsExplodedTableRecords = bomDoc.exploded_items
			if bomItemsExplodedTableRecords:
				for item in bomItemsExplodedTableRecords:
					innerJson = {}
					innerJson['item_code'] = item.item_code
					innerJson['stock_uom'] = item.stock_uom
					innerJson['qnty_consumed_per_unit'] = item.qty_consumed_per_unit
					innerJson['stock_qnty'] = item.stock_qty
					itemRecord = frappe.db.sql("""select itm.has_batch_no, itm.has_serial_no from `tabItem` itm where itm.item_code = %s""",(item.item_code))
					if itemRecord:
						innerJson['has_batch_no'] = itemRecord[0][0]
						innerJson['has_serial_no'] = itemRecord[0][1]
						uomRecord = frappe.db.sql("""select uom.must_be_whole_number from `tabUOM` uom where uom.name = %s""",(item.stock_uom))
						if uomRecord:
							innerJson['must_be_whole_no'] = uomRecord[0][0]
						else:
							innerJson['must_be_whole_no'] = True
					else:
						innerJson['has_batch_no'] = False
						innerJson['has_serial_no'] = False
					outerJson.append(innerJson)
	#for i in range(1,10):
	#	innerJson = {}
	#	innerJson['item_code'] = "itemCode"+str(i)
	#	outerJson.append(innerJson)
	return outerJson
