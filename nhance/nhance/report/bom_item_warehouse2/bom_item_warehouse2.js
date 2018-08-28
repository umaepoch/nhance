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
            "get_query": function() {
                return {
                    "doctype": "Project",
                    "filters": {
                        "is_active": "Yes"
                    }
                }
            },
            "on_change": function(query_report) {
                var project = frappe.query_report_filters_by_name.project.get_value();
                console.log("project-------" + project);
                frappe.call({
                    method: "nhance.nhance.report.bom_item_warehouse2.bom_item_warehouse2.fetch_project_details",
                    args: {
                        "project": project
                    },
                    async: false,
                    callback: function(r) {
                        if (r.message) {
                            console.log("docids options::" + r.message.length);
                            console.log("result::" + JSON.stringify(r.message));
                            console.log("----------------Break Point 1");
                            var warehouse_filter = frappe.query_report_filters_by_name.warehouse;
                            console.log("----------------Break Point 2");
                            warehouse_filter.df.options = r.message[0].project_warehouse;
                            warehouse_filter.df.default = r.message[0].project_warehouse;
                            warehouse_filter.refresh();
                            warehouse_filter.set_input(warehouse_filter.df.default);
			    query_report.refresh();
                            console.log("----------------Break Point 3");
                        } //end of if..
                    } //end of call-back function..
                }); //end of frappe call..
            } //end of on_change
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
    ]
} //end of report..
