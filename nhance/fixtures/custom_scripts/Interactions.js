frappe.ui.form.on("Interactions", {
    document_id: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        console.log("items.....", +JSON.stringify(d));
        var document_id = d.document_id;
        console.log("document_id.....", document_id);
        var document_type = d.document_type;
        console.log("document_type.....", document_type);

        var customerName = fetch_customer_name(document_id);
        console.log("customerName", customerName);

	var customerNamequotation = fetch_customer_name_quotation(document_id);
        console.log("customerNamequotation", customerNamequotation);

        var status_of_lead = fetch_status(document_id);
        console.log("status_of_lead", status_of_lead);

        var LeadName = fetch_name_of_lead(document_id);
        console.log("LeadName", LeadName);

        var customer_name_sales_order = fetch_customer_name_sales_order(document_id);
        console.log("customer_name_sales_order", customer_name_sales_order);

        var sales_invoice_customer_name = fetch_customer_name_sales_invoice(document_id);
        console.log("sales_invoice_customer_name", sales_invoice_customer_name);

        if (status_of_lead == "Converted" && document_type == "Lead") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);
            cur_frm.set_df_property("customer", "hidden", false);
            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['lead_name', '=', document_id]
                    ]
                }
            }

        }

        if (document_type == "Opportunity") {

            var status_of_lead_from_opportunity = fetch_status_of_lead_from_opportunity(document_id);
            console.log("status_of_lead_from_opportunity", status_of_lead_from_opportunity);


            var party_name = fetch_party_name_from_opportunity(document_id);
            console.log("party_name", party_name);

            if (status_of_lead_from_opportunity == "Lead") {
                var status = fetch_status_of_lead_from_opportunity_party_name(party_name);
                console.log("status", status);

		var lead_name = fetch_lead_name(party_name);
                console.log("lead_name", lead_name);

                if (status != "Converted") {
                    
		    frappe.model.set_value(cdt, cdn, "customer_or_lead", lead_name);
            cur_frm.set_df_property("customer", "hidden", true);

            var link_doctype = "Lead";
            console.log("link_doctype", link_doctype);
	

            var link_name = fetch_party_name_from_opportunity(document_id);
            console.log("link_name", link_name);

            var parenttypecontact = "Contact";
            console.log("parenttypecontact", parenttypecontact);

            var parenttypeaddress = "Address";
            console.log("parenttypeaddress", parenttypeaddress);

            //var customerName = fetch_customer_name(document_id);
           // console.log("customerName", customerName);

            var dynamic_parent_contact = [];
            dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
            console.log("dynamic_parent_contact", dynamic_parent_contact);

            var dynamic_parent_address = [];
            dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
            console.log("dynamic_parent_address", dynamic_parent_address);



            cur_frm.fields_dict.contact.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_contact],


                        ]
                    }
                },

                cur_frm.fields_dict.address.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_address],


                        ]
                    }
                }




                } //end of if status
                else if (status == "Converted") {
                    cur_frm.set_df_property("customer_or_lead", "hidden", true);


                } //end of if status
            } //end of if opportuniy from
            else {
                cur_frm.set_df_property("customer_or_lead", "hidden", true);

            }

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', customerName]
                    ]
                }
            }


        }

	if (document_type == "Quotation") {
            var status_of_lead_from_opportunity = fetch_status_of_lead_from_quotation(document_id);
            console.log("status_of_lead_from_opportunity", status_of_lead_from_opportunity);


            var party_name = fetch_party_name_from_quotation(document_id);
            console.log("party_name", party_name);

            if (status_of_lead_from_opportunity == "Lead") {
                var status = fetch_status_of_lead_from_opportunity_party_name(party_name);
                console.log("status", status);

		var lead_name = fetch_lead_name(party_name);
                console.log("lead_name", lead_name);

                if (status != "Converted") {
                    
		    frappe.model.set_value(cdt, cdn, "customer_or_lead", lead_name);
            cur_frm.set_df_property("customer", "hidden", true);

            var link_doctype = "Lead";
            console.log("link_doctype", link_doctype);
	

            var link_name = fetch_party_name_from_quotation(document_id);
            console.log("link_name", link_name);

            var parenttypecontact = "Contact";
            console.log("parenttypecontact", parenttypecontact);

            var parenttypeaddress = "Address";
            console.log("parenttypeaddress", parenttypeaddress);

            //var customerName = fetch_customer_name_quotation(document_id);
            //console.log("customerName", customerName);

            var dynamic_parent_contact = [];
            dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
            console.log("dynamic_parent_contact", dynamic_parent_contact);

            var dynamic_parent_address = [];
            dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
            console.log("dynamic_parent_address", dynamic_parent_address);



            cur_frm.fields_dict.contact.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_contact],


                        ]
                    }
                },

                cur_frm.fields_dict.address.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_address],


                        ]
                    }
                }




                } //end of if status
                else if (status == "Converted") {
                    cur_frm.set_df_property("customer_or_lead", "hidden", true);


                } //end of if status
            } //end of if opportuniy from
            else {
                cur_frm.set_df_property("customer_or_lead", "hidden", true);

            }

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', customerNamequotation]
                    ]
                }
            }



        }

        if (document_type == "Sales Order") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', customer_name_sales_order]
                    ]
                }
            }


        }

        if (document_type == "Customer") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', document_id]
                    ]
                }
            }


        }

        if (document_type == "Sales Invoice") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', sales_invoice_customer_name]
                    ]
                }
            }


        }


        if (status_of_lead != "Converted" && document_type == "Lead") {
            frappe.model.set_value(cdt, cdn, "customer_or_lead", LeadName);
            cur_frm.set_df_property("customer", "hidden", true);

            var link_doctype = "Lead";
            console.log("link_doctype", link_doctype);

            var link_name = d.document_id;
            console.log("link_name", link_name);

            var parenttypecontact = "Contact";
            console.log("parenttypecontact", parenttypecontact);

            var parenttypeaddress = "Address";
            console.log("parenttypeaddress", parenttypeaddress);

            //var customerName = fetch_customer_name(document_id);
            //console.log("customerName", customerName);

            var dynamic_parent_contact = [];
            dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
            console.log("dynamic_parent_contact", dynamic_parent_contact);

            var dynamic_parent_address = [];
            dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
            console.log("dynamic_parent_address", dynamic_parent_address);



            cur_frm.fields_dict.contact.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_contact],


                        ]
                    }
                },

                cur_frm.fields_dict.address.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_address],


                        ]
                    }
                }




        }


    }

});

