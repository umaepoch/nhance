// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Resource Deployment', {
	refresh: function(frm) {
		cur_frm.set_query("resource_deployed", "items", function(frm, cdt, cdn) {
			//console.log("hello-------------")
			var d = locals[cdt][cdn];
			var skill_level = d.skill_level;
			 var resource_deployed_list = get_resource_master(skill_level);
			 //console.log("resource_deployed_list--------"+resource_deployed_list);
			 return {
				    "filters": [
					["Resource", "name", "in", resource_deployed_list],

				]
				}
			cur_frm.refresh_field("items");
			cur_frm.refresh_field("resource_deployed");
		});
		frappe.ui.form.on("Resource Requirement" , "resource_deployed", function(frm,cdt,cdn){
			var d = locals[cdt][cdn];
			
			if (d.resource_deployed){
				var resouce_and_skill = get_resource_and_skill(d.resource_deployed , d.skill_level);
				
				if (resouce_and_skill == true){
					 $.each(frm.doc.items, function(i, item) {
						
				
						if (d.idx != item.idx && d.resource_deployed == item.resource_deployed){
							$.each(frm.doc.items, function(i, item) {
						
				
								if (d.idx == item.idx ){
									item.resource_deployed = ""
								}
								cur_frm.refresh_field("items")
							})
							frappe.throw("already asigned in previous row "+item.idx+" please select some other resource");
						}
					})
				}else{
					 $.each(frm.doc.items, function(i, item) {
						
				
						if (d.idx == item.idx ){
							item.resource_deployed = ""
						}
						cur_frm.refresh_field("items")
					})
					frappe.throw("this resource "+d.resource_deployed +" is not allocated for this skill - level "+d.skill_level+" in Resource Master ");
					
				}
			}
			
		}); 
		
	},
	project:function(frm){
		////console.log("project -----------------"+cur_frm.doc.project);
		if (cur_frm.doc.project){
			var project_resource = get_project_resource_plan(cur_frm.doc.project);
			////console.log("project_resource----------------"+JSON.stringify(project_resource))
			for (var i=0; i < project_resource.length; i++){
				for(var j =1; j <=  project_resource[i].required; j++){
					var child = cur_frm.add_child("items");
			
					frappe.model.set_value(child.doctype, child.name, "skill_level", project_resource[i].skill+" - "+ project_resource[i].level);
					}
				cur_frm.refresh_field("items");
				}
		}
	
	}
});
function get_project_resource_plan(project){
	var supplier_criticality = "";
	frappe.call({
        	method: 'nhance.nhance.doctype.project_resource_deployment.project_resource_deployment.get_project_resource_plan',
		args: {
		   "project":project,
		  
		},
		async: false,
		callback: function(r) {
		   // //console.log("supplier criticality..." + JSON.stringify(r.message));
		   supplier_criticality = r.message;
		   // end_date = (new Date(supplier_criticality-1));
		//  //console.log("current date------------"+supplier_criticality);
		}
	    });
	    return supplier_criticality;
}
function  get_resource_and_skill(resource_deployed , skill_level){
	var supplier_criticality = "";
	frappe.call({
        	method: 'nhance.nhance.doctype.project_resource_deployment.project_resource_deployment.get_resource_and_skill',
		args: {
		   "resource_deployed":resource_deployed,
		   "skill_level":skill_level,
		  
		},
		async: false,
		callback: function(r) {
		   // //console.log("supplier criticality..." + JSON.stringify(r.message));
		   supplier_criticality = r.message;
		   // end_date = (new Date(supplier_criticality-1));
		//  //console.log("current date------------"+supplier_criticality);
		}
	    });
	    return supplier_criticality;
}
function get_resource_master(skill_level){
	var supplier_criticality = [];
	frappe.call({
        	method: 'nhance.nhance.doctype.project_resource_deployment.project_resource_deployment.get_resource_master',
		args: {
		  
		   "skill_level":skill_level,
		  
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
		   for (var i =0; i < r.message.length; i++){
		   	supplier_criticality.push(r.message[i].resource);
		   }
		   // end_date = (new Date(supplier_criticality-1));
		  //console.log("current date------------"+supplier_criticality);
		}
	    });
	    return supplier_criticality;
}
