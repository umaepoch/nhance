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
	    "on_change": function(query_report){
		var docName = frappe.query_report.get_filter_value("for");
		console.log("on change...."+docName);
		frappe.query_report.set_filter_value("docIds", []);
		frappe.query_reports["BOM Item Warehouse Status Report"].filters[1].options = docName;
		frappe.query_report.refresh();
	    }//end of on_change..
        },
	{
	   "fieldname":"docIds",
	   "label": __("Doc Ids"),
	   "fieldtype": "Link",
	   "get_query": function() {
                var docName = frappe.query_report.get_filter_value("for");
		if (docName == "BOM"){
                	return {
                    	"doctype": docName,
                    	"filters": {
                        	"docstatus": 1,
                    	}
                }
		}else if (docName == "Project"){
			return {
                    	"doctype": docName,
                    	"filters": {"status": ["not in", ["Completed","Cancelled"]]}
			}
		}else if (docName == "Sales Order"){
			return {
                    	"doctype": docName,
                    	"filters": {"status": ["!=", "Cancelled"], "docstatus": 1}
			}
		}
            },
	   "on_change": function(query_report){
		var docName = frappe.query_report.get_filter_value("for");
		var docID = frappe.query_report.get_filter_value("docIds");
		if(docName=="Project"){

		if (docID != undefined && docID != ""){
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
		frappe.msgprint(__("Master BOM Not Found In The Project."));
		//setMasterBOM_Value(masterBOM,query_report);

		}else{
		console.log("success.."+masterBOM[0].master_bom);
		var master_bom = masterBOM[0].master_bom;
		//setMasterBOM_Value(master_bom,query_report);

		console.log("masterBOM-----:: "+master_bom);
		frappe.query_report.set_filter_value("master_bom_hidden", "");
		frappe.query_report.set_filter_value("master_bom_hidden", master_bom);
		var status = get_record_status();
		if(status == -1){
			frappe.msgprint(__("Records Not Found For "+docID));
			}

		}
		}//end of call-back function..
		});//end of frappe call..
		}

		}//end of if..
		else if(docName=="BOM"){
			frappe.query_report.refresh();
			
			var status = get_record_status();
			if(status == -1){
				frappe.msgprint(__("Records Not Found For "+docID));
			}
		}
		else if(docName=="Sales Order"){
			frappe.query_report.refresh();
			
			var status = get_record_status();
			if(status == -1){
				frappe.msgprint(__("Records Not Found For "+docID));
			}
		}
		frappe.query_report.refresh();
		
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

function get_record_status() {
    var status = 1;
    frappe.call({
        method: "nhance.nhance.report.bom_item_warehouse_status_report.bom_item_warehouse_status_report.get_record_status",
        async: false,
        callback: function(r) {
		status = r.message;
        } //end of call back fun..
    }); //end of frappe call..
console.log("status-----:: "+status);
return status;
}
