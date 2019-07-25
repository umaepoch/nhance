from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime
from erpnext.stock.utils import get_latest_stock_qty
from erpnext.stock.get_item_details import get_batch_qty
from erpnext.stock.doctype.batch.batch import get_batch_no
from erpnext.stock.doctype.batch.batch import get_batches
from erpnext.stock.get_item_details import get_serial_no
import json

@frappe.whitelist()
def get_transformed_items_details(loggedInUser):
	outerJson = []
		
	record = frappe.db.sql("""select usr.role_profile_name from `tabUser` usr where usr.name = %s""",(loggedInUser))
	if record:
		cdrecord = frappe.db.sql("""select cd.name, cd.warehouse, cd.upstream_warehouse, cd.downstream_warehouse from `tabControlDocument` cd where cd.user =%s and cd.docstatus = 1 and cd.is_active = 1 and cd.is_default = 1""",(record[0]))
		if cdrecord:
			transformedItemMaterials = frappe.db.sql(""" select trsmditms.transformed_materials, trsmditms.pass_manufacturing_entries_based_on, trsmditms.bom_to_be_used from `tabControlDocument Transformed Item` trsmditms where trsmditms.parent = %s""",(cdrecord[0][0]))
			warehouse = cdrecord[0][1]
			upstream_warehouse = cdrecord[0][2]
			downstream_warehouse = cdrecord[0][3]
			for itemRecord in transformedItemMaterials:
				if itemRecord:
					passBasedOn = itemRecord[1]
					transformedMaterialItemCode = itemRecord[0]
					bomRecord = itemRecord[2]
					#print "The BOM used for item "+itemRecord[0]+"is:"+itemRecord[2]
					if bomRecord:
						bomDoc = frappe.get_doc("BOM", bomRecord)
						if bomDoc:
							bomquantity = bomDoc.quantity
						else:
							bomquantity = 1
					detailsOfItemToBeTransformed = frappe.db.sql("""select it.has_batch_no, it.has_serial_no, it.stock_uom from `tabItem` it where it.item_code = %(itemCode)s""",{'itemCode':transformedMaterialItemCode})
					if detailsOfItemToBeTransformed:
						
						#do something here
						hasBatchNumber = detailsOfItemToBeTransformed[0][0]
						if hasBatchNumber == 1:
							batchRecords = getBatchNos(transformedMaterialItemCode, warehouse)
						else:
							batchRecords = None
						hasSerialNumber = detailsOfItemToBeTransformed[0][1]
						if hasSerialNumber == 1:
							serialNoRecords = getSerialNoRecords(transformedMaterialItemCode, warehouse)
						else:
							serialNoRecords = None
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
						itemsJson['items_consumed'] = fetchItemsConsumedListFromBom(transformedMaterialItemCode, warehouse, bomRecord)
						itemsJson['batch_nos'] = batchRecords
						itemsJson['serial_nos'] = serialNoRecords
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

def fetchItemsConsumedListFromBom(transformedMaterialItemCode, warehouse, bomRecord):
	outerJson = []
	
	#bomRecord = frappe.db.sql("""select it.default_bom from `tabItem` it where it.item_code = %s""",(transformedMaterialItemCode))
	if bomRecord:
		bomDoc = frappe.get_doc("BOM", bomRecord)
		#print "The BOM in fetchItemsConsumedListFromBOM is: "+bomRecord
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
						if itemRecord[0][0] == 1: 
							innerJson['batch_nos'] = getBatchNos(item.item_code, warehouse)
						else:
							innerJson['batch_nos'] = None
						innerJson['has_serial_no'] = itemRecord[0][1]
						if itemRecord[0][1] == 1:
							innerJson['serial_nos'] = getSerialNoRecords(item.item_code, warehouse)
						else:
							innerJson['serial_nos'] = None
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


def getBatchNos(transformedMaterialItemCode, warehouse):
	
	outerJson = []
	#batchRecords = frappe.db.sql("""select sle.batch_no, sle.qty_after_transaction from `tabStock Ledger Entry` sle where sle.item_code = %(str1)s and sle.warehouse = %(str2)s""",{'str1': transformedMaterialItemCode, 'str2': warehouse})
	batchRecords = get_batches(transformedMaterialItemCode, warehouse)
	if batchRecords:
		for record in batchRecords:
			innerJson = {}
			innerJson['batch_no'] = record.batch_id
			innerJson['batch_qty_at_warehouse'] = record.qty
			
			outerJson.append(innerJson)
		return outerJson
	else:
		#print "I am in else part of if batchRecords: why?" 		
		return None

