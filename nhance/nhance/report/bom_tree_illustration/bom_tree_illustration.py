# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, datetime,comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
from datetime import datetime
import time
import math
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def execute(filters=None):
    data = []
    bom = filters.get("bom")
    explosion_items = fetch_explosion_items(bom)
    #print "--------explosion_items--------", explosion_items
    columns = get_columns()
    data.append([bom, "", "", "", ""])
    for items in explosion_items:
        bi_item = items['bi_item']
        bom_no = items['bom_no']
        uom = items['uom']
        whse_list = get_whse_stock_uom(bi_item)
        if whse_list is not None:
            data.append(["|", bi_item+" ("+uom+")", "", "", ""])
            for whse_data in whse_list:
                actual_qty = whse_data['actual_qty']
                warehouse = whse_data['warehouse']
                data.append(["|", warehouse, actual_qty, "", ""])
            if bom_no is not None:
                child_items = fetch_explosion_items(bom_no)
                for items_data in child_items:
                    bi_item = items_data['bi_item']
                    bom_no = items_data['bom_no']
                    uom = items_data['uom']
                    whse_list = get_whse_stock_uom(bi_item)
                    if whse_list is not None:
                        data.append(["|", "|", bi_item+" ("+uom+")", "", ""])
                        for whse_data in whse_list:
                            actual_qty = whse_data['actual_qty']
                            warehouse = whse_data['warehouse']
                            data.append(["|", "|", warehouse, actual_qty, ""])
                        if bom_no is not None:
                            child_items1 = fetch_explosion_items(bom_no)
                            for items_data in child_items1:
                                bi_item = items_data['bi_item']
                                bom_no = items_data['bom_no']
                                uom = items_data['uom']
                                whse_list = get_whse_stock_uom(bi_item)
                                if whse_list is not None:
                                    data.append(["|", "|", "|", bi_item+" ("+uom+")", ""])
                                    for whse_data in whse_list:
                                        actual_qty = whse_data['actual_qty']
                                        warehouse = whse_data['warehouse']
                                        data.append(["|", "|", "|",warehouse, actual_qty])
                                    if bom_no is not None:
                                        child_items1 = fetch_explosion_items(bom_no)
                                        for items_data in child_items1:
                                            bi_item = items_data['bi_item']
                                            bom_no = items_data['bom_no']
                                            uom = items_data['uom']
                                            whse_list = get_whse_stock_uom(bi_item)
                                            if whse_list is not None:
                                                data.append(["|", "|", "|", "|", bi_item+" ("+uom+")"])
                                                for whse_data in whse_list:
                                                    actual_qty = whse_data['actual_qty']
                                                    warehouse = whse_data['warehouse']
                                                    data.append(["|", "|", "|","|",warehouse, actual_qty])
                                            if bom_no is not None:
                                                child_items1 = fetch_explosion_items(bom_no)
                                                for items_data in child_items1:
                                                    bi_item = items_data['bi_item']
                                                    bom_no = items_data['bom_no']
                                                    uom = items_data['uom']
                                                    whse_list = get_whse_stock_uom(bi_item)
                                                    if whse_list is not None:
                                                        data.append(["|", "|", "|", "|", "|", bi_item+" ("+uom+")",""])
                                                        for whse_data in whse_list:
                                                            actual_qty = whse_data['actual_qty']
                                                            warehouse = whse_data['warehouse']
                                                            data.append(["|", "|", "|","|", "|", warehouse, actual_qty])
                                                    if bom_no is not None:
                                                        child_items1 = fetch_explosion_items(bom_no)
                                                        for items_data in child_items1:
                                                            bi_item = items_data['bi_item']
                                                            bom_no = items_data['bom_no']
                                                            uom = items_data['uom']
                                                            whse_list = get_whse_stock_uom(bi_item)
                                                            if whse_list is not None:
                                                                data.append(["|", "|", "|", "|", "|", "|", bi_item+" ("+uom+")",""])
                                                                for whse_data in whse_list:
                                                                    actual_qty = whse_data['actual_qty']
                                                                    warehouse = whse_data['warehouse']
                                                                    data.append(["|", "|", "|","|", "|", "|", warehouse, actual_qty])
                                                            if bom_no is not None:
                                                                child_items1 = fetch_explosion_items(bom_no)
                                                                for items_data in child_items1:
                                                                    bi_item = items_data['bi_item']
                                                                    bom_no = items_data['bom_no']
                                                                    uom = items_data['uom']
                                                                    whse_list = get_whse_stock_uom(bi_item)
                                                                    if whse_list is not None:
                                                                        data.append(["|", "|", "|", "|", "|", "|", "|", bi_item+" ("+uom+")",""])
                                                                        for whse_data in whse_list:
                                                                            actual_qty = whse_data['actual_qty']
                                                                            warehouse = whse_data['warehouse']
                                                                            data.append(["|", "|", "|","|", "|", "|", "|", warehouse,actual_qty])
                                                                    if bom_no is not None:
                                                                        child_items1 = fetch_explosion_items(bom_no)
                                                                        for items_data in child_items1:
                                                                            bi_item = items_data['bi_item']
                                                                            bom_no = items_data['bom_no']
                                                                            uom = items_data['uom']
                                                                            whse_list = get_whse_stock_uom(bi_item)
                                                                            if whse_list is not None:
                                                                                data.append(["|", "|", "|", "|", "|", "|", "|", "|", bi_item+" ("+uom+")",""])
                                                                                for whse_data in whse_list:
                                                                                    actual_qty = whse_data['actual_qty']
                                                                                    warehouse = whse_data['warehouse']
                                                                                    data.append(["|", "|", "|","|", "|", "|", "|", "|", warehouse,actual_qty])
                                                                            if bom_no is not None:
                                                                                child_items1 = fetch_explosion_items(bom_no)
                                                                                for items_data in child_items1:
                                                                                    bi_item = items_data['bi_item']
                                                                                    bom_no = items_data['bom_no']
                                                                                    uom = items_data['uom']
                                                                                    whse_list = get_whse_stock_uom(bi_item)
                                                                                    if whse_list is not None:
                                                                                        data.append(["|", "|", "|", "|", "|", "|", "|", "|", "|", bi_item+" ("+uom+")",""])
                                                                                        for whse_data in whse_list:
                                                                                            actual_qty = whse_data['actual_qty']
                                                                                            warehouse = whse_data['warehouse']
                                                                                            data.append(["|", "|", "|","|", "|", "|", "|", "|", "|", warehouse,actual_qty])

    return columns, data


def fetch_explosion_items(bom):
	return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code as bi_item, bi.stock_qty as bi_qty, bi.bom_no as bom_no, bi.stock_uom as uom from `tabBOM` bo, `tabBOM Item` bi where bo.name = %s and bo.is_active=1 and bo.docstatus = 1 and bo.name=bi.parent order by bo.name, bi.item_code""", bom, as_dict=1)

def get_whse_stock_uom(bi_item):
	whse_list = frappe.db.sql(""" select warehouse,actual_qty,stock_uom from `tabBin` where item_code=%s and actual_qty>0""", bi_item, as_dict=1)
	if len(whse_list)!=0:
		return whse_list
	else:
		return None

def get_columns():
	"""return columns"""
	columns = [
	_("BOM")+":100",
	_("-")+":100",
	_("--")+"::100",
	_("---")+"::140",
	_("----")+"::100",
	_("-----")+"::100",
	_("------")+"::100",
	_("-------")+"::100",
	_("--------")+"::100",
	_("---------")+"::100",
	_("----------")+"::100",
	_("-----------")+"::100"]
	return columns
