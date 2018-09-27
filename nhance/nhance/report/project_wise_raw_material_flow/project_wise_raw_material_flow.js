// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Wise Raw Material Flow"] = {
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
			method: "nhance.nhance.report.project_wise_raw_material_flow.project_wise_raw_material_flow.fetch_project_details",
			args: {
         	 		"project":project
        		},
			async: false,
			callback: function(r) 
      			{ 
				if(r.message){
				console.log("docids options::"+r.message.length);
				console.log("message::"+JSON.stringify(r.message));

				var project_warehouse = r.message[0].project_warehouse;
				var reserve_warehouse = r.message[0].reserve_warehouse;
				var master_bom = r.message[0].master_bom;
				var core_team_coordinator = r.message[0].core_team_coordinator;
				var planner = r.message[0].planner;
				var start_date = r.message[0].start_date;


				var warehouse_filter = frappe.query_report_filters_by_name.warehouse;
				var reserve_warehouse_filter = frappe.query_report_filters_by_name.reserve_warehouse;
				var bom_filter = frappe.query_report_filters_by_name.bom;
				var core_team_coordinator_filter = frappe.query_report_filters_by_name.core_team_coordinator;
				var planner_filter = frappe.query_report_filters_by_name.planner;
				var start_date_filter = frappe.query_report_filters_by_name.start_date;

				if (project_warehouse != null) {
				console.log("project_warehouse::"+ project_warehouse);
				warehouse_filter.df.options = project_warehouse;
				warehouse_filter.df.default = project_warehouse;
				warehouse_filter.refresh();
				warehouse_filter.set_input(warehouse_filter.df.default);
				query_report.refresh();
				}else{
				warehouse_filter.df.options = "";
				warehouse_filter.df.default = "";
				warehouse_filter.refresh();
				warehouse_filter.set_input(warehouse_filter.df.default);
				query_report.refresh();
				}
				
				if (reserve_warehouse != null) {
				console.log("reserve_warehouse::"+ reserve_warehouse);
				reserve_warehouse_filter.df.options = reserve_warehouse;
				reserve_warehouse_filter.df.default = reserve_warehouse;
				reserve_warehouse_filter.refresh();
				reserve_warehouse_filter.set_input(reserve_warehouse_filter.df.default);
				query_report.refresh();
				}else{
				reserve_warehouse_filter.df.options = "";
				reserve_warehouse_filter.df.default = "";
				reserve_warehouse_filter.refresh();
				reserve_warehouse_filter.set_input(reserve_warehouse_filter.df.default);
				query_report.refresh();
				}

				if (master_bom != null) {
				console.log("master_bom::"+ master_bom);
				bom_filter.df.options = master_bom;
				bom_filter.df.default = master_bom;
				bom_filter.refresh();
				bom_filter.set_input(bom_filter.df.default);
				var qty = frappe.query_report_filters_by_name.qty_to_make.get_value();
		    		var check_for_whole_number_flag = check_for_whole_number(master_bom, qty, query_report);
		    		if (check_for_whole_number_flag) {
                    		frappe.msgprint(__("Quantity to Make should be whole number"));
				}
				query_report.refresh();
				}else{
				bom_filter.df.options = "";
				bom_filter.df.default = "";
				bom_filter.refresh();
				bom_filter.set_input(bom_filter.df.default);
				query_report.refresh();
				}
				
				if (core_team_coordinator != null) {
				core_team_coordinator_filter.df.options = core_team_coordinator;
				core_team_coordinator_filter.df.default = core_team_coordinator;
				core_team_coordinator_filter.refresh();
				core_team_coordinator_filter.set_input(core_team_coordinator_filter.df.default);
				query_report.refresh();
				}else{
				console.log("core_team_coordinator::"+ core_team_coordinator);
				core_team_coordinator_filter.df.options = "null";
				core_team_coordinator_filter.df.default = "null";
				core_team_coordinator_filter.refresh();
				core_team_coordinator_filter.set_input(core_team_coordinator_filter.df.default);
				query_report.refresh();
				}
				
				if (planner != null) {
				planner_filter.df.options = planner;
				planner_filter.df.default = planner;
				planner_filter.refresh();
				planner_filter.set_input(planner_filter.df.default);
				query_report.refresh();
				}else{
				console.log("planner::"+ planner);
				planner_filter.df.options = "null";
				planner_filter.df.default = "null";
				planner_filter.refresh();
				planner_filter.set_input(planner_filter.df.default);
				query_report.refresh();
				}
				
				if (start_date != null) {
				start_date_filter.df.options = start_date;
				start_date_filter.df.default = start_date;
				start_date_filter.refresh();
				start_date_filter.set_input(start_date_filter.df.default);
				query_report.refresh();
				}else{
				start_date_filter.df.options = "";
				start_date_filter.df.default = "";
				start_date_filter.refresh();
				start_date_filter.set_input(start_date_filter.df.default);
				query_report.refresh();
				}
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
            "fieldname": "qty_to_make",
            "label": __("Quantity To Make"),
            "fieldtype": "Data",
            "default": "1",
            "reqd": 1,
	    "on_change": function(query_report) {
		var qty = frappe.query_report_filters_by_name.qty_to_make.get_value();
		var bom = frappe.query_report_filters_by_name.bom.get_value();

		if (!jQuery.isNumeric(qty)) {
                    frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                    frappe.throw("Quantity to Make value is not in proper format")
                }
                if (qty < 0) {
                    frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                    frappe.throw("Quantity to Make cannot be nagative please input positive value")
                }
                if (qty < 1) {
                    frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                    frappe.throw(" Quantity to Make should be greater than Zero")
                }
		if (bom!=null){
		    var check_for_whole_number_flag = check_for_whole_number(bom, qty, query_report);
		    if (check_for_whole_number_flag) {
                    	frappe.msgprint(__("Quantity to Make should be whole number"));
                    }
		}
		query_report.refresh();
	    }
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
                var reporter = frappe.query_reports["Project Wise Raw Material Flow"];
                reporter.makeIssue(report);
            });
	},//end of onload..
	isNumeric: function(obj) {
        return !jQuery.isArray(obj) && (obj - parseFloat(obj) + 1) >= 0;
    	},
	makeIssue: function(report) {
        makeMaterialIssue(report);
    	}
}//end of report..

function makeMaterialIssue(report){
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
        			method:"nhance.nhance.report.project_wise_raw_material_flow.project_wise_raw_material_flow.make_issue",
        			args: {
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
        method: "nhance.nhance.report.project_wise_raw_material_flow.project_wise_raw_material_flow.get_report_data",
        async: false,
        callback: function(r) {
            console.log("reportData::" + JSON.stringify(r.message));
            reportData = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return reportData;
}
function check_for_whole_number(bomNO, qty, query_report) {
    var check_for_whole_number = false;
    frappe.call({
        method: "nhance.nhance.report.project_wise_raw_material_flow.project_wise_raw_material_flow.check_for_whole_number",
        args: {
            "bomno": bomNO
        },
        async: false,
        callback: function(r) {
            if (r.message && qty % 1 != 0) {
                check_for_whole_number = true;
                frappe.query_report_filters_by_name.qty_to_make.set_input("1");
                query_report.refresh();
            } else {
                check_for_whole_number = false;
                query_report.refresh();
            }
        } //end of callback fun..
    }) //end of frappe call..
    return check_for_whole_number;
}