def getSerialNoRecords(transformedMaterialItemCode, warehouse):
	
	outerJson = []
	serialNoRecords = frappe.db.sql("""select sn.serial_no from `tabSerial No` sn where sn.item_code = %(str1)s and sn.warehouse = %(str2)s""", {'str1': transformedMaterialItemCode, 'str2': warehouse})
	if serialNoRecords:
		for record in serialNoRecords:
			innerJson = {}
			innerJson['serial_no'] = record[0]
			innerJson['warehouse'] = warehouse
			outerJson.append(innerJson)
		return outerJson
	else:
		#print "I am in else part of if serialNoRecords..why? this is strange behaviour"
		return None	

def getBatchAndSerialNos(itemCode, warehouse):
	outerJson = []
	records = frappe.db.sql("""select sle.batch_no, sle.serial_no, sle.qty_after_transaction from `tabStock Ledger Entry` sle where sle.item_code = %(str1)s and sle.warehouse = %(str2)s """,{'str1': itemCode, 'str2': warehouse})
	if records:
		for record in records:
			innerJson = {}
			if record[0]:
				innerJson['batch_no'] = record[0]
				innerJson['batch_qty_at_warehouse'] = get_batch_qty(record[0], warehouse, itemCode)
			else:
				innerJson['batch_no'] = None
				innerJson['batch_qty_at_warehouse'] = None
			if record[1]:
				innerJson['serial_no'] = record[1]
			else:
				innerJson['serial_no'] = None
			outerJson.append(innerJson)
		return outerJson
		
	else:
		return None

@frappe.whitelist()
def set_transformed_items_details(loggedInUser,transformedItemsList):
	
	item_consumed_list = []
	record = frappe.db.sql("""select usr.role_profile_name from `tabUser` usr where usr.name = %s""",(loggedInUser))
	if record:
		cdrecord = frappe.db.sql("""select cd.name, cd.warehouse, cd.upstream_warehouse, cd.downstream_warehouse from `tabControlDocument` cd where cd.user =%s and cd.docstatus = 1 and cd.is_active = 1 and cd.is_default = 1""",(record[0]))
		if cdrecord:
			company = frappe.defaults.get_user_default("Company")
			purposeType = "Manufacture"
			warehouse = cdrecord[0][1]
			upstream_warehouse = cdrecord[0][2]
			downstream_warehouse = cdrecord[0][3]
			newJson = {
					"company": company,
					"docType": "Stock Entry",
					"title"  : "Manufacture",
					"purpose": "Manufacture",
					"items"  :[
						  ]
				 }	
			data = json.loads(transformedItemsList)
			for jsonobj in data['itemMadeModelList']:
				item_made_code = jsonobj['itemMadeCode']
				slNos = " "
				batchNos = " "
				item_made_qty = jsonobj['qtyReqd']
				item_made_stock_uom = jsonobj['stockUOM']
				item_made_json = {
							"doctype": "Stock Entry Detail",
							"item_code": item_made_code,
							"description": "item_record.description",
							"uom": item_made_stock_uom,
							"qty": item_made_qty,
							"t_warehouse": warehouse
						 }
				if jsonobj['hasSerialNos']:
					for entry in jsonobj['selectedSerialNos']:
						slNos= slNos+entry+'\n'
					item_made_json["serial_no"] = slNos
				
				if jsonobj['hasBatchNos']:
					batch = jsonobj['batchNoModelArrayList'][0]
					batchjson = {
							"batch_id": batch['batchNo'],
							"item" : item_made_code,
							"expiry_date": batch['batchExpDate']
						    }
					new_batch = frappe.new_doc("Batch")
					new_batch.update(batchjson)
					new_batch.save()
					item_made_json["batch_no"] = batch['batchNo']
				newJson["items"].append(item_made_json)
							
				item_consumed_list = jsonobj['itemConsumedModelList']
				if item_consumed_list is None:
					return """Error: Could not make entry in the items table for the items consumed in the Stock Entry document, the list of items consumed is missing. Could not create a Stock Entry document on ERPNext"""
				for item_consumed in item_consumed_list:
					item_consumed_json_list = get_the_item_consumed_json(item_consumed, warehouse)
					if item_consumed_json_list is not None:
						for  item  in item_consumed_json_list:
							newJson["items"].append(item)
					else:
						return """Error: Something went wrong while entering the items in the Stock Entry document, Could not create a stock entry document on ERPNext""".encode('ascii')
			doc = frappe.new_doc("Stock Entry")
			doc.update(newJson)
			doc.save()
			doc.submit()
			frappe.db.commit()
			return """Success: Items have been succesfully transformed and Stock Entry document has been created"""
		else:
			return """Error: Could not find the control document for the user {usr}""".format(usr = loggedInUser).encode('ascii')
	else:
		return """Error: Could not find the user {usr} on ERPNext. Please make sure the user credentials are correct""".format(usr = loggedInUser).encode('ascii')