frappe.ui.form.on("Interactions", {
    customer: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        console.log("items.....", +JSON.stringify(d));
        var document_id = d.document_id;
        console.log("document_id.....", document_id);
        var document_type = d.document_type;
        console.log("document_type.....", document_type);
        var customer = d.customer;
        console.log("customer", customer);
        var link_doctype = "Customer";
        console.log("link_doctype", link_doctype);

        var link_name = d.customer;
        console.log("link_name", link_name);

        var parenttypecontact = "Contact";
        console.log("parenttypecontact", parenttypecontact);

        var parenttypeaddress = "Address";
        console.log("parenttypeaddress", parenttypeaddress);

        //var customerName = fetch_customer_name(document_id);
        //console.log("customerName", customerName);

        var dynamic_parent_contact = [];
        dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
        console.log("dynamic_parent_contact", dynamic_parent_contact);

        var dynamic_parent_address = [];
        dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
        console.log("dynamic_parent_address", dynamic_parent_address);




        cur_frm.fields_dict.contact.get_query = function(d) {
                return {
                    filters: [
                        ['name', 'In', dynamic_parent_contact],


                    ]
                }
            },

            cur_frm.fields_dict.address.get_query = function(d) {
                return {
                    filters: [
                        ['name', 'In', dynamic_parent_address],


                    ]
                }
            }
    }
});

function fetch_customer_name(document_id) {
    console.log("entered into function");
    var customer_name = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Opportunity',
            'fieldname': 'customer_name',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                customer_name = r.message.customer_name;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return customer_name
}

