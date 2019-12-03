// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */
var project_details = [];
var col_data= [];
var company = "";
frappe.query_reports["Project Material Requisition Tool"] = {
	"filters": [
		{
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
											//console.log(" Changed project ********* ");
											var project = frappe.query_report.get_filter_value("project");
											//console.log("Selected project******************:::::"+project);
											frappe.call({
													method: "nhance.nhance.report.project_material_requisition_tool.project_material_requisition_tool.fetch_project_details",
													args: {
													"project":project
													},
													async: false,
													callback: function(r)
													{
																				if(r.message){
																				var master_bom = r.message[0].master_bom;
																				project_details = r.message[0]
																				//////console.log("project_details  :::::"+JSON.stringify(project_details));
																				//console.log("MAster Bom :::::"+master_bom);

																				}//end of if..
													}//end of call-back function..
											});//end of frappe call..

											if( project_details['reserve_warehouse'] == null || project_details['master_bom'] == null || project_details['project_warehouse'] == null)
											{
												frappe.throw("The Project Master for Project "+ project +" is not updated with Master BOM/Reserve Warehouse/Project Warehouse. Please update these values in the Project Master and run this report again. ");
											}

											frappe.query_report.refresh();

			} //End of on change


	  } //end of prject filter

	],
	onload: function(report) {
				//console.log("onload.............");
				//console.log("Make Stock Requisition button created...");

				report.page.add_inner_button(__("Make Stock Requistion"),
						function() {
								frappe.query_report.refresh();  //beacause of that col data issue
								frappe.query_report.refresh();	//beacause of that col data issue

								var onclick_project = frappe.query_report.get_filter_value("project");

								var reporter = frappe.query_reports["Project Material Requisition Tool"];
								//console.log("Button Clicked...");
								frappe.call({
										method: "nhance.nhance.report.project_material_requisition_tool.project_material_requisition_tool.get_col_data",
										args:{
											"onclick_project":onclick_project
										},
										async: false,
										callback: function(r)
										{
																	if(r.message){
																	col_data = r.message
																	//console.log("COl data::"+ JSON.stringify(col_data));
																	}//end of if..
										}//end of call-back function..
								});//end of frappe call..

								  var short_qty_flag="false"
									for (i = 0; i < col_data.length; i++) {
										var short_qty = parseFloat (col_data[i][12])
										//console.log("Short qty "+i +"st row"+  short_qty );

										//console.log("Short qty type"+ typeof short_qty );

										if (short_qty > 0) {
											//console.log("came inside check loop");
											short_qty_flag = "true";
											break;
										}
								  }
								//reporter.makeStockRequisition(report, "");

								if (short_qty_flag == "true"){
									reporter.makeStockRequisition(report, "");
								}
								else{
									frappe.throw("Short qty for all items are empty,Cannot makeStockRequistion");
								}
								//reporter.makeIssue(report);
						});
	},//end of onload..

	makeStockRequisition: function(report, status) {
				//console.log("from first makeStockRequisition fun entry check ");
				var filters = report.get_values();
				//console.log("makeStockRequisition fun inside filters:: "+filters);
				//console.log("makeStockRequisition fun inside filters:: "+filters.project);

        var flag = "";
        makeStockRequistionn(filters);
  }
} //end of frappe.query_reports

function makeStockRequistionn(filters) {
		//console.log("from second makeStockRequisition fun entry check ");
		//console.log("makeStockRequisition fun inside filters:: "+filters.project);

		if (project_details['reserve_warehouse'] == null){
			frappe.throw("Please update Reserver Warehouse field for Project" +filters.project+" and try running the report again")
		}
		else{
			//console.log("reserve_warehouse is there:"+project_details['reserve_warehouse']);
		}

		var required_date ;
    var dialog = new frappe.ui.Dialog({
        title: __("This Tool can only be used to Request Quantities that have not been requested as per BOM " +project_details['master_bom']+ " for delivery to Warehouse "+project_details['reserve_warehouse']+" and as represented in Column Short Quantity. If you have to request for additional quantities, please change the BOM to reflect additional quantities or use the Stock Requisition Tool Directly"),
				'fields': [
					{
							"fieldtype": "Date",
							"label": "Required By Date",
							"fieldname": "required_date",
							"reqd":1
					}
				],
				primary_action : function() {
					dialog.hide();

					//console.log("After submit dialog.get_values()"+JSON.stringify( dialog.get_values() ));
					//console.log("After submit ,COl data::"+ JSON.stringify(col_data));

					//workflowStatus =get_workflowStatus(col_data);  //for future puprose pass it as argu
					//console.log("After submit ,workflowStatus"+ workflowStatus );
					console.log("After submit ,project"+ filters.project );

					dialog_data = dialog.get_values() ;
					required_date = dialog_data.required_date ;
					console.log("After submit dialog date,required_date final"+ required_date);

					if (filters.project && project_details['reserve_warehouse'] ) {
						return frappe.call({
                    method: "nhance.nhance.report.project_material_requisition_tool.project_material_requisition_tool.make_stock_requisition",
                    args: {
											"project":filters.project,
											"company":filters.company,
											"col_data" : col_data,
											"required_date" : required_date,
											"master_bom" : project_details['master_bom']
                    },
                    callback: function(r) {
                        if (r.message != "failed") {
                            frappe.set_route('List', r.message);
                        }
                    } //end of callback fun..
                });//end of frappe call.
					} //end of if
				} //end of set_primary_action

		}); //end of dialog box..
		dialog.show();

		/*dialog.set_primary_action(__(“Proceed”), function() {
			dialog.hide();
			console.log("Proceed button has been clicked ");
		}); */
}
function get_workflowStatus(col_data)
{
	workflowStatus = ""
	frappe.call({
			method: "nhance.nhance.report.project_material_requisition_tool.project_material_requisition_tool.get_workflowStatus",
			args: {
				"master_bom":project_details.master_bom,
				"col_data" :col_data
			},
			async: false,
			callback: function(r)
			{
										if(r.message){
										//console.log("get_workflowStatus"+ JSON.stringify(r.message));
										workflowStatus = r.message
										//console.log("COl data::"+ JSON.stringify(col_data));

										}//end of if..
			}//end of call-back function..
	});//end of frappe call..
	return workflowStatus

}

function makeStockOperations(report, status, flag) {
		//console.log("Inside make makeStockOperations ");
    var filters = report.get_values();
    var project = frappe.query_report.get_filter_value("project");
		//console.log("makeStockRequisition fun project:::::::: "+project);
		var warehouse = getWarehouseName(project)
		//console.log("makeStockRequisition fun warehouse::::: "+warehouse);


}

function getWarehouseName(project_name) {
		//console.log("from getWarehouseName ::::: "+project_name);

    var wharehouse = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: "Project",
            filters: {
                name: ["=", project_name]
            },

            fieldname: ["project_warehouse"]
        },
        async: false,
        callback: function(r) {
            //console.log("warehouse..." + r.message.warehouse);
            wharehouse = r.message.project_warehouse;
        }
    });
    return wharehouse;

}

