// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Label Generation For Purchase Receipt Items"] = {
	"filters": [{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1
        },{
            "fieldname": "purchase_receipt",
            "label": __("Purchase Receipt"),
            "fieldtype": "Link",
            "options": "Purchase Receipt"
        },
	{
            "fieldname": "date_of_creation",
            "label": __("Creation Date"),
            "fieldtype": "Date"
        },
	{
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item"
        }],
    onload: function(report) {
        console.log("onload.............");
        console.log("Make Label...");
        report.page.add_inner_button(__("Make Label"),
            function() {
                var reporter = frappe.query_reports["Label Generation For Purchase Receipt Items"];
                reporter.make_label(report);
            });
    },
    make_label: function(report) {
        makeLabel(report);
    }
}


function makeLabel(report) {
    console.log("Make Label...Entered");
    var label_flag = false;
    var d = new frappe.ui.Dialog({
        title: __("Select The Printer!"),
        'fields': [{
            "fieldname": 'label_printer',
            "fieldtype": 'Link',
            "options": "Label Printer",
            "reqd": 1,
            "onchange": function(e) {
                console.log(" label_flag-----" + label_flag);
                if (label_flag == false) {
                    if (this.value != "Citizen" && this.value != "") {
                        label_flag = true;
                        frappe.throw("Sorry!! This printer not available!");
                    }
                } else {
                    label_flag = false;
                }
            }
        }],
        primary_action: function() {
            d.hide();
            var label = d.get_values();
            console.log(" label_printer-----" + label.label_printer);
            display_dialog_box_for_ncopies(label.label_printer);
        }
    });
    d.show();
} //end of makeLabel..

function display_dialog_box_for_ncopies(label){
var d = new frappe.ui.Dialog({
	title: __("Please Submit how many copies you want!"),
    'fields': [
        {
                'fieldname': 'ncopies',
                'fieldtype': 'Data',
                "label": 'Enter Copies',
                "reqd": 1,
                "onchange": function(e) {
                    console.log(" ncopies-----" + this.value);
                    var ncopies = Number(this.value);
                    if (ncopies % 1 != 0) {
                        frappe.throw(" The Entered Copies value should be integer!");
                    } else if (ncopies < 0) {
                        frappe.throw(" The Entered Copies value should be positive!");
                    } else if (ncopies == 0) {
                        frappe.throw(" The Entered Copies value should be greater than zero!");
                    }
                }
            }
    ],
    primary_action: function(){
        d.hide();
	var label_input = d.get_values();
	console.log(" ncopies-----"+label_input.ncopies);
	console.log(" label-----"+label);
	make_prn_file(label_input.ncopies,label);
    }
});
d.show();
} 

function make_prn_file(ncopies,label){
frappe.call({
            method: "nhance.nhance.report.label_generation_for_purchase_receipt_items.label_generation_for_purchase_receipt_items.make_prnfile",
            args: {
		"ncopies": ncopies,
		"label": label
            },
            async: false,
            callback: function(r) {}
        });
}

