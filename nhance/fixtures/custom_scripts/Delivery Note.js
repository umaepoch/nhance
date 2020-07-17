//make pick list button and child table of pick list*******************************************************************************

frappe.ui.form.on("Delivery Note", {
	refresh: function(frm, cdt, cdn){
		if (cur_frm.doc.__islocal){
		if(cur_frm.doc.amended_from == undefined){
			cur_frm.set_df_property("pch_pick_list", "hidden", true);
		}
		}
		

		
	},
	make_pick_list: function(frm, cdt,cdn){
		cur_frm.set_df_property("pch_pick_list", "hidden", false);

		 $.each(frm.doc.items, function(i, d) {
			var item_code = d.item_code;
			var qty = d.qty;
			var stock_uom = d.stock_uom;
			var rarb_location = d.pch_rarb_location_src;
			var warehouse = d.warehouse;
			var parent  = cur_frm.doc.name;
			var rarb_warehouse = get_rarb_warehouses(warehouse);
			if(rarb_warehouse.length != 0){
			if(rarb_location != undefined && rarb_location != ""){
			 var item_qty_available = get_qty_available(item_code,warehouse);
			var available_qty = item_qty_available[0].actual_qty;
			if(d.stock_qty <= available_qty){
			 var child = cur_frm.add_child("pch_pick_list");
		                 frappe.model.set_value(child.doctype, child.name, "item",item_code );
				 frappe.model.set_value(child.doctype, child.name, "qty",d.stock_qty);
				 frappe.model.set_value(child.doctype, child.name, "stock_uom",stock_uom );
				 frappe.model.set_value(child.doctype, child.name, "rarb_location",rarb_location );
				 frappe.model.set_value(child.doctype, child.name, "warehouse",warehouse );
				 var get_batch = get_batch_name(item_code);
				var get_name = get_batch[0].name;
				if(get_name != "" && get_name != undefined){
					frappe.model.set_value(child.doctype, child.name, "batch_number",get_name);
					
					var serial_no = get_serial_no(warehouse,get_name,item_code,d.stock_qty);
					var serial_no_list = "";
					for(var i =0; i < serial_no.length; i++){
						serial_no_list=serial_no_list.concat((serial_no[i].name).concat("\n"));
						//serial_no_list.push("\n");
						
						//console.log("serial no---------------"+serial_no_list);
						
						
					}
					var no_of_serial_no = 0;
					/*for(var i=0; i < serial_no_list.length; i++) {
						
						no_of_serial_no = no_of_serial_no + i;
						}*/
					//console.log("serial_no_list---------2------------"+serial_no.length);
					frappe.model.set_value(child.doctype, child.name, "serial_numbers",serial_no_list.toString());
					frappe.model.set_value(child.doctype, child.name, "picked_qty",serial_no.length);
				}
				refresh_field("pch_pick_list");
			}
			}
			else{
				frappe.msgprint("RARB Location(Source Warehouse) Not Provided Please specify RARB Location");
				cur_frm.set_df_property("pch_pick_list", "hidden", true);
			}
			}else{
				 var child = cur_frm.add_child("pch_pick_list");
				 frappe.model.set_value(child.doctype, child.name, "warehouse",warehouse );
				 cur_frm.refresh_field("pch_pick_list");
				 
			}
		})
	},
	onload: function(frm){
		if(!cur_frm.doc.__islocal){
			var stock = cur_frm.doc.name;
			
			 $.each(frm.doc.pch_pick_list, function(i, d) {
				var item = d.item;
				var name = get_name(stock,item);
				//console.log("name -------------"+JSON.stringify(name));
				//console.log("second name------------"+name[0].name);
				d.id = name[0].name;
			})
		}
	}

	
})
function get_name(parent,item){
	var supplier_criticality = ""
	frappe.call({
		method: 'nhance.nhance.doctype.pick_list.pick_list.get_name',
		args: {
		   "parent":parent,
		   "item":item
		},
		async: false,
		callback: function(r) {
		    if(r.message){
			  supplier_criticality = r.message;
				    
		}		
			
		}
    });
    return supplier_criticality
}
function get_batch_name(item_code){
	var batch_name = ""
	frappe.call({
		method: 'nhance.nhance.doctype.pick_list.pick_list.get_batch_name',
		args: {
		    "item_code":item_code
		},
		async: false,
		callback: function(r) {
		    if(r.message){
			  batch_name = r.message;
	                  //console.log("bach name-------------------"+JSON.stringify(batch_name));
		}		
			
		}
    });
    return batch_name
}
function get_qty_available(item_code,warehouse){
	var item_available_qty = ""
	frappe.call({
		method: 'nhance.nhance.doctype.pick_list.pick_list.get_qty_available',
		args: {
		 "item_code":item_code,
		   "warehouse":warehouse
		   
		},
		async: false,
		callback: function(r) {
		    if(r.message){
			  item_available_qty = r.message;
	                  //console.log("bach name-------------------"+JSON.stringify(batch_name));
		}		
			
		}
    });
    return item_available_qty

}
function get_serial_no(s_warehouse,batch,item_code,qty){
	var serial_no = ""
	frappe.call({
		method: 'nhance.nhance.doctype.pick_list.pick_list.get_serial_no',
		args: {
		 "s_warehouse":s_warehouse,
		   "batch":batch,
		   "item_code":item_code,
		   "qty":qty
		   
		},
		async: false,
		callback: function(r) {
		    if(r.message){
			  serial_no = r.message;
	                  //console.log("bach name-------------------"+JSON.stringify(batch_name));
		}		
			
		}
    });
    return serial_no
}
function get_rarb_warehouses(warehouse){
	var supplier_criticality = "";
	frappe.call({
		method: 'nhance.nhance.doctype.pick_list.pick_list.get_rarb_warehouses',
		args: {
		   "warehouse":warehouse
		},
		async: false,
		callback: function(r) {
		   if(r.message != undefined){
			    //console.log("supplier criticality..." + JSON.stringify(r.message));
			   supplier_criticality = r.message[0].warehouse;
			  // console.log("warehnouse=============="+supplier_criticality);
			}
		}
    });
    return supplier_criticality;
}
//end of make pick list button and child table of pick list


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
frappe.ui.form.on("Delivery Note Item", "item_code", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    
    var items = frm.doc.items;
    // //console.log("items....."+JSON.stringify(items));
    var flag=0;
    for (var i = 0; i < items.length; i++) {
        var item_code = items[i]['item_code'];
        
        var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
        var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
       

        if(HasBatchNumber==0 && HasSerialNumber==0) {
         console.log("no batch no");
	flag+=1;
	console.log(flag);
	if(flag>1){
	    console.log("falg is greater than 1")
       cur_frm.fields_dict.items.grid.toggle_reqd("revision_number", false)
	}
       // cur_frm.refresh_field("items")
    }
    else if(HasBatchNumber==1 || HasSerialNumber==1) {
        console.log("has batch no");
	flag=0;
	console.log("flag",flag);
	if(flag===0){
         cur_frm.fields_dict.items.grid.toggle_reqd("revision_number", true)
	}
    }

 
       
    }
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

frappe.ui.form.on("Delivery Note Item", "item_code", function(frm, cdt, cdn) {
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
        var posting_date = frm.doc.posting_date;
        console.log("posting_date", posting_date);
        var posting_time = frm.doc.posting_time;
        console.log("posting_time", posting_time);

	
       var available_qty_warehouse_date = fetch_qty_at_from_warehouse(item_code, warehouse);
        console.log("available_qty_warehouse_date", available_qty_warehouse_date);

	var converted_posting_date=new Date(posting_date).getTime();
            console.log("converted_posting_date", converted_posting_date);

var available_qty_warehouse_date_beforePostingDate =[];

        for (var z = 0; z < available_qty_warehouse_date.length; z++) {
            //var dates=available_qty_warehouse_date[z];
            available_qty_warehouse_date[z] = new Date(available_qty_warehouse_date[z]).getTime();
            console.log("date", available_qty_warehouse_date[z], z);
            
if(available_qty_warehouse_date[z] < converted_posting_date){
available_qty_warehouse_date_beforePostingDate.push(available_qty_warehouse_date[z]);
console.log("available_qty_warehouse_date_beforePostingDate",available_qty_warehouse_date_beforePostingDate);
}
		

        }

        var sorted_date = available_qty_warehouse_date_beforePostingDate.sort();
        console.log("sorted_date", sorted_date);
        for (var i = 0; i < sorted_date.length; i++) {
            var todate = new Date(sorted_date[i]).getDate();
            if (todate < 10) {
                todate = "0" + todate;
            }
            var tomonth = new Date(sorted_date[i]).getMonth() + 1;
            if (tomonth < 10) {
                tomonth = "0" + tomonth;
            }
            var toyear = new Date(sorted_date[i]).getFullYear();
            sorted_date[i] = toyear + '-' + tomonth + '-' + todate;

            console.log("original_date", sorted_date[i]);

        }
        var heighest_date;
        var heighest_date = sorted_date[sorted_date.length - 1];
        console.log("heighest_date", heighest_date);
       var available_qty_warehouse_time;
       
        available_qty_warehouse_time = fetch_qty_at_from_warehouse_time(item_code, warehouse, heighest_date);
        console.log("available_qty_warehouse_time", available_qty_warehouse_time);
        
        var newarray = [];
        for (var p = 0; p < available_qty_warehouse_time.length; p++) {
            console.log("entered in loop");


            newarray.push(available_qty_warehouse_time[p]);

        }
        var newest_array = newarray.sort();
        console.log("newest_array", newest_array);
        var lenght_array = newest_array.length - 1;
        var time = newest_array[lenght_array];
        console.log("time", time);
        if (time != undefined ) {
          var available_qty_warehouse = fetch_qty_at_from_warehouse_qty(item_code, warehouse, heighest_date,time);
            console.log("available_qty_warehouse", available_qty_warehouse);
           

            items[j]['pch_available_qty_of_transcation_at_posting_date_and_time'] = available_qty_warehouse;
        } 
else {
            items[j]['pch_available_qty_of_transcation_at_posting_date_and_time'] = 0;
        }
       frm.refresh_field("items") 
    }

  

});


