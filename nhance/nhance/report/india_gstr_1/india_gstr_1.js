// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

const d = new Date();
var currentMonth = monthNames[d.getMonth()];
<<<<<<< HEAD
frappe.query_reports["INDIA GSTR 1"] = {
=======
frappe.query_reports["India GSTR-1"] = {
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
    "filters": [{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
            "default": frappe.defaults.get_user_default("Company")
        },
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
            "fieldname": "fetch_days_data",
            "label": __("Fetch Days Data"),
            "fieldtype": "Data",
            "on_change": function(query_report) {
<<<<<<< HEAD
                //console.log("Fetch Days Data Entered---------");
=======
                console.log("Fetch Days Data Entered---------");
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                var from_date = frappe.query_report_filters_by_name.from_date.get_value();
                var to_date = frappe.query_report_filters_by_name.to_date.get_value();
                var fetch_days_data = frappe.query_report_filters_by_name.fetch_days_data.get_value();
		var temp_from_date_filter = frappe.query_report_filters_by_name.temp_from_date;
                var temp_to_date_filter = frappe.query_report_filters_by_name.temp_to_date;

                if (!jQuery.isNumeric(fetch_days_data)) {
                    frappe.query_report_filters_by_name.fetch_days_data.set_input("");
                    frappe.throw("Fetch Days Data value is not in proper format");
                }
                if (fetch_days_data < 0) {
                    frappe.query_report_filters_by_name.fetch_days_data.set_input("");
                    frappe.throw("Fetch Days Data value cannot be nagative please input positive value!");
                } else if (fetch_days_data < 1) {
                    frappe.query_report_filters_by_name.fetch_days_data.set_input("");
                    frappe.throw(" Fetch Days Data value should be greater than zero!");
                } else if (Number(fetch_days_data) % 1 != 0) {
                    frappe.query_report_filters_by_name.fetch_days_data.set_input("");
                    frappe.throw(" Fetch Days Data value should be integer!");
                }
                var date1 = new Date(from_date);
                var date2 = new Date(to_date);
                var diffDays = parseInt((date2 - date1) / (1000 * 60 * 60 * 24));
<<<<<<< HEAD
              //  console.log("diffDays------" + diffDays);
=======
                console.log("diffDays------" + diffDays);
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                if (fetch_days_data > diffDays) {
                    frappe.query_report_filters_by_name.fetch_days_data.set_input("");
                    frappe.throw(" Fetch Days Data value should be less than: " + (diffDays + 1));
                }else{
			var temp_from_date = from_date;
                        temp_from_date_filter.df.options = temp_from_date;
                        temp_from_date_filter.df.default = temp_from_date;
                        temp_from_date_filter.refresh();
                        temp_from_date_filter.set_input(temp_from_date_filter.df.default);

			var temp_to_date = frappe.datetime.add_days(from_date, (fetch_days_data - 1));
                        temp_to_date_filter.df.default = temp_to_date;
                        temp_to_date_filter.refresh();
                        temp_to_date_filter.set_input(temp_to_date_filter.df.default);

<<<<<<< HEAD
			//console.log("temp_from_date in --fetch_days_data----" + frappe.query_report_filters_by_name.temp_from_date.get_value());
                      //  console.log("temp_to_date--in---fetch_days_data----" + frappe.query_report_filters_by_name.temp_to_date.get_value());
=======
			console.log("temp_from_date in --fetch_days_data----" + frappe.query_report_filters_by_name.temp_from_date.get_value());
                        console.log("temp_to_date--in---fetch_days_data----" + frappe.query_report_filters_by_name.temp_to_date.get_value());
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
		}
                query_report.refresh();
            }
        },
        {
            "fieldname": "type_of_business",
            "label": __("Type of Business"),
            "fieldtype": "Select",
            "reqd": 1,
            "options": ["B2B", "B2C Large", "B2C Small", "CDNR", "EXPORT"],
            "default": "B2B"
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "reqd": 1,
            "options": ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ],
            "default": currentMonth
        },
        {
            "fieldname": "temp_from_date",
            "label": __("Temp From Date"),
            "fieldtype": "Date",
            "hidden": 1
        },
        {
            "fieldname": "temp_to_date",
            "label": __("Temp TO Date"),
            "fieldtype": "Date",
            "hidden": 1
        }
    ],
    onload: function(report) {
<<<<<<< HEAD
      //  console.log("onload.............");
=======
        console.log("onload.............");
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
        report.page.add_inner_button(__("Previous"),
            function() {
                var filters = report.get_values();
                var from_date = filters.from_date;
                var to_date = filters.to_date;
                var temp_from_date = filters.temp_from_date;
                var temp_to_date = filters.temp_to_date;

                var temp_from_date_filter = frappe.query_report_filters_by_name.temp_from_date;
                var temp_to_date_filter = frappe.query_report_filters_by_name.temp_to_date;
                var fetch_days_data = frappe.query_report_filters_by_name.fetch_days_data.get_value();

                if (fetch_days_data != "" && fetch_days_data != null) {

                    if (temp_from_date == "" || temp_from_date == null) {
                        var temp_from_date = frappe.datetime.add_days(to_date, -(fetch_days_data));
                        temp_from_date_filter.df.options = temp_from_date;
                        temp_from_date_filter.df.default = temp_from_date;
                        temp_from_date_filter.refresh();
                        temp_from_date_filter.set_input(temp_from_date_filter.df.default);

                        temp_to_date_filter.df.options = to_date;
                        temp_to_date_filter.df.default = to_date;
                        temp_to_date_filter.refresh();
                        temp_to_date_filter.set_input(temp_to_date_filter.df.default);

                        report.refresh();
                    } else {
<<<<<<< HEAD
                    //    console.log("Previous-primary-temp_from_date---------" + temp_from_date);
=======
                        console.log("Previous-primary-temp_from_date---------" + temp_from_date);
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                        var to_date = temp_from_date;
                        var temp_from_date = frappe.datetime.add_days(temp_from_date, -(fetch_days_data));
                        temp_from_date_filter.df.options = temp_from_date;
                        temp_from_date_filter.df.default = temp_from_date;
                        temp_from_date_filter.refresh();
                        temp_from_date_filter.set_input(temp_from_date_filter.df.default);

                        var temp_to_date = frappe.datetime.add_days(to_date, -1);
                        temp_to_date_filter.df.options = temp_to_date;
                        temp_to_date_filter.df.default = temp_to_date;
                        temp_to_date_filter.refresh();
                        temp_to_date_filter.set_input(temp_to_date_filter.df.default);

<<<<<<< HEAD
                        //console.log("temp_from_date---------" + temp_from_date);
                        //console.log("temp_to_date---------" + temp_to_date);
=======
                        console.log("temp_from_date---------" + temp_from_date);
                        console.log("temp_to_date---------" + temp_to_date);
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                        report.refresh();
                    }
                }else{
			frappe.throw(" Fetch Days Data value should be required..!");
		    } //end of final if..
                report.refresh();
            });
        report.page.add_inner_button(__("Next"),
            function() {
                var filters = report.get_values();
                var from_date = filters.from_date;
                var to_date = filters.to_date;
                var temp_from_date = filters.temp_from_date;
                var temp_to_date = filters.temp_to_date;
                var temp_from_date_filter = frappe.query_report_filters_by_name.temp_from_date;
                var temp_to_date_filter = frappe.query_report_filters_by_name.temp_to_date;
                var fetch_days_data = frappe.query_report_filters_by_name.fetch_days_data.get_value();
                if (fetch_days_data != "" && fetch_days_data != null) {
                    if (temp_from_date == "" || temp_from_date == null) {
                        var temp_from_date = frappe.datetime.add_days(from_date, fetch_days_data);
                        var temp_to_date = frappe.datetime.add_days(temp_from_date, (fetch_days_data - 1));
                        if (temp_to_date < to_date) {
                            temp_from_date_filter.df.options = temp_from_date;
                            temp_from_date_filter.df.default = temp_from_date;
                            temp_from_date_filter.refresh();
                            temp_from_date_filter.set_input(temp_from_date_filter.df.default);

                            temp_to_date_filter.df.options = temp_to_date;
                            temp_to_date_filter.df.default = temp_to_date;
                            temp_to_date_filter.refresh();
                            temp_to_date_filter.set_input(temp_to_date_filter.df.default);
                            report.refresh();
                        } else {
                            console.log("fail.....");
                            report.refresh();
                        }
<<<<<<< HEAD
                        //console.log("Next-temp_from_date---------" + temp_from_date);
                        //console.log("Next-temp_to_date---------" + temp_to_date);
                        report.refresh();
                    } else {

                        //console.log("Next--primary-temp_from_date---------" + temp_from_date);
                      //  console.log("Next--primary-typeof temp_to_date---------" + typeof temp_from_date);
                      //  console.log("Next--primary-temp_to_date---------" + temp_to_date);
                        //console.log("Next--to_date---------" + to_date);
=======
                        console.log("Next-temp_from_date---------" + temp_from_date);
                        console.log("Next-temp_to_date---------" + temp_to_date);
                        report.refresh();
                    } else {

                        console.log("Next--primary-temp_from_date---------" + temp_from_date);
                        console.log("Next--primary-typeof temp_to_date---------" + typeof temp_from_date);
                        console.log("Next--primary-temp_to_date---------" + temp_to_date);
                        console.log("Next--to_date---------" + to_date);
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                        if (temp_to_date < to_date) {
                            var date1 = new Date(temp_to_date);
                            var date2 = new Date(to_date);
                            var diffDays = parseInt((date2 - date1) / (1000 * 60 * 60 * 24));
<<<<<<< HEAD
                            //console.log("diffDays---------" + diffDays);
=======
                            console.log("diffDays---------" + diffDays);
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d

                            if (diffDays > (fetch_days_data - 1)) {
                                temp_from_date = frappe.datetime.add_days(temp_from_date, fetch_days_data);
                                temp_to_date = frappe.datetime.add_days(temp_from_date, (fetch_days_data - 1));
                            } else {
                                temp_from_date = frappe.datetime.add_days(temp_from_date, fetch_days_data);
                                temp_to_date = frappe.datetime.add_days(temp_from_date, (diffDays - 1));
                            }

                            temp_from_date_filter.df.options = temp_from_date;
                            temp_from_date_filter.df.default = temp_from_date;
                            temp_from_date_filter.refresh();
                            temp_from_date_filter.set_input(temp_from_date_filter.df.default);

                            temp_to_date_filter.df.options = temp_to_date;
                            temp_to_date_filter.df.default = temp_to_date;
                            temp_to_date_filter.refresh();
                            temp_to_date_filter.set_input(temp_to_date_filter.df.default);
                            report.refresh();
                        }
<<<<<<< HEAD
                        //console.log("Next-temp_from_date-----else----" + temp_from_date);
                        //console.log("Next-temp_to_date-----else----" + temp_to_date);
=======
                        console.log("Next-temp_from_date-----else----" + temp_from_date);
                        console.log("Next-temp_to_date-----else----" + temp_to_date);
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                        report.refresh();
                    }
                    report.refresh();
                }else{
			frappe.throw(" Fetch Days Data value should be required..!");
<<<<<<< HEAD
		    }
            });
	report.page.add_inner_button(__("Fetch All"),
            function() {

		//console.log("Fetch All entered.............!");
=======
		    } 
            });
	report.page.add_inner_button(__("Fetch All"),
            function() {
               
		console.log("Fetch All entered.............!");
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
		var temp_from_date_filter = frappe.query_report_filters_by_name.temp_from_date;
                var temp_to_date_filter = frappe.query_report_filters_by_name.temp_to_date;
		/**
                temp_from_date_filter.df.default = "";
                temp_from_date_filter.refresh();
                temp_from_date_filter.set_input(temp_from_date_filter.df.default);
<<<<<<< HEAD

=======
		
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d

                temp_to_date_filter.df.default = "";
                temp_to_date_filter.refresh();
                temp_to_date_filter.set_input(temp_to_date_filter.df.default);**/

		frappe.query_report_filters_by_name.temp_from_date.set_input("");
		frappe.query_report_filters_by_name.temp_to_date.set_input("");
		frappe.query_report_filters_by_name.fetch_days_data.set_input("");
<<<<<<< HEAD
		//console.log("Fetch All entered......temp_from_date.......!"+ frappe.query_report_filters_by_name.temp_from_date.get_value());
		//console.log("Fetch All entered........temp_to_date.....!"+ frappe.query_report_filters_by_name.temp_to_date.get_value());
=======
		console.log("Fetch All entered......temp_from_date.......!"+ frappe.query_report_filters_by_name.temp_from_date.get_value());
		console.log("Fetch All entered........temp_to_date.....!"+ frappe.query_report_filters_by_name.temp_to_date.get_value());
>>>>>>> 2694da8b27676ae0b56f81eb413bc858cce8bf3d
                report.refresh();
            });

    }, //end of onload..
    isNumeric: function(obj) {
        return !jQuery.isArray(obj) && (obj - parseFloat(obj) + 1) >= 0;
    }
}
