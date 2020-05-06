// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Being Ordered', {
	refresh: function(frm) {
		frappe.ui.form.on("Project Childs",{
			 project: function(frm , cdt, cdn){
				console.log("yes its comiibngjfg---")
				var d = locals[cdt][cdn];
				var idx = d.idx;
				if(d.idx >= 2){
					console.log("yes its more 2 ----------------")
					 $.each(frm.doc.projects, function(i, item) {
						if(idx != item.idx){
							if(item.project == d.project){
								frappe.msgprint("you have already selected this project "+ '"'+d.project+'"'+ " in previous row . Please select any other project");
								d.project = "";
								cur_frm.refresh_field("projects")
								
							}
							
						}
					})
				}
			}	
		});
	}
});
