# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# ERPNext - web based ERP (http://erpnext.com)
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import cstr, flt, getdate, new_line_sep, nowdate, add_days
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.stock_balance import update_bin_qty, get_indented_qty
from erpnext.controllers.buying_controller import BuyingController
from erpnext.manufacturing.doctype.production_order.production_order import get_item_details#from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.buying.utils import check_for_closed_status, validate_for_items
import datetime
from collections import defaultdict
import operator
import frappe
import json
import time
import math
import ast
form_grid_templates = {
	"items": "templates/form_grid/material_request_grid.html"
}

class StockRequisition(BuyingController):
	def get_feed(self):
		return _("{0}: {1}").format(self.status, self.material_request_type)

	def check_if_already_pulled(self):
		pass

	def validate_qty_against_so(self):
		so_items = {} # Format --> {'SO/00001': {'Item/001': 120, 'Item/002': 24}}
		for d in self.get('items'):
			if d.sales_order:
				if not so_items.has_key(d.sales_order):
					so_items[d.sales_order] = {d.item_code: flt(d.qty)}
				else:
					if not so_items[d.sales_order].has_key(d.item_code):
						so_items[d.sales_order][d.item_code] = flt(d.qty)
					else:
						so_items[d.sales_order][d.item_code] += flt(d.qty)

		for so_no in so_items.keys():
			for item in so_items[so_no].keys():
				already_indented = frappe.db.sql("""select sum(qty)
					from `tabStock Requisition Item`
					where item_code = %s and sales_order = %s and
					docstatus = 1 and parent != %s""", (item, so_no, self.name))
				already_indented = already_indented and flt(already_indented[0][0]) or 0

				actual_so_qty = frappe.db.sql("""select sum(stock_qty) from `tabSales Order Item`
					where parent = %s and item_code = %s and docstatus = 1""", (so_no, item))
				actual_so_qty = actual_so_qty and flt(actual_so_qty[0][0]) or 0

				if actual_so_qty and (flt(so_items[so_no][item]) + already_indented > actual_so_qty):
					frappe.throw(_("Material Request of maximum {0} can be made for Item {1} against Sales Order {2}").format(actual_so_qty - already_indented, item, so_no))

	# Validate
	# ---------------------
	def validate(self):
		super(StockRequisition, self).validate()

		self.validate_schedule_date()
		self.validate_uom_is_integer("uom", "qty")

		if not self.status:
			self.status = "Draft"

		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, 
			["Draft", "Submitted", "Stopped", "Cancelled", "Pending",
			"Partially Ordered", "Ordered", "Issued", "Transferred"])

		validate_for_items(self)

		# self.set_title()
		# self.validate_qty_against_so()
		# NOTE: Since Item BOM and FG quantities are combined, using current data, it cannot be validated
		# Though the creation of Material Request from a Production Plan can be rethought to fix this

	def set_title(self):
		'''Set title as comma separated list of items'''
		items = []
		for d in self.items:
			if d.item_code not in items:
				items.append(d.item_code)
			if(len(items)==4):
				break

		self.title = ', '.join(items)

	def on_submit(self):
		# frappe.db.set(self, 'status', 'Submitted')
		self.update_requested_qty()

	def before_save(self):
		self.set_status(update=True)

	def before_submit(self):
		self.set_status(update=True)

	def before_cancel(self):
		# if MRQ is already closed, no point saving the document
		check_for_closed_status(self.doctype, self.name)
		self.set_status(update=True, status='Cancelled')

	def check_modified_date(self):
		mod_db = frappe.db.sql("""select modified from `tabStock Requisition` where name = %s""",
			self.name)
		date_diff = frappe.db.sql("""select TIMEDIFF('%s', '%s')"""
			% (mod_db[0][0], cstr(self.modified)))

		if date_diff and date_diff[0][0]:
			frappe.throw(_("{0} {1} has been modified. Please refresh.").format(_(self.doctype), self.name))

	def update_status(self, status):
		self.check_modified_date()
		self.status_can_change(status)
		self.set_status(update=True, status=status)
		self.update_requested_qty()

	def status_can_change(self, status):
		"""
		validates that `status` is acceptable for the present controller status
		and throws an Exception if otherwise.
		"""
		if self.status and self.status == 'Cancelled':
			# cancelled documents cannot change
			if status != self.status:
				frappe.throw(
					_("{0} {1} is cancelled so the action cannot be completed").
						format(_(self.doctype), self.name),
					frappe.InvalidStatusError
				)

		elif self.status and self.status == 'Draft':
			# draft document to pending only
			if status != 'Pending':
				frappe.throw(
					_("{0} {1} has not been submitted so the action cannot be completed").
						format(_(self.doctype), self.name),
					frappe.InvalidStatusError
				)

	def on_cancel(self):
		self.update_requested_qty()

	def update_completed_qty(self, mr_items=None, update_modified=True):
		if self.material_request_type == "Purchase":
			return

		if not mr_items:
			mr_items = [d.name for d in self.get("items")]

		for d in self.get("items"):
			if d.name in mr_items:
				if self.material_request_type in ("Material Issue", "Material Transfer"):
					d.ordered_qty =  flt(frappe.db.sql("""select sum(transfer_qty)
						from `tabStock Entry Detail` where material_request = %s
						and material_request_item = %s and docstatus = 1""",
						(self.name, d.name))[0][0])

					if d.ordered_qty and d.ordered_qty > d.stock_qty:
						frappe.throw(_("The total Issue / Transfer quantity {0} in Material Request {1}  \
							cannot be greater than requested quantity {2} for Item {3}").format(d.ordered_qty, d.parent, d.qty, d.item_code))

				elif self.material_request_type == "Manufacture":
					d.ordered_qty = flt(frappe.db.sql("""select sum(qty)
						from `tabProduction Order` where material_request = %s
						and material_request_item = %s and docstatus = 1""",
						(self.name, d.name))[0][0])

				frappe.db.set_value(d.doctype, d.name, "ordered_qty", d.ordered_qty)

		target_ref_field = 'qty' if self.material_request_type == "Manufacture" else 'stock_qty'
		self._update_percent_field({
			"target_dt": "Stock Requisition Item",
			"target_parent_dt": self.doctype,
			"target_parent_field": "per_ordered",
			"target_ref_field": target_ref_field,
			"target_field": "ordered_qty",
			"name": self.name,
		}, update_modified)

	def update_requested_qty(self, mr_item_rows=None):
		"""update requested qty (before ordered_qty is updated)"""
		item_wh_list = []
		for d in self.get("items"):
			if (not mr_item_rows or d.name in mr_item_rows) and [d.item_code, d.warehouse] not in item_wh_list \
					and frappe.db.get_value("Item", d.item_code, "is_stock_item") == 1 and d.warehouse:
				item_wh_list.append([d.item_code, d.warehouse])

		for item_code, warehouse in item_wh_list:
			update_bin_qty(item_code, warehouse, {
				"indented_qty": get_indented_qty(item_code, warehouse)
			})

