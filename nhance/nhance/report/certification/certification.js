// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Certification"] = {
	"filters": [
		{
        "fieldname": "customer_po",
        "label": __("Customer PO"),
        "fieldtype": "Link",
        "options": "Purchase Order",
        "reqd": 0
	},
	{
        "fieldname": "item_code",
        "label": __("Item Code"),
        "fieldtype": "Link",
        "options": "Item",
        "reqd": 0
	},
	{
        "fieldname": "item_serial_no",
        "label": __("Item Serial No"),
        "fieldtype": "Link",
        "options": "Serial No",
        "reqd": 1
	},
	{
        "fieldname": "delivery_note",
        "label": __("Delivery Note"),
        "fieldtype": "Link",
        "options": "Delivery Note",
        "reqd": 0
	},
	{
        "fieldname": "sales_order_acknowleggement",
        "label": __("Sales Order Acknowledgement"),
        "fieldtype": "Link",
        "options": "Sales Order",
	"reqd": 0
	}

	]
}
