// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Daily Site Report', {
	refresh: function(frm) {
		frappe.ui.form.on("Daily Site skill",{
			skill: function(frm, cdt, cdn){
				var d = locals[cdt][cdn];
				$.each(frm.doc.items, function(i, item) {
					console.log("hello-------------skill");
					if (d.resource_deployed == item.resource_deployed && d.skill == item.skill){
						var resource_skill_list = get_skill_level_master(cur_frm.doc.project,d.resource_deployed);
						item.level = resource_skill_list[0];
					}
					cur_frm.refresh_field("items");
					cur_frm.refresh_field("level");
				});
			},
			resource_deployed: function(frm,cdt,cdn){
				var d = locals[cdt][cdn];
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
			}
		});
		cur_frm.set_query("resource_deployed", "items", function(frm, cdt, cdn) {
			//console.log("hello-------------")
			var d = locals[cdt][cdn];
			 var resource_deployed_list = get_resource_master(cur_frm.doc.project);
			 //console.log("resource_deployed_list--------"+resource_deployed_list);
			 return {
				    "filters": [
					["Resource", "name", "in", resource_deployed_list],

				]
				}
			cur_frm.refresh_field("items");
			cur_frm.refresh_field("resource_deployed");
		});
		cur_frm.set_query("skill", "items", function(frm, cdt, cdn) {
			//console.log("hello-------------")
			var d = locals[cdt][cdn];
			 var resource_skill_list = get_skill_master(cur_frm.doc.project,d.resource_deployed);
			 ////console.log("resource_deployed_list--------"+resource_deployed_list);
			 return {
				    "filters": [
					["Skills", "name", "in", resource_skill_list],

				]
				}
			
			cur_frm.refresh_field("items");
			cur_frm.refresh_field("skill");
		});
		cur_frm.set_query("level", "items", function(frm, cdt, cdn) {
			//console.log("hello-------------")
			var d = locals[cdt][cdn];
			 var resource_skill_list = get_skill_level_master(cur_frm.doc.project,d.resource_deployed);
			 ////console.log("resource_deployed_list--------"+resource_deployed_list);
			 return {
				    "filters": [
					["Skill Levels", "name", "in", resource_skill_list],

				]
				}
			cur_frm.refresh_field("items");
			cur_frm.refresh_field("level");
		});
	}
});
function get_resource_master(project){
	var supplier_criticality = [];
	frappe.call({
        	method: 'nhance.nhance.doctype.daily_site_report.daily_site_report.get_resource_master',
		args: {
		  
		   "project":project,
		  
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
		   for (var i =0; i < r.message.length; i++){
		   	supplier_criticality.push(r.message[i].resource_deployed);
		   }
		   // end_date = (new Date(supplier_criticality-1));
		  //console.log("current date------------"+supplier_criticality);
		}
	    });
	    return supplier_criticality;
}
function get_skill_master(project,resource_deployed){
	var supplier_criticality = [];
	frappe.call({
        	method: 'nhance.nhance.doctype.daily_site_report.daily_site_report.get_skill_master',
		args: {
		  
		   "project":project,
	           "resource_deployed":resource_deployed
		  
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
		  
		   	supplier_criticality.push(r.message);
		 
		   // end_date = (new Date(supplier_criticality-1));
		  //console.log("current date------------"+supplier_criticality);
		}
	    });
	    return supplier_criticality;
}
function get_skill_level_master(project,resource_deployed){
	var supplier_criticality = [];
	frappe.call({
        	method: 'nhance.nhance.doctype.daily_site_report.daily_site_report.get_skill_level_master',
		args: {
		  
		   "project":project,
	           "resource_deployed":resource_deployed
		  
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
		  
		   	supplier_criticality.push(r.message);
		 
		   // end_date = (new Date(supplier_criticality-1));
		  //console.log("current date------------"+supplier_criticality);
		}
	    });
	    return supplier_criticality;
}