def update_completed_and_requested_qty(stock_entry, method):
	if stock_entry.doctype == "Stock Entry":
		material_request_map = {}

		for d in stock_entry.get("items"):
			if d.material_request:
				material_request_map.setdefault(d.material_request, []).append(d.material_request_item)

		for mr, mr_item_rows in material_request_map.items():
			if mr and mr_item_rows:
				mr_obj = frappe.get_doc("Stock Requisition", mr)

				if mr_obj.status in ["Stopped", "Cancelled"]:
					frappe.throw(_("{0} {1} is cancelled or stopped").format(_("Stock Requisition"), mr),
						frappe.InvalidStatusError)

				mr_obj.update_completed_qty(mr_item_rows)
				mr_obj.update_requested_qty(mr_item_rows)

def set_missing_values(source, target_doc):
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")

def update_item(obj, target, source_parent):
	target.conversion_factor = obj.conversion_factor
	target.qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor
	target.stock_qty = (target.qty * target.conversion_factor)

@frappe.whitelist()
def get_Uom_Data(purchase_uom):
	uom_details = frappe.db.sql("""select must_be_whole_number, needs_to_be_whole_number_in_stock_transactions  from `tabUOM` where uom_name = %s """, (purchase_uom), as_dict=1)
	return uom_details

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)
	doclist = get_mapped_doc("Stock Requisition", source_name, 	{
		"Stock Requisition": {
			"doctype": "Purchase Order",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Stock Requisition Item": {
			"doctype": "Purchase Order Item",
			"field_map": [
				["name", "stock_requisition_item"],
				["parent", "stock_requisition"],
				["uom", "stock_uom"],
				["uom", "uom"]
			],
			"postprocess": update_item,
			"condition": lambda doc: doc.ordered_qty < doc.stock_qty
		}
	}, target_doc, postprocess)

	return doclist

