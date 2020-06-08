// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Simple Stock Balance"] = {
    "filters": [

                
                {      "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                       "default": frappe.datetime.get_today()
                },
                {
                        "fieldname":"to_date",
                        "label": __("Committed Delivery To Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today()
                },
            {
                "fieldname": "item_code",
                "label": __("Item"),
                "fieldtype": "Link",
                "options": "Item"
            },
    {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group"
        },

                {
                        "fieldname":"item_name",
                        "label": __("Item Name"),
                        "fieldtype": "Data"
                },

        {
                        "fieldname":"cases",
                        "label": __("Case"),
            "fieldtype": "Data"

                    

                },

        {
                        "fieldname":"warehouse",
                        "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse"
                

                },
        
                {
                        "fieldname":"detail",
                        "label": __("Detail"),
                        "fieldtype": "Data"
                },
        
        {
                        "fieldname":"mfr",
                        "label": __("MFR"),
                        "fieldtype": "Link",
            "options": "Manufacturer"
                },

{
                        "fieldname":"mfr_pn",
                        "label": __("MFR PN"),
                        "fieldtype": "Data"
                },
        
        
                                  
                
        ],
 onload: function(report) {
        report.page.add_inner_button(__("Clear Filters"),
                function() {
                  var args = "as a draft"
          var filters = report.get_values();
                  var reporter = frappe.query_reports["Simple Stock Balance"];
                    reporter.ClearFilters(report,args);})
                    

              },
    isNumeric: function( obj ) {
    return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
  },
   ClearFilters: function(report,status){
        frappe.query_report_filters_by_name.item_group.set_input("");
        frappe.query_report_filters_by_name.item_code.set_input("");
        frappe.query_report_filters_by_name.item_name.set_input("");
        frappe.query_report_filters_by_name.cases.set_input("");
        frappe.query_report_filters_by_name.warehouse.set_input("");
        frappe.query_report_filters_by_name.detail.set_input("");
        frappe.query_report_filters_by_name.mfr.set_input("");
        frappe.query_report_filters_by_name.mfr_pn.set_input("");

   }
}
