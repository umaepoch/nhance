// Copyright (c) 2016, Epoch and contributors
// For license information, please see license.txt
/* eslint-disable */
var docIdss = "";
var doctype = "";
frappe.query_reports["Document Review Template"] = {
    "filters": [{
            "fieldname": "document_type",
            "label": __("Doument Type"),
            "fieldtype": "Select",
            "options": ["Sales Order", "Purchase Order", "Purchase Receipt"],
            "reqd": 1,
            "on_change": function(query_report) {
                frappe.query_report.refresh();
                frappe.query_report.set_filter_value("docIds", []);
                console.log("on_change....of for");
                frappe.query_reports["Document Review Template"].filters[1].options = "";
                frappe.query_reports["Document Review Template"].filters[1].refresh;
                frappe.query_report.refresh();

                var docName = frappe.query_report.get_filter_value("document_type");
                var docIds_filter = frappe.query_report.get_filter_value("docIds");

                frappe.query_reports["Document Review Template"].filters[1].options = docName;
                console.log("on_change....of for docName" + docName);
                frappe.query_report.refresh();
            } //end of on_change function..
        },
        {
            "fieldname": "docIds",
            "label": __("Doc Ids"),
            "fieldtype": "Link"
        },
        {
            "fieldname": "required_for_review",
            "label": __("Required for Review"),
            "fieldtype": "Select",
            "options": ["Yes", "No"],
            "default": "No",
            "on_change": function(query_report) {
                frappe.query_report.refresh();
                frappe.query_reports["Document Review Template"].filters[1].refresh;
                console.log("-----------" + frappe.query_reports["Document Review Template"].filters[2].options);
                var docName = frappe.query_report.get_filter_value("required_for_review");
                if (docName == "No") {
                    console.log("selected No options");
                    frappe.query_reports["Document Review Template"].filters[3].options = "";
                    frappe.query_reports["Document Review Template"].filters[3].refresh;
                    frappe.query_reports["Document Review Template"].filters[4].refresh;
                    // frappe.query_reports["Document Review Template"].filters[4].options = "";
                    frappe.query_reports["Document Review Template"].filters[4].read_only = 1;

                } else {
                    frappe.query_reports["Document Review Template"].filters[3].options = "Sales Invoice";
                    frappe.query_reports["Document Review Template"].filters[3].refresh;
                    frappe.query_reports["Document Review Template"].filters[4].refresh;
                    var list = ["Information/Read Only", "Accept/Reject/Enter New Value"];


                }
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "reviewed_by",
            "label": __(" Reviewed By"),
            "fieldtype": "Link"

        },
        {
            "fieldname": "review_outcome",
            "label": __("Review Outcome"),
            "fieldtype": "Select",
            "options": ["Information/Read Only", "Accept/Reject/Enter New Value"],
            "default": "Information/Read Only",
            "on_change": function(query_report) {
                var required_for_review = frappe.query_report.get_filter_value("required_for_review");
                var docName = frappe.query_report.get_filter_value("review_outcome");
                docIdss = frappe.query_report.get_filter_value("docIds");
                doctype = frappe.query_report.get_filter_value("document_type");
                var date = function_for_date(doctype, docIdss);
                var delivery_date = JSON.stringify(date);
                console.log("date-------" + delivery_date);
                //var date1 =date.toDateString("dd-mm-yyyy");
                //console.log(date1);
                if (docName == "Accept/Reject/Enter New Value" && required_for_review == "Yes") {
                    var d = new frappe.ui.Dialog({
                        'fields': [{
                                "fieldtype": "Button",
                                "label": "Accept",
                                "fieldname": "butn"
                            },
                            {
                                "fieldtype": "Column Break",
                                "fieldname": "column_break1"
                            },
                            {
                                "fieldtype": "Button",
                                "label": "Reject",
                                "fieldname": "butn1"
                            },
                            {
                                "fieldtype": "Column Break",
                                "fieldname": "column_break2"
                            },
                            {
                                "fieldtype": "Button",
                                "label": "Enter New Value",
                                "fieldname": "butn2"
                            },
                            {
                                "fieldname": "sb_14",
                                "fieldtype": "Section Break",
                            },
                            {
                                "fieldtype": "Date",
                                "label": "Enter Date",
                                "fieldname": "date",
                                'default': delivery_date
                            },
                        ],

                    });
                    d.fields_dict.butn.$wrapper.on('click', function() {
                       // var date = $("input[data-fieldname='date']").val();
                        show_alert("clicked");
                        //selectStudentIdFromStudentDocType(batch_name);
                        d.hide();
                    });
                    d.fields_dict.butn1.$wrapper.on('click', function() {
                        show_alert('hello2');
                        console.log("doc ids--------" + docIdss);
                        function_doctype(doctype, docIdss);
                        d.hide();
                    });
                    //  d.fields_dict.butn2.$wrapper.on('click', function() {
                    //   show_alert('hello3');
                    d.fields_dict.butn2.input.onclick = function() {
                        var input_date = "";
			console.log("before get date-----"+input_date);
                        input_date = $("input[data-fieldname='date']").val();
			console.log("after get date------"+input_date);
                        var newdate = input_date.split("-").reverse().join("-");
                        show_alert(newdate);
                        var new_id =  function_doctype_cancell_amended(doctype, docIdss, newdate);
			show_alert(new_id);
			frappe.query_report.refresh();
			frappe.query_report.set_filter_value("docIds", "");
			frappe.query_report.set_filter_value("docIds", new_id);
			frappe.query_report.refresh();
			
			d.hide();
			
                       
                    }

                    //  });
                    d.show();
                } else {
                    show_alert("information of document");
                }
            }
        },
        {
            "fieldname": "details",
            "label": __("Doctype Details"),
            "fieldtype": "Select",
            "options": ["Parent", "Items", "Taxes and Charges"],
            "default": "Parent"
        }
    ]
}

function function_doctype(doctype, docIdss) {
    var expense_account = "";
    frappe.call({
        method: "nhance.nhance.report.document_review_template.document_review_template.cancel_doc",
        args: {
            "doctype": doctype,
            "docIdss": docIdss
        },
        async: false,

        callback: function(r) {
            console.log("r.message ------" + JSON.stringify(r.message));

        }
    });

}

function function_doctype_cancell_amended(doctype, docIdss, newdate) {
    var new_doctype = [];
    frappe.call({
        method: "nhance.nhance.report.document_review_template.document_review_template.cancel_and_amend_doc",
        args: {
            "doctype": doctype,
            "docIdss": docIdss,
            "newdate": newdate
        },
        async: false,

        callback: function(r) {
            console.log("r.message ------" + JSON.stringify(r.message));
	   new_doctype = r.message;
        }
    });
	return new_doctype
}

function function_for_date(doctype, docIdss) {
    var expense_account = "";
    frappe.call({
        method: "nhance.nhance.report.document_review_template.document_review_template.date_details",
        args: {
            "doctype": doctype,
            "docIdss": docIdss
        },
        async: false,

        callback: function(r) {
            console.log("r.message ------" + JSON.stringify(r.message));
            expense_account = r.message;
            console.log("expense_account---------" + expense_account);

        }
    });
    return expense_account;
}