def get_Purchase_Taxes_and_Charges(account_head, tax_name):
	tax_List = frappe.db.sql("""select rate, charge_type, description  from `tabPurchase Taxes and Charges` where account_head = %s and parent = %s""", (account_head, tax_name), as_dict=1)
	return tax_List


@frappe.whitelist()
def making_PurchaseOrder_For_SupplierItems(args, company, tax_template, srID):
	print "##-tax_template::", tax_template
	order_List = json.loads(args)
	items_List = json.dumps(order_List)
	items_List = ast.literal_eval(items_List)
	creation_Date = datetime.datetime.now()
	outerJson_Transfer = {
				"doctype": "Purchase Order",
				"title": "Purchase Order",
				"creation": creation_Date,
				"owner": "Administrator",
				"taxes_and_charges": tax_template,
				"company": company,
				"stock_requisition_id": srID,
				"due_date": creation_Date,
				"docstatus": 0,
				"supplier":"",
				"items": [
				],
				"taxes": [			 
        			],
			     }
	i = 0
	if tax_template is not None and tax_template is not "":
		tax_Name = frappe.get_doc("Purchase Taxes and Charges Template", tax_template)
		for taxes in tax_Name.taxes:
			account_Name = taxes.account_head
			if account_Name:
				tax_Rate_List = get_Purchase_Taxes_and_Charges(account_Name, tax_Name.name)
				print "####-account_Name::", account_Name
				print "####-tax_Name::", tax_Name.name
				if tax_Rate_List is not None and len(tax_Rate_List) != 0:
					charge_type = tax_Rate_List[0]['charge_type']
					rate = tax_Rate_List[0]['rate']
					description = tax_Rate_List[0]['description']
					taxes_Json_Transfer = {"owner": "Administrator",
        						       "charge_type": charge_type,
        				                       "account_head": account_Name,
        						       "rate": rate,
        						       "parenttype": "Purchase Order",
        						       "description": description,
        						       "parentfield": "taxes"
								}
					outerJson_Transfer["taxes"].append(taxes_Json_Transfer)
	i = 0
	for items in items_List:
		"""
		stock_uom = items_List[i]['stock_uom']
		uom = items_List[i]['purchase_uom']
		stock_uom = stock_uom.replace(" ", "")
		uom = uom.replace(" ", "")
		print "stock_uom::", stock_uom
		print "uom::", uom
		"""
		outerJson_Transfer['supplier'] = items_List[i]['supplier']
		innerJson_Transfer =	{
					"creation": creation_Date,
					"qty": items_List[i]['qty'],
					"item_code": items_List[i]['item_code'],
					"stock_uom": items_List[i]['stock_uom'],
					"uom": items_List[i]['purchase_uom'],
					"stock_qty": items_List[i]['stock_qty'],
					"doctype": "Purchase Order Item",
					"parenttype": "Purchase Order",
					"schedule_date": creation_Date,
					"parentfield": "items",
					"warehouse": items_List[i]['warehouse']
				   	}
		outerJson_Transfer["items"].append(innerJson_Transfer)
		i = i + 1
	print "########-Final Purchase Order Json::", outerJson_Transfer
	doc = frappe.new_doc("Purchase Order")
	doc.update(outerJson_Transfer)
	doc.save()
	ret = doc.doctype
	if ret:
		frappe.msgprint("Purchase Order is Created:"+doc.name)
	return doc.name

