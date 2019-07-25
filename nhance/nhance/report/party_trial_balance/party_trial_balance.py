# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint
from erpnext.accounts.report.trial_balance.trial_balance import validate_filters

def execute(filters=None):

	validate_filters(filters)
	show_party_name = is_party_name_visible(filters)
	columns = get_columns(filters, show_party_name)

	opening_balances = get_opening_balances1(filters)
	#print "opening_balances----------------", opening_balances

	balances_within_period = get_balances_within_period1(filters)
	#print "balances_within_period----------------", balances_within_period
	
	final_result = []
	opening_balance_map = {}
	total_credit = 0.0
	total_debit = 0.0
	total_opening_debit = 0.0
	total_opening_credit = 0.0
	total_closing_debit = 0.0
	total_closing_credit = 0.0
	party_list = []
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
	party_name_field = "{0}_name".format(frappe.scrub(filters.get('party_type')))
	party_filters1 = {"name": filters.get("party")} if filters.get("party") else {}
	parties1 = frappe.get_all(filters.get("party_type"), fields = ["name", party_name_field], 
		filters = party_filters1, order_by="name")
	for opening_balance in opening_balances:
		credit = 0.0
		debit = 0.0
		key = opening_balance['name']
		credit = opening_balance['credit']
		debit = opening_balance['credit']
		if key not in opening_balance_map:
			opening_balance_map[key] = frappe._dict({
				"opening_credit": credit, 
				"opening_debit": debit	   
				})

	for balances in balances_within_period:
		opening_debit = 0.0
		opening_credit = 0.0
		closing_credit = 0.0
		closing_debit = 0.0
		name = balances['name']
		party = balances['party']
		account = balances['account']
		debit = balances['debit']
		credit = balances['credit']
		
		if name in opening_balance_map:
			balance_entry = opening_balance_map[name]
			opening_debit, opening_credit = toggle_debit_credit(balance_entry.opening_debit, balance_entry.opening_credit)
			balances['opening_credit'] = opening_credit
			balances['opening_debit'] = opening_debit
		else:
			balances['opening_credit'] = opening_credit
			balances['opening_debit'] = opening_debit

		closing_debit, closing_credit = toggle_debit_credit(balances['opening_debit'] + debit, balances['opening_credit'] + credit)
		
		balances['closing_credit'] = closing_credit
		balances['closing_debit'] = closing_debit
		
		total_credit = total_credit + credit
		total_debit = total_debit + debit
		
		total_opening_debit = total_opening_debit + balances['opening_debit']
		total_opening_credit = total_opening_credit + balances['opening_credit']

		total_closing_debit = total_closing_debit + balances['closing_debit']
		total_closing_credit = total_closing_credit + balances['closing_credit']

		party_list.append(party)
		
		final_result.append([party, account, balances['opening_debit'], balances['opening_credit'], debit, credit, balances['closing_debit'], balances['closing_credit'], company_currency])

	if filters.get("show_zero_values") == 1:
		name = ""
		unique_party_list = list(set(party_list))
		if filters.get("party_type") == "Customer":
			name = "customer_name"
		elif filters.get("party_type") == "Supplier":
			name = "supplier_name"
		elif filters.get("party_type") == "Employee":
			name = "name"
		for party_names in parties1:
			if party_names[name] not in unique_party_list:
				final_result.append([party_names[name], "", "", "", "", "", "", "", company_currency])

	final_result.append(["Totals", "", total_opening_debit, total_opening_credit, total_debit, total_credit, total_closing_debit, total_closing_credit, company_currency])
	#print "final_result----------------", final_result

	return columns, final_result



def get_opening_balances1(filters):
	conditions = get_filter_conditions(filters,"opening")
	if conditions is not "":
		return frappe.db.sql("""select name,party,credit,debit from `tabGL Entry`  where {}""" .format(" and ".join(conditions)), filters, as_dict=1)
	else:
		return None

def get_balances_within_period1(filters):
	conditions = get_filter_conditions(filters,"")
	if conditions:
		return frappe.db.sql("""select name,party,account,credit,debit,is_opening from `tabGL Entry`  where {}""" .format(" and ".join(conditions)), filters, as_dict=1)
	else:
		return None

def get_filter_conditions(filters,balance_type):
	conditions = []
	if filters.get("company"):
		conditions.append("company=%(company)s")
    	if balance_type == "":
    		if filters.get("from_date"):
			conditions.append("posting_date >=%(from_date)s")
    		if filters.get("to_date"):
			conditions.append("posting_date <=%(to_date)s")
   	else:
		if filters.get("from_date"):
			conditions.append("posting_date <%(from_date)s")
    	if filters.get("party_type"):
		conditions.append("party_type =%(party_type)s")
    	if filters.get("party"):
		conditions.append("party =%(party)s")
    	if filters.get("account"):
		conditions.append("account =%(account)s")
	return conditions

def toggle_debit_credit(debit, credit):
	if flt(debit) > flt(credit):
		debit = flt(debit) - flt(credit)
		credit = 0.0
	else:
		credit = flt(credit) - flt(debit)
		debit = 0.0

	return debit, credit

def get_columns(filters, show_party_name):
	columns = [
		{
			"fieldname": "party",
			"label": _(filters.party_type),
			"fieldtype": "Link",
			"options": filters.party_type,
			"width": 200
		},
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": filters.account,
			"width": 200
		},
		{
			"fieldname": "opening_debit",
			"label": _("Opening (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "opening_credit",
			"label": _("Opening (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_debit",
			"label": _("Closing (Dr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "closing_credit",
			"label": _("Closing (Cr)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		}
	]
	if show_party_name:
		columns.insert(1, {
			"fieldname": "party_name",
			"label": _(filters.party_type) + " Name",
			"fieldtype": "Data",
			"width": 200
		})
	return columns

def is_party_name_visible(filters):
	show_party_name = False

	if filters.get('party_type') in ['Customer', 'Supplier', 'Employee']:
		if filters.get("party_type") == "Customer":
			party_naming_by = frappe.db.get_single_value("Selling Settings", "cust_master_name")
		else:
			party_naming_by = frappe.db.get_single_value("Buying Settings", "supp_master_name")

		if party_naming_by == "Naming Series":
			show_party_name = True
	else:
		show_party_name = True

	return show_party_name