function fetch_customer_name_quotation(document_id) {
    console.log("entered into function");
    var customer_name = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Quotation',
            'fieldname': 'customer_name',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                customer_name = r.message.customer_name;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return customer_name
}

function fetch_status(document_id) {
    console.log("entered into function");
    var status = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Lead',
            'fieldname': 'status',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                status = r.message.status;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return status
}

function fetch_lead_name(party_name) {
    console.log("entered into function");
    var lead_name = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Lead',
            'fieldname': 'lead_name',

            'filters': {
                name: party_name,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                lead_name = r.message.lead_name;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return lead_name
}

function fetch_status_of_lead_from_opportunity(document_id) {
    console.log("entered into function");
    var opportunity_from = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Opportunity',
            'fieldname': 'opportunity_from',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                opportunity_from = r.message.opportunity_from;


                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return opportunity_from
}

function fetch_status_of_lead_from_quotation(document_id) {
    console.log("entered into function");
    var quotation_from = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Quotation',
            'fieldname': 'quotation_to',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                quotation_from = r.message.quotation_to;


                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return quotation_from
}

function fetch_party_name_from_opportunity(document_id) {
    console.log("entered into function");
    var party_name = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Opportunity',
            'fieldname': 'party_name',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                party_name = r.message.party_name;


                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return party_name
}

function fetch_party_name_from_quotation(document_id) {
    console.log("entered into function");
    var party_name = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Quotation',
            'fieldname': 'party_name',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                party_name = r.message.party_name;


                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return party_name
}

function fetch_status_of_lead_from_opportunity_party_name(party_name) {
    console.log("entered into function");
    var status = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Lead',
            'fieldname': 'status',

            'filters': {
                name: party_name,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                status = r.message.status;

                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return status
}

function fetch_name_of_lead(document_id) {
    console.log("entered into function");
    var leadName = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Lead',
            'fieldname': 'lead_name',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                leadName = r.message.lead_name;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return leadName
}

function fetch_customer_name_sales_order(document_id) {
    console.log("entered into function");
    var customer = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Sales Order',
            'fieldname': 'customer',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                customer = r.message.customer;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return customer
}

function fetch_customer_name_sales_invoice(document_id) {
    console.log("entered into function");
    var customer = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Sales Invoice',
            'fieldname': 'customer',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                customer = r.message.customer;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return customer
}

function fetch_parent_name_dynamic_table_contact(link_doctype, link_name) {
    console.log("entered into function");
    var dynamic_parent = [];
    frappe.call({
        method: "nhance.api.get_parent_dynamic_value_contact",
        args: {

            "link_doctype": link_doctype,
            "link_name": link_name

        },
        async: false,
        callback: function(r) {
            if (r.message) {

                for (var i = 0; i < r.message.length; i++) {
                    dynamic_parent.push(r.message[i].parent);

                }

            }
        }
    });
    return dynamic_parent
}

function fetch_parent_name_dynamic_table_address(link_doctype, link_name) {
    console.log("entered into function");
    var dynamic_parent_address = [];
    frappe.call({
        method: "nhance.api.get_parent_dynamic_value_address",
        args: {

            "link_doctype": link_doctype,
            "link_name": link_name


        },
        async: false,
        callback: function(r) {
            if (r.message) {


                for (var i = 0; i < r.message.length; i++) {
                    dynamic_parent_address.push(r.message[i].parent);


                }

            }
        }
    });
    return dynamic_parent_address
}

frappe.ui.form.on("Interactions", {
	refresh:  function(frm, cdt, cdn)  {
	    console.log("-----------------------");
	     var d = locals[cdt][cdn];
	    var document_id = d.document_id;
        console.log("document_id.....", document_id);
        var document_type = d.document_type;
        console.log("document_type.....", document_type);
		var customer_name_sales_order = fetch_customer_name_sales_order(document_id);
        console.log("customer_name_sales_order", customer_name_sales_order);
        var sales_invoice_customer_name = fetch_customer_name_sales_invoice(document_id);
        console.log("sales_invoice_customer_name", sales_invoice_customer_name);
        var customerNamequotation = fetch_customer_name_quotation(document_id);
        console.log("customerNamequotation", customerNamequotation);
        var customerName = fetch_customer_name_opportunity(document_id);
        console.log("customerName", customerName);

          var customer = d.customer;
        console.log("customer", customer);
        
	if(customer!=undefined){

        var link_doctype = "Customer";
        console.log("link_doctype", link_doctype);

        var link_name = d.customer;
        console.log("link_name", link_name);

        var parenttypecontact = "Contact";
        console.log("parenttypecontact", parenttypecontact);

        var parenttypeaddress = "Address";
        console.log("parenttypeaddress", parenttypeaddress);

        var customerName = fetch_customer_name(document_id);
        console.log("customerName", customerName);

        var dynamic_parent_contact = [];
        dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
        console.log("dynamic_parent_contact", dynamic_parent_contact);

        var dynamic_parent_address = [];
        dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
        console.log("dynamic_parent_address", dynamic_parent_address);




        cur_frm.fields_dict.contact.get_query = function(d) {
                return {
                    filters: [
                        ['name', 'In', dynamic_parent_contact],


                    ]
                }
            },

            cur_frm.fields_dict.address.get_query = function(d) {
                return {
                    filters: [
                        ['name', 'In', dynamic_parent_address],


                    ]
                }
            }
        if (document_type == "Sales Order") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', customer_name_sales_order]
                    ]
                }
            }


        }
        if (document_type == "Sales Invoice") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', sales_invoice_customer_name]
                    ]
                }
            }


        }
        if (document_type == "Customer") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', document_id]
                    ]
                }
            }


        }
        if (document_type == "Quotation") {
            var status_of_lead_from_opportunity = fetch_status_of_lead_from_quotation(document_id);
            console.log("status_of_lead_from_opportunity", status_of_lead_from_opportunity);


            var party_name = fetch_party_name_from_quotation(document_id);
            console.log("party_name", party_name);

            if (status_of_lead_from_opportunity == "Lead") {
                var status = fetch_status_of_lead_from_opportunity_party_name(party_name);
                console.log("status", status);

		var lead_name = fetch_lead_name(party_name);
                console.log("lead_name", lead_name);

                if (status != "Converted") {
                    
		    frappe.model.set_value(cdt, cdn, "customer_or_lead", lead_name);
            cur_frm.set_df_property("customer", "hidden", true);

            var link_doctype = "Lead";
            console.log("link_doctype", link_doctype);
	

            var link_name = fetch_party_name_from_quotation(document_id);
            console.log("link_name", link_name);

            var parenttypecontact = "Contact";
            console.log("parenttypecontact", parenttypecontact);

            var parenttypeaddress = "Address";
            console.log("parenttypeaddress", parenttypeaddress);

            //var customerName = fetch_customer_name_quotation(document_id);
            //console.log("customerName", customerName);

            var dynamic_parent_contact = [];
            dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
            console.log("dynamic_parent_contact", dynamic_parent_contact);

            var dynamic_parent_address = [];
            dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
            console.log("dynamic_parent_address", dynamic_parent_address);



            cur_frm.fields_dict.contact.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_contact],


                        ]
                    }
                },

                cur_frm.fields_dict.address.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_address],


                        ]
                    }
                }




                } //end of if status
                else if (status == "Converted") {
                    cur_frm.set_df_property("customer_or_lead", "hidden", true);


                } //end of if status
            } //end of if opportuniy from
            else {
                cur_frm.set_df_property("customer_or_lead", "hidden", true);

            }

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', customerNamequotation]
                    ]
                }
            }



        }
        
        if (document_type == "Opportunity") {

            var status_of_lead_from_opportunity = fetch_status_of_lead_from_opportunity(document_id);
            console.log("status_of_lead_from_opportunity", status_of_lead_from_opportunity);


            var party_name = fetch_party_name_from_opportunity(document_id);
            console.log("party_name", party_name);

            if (status_of_lead_from_opportunity == "Lead") {
                var status = fetch_status_of_lead_from_opportunity_party_name(party_name);
                console.log("status", status);

		var lead_name = fetch_lead_name(party_name);
                console.log("lead_name", lead_name);

                if (status != "Converted") {
                    
		    frappe.model.set_value(cdt, cdn, "customer_or_lead", lead_name);
            cur_frm.set_df_property("customer", "hidden", true);

            var link_doctype = "Lead";
            console.log("link_doctype", link_doctype);
	

            var link_name = fetch_party_name_from_opportunity(document_id);
            console.log("link_name", link_name);

            var parenttypecontact = "Contact";
            console.log("parenttypecontact", parenttypecontact);

            var parenttypeaddress = "Address";
            console.log("parenttypeaddress", parenttypeaddress);

            

            var dynamic_parent_contact = [];
            dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
            console.log("dynamic_parent_contact", dynamic_parent_contact);

            var dynamic_parent_address = [];
            dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
            console.log("dynamic_parent_address", dynamic_parent_address);



            cur_frm.fields_dict.contact.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_contact],


                        ]
                    }
                },

                cur_frm.fields_dict.address.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_address],


                        ]
                    }
                }




                } //end of if status
                else if (status == "Converted") {
                    cur_frm.set_df_property("customer_or_lead", "hidden", true);


                } //end of if status
            } //end of if opportuniy from
            else {
                cur_frm.set_df_property("customer_or_lead", "hidden", true);

            }

            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['customer_name', '=', customerName]
                    ]
                }
            }


        }
        
