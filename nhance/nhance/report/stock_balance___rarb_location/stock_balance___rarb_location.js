
frappe.query_reports["Stock Balance - RARB Location"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		{
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query"
				}
			}
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse",
			"reqd":1,
			"get_query": function() {
				 var rarb_warehouse = []
				
				 rarb_warehouse = get_rarb_warehouse_item_name();
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
			"fieldname":"include_uom",
			"label": __("Include UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
		{
			"fieldname": "show_variant_attributes",
			"label": __("Show Variant Attributes"),
			"fieldtype": "Check"
		},
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