@frappe.whitelist()
def make_request_for_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc("Stock Requisition", source_name, 	{
		"Stock Requisition": {
			"doctype": "Request for Quotation",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Stock Requisition Item": {
			"doctype": "Request for Quotation Item",
			"field_map": [
				["name", "stock_requisition_item"],
				["parent", "stock_requisition"],
				["uom", "uom"]
			]
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_purchase_order_based_on_supplier(source_name, target_doc=None):
	if target_doc:
		if isinstance(target_doc, basestring):
			import json
			target_doc = frappe.get_doc(json.loads(target_doc))
		target_doc.set("items", [])

	material_requests, supplier_items = get_material_requests_based_on_supplier(source_name)

	def postprocess(source, target_doc):
		target_doc.supplier = source_name
		target_doc.schedule_date = add_days(nowdate(), 1)
		target_doc.set("items", [d for d in target_doc.get("items")
			if d.get("item_code") in supplier_items and d.get("qty") > 0])

		set_missing_values(source, target_doc)

	for mr in material_requests:
		target_doc = get_mapped_doc("Stock Requisition", mr, 	{
			"Stock Requisition": {
				"doctype": "Purchase Order",
			},
			"Stock Requisition Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "stock_requisition_item"],
					["parent", "stock_requisition"],
					["uom", "stock_uom"],
					["uom", "uom"]
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.ordered_qty < doc.qty
			}
		}, target_doc, postprocess)

	return target_doc

def get_material_requests_based_on_supplier(supplier):
	supplier_items = [d[0] for d in frappe.db.get_values("Item",
		{"default_supplier": supplier})]
	if supplier_items:
		material_requests = frappe.db.sql_list("""select distinct mr.name
			from `tabStock Requisition` mr, `tabStock Requisition Item` mr_item
			where mr.name = mr_item.parent
				and mr_item.item_code in (%s)
				and mr.material_request_type = 'Purchase'
				and mr.per_ordered < 99.99
				and mr.docstatus = 1
				and mr.status != 'Stopped'
			order by mr_item.item_code ASC""" % ', '.join(['%s']*len(supplier_items)),
			tuple(supplier_items))
	else:
		material_requests = []
	return material_requests, supplier_items

@frappe.whitelist()
def make_supplier_quotation(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)

	doclist = get_mapped_doc("Stock Requisition", source_name, {
		"Stock Requisition": {
			"doctype": "Supplier Quotation",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["=", "Purchase"]
			}
		},
		"Stock Requisition Item": {
			"doctype": "Supplier Quotation Item",
			"field_map": {
				"name": "material_request_item",
				"parent": "material_request"
			}
		}
	}, target_doc, postprocess)

	return doclist

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		qty = flt(flt(obj.stock_qty) - flt(obj.ordered_qty))/ target.conversion_factor \
			if flt(obj.stock_qty) > flt(obj.ordered_qty) else 0
		target.qty = qty
		target.transfer_qty = qty * obj.conversion_factor
		target.conversion_factor = obj.conversion_factor

		if source_parent.material_request_type == "Material Transfer":
			target.t_warehouse = obj.warehouse
		else:
			target.s_warehouse = obj.warehouse

	def set_missing_values(source, target):
		target.purpose = source.material_request_type
		target.run_method("calculate_rate_and_amount")

	doclist = get_mapped_doc("Stock Requisition", source_name, {
		"Stock Requisition": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1],
				"material_request_type": ["in", ["Material Transfer", "Material Issue"]]
			}
		},
		"Stock Requisition Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"name": "stock_requisition_item",
				"parent": "stock_requisition",
				"uom": "stock_uom",
			},
			"postprocess": update_item,
			"condition": lambda doc: doc.ordered_qty < doc.stock_qty
		}
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def raise_production_orders(stock_requisition):
	mr= frappe.get_doc("Stock Requisition", stock_requisition)
	errors =[]
	production_orders = []
	default_wip_warehouse = frappe.db.get_single_value("Manufacturing Settings", "default_wip_warehouse")
	for d in mr.items:
		if (d.qty - d.ordered_qty) >0:
			if frappe.db.get_value("BOM", {"item": d.item_code, "is_default": 1}):
				prod_order = frappe.new_doc("Production Order")
				prod_order.production_item = d.item_code
				prod_order.qty = d.qty - d.ordered_qty
				prod_order.fg_warehouse = d.warehouse
				prod_order.wip_warehouse = default_wip_warehouse
				prod_order.description = d.description
				prod_order.stock_uom = d.stock_uom
				prod_order.expected_delivery_date = d.schedule_date
				prod_order.sales_order = d.sales_order
				prod_order.bom_no = get_item_details(d.item_code).bom_no
				prod_order.material_request = mr.name
				prod_order.material_request_item = d.name
				prod_order.planned_start_date = mr.transaction_date
				prod_order.company = mr.company
				prod_order.save()
				production_orders.append(prod_order.name)
			else:
				errors.append(_("Row {0}: Bill of Materials not found for the Item {1}").format(d.idx, d.item_code))
	if production_orders:
		message = ["""<a href="#Form/Production Order/%s" target="_blank">%s</a>""" % \
			(p, p) for p in production_orders]
		msgprint(_("The following Production Orders were created:") + '\n' + new_line_sep(message))
	if errors:
		frappe.throw(_("Productions Orders cannot be raised for:") + '\n' + new_line_sep(errors))
	return production_orders

@frappe.whitelist()
def get_po_list(srID):
	po_list = frappe.db.sql("""select po_list from `tabStock Requisition` where name=%s""", srID, as_dict=1)
	pos_list = po_list[0]['po_list']
	return pos_list

