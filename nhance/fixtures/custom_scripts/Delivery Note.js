//revision_number

frappe.ui.form.on("Delivery Note Item", {


    batch_no: function(frm, cdt, cdn) {
        console.log("-----------");
        //cur_frm.refresh_field("items")
        var d = locals[cdt][cdn];
        var item_code = d.item_code;

        var batch_no = d.batch_no;
        var revision_no = d.revision_number;

        console.log("revision_no----------------" + revision_no);



        var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
        var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
        var HasRevisionNumber = null;
        HasRevisionNumber = fetch_has_revision_number(batch_no);
        console.log("HasRevisionNumber", HasRevisionNumber);

        if ((HasRevisionNumber != null || HasRevisionNumber != undefined || HasRevisionNumber != "") && HasBatchNumber == 1) {
            d.revision_number = HasRevisionNumber;
        }
        var df = frappe.meta.get_docfield("Delivery Note Item", "revision_number", cur_frm.doc.name);

        df.read_only = 1;
        cur_frm.refresh_field("items")
    }


})


frappe.ui.form.on("Delivery Note Item", {


   serial_no: function(frm, cdt, cdn) {
        console.log("-----------");
        //cur_frm.refresh_field("items")
        var d = locals[cdt][cdn];
        var item_code = d.item_code;

        var batch_no = d.batch_no;
        var revision_no = d.revision_number;

        console.log("revision_no----------------" + revision_no);

	var serial_no = d.serial_no;

        console.log("revision_no----------------" + revision_no);


        var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
        var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
        var HasRevisionNumberSerial = null;
        HasRevisionNumberSerial = fetch_has_revision_number_serial(serial_no) ;
        console.log("HasRevisionNumberSerial", HasRevisionNumberSerial);

        if ((HasRevisionNumberSerial != null || HasRevisionNumberSerial != undefined || HasRevisionNumberSerial != "") && HasSerialNumber == 1) {
            d.revision_number = HasRevisionNumberSerial;
        }
        var df = frappe.meta.get_docfield("Delivery Note Item", "revision_number", cur_frm.doc.name);

        df.read_only = 1;
        cur_frm.refresh_field("items")
}

})

 function fetch_has_serial_no(item_code) {
    console.log("entered into function");
    var has_serial_no = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Item',
            'fieldname': ["has_serial_no", "item_code"],

            'filters': {
                item_code: item_code,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                has_serial_no = r.message.has_serial_no;
                console.log(has_serial_no);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_serial_no
}


function fetch_has_batch_no(item_code) {
    console.log("entered into has_batch_no function");
    var has_batch_no = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Item',
            'fieldname': ["has_batch_no", "item_code"],

            'filters': {
                item_code: item_code,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                has_batch_no = r.message.has_batch_no;
                console.log(has_batch_no);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_batch_no
}

function fetch_has_revision_number(batch_no) {
    console.log("entered into fetch_has_revision_number function");
    var has_revision_number = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Batch',
            'fieldname': ["revision_number", "name"],

            'filters': {
                name: batch_no,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                has_revision_number = r.message.revision_number;
                console.log(has_revision_number);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_revision_number
}


function fetch_has_revision_number_serial(serial_no) {
    //console.log("entered into fetch_has_revision_number_serial function");
    var has_revision_number_serial = "";
    frappe.call({
           method: 'frappe.client.get_value',
         args: {
            'doctype': 'Serial No',
            'fieldname': ["revision_number", "serial_no"],

            'filters': {
                name: serial_no,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                has_revision_number_serial = r.message.revision_number;
                //console.log(has_revision_number_serial);
                //console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_revision_number_serial
}
frappe.ui.form.on("Delivery Note", "after_save", function(frm, cdt, cdn) {

    $.each(frm.doc.items, function(i, d) {
        var item_code = d.item_code;
        var revision_number = d.revision_number;
        console.log("revision_number", revision_number);
        if (revision_number != "") {
            var df = frappe.meta.get_docfield("Delivery Note Item", "revision_number", cur_frm.doc.name);

            df.read_only = 1;
        }
    })
});

//check item has batch or serial number
//To check item has serial or batch number
frappe.ui.form.on("Delivery Note", "after_save", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    //console.log("Entered------" + d);
    ////console.log(".........."+JSON.stringify(d));
    var purpose = frm.doc.purpose;
    //console.log("purpose...." + purpose);
    var items = frm.doc.items;
    // //console.log("items....."+JSON.stringify(items));
    for (var i = 0; i < items.length; i++) {
        var item_code = items[i]['item_code'];
        var source_warehouse = items[i]['s_warehouse'];
        //console.log("source_warehouse.." + source_warehouse);
        var target_warehouse = items[i]['t_warehouse'];
        //console.log("target_warehouse.." + target_warehouse);
        var serial_no = items[i]['serial_no'];
        //console.log("serial_no.." + serial_no);
        var child_received_qty = items[i]['qty'];
        //console.log("child_received_qty", child_received_qty);
        var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
	var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
	if(HasSerialNumber == 1 ||HasBatchNumber==1){
        console.log("item has batch or serial number make feild mandondatory");
   	cur_frm.fields_dict.items.grid.toggle_reqd("revision_number", true)
        }
	else{
	console.log("item has no  batch or no serial number don't make feild mandondatory");

}//end of else
    }//end of for loop
});

function fetch_has_serial_no(item_code) {
    console.log("entered into function");
    var has_serial_no = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Item',
            'fieldname': ["has_serial_no", "item_code"],

            'filters': {
                item_code: item_code,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                has_serial_no = r.message.has_serial_no;
                console.log(has_serial_no);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_serial_no
}


function fetch_has_batch_no(item_code) {
    console.log("entered into has_batch_no function");
    var has_batch_no = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Item',
            'fieldname': ["has_batch_no", "item_code"],

            'filters': {
                item_code: item_code,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                has_batch_no = r.message.has_batch_no;
                console.log(has_batch_no);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_batch_no
}


//available qty from stock ledger entry

frappe.ui.form.on("Delivery Note", "before_save", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var customer = frm.doc.customer;
    console.log("customer", customer);
    var company = frm.doc.company;
    console.log("company", company);
    var items = frm.doc.items;

    for (var j = 0; j < items.length; j++) {
        var item_code = items[j]['item_code'];
        console.log("item_code", item_code);
        var status = frm.doc.docstatus;
        console.log("status", status);
        var name = frm.doc.name;
        console.log("name", name);
        var warehouse = items[j]['warehouse'];
        console.log("warehouse", warehouse);
        var posting_date1 = frm.doc.posting_date;
        console.log("posting_date1", posting_date1);
        var posting_time1 = frm.doc.posting_time;
        console.log("posting_time1", posting_time1);

        var combined_datetime = posting_date1 + " " + posting_time1;
        console.log("combined_datetime", combined_datetime);
        var converted_posting_date = new Date(combined_datetime).getTime();
        console.log("converted_posting_date", converted_posting_date);
        var available_qty_warehouse_date = fetch_qty_at_from_warehouse(item_code, warehouse);
        console.log("available_qty_warehouse_date", available_qty_warehouse_date);
        var available_qty_warehouse_date_beforePostingDate = [];
        var available_qty_warehouse_date_beforePostingTime = [];
        var heighest_date;
        for (var z = 0; z < available_qty_warehouse_date.length; z++) {
            //var dates=available_qty_warehouse_date[z];
            available_qty_warehouse_date[z] = new Date(available_qty_warehouse_date[z]).getTime();
            console.log("date", available_qty_warehouse_date[z], z);
            if (available_qty_warehouse_date[z] <= converted_posting_date) {
                available_qty_warehouse_date_beforePostingDate.push(available_qty_warehouse_date[z]);
                console.log("available_qty_warehouse_date_beforePostingDate", available_qty_warehouse_date_beforePostingDate);

            }
            z = z + 1;
        }
        var sorted_date = available_qty_warehouse_date_beforePostingDate.sort();
        console.log("sorted_date", sorted_date);

        var heighest_date = sorted_date[sorted_date.length - 1];
        console.log("heighest_date", heighest_date);
        var qty;
        for (var i = 0; i <= available_qty_warehouse_date.length; i++) {
            if (heighest_date == available_qty_warehouse_date[i]) {
                qty = available_qty_warehouse_date[i + 1];
                console.log("qty", qty);
            }
        }


        if (heighest_date != undefined) {
            console.log("entered in if block");

            items[j]['pch_available_qty_of_transcation_at_posting_date_and_time'] = qty;
        } else {
            console.log("entered in else block");
            items[j]['pch_available_qty_of_transcation_at_posting_date_and_time'] = 0;
        }
        frm.refresh_field("items")
    }



});


function fetch_qty_at_from_warehouse(item_code, warehouse) {
    var qty_after_transaction_posting_date = [];
    frappe.call({
        method: 'nhance.api.get_stock_qty',
        args: {
            "item_code": item_code,
            "warehouse": warehouse

        },
        async: false,
        callback: function(r) {
            for (var i = 0; i < r.message.length; i++) {
                qty_after_transaction_posting_date.push(r.message[i].date);
                qty_after_transaction_posting_date.push(r.message[i].qty_after_transaction);

            }


        }
    });
    return qty_after_transaction_posting_date
}


//for testing
frappe.ui.form.on("Delivery Note", "refresh", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var customer = frm.doc.customer;
    console.log("customer", customer);
    var company = frm.doc.company;
    console.log("company", company);
    var items = frm.doc.items;
    var test = fetch_from_api();
    console.log("test", test);
});


function fetch_from_api() {
    var qty_after_transaction_posting_date = "";
    frappe.call({
        method: 'nhance.api.testing_api',
        async: false,
        callback: function(r) {
            
       if (r.message) {
                qty_after_transaction_posting_date = r.message;
                console.log(qty_after_transaction_posting_date);
                console.log("readings-----------" + JSON.stringify(r.message));

            }

        }
    });
    return qty_after_transaction_posting_date
}