function fetch_qty_at_from_warehouse(item_code, warehouse){
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
                qty_after_transaction_posting_date.push(r.message[i].posting_date);

            }
		}
    });
    return qty_after_transaction_posting_date
}


function fetch_qty_at_from_warehouse_time(item_code, warehouse, heighest_date) {
    console.log("entered into function");
    var qty_after_transaction_posting_time = [];
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            'doctype': 'Stock Ledger Entry',
            'fields': ['qty_after_transaction', 'posting_date', 'posting_time'],

            'filters': {
                item_code: item_code,
                warehouse: warehouse,
                posting_date: heighest_date
            }
        },
        async: false,
        callback: function(r) {
            //console.log("qty_after_transaction_posting_time" + JSON.stringify(r.message));
            for (var i = 0; i < r.message.length; i++) {
                qty_after_transaction_posting_time.push(r.message[i].posting_time);

            }


        }
    });
    return qty_after_transaction_posting_time
}

function fetch_qty_at_from_warehouse_qty(item_code, warehouse,heighest_date, time) {
    console.log("entered into function");
    var qty_after_transaction_qty = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Stock Ledger Entry',
            'fieldname': 'qty_after_transaction',

            'filters': {
                item_code: item_code,
                warehouse: warehouse,
		posting_date:heighest_date,
                posting_time: time
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                qty_after_transaction_qty = r.message.qty_after_transaction;
                //console.log(qty_after_transaction_qty);
                //console.log("readings-----------" + JSON.stringify(r.message));

            }

        }
    });
    return qty_after_transaction_qty
}
