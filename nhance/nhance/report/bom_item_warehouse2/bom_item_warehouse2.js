// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM Item Warehouse2"] = {
	"filters": [{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },
	{
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
	    "reqd": 1,
	    "get_query": function(){
		return {
			"doctype": "Project",
			"filters": {
				"is_active": "Yes"
			}
		}
	    },
	    "on_change": function(query_report) {
	     	var project = frappe.query_report_filters_by_name.project.get_value();
		console.log("project-------"+project);
		frappe.call({
			method: "nhance.nhance.report.bom_item_warehouse2.bom_item_warehouse2.fetch_project_details",
			args: {
         	 		"project":project
        		},
			async: false,
			callback: function(r) 
      			{ 
				if(r.message){
				console.log("docids options::"+r.message.length);
				console.log("result::"+JSON.stringify(r.message));
				console.log("----------------Break Point 1");
				var warehouse_filter = frappe.query_report_filters_by_name.warehouse;
				console.log("----------------Break Point 2");
				warehouse_filter.df.options = r.message[0].project_warehouse;
				warehouse_filter.df.default = r.message[0].project_warehouse;
				warehouse_filter.refresh();
				warehouse_filter.set_input(warehouse_filter.df.default);
				console.log("----------------Break Point 3");

				var reserve_warehouse_filter = frappe.query_report_filters_by_name.reserve_warehouse;
				reserve_warehouse_filter.df.options = r.message[0].reserve_warehouse;
				reserve_warehouse_filter.df.default = r.message[0].reserve_warehouse;
				reserve_warehouse_filter.refresh();
				reserve_warehouse_filter.set_input(reserve_warehouse_filter.df.default);

				var bom_filter = frappe.query_report_filters_by_name.bom;
				bom_filter.df.options = r.message[0].master_bom;
				bom_filter.df.default = r.message[0].master_bom;
				bom_filter.refresh();
				bom_filter.set_input(bom_filter.df.default);
				
				var core_team_coordinator_filter = frappe.query_report_filters_by_name.core_team_coordinator;
				core_team_coordinator_filter.df.options = r.message[0].core_team_coordinator;
				core_team_coordinator_filter.df.default = r.message[0].core_team_coordinator;
				core_team_coordinator_filter.refresh();
				core_team_coordinator_filter.set_input(core_team_coordinator_filter.df.default);

				var planner_filter = frappe.query_report_filters_by_name.planner;
				planner_filter.df.options = r.message[0].planner;
				planner_filter.df.default = r.message[0].planner;
				planner_filter.refresh();
				planner_filter.set_input(planner_filter.df.default);

				var start_date_filter = frappe.query_report_filters_by_name.start_date;
				start_date_filter.df.options = r.message[0].start_date;
				start_date_filter.df.default = r.message[0].start_date;
				start_date_filter.refresh();
				start_date_filter.set_input(start_date_filter.df.default);

				query_report.refresh();
				}//end of if..
			}//end of call-back function..
		});//end of frappe call..
	    }//end of on_change
        },
	{
            "fieldname": "include_exploded_items",
            "label": __("Include Exploded Items"),
            "fieldtype": "Data",
	    "options": "",
	    "default": "Y"
        },
	{
            "fieldname": "bom",
            "label": __("BOM"),
            "fieldtype": "Data",
	    "read_only": 1
        },
	{
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Data",
	    "read_only": 1
        },
	{
            "fieldname": "reserve_warehouse",
            "label": __("Reserve Warehouse"),
            "fieldtype": "Data",
	    "read_only": 1
        },
	{
            "fieldname": "core_team_coordinator",
            "label": __("Core Team Coordinator"),
            "fieldtype": "Data",
	    "read_only": 1,
	    "hidden": 1
        },
	{
            "fieldname": "planner",
            "label": __("Planner"),
            "fieldtype": "Data",
	    "read_only": 1,
	    "hidden": 1
        },
	{
            "fieldname": "start_date",
            "label": __("Start Date"),
            "fieldtype": "Data",
	    "read_only": 1,
	    "hidden": 1
        }
	],
	onload: function(report) {
        console.log("onload.............");
        console.log("Make Stock Requisition...");
        report.page.add_inner_button(__("Make Issue"),
            function() {
                var reporter = frappe.query_reports["BOM Item Warehouse2"];
                reporter.makeIssue(report);
            });
	},//end of onload..
	makeIssue: function(report) {
        makeMaterialIssue(report);
    	}
}//end of report..

function makeMaterialIssue(report){
	console.log("----------------makeMaterialIssue report...");
	var filters = report.get_values();
	var reportData = getReportData();
	var project = filters.project;
	var core_team_coordinator = filters.core_team_coordinator;
	var planner = filters.planner;
	console.log("core_team_coordinator--------"+core_team_coordinator);
	console.log("planner--------"+planner);
	if (reportData.length != 0) {
		for (var i = 0; i < reportData.length; i++) {
			var table_data_list = [];
                        var item_code = reportData[i]['item_code'];
                        var bom_qty = reportData[i]['bom_qty'];
                        var qty = reportData[i]['qty'];
			var qty_in_reserved_whse = reportData[i]['qty_in_reserved_whse'];
			var qty_in_production_whse = reportData[i]['qty_in_production_whse'];
			var total_qty = reportData[i]['total_qty'];
			if (qty > 0) {
				table_data_list.push({"item_code":item_code,
						      "bom_qty":bom_qty,
						      "qty":qty,
						      "project": project,
						      "planner": planner,
						      "qty_in_reserved_whse":qty_in_reserved_whse,
						      "qty_in_production_whse":qty_in_production_whse,
						      "total_qty":total_qty,
						      "core_team_coordinator": core_team_coordinator
							});
			    	frappe.call({
        			method:"nhance.nhance.report.bom_item_warehouse2.bom_item_warehouse2.make_issue",
        			args: {
					/**
            				"item_code": item_code,
					"project": project,
					"qty": qty,
					"planner": planner,
					"core_team_coordinator": core_team_coordinator
					**/
					"issue_items": table_data_list
        			},
        		       async: false,
        		       callback: function(r) {
            		       if (r.message) {
                			frappe.set_route('List', r.message);
            			}
        		       }//end of callback fun..
    			    })//end of frappe call.
                        }//end of if..
		}//end of for loop..
	}//end of if..
}//end of function..

function getReportData() {
    var reportData = [];
    frappe.call({
        method: "nhance.nhance.report.bom_item_warehouse2.bom_item_warehouse2.get_report_data",
        async: false,
        callback: function(r) {
            console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}

