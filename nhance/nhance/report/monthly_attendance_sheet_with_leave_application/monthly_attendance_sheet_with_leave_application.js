// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


frappe.query_reports["Monthly Attendance Sheet with Leave Application"] = {
	"filters": [
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
				"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		}
	],

	"onload": function(report) {
		report.page.add_inner_button(__("Submit Leave Application"),
			function() {
				var reporter = frappe.query_reports["Monthly Attendance Sheet with Leave Application"];
				reporter.make_leave_application(report);
			});
		return  frappe.call({
			method: "erpnext.hr.report.monthly_attendance_sheet.monthly_attendance_sheet.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
		
	},
	make_leave_application:function(report){
		var filters = report.get_values();
		
		frappe.call({
			method: "nhance.nhance.report.monthly_attendance_sheet_with_leave_application.monthly_attendance_sheet_with_leave_application.create_leave_application",
			args:{
				"filters":filters
			},
			callback: function(r) {
				var list = r.message
			}
		});
	
		
	}
}

