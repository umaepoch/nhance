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
frappe.ui.form.on("Delivery Note", {
    refresh: function(frm) {
        var items = frm.doc.items;
        console.log("items....." + JSON.stringify(items));
        var purchase_document_no = frm.doc.name;
        console.log("purchase_document_no", purchase_document_no);
        for (var i = 0; i < items.length; i++) {
            var item_code = items[i]['item_code'];
            console.log("item_code", item_code);
            var batch_no = items[i]['batch_no'];
            console.log("batch_no", batch_no);
            var serial_no = items[i]['serial_no'];
            console.log("serial_no", serial_no);
            var HasSerialNumber = null;
            HasSerialNumber = fetch_item_has_serial_no(item_code);
            console.log("HasSerialNumber", HasSerialNumber);
            var HasBatchNumber = null;
            HasBatchNumber = fetch_has_batch_no(item_code);
            console.log("HasBatchNumber", HasBatchNumber);
            var HasRevisionNumberBatch = null;
            HasRevisionNumberBatch = fetch_has_revision_number(batch_no);
            console.log("HasRevisionNumberBatch", HasRevisionNumberBatch);
            var HasRevisionNumberSerial = null;
            HasRevisionNumberSerial = fetch_has_revision_number_serial(serial_no);
            console.log("HasRevisionNumberSerial", HasRevisionNumberSerial);


            if (HasRevisionNumberBatch != null && HasBatchNumber == 1) {
                items[i]['revision_number'] = HasRevisionNumberBatch;

                var df = frappe.meta.get_docfield("Delivery Note Item", "revision_number", cur_frm.doc.name);
                df.read_only = 1;
            } else if ((HasRevisionNumberSerial != null || HasRevisionNumberSerial == "" || HasRevisionNumberSerial == undefined) && HasSerialNumber == 1) {
                console.log("entered in else");

                items[i]['revision_number'] = HasRevisionNumberSerial;

                var df = frappe.meta.get_docfield("Delivery Note Item", "revision_number", cur_frm.doc.name);
                df.read_only = 1;



            }

        }

    }
});

function fetch_item_has_serial_no(item_code) {
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
    console.log("entered into fetch_has_revision_number_serial function");
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
                console.log(has_revision_number_serial);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_revision_number_serial
}
