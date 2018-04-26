// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM Item Warehouse Status Report"] = {
	"filters": [
	{
            "fieldname":"for",
            "label": __("For"),
            "fieldtype": "Select",
            "options": ["Sales Order", "BOM", "Project"],
	    "reqd": 1,
	    "on_change": function(){
		var docName = frappe.query_report_filters_by_name.for.get_value();
		console.log("on change...."+docName);
		frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse_status_report.bom_item_warehouse_status_report.fetch_Records",
			args: {
         	 		"docName":docName,
        	},
		async: false,
		callback: function(r) 
      		 { 
			var docIds_filter = frappe.query_report_filters_by_name.docIds;
			docIds_filter.df.options = r.message;
			docIds_filter.df.default = "";
			docIds_filter.refresh();
			docIds_filter.set_input(docIds_filter.df.default);
			
		}//end of call back fun..
		});//end of frappe call..
	    }//end of on_change..
        },
	{
	   "fieldname":"docIds",
	   "label": __("Doc Ids"),
	   "fieldtype": "Select",
	   "on_change": function(query_report){
		var docName = frappe.query_report_filters_by_name.for.get_value();
		var docID = frappe.query_report_filters_by_name.docIds.get_value();
		if(docName=="Project"){
		frappe.call({
			method: 			    				    					"nhance.nhance.report.bom_item_warehouse_status_report.bom_item_warehouse_status_report.get_master_bom",
			args: {
         	 		"docId":docID,
				"docName":docName
        	},
		async: false,
		callback: function(r) 
      		{ 
		var masterBOM = r.message;
		console.log("masterBOM....."+masterBOM);
		if(masterBOM == "null"){
		//frappe.msgprint(__("Master BOM Not Found In The Project."));
		setMasterBOM_Value(masterBOM,query_report);
		}else{
		console.log("success.."+masterBOM[0].master_bom);
		var master_bom = masterBOM[0].master_bom;
		setMasterBOM_Value(master_bom,query_report);
		}
		}//end of call-back function..
		});//end of frappe call..
		}//end of if..
		else if(docName=="BOM"){
		query_report.refresh();
		}
		else if(docName=="Sales Order"){
		query_report.refresh();
		}
	   }//end of on_change..
	},
	{
            "fieldname": "master_bom_hidden",
            "label": __("Master BOM"),
            "fieldtype": "Data",
	    "hidden": 1
        }
	],
    onload: function(report) {
	//on change function start..
}
}
function setMasterBOM_Value(masterBOM,query_report){
var master_bom_hidden_filter = frappe.query_report_filters_by_name.master_bom_hidden;
master_bom_hidden_filter.df.options = masterBOM;
master_bom_hidden_filter.df.default = masterBOM;
master_bom_hidden_filter.refresh();
master_bom_hidden_filter.set_input(master_bom_hidden_filter.df.default);
query_report.refresh();
}

