// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Label Generation For Master Items"] = {
    "filters": [{
        "fieldname": "item_group",
        "label": __("Item Group"),
        "fieldtype": "Link",
        "options": "Item Group"
    }, {
        "fieldname": "item_name",
        "label": __("Item Name"),
        "fieldtype": "Data"
    }],
    onload: function(report) {
        console.log("onload.............");
        console.log("Make Label...");
        report.page.add_inner_button(__("Make Label"),
            function() {
                var reporter = frappe.query_reports["Label Generation For Master Items"];
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

function display_dialog_box_for_ncopies(label) {
    var d = new frappe.ui.Dialog({
        title: __("Please Submit below required fields!"),
        'fields': [{
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
            },
            {
                'fieldname': 'date_of_import',
                'fieldtype': 'Date',
                "label": 'Month & Year of Import',
                'reqd': 1
            }
        ],
        primary_action: function() {
            d.hide();
            var label_input = d.get_values();
            console.log(" ncopies-----" + label_input.ncopies);
            console.log(" date_of_import-----" + label_input.date_of_import);
            console.log(" label-----" + label);
            make_prn_file(label_input.ncopies, label, label_input.date_of_import);
        }
    });
    d.show();
}

function make_prn_file(ncopies, label, date_of_import) {
    frappe.call({
        method: "nhance.nhance.report.label_generation_for_master_items.label_generation_for_master_items.make_prnfile",
        args: {
            "ncopies": ncopies,
            "label": label,
            "date_of_import": date_of_import
        },
        async: false,
        callback: function(r) {}
    });
}
