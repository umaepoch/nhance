/**
 *
 */
// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
frappe.query_reports["BOM Item Warehouse"] = {

    "filters": [{
            "fieldname": "bom",
            "label": __("BOM"),
            "fieldtype": "Link",
            "width": "50",
            "options": "BOM",
            "reqd": 1,
            "get_query": function() {
                return {
                    'filters': [
                        ['BOM', 'docstatus', '=', '1']
                    ]
                }
            }
        },

        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1

        },

        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "default": "All"
        }, {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item"
        },

        {
            "fieldname": "include_exploded_items",
            "label": __("Include Exploded Items"),
            "fieldtype": "Data",
            "default": "Y"

        },
	{
	    "fieldname": "current_stock_balance",
            "label": __("Current Stock Balance to be considered?"),
            "fieldtype": "Check",
            "default": "0"
	},

 //       {
//            "fieldname": "planning_warehouse",
  //          "label": __("Planning Warehouse"),
    //        "fieldtype": "Link",
      //      "reqd": 1,
//            "options": "Warehouse",
  //          "get_query": function() {
    //            return {
      //              'filters': [
        //                ['Warehouse', 'is_group', '=', '0']
          //          ]
//            //    }
  //          }
    //    },
//        {
  //        "fieldname":"required_on",
//          "label": __("Required Date"),
  //        "fieldtype": "Date",
    //      "default": get_today(),
//          "on_change": function(query_report) {
//            query_report.trigger_refresh();
//	    var filters = query_report.get_values();
  //          var required_date = filters.required_on;
    ////        if (required_date < get_today()){
        //      frappe.msgprint("Required Date cannot be an Earlier Date than today")
          //    frappe.query_report_filters_by_name.required_on.set_input(get_today());
//            }
  //        }
    //    },

        {
            "fieldname": "qty_to_make",
            "label": __("Quantity to Make"),
            "fieldtype": "Data",
            "default": "1",
            "on_change": function(query_report) {

                var qty = frappe.query_report_filters_by_name.qty_to_make.get_value();
                if (!jQuery.isNumeric(qty)){
                  frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                  frappe.throw("Quantity to Make value is not in proper format")
                }
                if (qty < 0){
                  frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                  frappe.throw("Quantity to Make cannot be nagative please input positive value")
                }
                if (qty < 1){
                  frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                  frappe.throw(" Quantity to Make should be greater than one")
                }
                return frappe.call({
                    method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.check_for_whole_number",
                    args: {
                        "bomno": frappe.query_report_filters_by_name.bom.get_value()
                    },
                    callback: function(r) {
                        if (r.message && qty % 1 != 0) {
                            frappe.msgprint(__("Quantity to Make should be whole number"));
                            frappe.query_report_filters_by_name.qty_to_make.set_input("1");
			    query_report.trigger_refresh();

                        } else {
                            query_report.trigger_refresh();
                        }
                    }
                })
            }
        },
//	{
//            "fieldname": "reference_no",
//            "label": __("Reference Number"),
//            "fieldtype": "Data",
//        },


    ],
    onload: function(report) {
        report.page.add_inner_button(__("As a draft"),
                function() {
                  var args = "as a draft"
                  var reporter = frappe.query_reports["BOM Item Warehouse"];
                    reporter.makeStockRequisition(report,args);},'Make Stock Requisition'),
                    report.page.add_inner_button(__("As final"),
                        function() {
                          var args = "submit"
                          var reporter = frappe.query_reports["BOM Item Warehouse"];
                          reporter.makeStockRequisition(report,args);},'Make Stock Requisition');
              },

    isNumeric: function( obj ) {
    return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
  },
   makeStockRequisition: function(report,status){
    
     var dialog = new frappe.ui.Dialog({
		title: __("Enter information for Stock Requisition"),
		fields: [
			{"fieldname": "planning_warehouse", "label": __("Planning Warehouse"), "fieldtype": "Link", "reqd": 1, "options": "Warehouse", "get_query": function() {
                return {
                    'filters': [
                        ['Warehouse', 'is_group', '=', '0']
                    ]
                }
            }},
			
//			{"fieldtype": "Date", "label": __("Required Date"), "fieldname": "required_on", "reqd": 1},
			{"fieldname":"required_on", "label": __("Required Date"), "fieldtype": "Date", "default": get_today()},
	                
			{"fieldname": "reference_no", "label": __("Reference Number"), "fieldtype": "Data"}
		],

		primary_action: function(){
        	dialog.hide();
        	show_alert(dialog.get_values());
		var filters = report.get_values();
		if (filters.company && filters.warehouse && filters.bom) {

		var planning_warehouse = dialog.fields_dict.planning_warehouse.get_value();
		var required_on = dialog.fields_dict.required_on.get_value();
		
		var reference_no = dialog.fields_dict.reference_no.get_value();
		

	         return frappe.call({
        	     method: "nhance.nhance.report.bom_item_warehouse.bom_item_warehouse.make_stock_requisition",
        	     args: {
        	         "args": status,
			 "planning_warehouse": planning_warehouse,
			 "required_date": required_on,
			 "reference_no": reference_no
			
        	     },
        	     callback: function(r) {
        	       if(r.message) {
        	         frappe.set_route('List',r.message );
        	     }
        	     }
        	 })
	     } else {
        	 frappe.msgprint("Please select all three filters For Stock Requisition")
	     }


	}
	});
	dialog.show();
	

     
   }
}

        /*
		 * report.page.add_inner_button(__("Select Warehouse"), function() {
		 * //var filters = report.get_values(); var d = new frappe.ui.Dialog({
		 * title : __("Select a Warehouse"), fields : [ { fieldname :
		 * 'Warehouse', fieldtype : 'Link', options : 'Warehouse', label :
		 * 'Warehouse', reqd : 1 }, { "fieldtype" : "Button", "label" :
		 * __("Submit"), "fieldname" : "submit" }, ] }); d.show()
		 *
		 * });
		 */
