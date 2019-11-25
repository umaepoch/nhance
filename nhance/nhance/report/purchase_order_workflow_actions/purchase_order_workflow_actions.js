// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Workflow Actions"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.month_start(), -1),
            "width": "80"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.month_end(), -1)
        },
	{
	    "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Link",
            "options": "Workflow State"
	}
	],
	onload: function(report) {
        //console.log("Make PO and Transfer Existing/Required Quantity..........");
        report.page.add_inner_button(__("Workflow Action"),
            function() {
		
                var reporter = frappe.query_reports["Purchase Order Workflow Actions"];
                reporter.make_PO_and_transfer_qty(report);
            });
    },
    make_PO_and_transfer_qty: function(report) {
	  var start_date = frappe.query_report.get_filter_value("from_date");
	   var end_date = frappe.query_report.get_filter_value("to_date");
	   var status = frappe.query_report.get_filter_value("status");
	   var purchase_order = "";
	   var purchase_data = []
	   if (status == ""){
	   	var purchase_order = get_purchase_order(start_date,end_date);
		}
	  if (status != ""){
		var start = start_date
		var with_status_details = {
					"start_date":start_date,
					"end_date":end_date,
					"status":status
				}
		purchase_data.push(with_status_details);
		var purchase_order = purchase_order_with_status(purchase_data);
		}
		//console.log("purchase order ----------"+JSON.stringify(purchase_order));
		var fields = [];
		var data1 = {
			    "fieldtype":"Read Only",
                            "label": "Purchase Order",
                            "fieldname": "purchase_order"

                        }
		 fields.push(data1);
		var data2=	{
			    
                            "fieldtype": "Column Break",
                            "fieldname": "column_breaks"
			}
		 fields.push(data2);
		var data3	= {   
			    "fieldtype":"Read Only",
                            "label": "Status",
                            "fieldname": "status"
			}
		 fields.push(data3);
		var data4=	{
                            "fieldtype": "Column Break",
                            "fieldname": "column_break2s"
			}
		 fields.push(data4);
		var data5=	{
			    "fieldtype":"Read Only",
                            "label": "Posting Date",
                            "fieldname": "posting_date"
			}
		 fields.push(data5);
		var data6=	{
			   "fieldtype": "Section Break",
                            "fieldname": "section_breaks"
			}		
			
                fields.push(data6);
		//console.log("fields-----------------"+fields);
		 for(var i =0; i < purchase_order.length;i++){
		//console.log("hello");
		
		var data = {
                            "fieldtype": "Check",
                            "label": purchase_order[i].name,
                            "fieldname": purchase_order[i].name

                        }
			fields.push(data);
		
		var data11 =	{
                            "fieldtype": "Column Break",
                            "fieldname": "column_break" + i + ""
			}
			fields.push(data11);
			
		var data12 =	{
			    "fieldtype":"Read Only",
                            "label": purchase_order[i].workflow_state,
                            "fieldname": purchase_order[i].workflow_state
			}
		fields.push(data12);
		
		var data13 ={
                            "fieldtype": "Column Break",
                            "fieldname": "column_break2" + i + ""
			}
		fields.push(data13);
		
		var data14 ={
			   "fieldtype":"Read Only",
                            "label": purchase_order[i].creation,
                            "fieldname": purchase_order[i].creation
			}
			fields.push(data14);
		
		var data15 ={
			     
			   "fieldtype": "Section Break",
                            "fieldname": "section_break"+i+""
			}
		fields.push(data15);
		}
		  var dialog = new frappe.ui.Dialog({
		 'fields': fields,
	    primary_action: function(){
		dialog.hide();
		var dialog_data = dialog.get_values();
		var purchase_name = [];
		  Object.keys(dialog_data).forEach(function(key) {
		   if (dialog_data[key] == 1) {
			console.log("purchase order---------------"+key);
			for (var pur =0; pur<purchase_order.length; pur++){
				if(purchase_order[pur].name == key){
					purchase_details = {
							"name": purchase_order[pur].name,
							"status":purchase_order[pur].workflow_state
						}
					purchase_name.push(purchase_details)
					
				
				}
			
			}
				}
			});
			//console.log("purchase name -------------"+purchase_name);
			//var actions = frappe.workflow.get_all_transition_actions("Purchase Order");
			
			if (!frappe.model.has_workflow("Purchase Order")) 
				return frappe.msgprint("worklow is not active");
			
			if (purchase_name.length > 0){
			var next_state = [];
			var role = "";
			var workflow_data = get_workflow_details(purchase_name)
			//console.log("workflow_data--------------"+JSON.stringify(workflow_data));
			for (var wrk =0; wrk < workflow_data.length; wrk++){
				var status = workflow_data[wrk].action;
				 role = workflow_data[wrk].allowed;
				next_state.push(status);
				//console.log("status--------------"+status);
			}
			var check_role = get_roles(frappe.session.user, role);
			console.log("next stage-----------"+next_state);
			console.log("check_role-----------"+check_role);
			if(check_role == role){
			//if(frappe.user_roles.indexOf(role) == 1){
			var s_dialog =new frappe.ui.Dialog({
				//title "please select  workflow Action";
				"fields":[
					{
					"fieldtype": "Select",
                           		 "fieldname": "actions",
					 "label":"Actions",
				         "options": next_state	
					}],
				  primary_action: function(){
					s_dialog.hide();
					var action_dialog = s_dialog.get_values();
					console.log("action_dialog------------"+JSON.stringify(action_dialog));
					var action = action_dialog.actions;
					console.log("action --------------"+action);
					var success = set_workflow_purchase_order(action,purchase_name);
					console.log("success------------",success);
					if(success == 1){
						frappe.msgprint("workflow has updated ");
					}
				}
			 });
			s_dialog.show();
			}else{
				frappe.msgprint('"'+frappe.session.user+'"'+" Don't have permission "+'"'+role+'"' +" to perform "+'"'+next_state+'"');
			}
		}
		else{
			frappe.msgprint("Please select atleast one purchase order");
		}
		
	    }
	});
	//dialog.fields_dict.ht.$wrapper.html('Hello World');
	/*for(var j = 0; j < purchase_order.length; j++){
	 var name = purchase_order[j].name;
	console.log("name---------"+name);
	
	  dialog.fields_dict.name.input.onclick = function() {
		console.log("checked");
		}
	}*/
	dialog.show();
	//console.log("fields-----------------------"+JSON.stringify(fields));
}	
}
function get_purchase_order(start_date,end_date){
	 var purchase = "";
    frappe.call({
        method: "nhance.nhance.report.purchase_order_workflow_actions.purchase_order_workflow_actions.purchase_order_detials",
        args: {
            "start_date": start_date,
           "end_date": end_date
        },
        async: false,
        callback: function(r) {
            //console.log("ItemValuationRateFromStockBalance::" + JSON.stringify(r.message));
            purchase = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return purchase;

}

function get_workflow_details(purchase_name){
	 var worflow = "";
    frappe.call({
        method: "nhance.nhance.report.purchase_order_workflow_actions.purchase_order_workflow_actions.workflow_details",
        args: {
            "purchase_name": purchase_name
        },
        async: false,
        callback: function(r) {
         
            worflow = r.message;

        } //end of call-back function..
    }); //end of frappe call..
    return worflow;

}

function purchase_order_with_status(purchase_data){
	
	 var purchase = "";
    frappe.call({
        method: "nhance.nhance.report.purchase_order_workflow_actions.purchase_order_workflow_actions.purchase_order_with_status",
        args: {
            "purchase_data": purchase_data
        },
        async: false,
        callback: function(r) {
      
            purchase = r.message;

        } 
    }); 
    return purchase;


}

function get_roles(user, role){
	var purchase = "";
    frappe.call({
        method: "nhance.nhance.report.purchase_order_workflow_actions.purchase_order_workflow_actions.user_details",
        args: {
            "user": user,
	    "role":role
        },
        async: false,
        callback: function(r) {
	if (r.message.length > 0){
      
            purchase = r.message[0].role;
	}
        } 
    }); 
    return purchase;


}

function set_workflow_purchase_order(action,purchase_name){
	var purchase = "";
    frappe.call({
        method: "nhance.nhance.report.purchase_order_workflow_actions.purchase_order_workflow_actions.ready_to_update_workflow_state",
        args: {
            "action": action,
	    "purchase_name":purchase_name
        },
        async: false,
        callback: function(r) {
	if (r.message){
      
            purchase = r.message;
	}
        } 
    }); 
	console.log("purchase-------------flag"+purchase);
    return purchase;


}