if (document_type == "Lead") {
var status_of_lead = fetch_status(document_id);
        console.log("status_of_lead", status_of_lead);

        var LeadName = fetch_name_of_lead(document_id);
        console.log("LeadName", LeadName);


if (status_of_lead == "Converted" && document_type == "Lead") {
            cur_frm.set_df_property("customer_or_lead", "hidden", true);
            cur_frm.set_df_property("customer", "hidden", false);
            cur_frm.fields_dict.customer.get_query = function(d) {
                return {
                    filters: [
                        ['lead_name', 'In', document_id]
                    ]
                }
            }

        }

if (status_of_lead != "Converted" && document_type == "Lead") {
            frappe.model.set_value(cdt, cdn, "customer_or_lead", LeadName);
            cur_frm.set_df_property("customer", "hidden", true);

            var link_doctype = "Lead";
            console.log("link_doctype", link_doctype);

            var link_name = d.document_id;
            console.log("link_name", link_name);

            var parenttypecontact = "Contact";
            console.log("parenttypecontact", parenttypecontact);

            var parenttypeaddress = "Address";
            console.log("parenttypeaddress", parenttypeaddress);

            
            var dynamic_parent_contact = [];
            dynamic_parent_contact = fetch_parent_name_dynamic_table_contact(link_doctype, link_name);
            console.log("dynamic_parent_contact", dynamic_parent_contact);

            var dynamic_parent_address = [];
            dynamic_parent_address = fetch_parent_name_dynamic_table_address(link_doctype, link_name);
            console.log("dynamic_parent_address", dynamic_parent_address);



            cur_frm.fields_dict.contact.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_contact],


                        ]
                    }
                },

                cur_frm.fields_dict.address.get_query = function(d) {
                    return {
                        filters: [
                            ['name', 'In', dynamic_parent_address],


                        ]
                    }
                }




        }
}//end of outer if lead type


	}//end of if customer is undefined
}
});
function fetch_customer_name_sales_order(document_id) {
    console.log("entered into function");
    var customer = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Sales Order',
            'fieldname': 'customer',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                customer = r.message.customer;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return customer
}
function fetch_customer_name_opportunity(document_id) {
    console.log("entered into function");
    var customer_name = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Opportunity',
            'fieldname': 'customer_name',

            'filters': {
                name: document_id,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                customer_name = r.message.customer_name;
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return customer_name
}

