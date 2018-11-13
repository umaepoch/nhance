// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];
const d = new Date();
var currentMonth = monthNames[d.getMonth()];
var currentYear = d.getFullYear();
console.log("currentYear----------"+currentYear);
//var company_gstino = fun_gstin();
//console.log("company_gstino----------"+company_gstino);
frappe.query_reports["GSTR-3B"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": ["2014","2015","2016","2017","2018","2019","2020", "2021", "2022","2023", "2024","2025","2026"],
			"default": currentYear
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": ["January", "February", "March", "April", "May", "June",
 			 "July", "August", "September", "October", "November", "December"],
			"default": currentMonth
		},
		{
			"fieldname":"type_of_taxes",
			"label": __("Type of Taxes"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": ["Outward Supplies and inward supplies", "Eligible ITC", "exempt, Nil-rated and non-GST","Interest & late fee payable", "State Supplier Taxes"],
			"default": "Outward Supplies and inward supplies",
			"width": "250"
		}
	]
}
/*
var company_gstin = "";
function fun_gstin(){
	
	var details = [];
	frappe.call({
           	 "method": "erpnext.regional.report.gstr_3b.gstr_3b.for_gstin",
              	
          	    callback: function(r) {
		      //console.log("item detail  -----------------------" + JSON.stringify(r.message));
			details = r.message;
				company_gstin =  JSON.stringify(r.message)
			
		//console.log("company_gstin----------"+company_gstin);
                }
		
            })
	
	return company_gstin
}
*/
