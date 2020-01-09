// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Ledger - RARB Location"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd":1,
			"get_query": function() {
				 var rarb_warehouse = []
				
				 rarb_warehouse = get_rarb_warehouse_item_name();
				//console.log("rarb_warehouse---------------"+rarb_warehouse);
				return{
				"filters": [
					["Warehouse", "name", "in", rarb_warehouse]
				    ]
				
				}
			},
		   "on_change":function(){
				 var data = []
				var for_verification = [];
				 data.push({'fildname':"title",'fieldtype':'Text', 'read_only':1, "default":"There is many RARB Warehouse created for this Warehosue So Please select date between start date to end date as given "},{'fieldname': 'section', 'fieldtype': 'Section Break'})
				data.push({'fieldname': 'start_date', 'fieldtype': 'Data','default':"Start Date", 'read_only':1},{'fieldname': 'cl1', 'fieldtype': 'Column Break'},{'fieldname': 'end_date', 'fieldtype': 'Data', 'default':'End Date', "read_only":1},{'fieldname': 'sc1', 'fieldtype': 'Section Break'})
				 var warehouse =frappe.query_report.get_filter_value("warehouse");
				 var rarb_warehouse = get_rarb_warehouse(warehouse);
				 if (rarb_warehouse.length == 1){
					var start_date = rarb_warehouse[0].start_date;
					frappe.query_report.set_filter_value("from_date",start_date);
					frappe.query_report.set_filter_value("to_date",frappe.datetime.get_today());
				}
				 if (rarb_warehouse.length > 1){
					for(var i=0; i < rarb_warehouse.length; i++){
						var start_date = rarb_warehouse[i].start_date;
						 var end_date = "";
						 if (rarb_warehouse[i].end_date != undefined){
							end_date = rarb_warehouse[i].end_date;
						}else{
								end_date=frappe.datetime.get_today();
						}
						for_verification.push({
									"start_date":start_date,
									"end_date":end_date
									})
						data.push({'fieldname': start_date, 'fieldtype': 'Check', 'label': start_date},{'fieldname': 'cl1', 'fieldtype': 'Column Break'},{'fieldname': end_date, 'fieldtype': 'Check', 'label': end_date},{'fieldname': 'sc1', 'fieldtype': 'Section Break'})
						
					}
					
					var d = new frappe.ui.Dialog({
						    'fields':data,
						    primary_action: function(){
							dialog_v = d.get_values();
							d.hide();
							 Object.keys(dialog_v).forEach(function(key) {
								console.log("dailog data -------------"+dialog_v[key])
								if(dialog_v[key] == 1){
								 	for (var j =0; j < for_verification.length; j++){
										if(for_verification[j].start_date == key){
											frappe.query_report.set_filter_value("from_date",for_verification[j].start_date);
										}
										else if(for_verification[j].end_date == key){
											frappe.query_report.set_filter_value("to_date",for_verification[j].end_date);
										}
									}
								}
							})
							
						    }
						});
						
						d.show();

					
				}
			}
		},
		{
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname":"batch_no",
			"label": __("Batch No"),
			"fieldtype": "Link",
			"options": "Batch"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname":"voucher_no",
			"label": __("Voucher #"),
			"fieldtype": "Data"
		},
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		{
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		}
	]
}
function get_rarb_warehouse_item_name(){
	var supplier_criticality = [];
	frappe.call({
		method: 'nhance.nhance.report.stock_balance___rarb_location.stock_balance___rarb_location.get_rarb_warehouse_item_name',
		args: {
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
			 for (var i = 0; i < r.message.length; i++) {
				    supplier_criticality.push(r.message[i].warehouse);
				    
				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
    return supplier_criticality;
}
function get_rarb_warehouse(warehouse){
	var rarb_warehosue_list = "";
	frappe.call({
		method: 'nhance.nhance.report.stock_balance___rarb_location.stock_balance___rarb_location.get_rarb_warehouse',
		args: {
			"warehouse":warehouse
		},
		async: false,
		callback: function(r) {
			rarb_warehosue_list=r.message;
				    
		}
	});
	return rarb_warehosue_list
}