def get_the_item_consumed_json(item_consumed, warehouse):
	
	item_consumed_code = item_consumed['itemConsumedCode']
	item_consumed_qty = item_consumed['itemConsumedQnty']
	item_consumed_stock_uom = item_consumed['stockUOM']
	item_consumed_json_list = []
	selected_sln_list = []
	selected_batch_list = []
	
	if item_consumed['hasSerialNos']:
		if item_consumed['serialNoModelList'] is not None:
			for sln in item_consumed['serialNoModelList']:
				if sln['selected']:
					selected_sln_list.append(sln)
	
	if item_consumed['hasBatchNos']:
		item_consumed_batch_list = item_consumed['batchNoModelList']
		if len(item_consumed_batch_list) == 1:
			item_consumed_json = {
						"doctype": "Stock Entry Detail",
						"item_code": item_consumed_code,
						"description": item_consumed_code,
						"uom": item_consumed_stock_uom,
						"qty": item_consumed_qty,
						"s_warehouse": warehouse,
						"batch_no": item_consumed_batch_list[0]['batchNo']
					     }
			if item_consumed['hasSerialNos'] and selected_sln_list:
				slns = " "
				for i in range(int(item_consumed_qty)):
					slns = slns+selected_sln_list[i]['serialNo']+'\n'
				item_consumed_json["serial_no"] = slns
			item_consumed_json_list.append(item_consumed_json)
		elif len(item_consumed_batch_list) > 1:
			for batch in item_consumed_batch_list:
				if batch['selected']:
					item_consumed_json = {
								"doctype": "Stock Entry Detail",
								"item_code": item_consumed_code,
								"description": item_consumed_code,
								"uom": item_consumed_stock_uom,
								"qty": batch['requestedBatchQty'],
								"s_warehouse":warehouse,
								"batch_no": batch['batchNo']
							    }
					if item_consumed['hasSerialNos'] and selected_sln_list is not None:
						batchslnlist = getbatchwiseserialnos(batch['batchNo'],warehouse,item_consumed_code)
						count =0
						slns = " "
						for serial_No in selected_sln_list:
							if serial_No['serialNo'] in batchslnlist and count < int(batch['requestedBatchQty']):
								slns = slns+serial_No['serialNo']+'\n'
								count = count + 1
						item_consumed_json["serial_no"] = slns
					item_consumed_json_list.append(item_consumed_json)
		else:
			return None
	else:
		item_consumed_json = {
			"doctype": "Stock Entry Detail",
			"item_code": item_consumed_code,
			"description": item_consumed_code,
			"uom": item_consumed_stock_uom,
			"qty": item_consumed_qty,
			"s_warehouse": warehouse,
		     }
		if item_consumed['hasSerialNos'] and selected_sln_list is not None:
			slnos = " "
			for i in range(int(item_consumed_qty)):
				slnos = slnos+selected_sln_list[i]['serialNo']+'\n'
			item_consumed_json["serial_no"] = slnos
		item_consumed_json_list.append(item_consumed_json)
	if item_consumed_json_list is not None:
		return item_consumed_json_list
	else:
		return None

@frappe.whitelist()
def getbatchwiseserialnos(batch_no,warehouse,item_code):

	slnlist = []
	records = frappe.db.sql("""select sle.serial_no from `tabStock Ledger Entry` sle where sle.item_code = %(str1)s and sle.batch_no = %(str2)s and sle.warehouse = %(wh)s""",{'str1': item_code, 'str2': batch_no, 'wh':warehouse })
	if records:
		for record in records:
			
			data = record[0].split('\n')
			for i in range(0,len(data)):
				snrecord = frappe.db.sql("""select sn.name from `tabSerial No` sn where sn.serial_no = %(sln)s and sn.warehouse = %(wh)s""", {'sln': data[i], 'wh': warehouse})
				for slno in snrecord:
					serialno = slno[0].encode('ascii')
					slnlist.append(serialno)
		return slnlist
