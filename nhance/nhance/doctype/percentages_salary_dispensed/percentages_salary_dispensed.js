// Copyright (c) 2020, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('Percentages Salary Dispensed', {
	refresh: function(frm) {
		frappe.ui.form.on("Employee Dispensed" , "employee", function(frm,cdt,cdn){
			var d = locals[cdt][cdn];
			if (d.employee){
				 $.each(frm.doc.employee_percent, function(i, item) {
						
			
					if (d.idx != item.idx && d.employee == item.employee){
						$.each(frm.doc.items, function(i, item) {
					
			
							if (d.idx == item.idx ){
								item.employee = ""
							}
							cur_frm.refresh_field("employee_percent")
						})
					frappe.throw("already asigned in previous row "+item.idx+" please select some other Employee");
					}
				})
			}
		});
	}
});