@frappe.whitelist()
def update_po_list(srID, po_list):
	result = frappe.db.sql("""update `tabStock Requisition` set po_list='""" + po_list + """' where name=%s""", (srID))
	print "####-result::", result

@frappe.whitelist()
def get_stock_requisition_items(parent):
	records = frappe.db.sql("""select hidden_item_code,hidden_qty from `tabStock Requisition Item` where parent=%s""", (parent), as_dict=1)
	print "####-Stock Requisition records::", records
	return records

@frappe.whitelist()
def get_stock_requisition_po_items_list(srID):
	po_items_map = {}
	po_items_list = []
	po_list = get_po_list(srID)
	print "po_list****************************************************9",po_list
	if po_list is not None and po_list is not "" and po_list != "NULL":
		pos = po_list.split(",")
		if len(pos)!=0:
			for po in pos:
				print "po--------------from pos",po
				data = get_ordered_items_and_qty(po)
				
				if len(data)!=0:
					for item in data:
						item_code = item['item_code']
						qty = item['qty']
						key = item_code	
						if key in po_items_map:
							item_entry = po_items_map[key]
							qty_temp = item_entry['qty']
							item_entry['qty'] = float(qty_temp) + float(qty)
						else:
							po_items_map[key] = frappe._dict({
							"item_code": item_code,
							"qty": qty
							})
	print "po_items_map::", po_items_map
	print "---------------------------po_items_map::", len(po_items_map) 
	for item_code in sorted(po_items_map):
		items_dict = po_items_map[item_code]
		item_code = items_dict.item_code;
		qty = items_dict.qty;
		data = {"item_code":item_code, "qty":qty}
		po_items_list.append(data)
	print "Po Item List************************************************8",po_items_list
	return po_items_list


def get_ordered_items_and_qty(po):
	data = {}
	items_list = []
	records = frappe.db.sql("""select tpoi.item_code,tpoi.qty from `tabPurchase Order Item` tpoi,`tabPurchase Order` tpo where
 				tpoi.parent=%s and tpo.docstatus=1 and tpo.name=tpoi.parent""", (po), as_dict=1)
	
	print "records::", records
	if len(records)!=0:
		for items in records:
			item_code = items.item_code
			qty = items.qty
			data = {"item_code":item_code, "qty":qty}
			items_list.append(data)
	print "Item_list-------",items_list
	return items_list

@frappe.whitelist()
def fetch_conversion_factor(purchase_uom, item_code):
	conversion_factor = 1
	records = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where uom=%s and parent=%s""", (purchase_uom, 					item_code), as_dict=1)
	print "records::", records
	if len(records)!=0:
		conversion_factor = records[0]['conversion_factor']
	return conversion_factor

@frappe.whitelist() 
def update_stock_requisition_status(srID,status):
	print "status---------------------",status
	result = frappe.db.sql("""update `tabStock Requisition` set status='""" + status + """' where name=%s""", (srID))
	print "####-result::", result

@frappe.whitelist()
def po_list_value(srID,po_list):
	print "SREQ from po_list value"
	print "hello"
	sreq_qty=""
	items_list = []	
	StockReqValue = frappe.db.sql("""select hidden_item_code,hidden_qty from `tabStock Requisition Item` where parent=%s""", (srID), as_dict=1)
	PurchaseOrderValue= frappe.db.sql("""select tpoi.item_code,tpoi.qty from `tabPurchase Order Item` tpoi,`tabPurchase Order` tpo where
 				tpoi.parent=%s  and tpo.name=tpoi.parent""", (po_list), as_dict=1)	
	print "####-StockReqValue::", StockReqValue
	print "####-PurchaseOrderValue::", PurchaseOrderValue
	status="";
	for item in StockReqValue:
		status="Partially Ordered"
		sreq_item_code = str(item['hidden_item_code'])
		print "Sr_item_code from if statement",sreq_item_code
		sreq_qty =float(item['hidden_qty'])
		print "Sr_qty from if statement",sreq_qty
		for item in PurchaseOrderValue:
			po_item_code=str(item['item_code'])
			po_item_qty=float(item['qty'])
			if(sreq_item_code==po_item_code):
				print "po_item_code-----",po_item_code
				print " po item qty---" ,po_item_qty
				if(sreq_qty<item['qty']):
					sreq_qty=sreq_qty
					data = {"item_code":po_item_code, "qty":sreq_qty}
					items_list.append(data)
					break;
			
	print "sreq_qty11",items_list
					
	return items_list
