// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Po Approval Sheet"] = {
    "filters": [{
            "fieldname": "date",
            "label": __("Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.nowdate(),
            "width": "60px"
        },
        {
            "label": __("Workflow Status"),
            "fieldname": "workflow_status",
            "fieldtype": "Select",
            "reqd":1,
            "options": ["",
                "Ready for Approval",
                "Approved By GM",
                "Being Modified",
                "Approved",
                "Rejected",
                "Cancelled"
            ],

        },

        {
            "label": __("PO Status"),
            "fieldname": "po_status",
            "fieldtype": "Select",
            "options": ["", "Draft",
                "To Bill",
                "To Receive",
                "To Receive and Bill",
                "Closed",
                "Completed",
                "Cancelled"
            ],

        },


    ],
    
    onload: function(report) {
        let doc = frappe.query_report.report_name;
        console.log("doc----",doc)
        var date = frappe.query_report.get_filter_value('date');
        console.log("date----",date)
        var workflow_status = frappe.query_report.get_filter_value('workflow_status');
        console.log("workflow_status----",workflow_status)
        /*
        report.page.add_action_item(__("Ready for Approval"), function() {

            let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
            let checked_rows = checked_rows_indexes.map(i => report.data[i]);
            console.log("checked_rows", checked_rows)
            for (var i = 0; i < checked_rows.length; ++i) {
                console.log("po number", checked_rows[i].po_number);
                var po_number = checked_rows[i].po_number;
                console.log(typeof po_number)

                if (po_number !== "") {
                    console.log("entered in if block")
                    ready_for_approval_po_number(po_number)
                    


                }
            }

        });

*/
        report.page.add_action_item(__("Approve"), function() {

            let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
            let checked_rows = checked_rows_indexes.map(i => report.data[i]);
            console.log("checked_rows", checked_rows)
            for (var i = 0; i < checked_rows.length; ++i) {
                console.log("po number", checked_rows[i].po_number);
                var po_number = checked_rows[i].po_number;
                console.log(typeof po_number)
                var doc=""
                if (po_number !== "") {
                    console.log("entered in if block")
                    
                   approve_po_number(po_number)


                }
            }

        });
        /*
        report.page.add_action_item(__("Reject"), function() {
            //frappe.msgprint("Approved");
            let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
            let checked_rows = checked_rows_indexes.map(i => report.data[i]);
            console.log("checked_rows", checked_rows)
            for (var i = 0; i < checked_rows.length; ++i) {
                console.log("po number", checked_rows[i].po_number);
                var po_number = checked_rows[i].po_number;
                console.log(typeof po_number)
                if (po_number !== "") {
                    console.log("entered in if block")
                    reject_po_number(po_number)
                }
            }
        });
        */
        report.page.add_action_item(__("Rework"), function() {
            let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
            let checked_rows = checked_rows_indexes.map(i => report.data[i]);
            console.log("checked_rows", checked_rows)
            for (var i = 0; i < checked_rows.length; ++i) {
                console.log("po number", checked_rows[i].po_number);
                var po_number = checked_rows[i].po_number;
                console.log(typeof po_number)
                if (po_number !== "") {
                    console.log("entered in if block")
                    rework_po_number(po_number)
                }
            }
        });
        
        report.page.add_action_item(__("Cancel"), function() {
            let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
            let checked_rows = checked_rows_indexes.map(i => report.data[i]);
            console.log("checked_rows", checked_rows)
            for (var i = 0; i < checked_rows.length; ++i) {
                console.log("po number", checked_rows[i].po_number);
                var po_number = checked_rows[i].po_number;
                console.log(typeof po_number)
                if (po_number !== "") {
                    console.log("entered in if block")
                    cancel_po_number(po_number)
                }
            }
        });
        

    },
    get_datatable_options(options) {
        return Object.assign(options, {
            checkboxColumn: true
        });
    },

};


function ready_for_approval_po_number(po_number) {
    frappe.call({
        method: 'shark.shark.report.po_approval_sheet.po_approval_sheet.ready_for_approval_po',
        args: {
            "po_number": po_number,
        },
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}

function approve_po_number(po_number) {
    console.log("---------------")
    frappe.call({
        method: 'shark.shark.report.po_approval_sheet.po_approval_sheet.approve_po',
        args: {
            "po_number": po_number,
        },
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}

function reject_po_number(po_number) {
    frappe.call({
        method: 'shark.shark.report.po_approval_sheet.po_approval_sheet.reject_po',
        args: {
            "po_number": po_number,
        },
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}

function rework_po_number(po_number) {
    frappe.call({
        method: 'shark.shark.report.po_approval_sheet.po_approval_sheet.rework_po',
        args: {
            "po_number": po_number,
        },
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}

function cancel_po_number(po_number) {
    frappe.call({
        method: 'shark.shark.report.po_approval_sheet.po_approval_sheet.cancel_po',
        args: {
            "po_number": po_number,
        },
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}