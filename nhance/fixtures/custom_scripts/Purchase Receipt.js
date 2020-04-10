frappe.ui.form.on("Purchase Receipt", {
   update_this_to_pch_work_order_items: function(frm, cdt, cdn) {

      $.each(frm.doc.items, function(i, d) {
	d.pch_supplier_workorder=" ";
         d.pch_supplier_workorder= frm.doc.pch_supplier_workorder;
         refresh_field("pch_supplier_workorder");
      }); //end of each...
   console.log("end of each");
refresh_field("items");
      frm.refresh_field(frm.doc.items);
      cur_frm.save();
   } //end of update_this_project function..
}); //end of form



frappe.ui.form.on("Purchase Receipt", "after_save", function(frm, cdt, cdn) {

    //var d = locals[cdt][cdn];
    var parent = frm.doc.name;
    console.log("parent", parent);
    var is_return=frm.doc.is_return;
    console.log("is_return...",is_return);
if(is_return!=1){
    var owner = frm.doc.items;
   
	for (var i = 0; i < owner.length; i++) {
        var child_item_code = owner[i]['item_code'];
        var child_serial_no = owner[i]['serial_no'];
        var child_pch_supplier_workorder = owner[i]['pch_supplier_workorder']; 
        var child_received_qty = owner[i]['received_qty'];
        console.log("child_item_code", owner[i]['item_code']);
        console.log("child_serial_no", owner[i]['serial_no']);
        console.log("child_pch_supplier_workorder", child_pch_supplier_workorder);

        
        var Sn = null;
	Sn = fetch_serial_no(child_item_code);
	console.log("Sn", Sn);

	var Hs= null;
	Hs=fetch_has_serial_no(child_item_code);
	console.log("Hs", Hs);


        var arr = [];
        arr = Sn.split('-');
        var nor = arr[2];

        var itemcode = child_item_code;
        var work_order = child_pch_supplier_workorder;
        var duplicate_serial = itemcode.concat("-").concat(work_order).concat("-");
        
	var duplicate_serial_no = fetch_duplicate_serial_no(duplicate_serial);
	console.log("duplicate_serial_no", duplicate_serial_no);

        console.log("item_code", itemcode);
        console.log("work order---", work_order);
        console.log("duplicate_serial", duplicate_serial);
        
        var test=duplicate_serial_no[0].serial_no;
        console.log("nor",test);
       
        var array = "";


        var num = 1;

        function pad(n) {
            var string = "" + n;
            var pad = "0000";
            n = pad.substring(0, pad.length - string.length) + string;
            return n;
        }

        //owner[i]['serial_no'] = "";
        //console.log("...", owner[i]['serial_no']);

 if (work_order==""  ||work_order==null || work_order==undefined ) {

            // call fun here 
            console.log("entered in else if");
           
        }
 else if(test==null){
    console.log("Entered.........................");
 for (; num <= child_received_qty; num += 1) { //appending loop start
                            console.log("num", num);
                            array = array.concat(owner[i]['item_code']).concat("-").concat(child_pch_supplier_workorder).concat("-").concat(pad(num)).concat("\n");

                            console.log("Serial No", array)
                        }
			owner[i]['serial_no'] = "";
                        owner[i]['serial_no'] = owner[i]['serial_no'].concat(array);



}
else {
                    console.log("entered in else");
		
                   //var test = null;
                   // var test = duplicate_serial_no[0].serial_no;
                   // console.log("nor", test);
                    var test1 = test.split('-');
                    console.log(">>>>>>>", test1);
                    console.log(test1.length - 1);
                    var nor=test1[2];
                    var nor = test1[test1.length - 1];
                    console.log("...........", nor);
                    if ( test == null) {
                    
                        console.log("entered in else in if");
                        for (; num <= child_received_qty; num += 1) { //appending loop start
                            console.log("num", num);
                            array = array.concat(owner[i]['item_code']).concat("-").concat(child_pch_supplier_workorder).concat("-").concat(pad(num)).concat("\n");

                            console.log("Serial No", array)
                        }
			owner[i]['serial_no'] = "";
                        owner[i]['serial_no'] = owner[i]['serial_no'].concat(array);

                    } else if (isNaN(nor)) {
                        //else if(!nor.match(Exp)) {
                        console.log("#################");

                        for (; num <= child_received_qty; num += 1) { //appending loop start
                            console.log("num", num);
                            array = array.concat(owner[i]['item_code']).concat("-").concat(child_pch_supplier_workorder).concat("-").concat(pad(num)).concat("\n");
                            console.log(owner[i]['item_code'].concat("-").concat(child_pch_supplier_workorder).concat("-").concat(pad(num)));

                        }
			owner[i]['serial_no'] = "";
                        owner[i]['serial_no'] = owner[i]['serial_no'].concat(array);

                    } else {
                        console.log("entered in else in else");

                        for (var z = 1; z <= child_received_qty; z += 1) {

                            nor++;
                            array = array.concat(owner[i]['item_code']).concat("-").concat(child_pch_supplier_workorder).concat("-").concat(pad(nor)).concat("\n");


                        }
                        console.log("calling set value");
			owner[i]['serial_no'] = "";
                        owner[i]['serial_no'] = owner[i]['serial_no'].concat(array);
                        //frappe.model.set_value("Purchase Receipt Item",child_item_code,"serial_no",array);
                    }
                }
refresh_field("items");

    } // end of items for loop
}//end of first loop

}); // end of refresh 

    





function fetch_serial_no(arg1) {
    console.log("entered into function");
    var serial_no_list = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Serial No',
            'fieldname': ["serial_no", "item_code"],

            'filters': {
                item_code: arg1,
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                serial_no_list = r.message.serial_no;
                console.log(serial_no_list);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return serial_no_list
}

function fetch_duplicate_serial_no(duplicate_serial) {
    console.log("entered into 2nd function");
    var duplicate_serial_no_list = "";
    frappe.call({
        method: "nhance.api.get_serial_number_details",
        args: {
            "duplicate_serial": duplicate_serial

        },
        async: false,
        callback: function(r) {
            if (r.message) {
                duplicate_serial_no_list = r.message;
                console.log("checking--------------" + duplicate_serial_no_list);
                console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    console.log("duplicate_serial_no_list", duplicate_serial_no_list);
    return duplicate_serial_no_list
}

function fetch_has_serial_no(arg2) {
    console.log("entered into function");
    var has_serial_no = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'Item',
            'fieldname': ["has_serial_no", "item_code"],

            'filters': {
                item_code: arg2,
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

frappe.ui.form.on("Purchase Receipt",{
	set_warehouse:function(frm){
		var warehouse = cur_frm.doc.set_warehouse;
		if(warehouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(warehouse);
			//console.log("target is not undefined");
			//console.log("rarb_warehouse------------"+rarb_warehouse);
			if(warehouse == rarb_warehouse){
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", true);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true)
				
					 cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
						var d = locals[cdt][cdn];
						var t_warehouse = d.warehouse;
						var rarb_warehouse_list = get_rarb_warehouse_item_name(t_warehouse);
						//console.log("rarb_warehouse-------trg--------"+rarb_warehouse_list);
						 return {
							    "filters": [
								["RARB ID", "name", "in", rarb_warehouse_list],

							]
							}
						cur_frm.refresh_field("items");
						cur_frm.refresh_field("pch_rarb_location_trg");
					});
					//rarb_warehouse_list = [1,2,3,4];
					//frappe.meta.get_docfield("Purchase Receipt Item", "pch_rarb_location_trg", frm.docname).options = rarb_warehouse_list;
						refresh_field("pch_rarb_location_trg");
						refresh_field("items");
				
			}else{
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
			}
		}else{
			//console.log("targer is undifined---------");
			//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
			 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
		}
		frappe.ui.form.on("Purchase Receipt Item",{
			warehouse: function(frm,cdt,cdn){
				var d = locals[cdt][cdn];
				var child_warehouse = d.warehouse;
				if(child_warehouse != undefined){
					var rarb_warehouse = get_rarb_warehouse(child_warehouse);
					//console.log("target is not undefined");
					//console.log("rarb_warehouse------------"+rarb_warehouse);
					if(child_warehouse == rarb_warehouse){
						var rarb_warehouse_name = []
						//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", true);
						 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true)
						 cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
						var d = locals[cdt][cdn];
						var t_warehouse = d.warehouse;
						var rarb_warehouse_list = get_rarb_warehouse_item_name(t_warehouse);
						//console.log("rarb_warehouse-------trg--------"+rarb_warehouse_list);
						 return {
							    "filters": [
								["RARB ID", "name", "in", rarb_warehouse_list],

							]
							}
						cur_frm.refresh_field("items");
						cur_frm.refresh_field("pch_rarb_location_trg");
					});
					//rarb_warehouse_list = [1,2,3,4];
					//frappe.meta.get_docfield("Purchase Receipt Item", "pch_rarb_location_trg", frm.docname).options = rarb_warehouse_list;
						refresh_field("pch_rarb_location_trg");
						refresh_field("items");
						
					}else{
						//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
						 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
					}
				}else{
					//console.log("targer is undifined---------");
					//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
					 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
				}
			}
		})
	},
	onload : function(frm){
		var warehouse = cur_frm.doc.set_warehouse;
		if(warehouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(warehouse);
			//console.log("target is not undefined");
			//console.log("rarb_warehouse------------"+rarb_warehouse);
			if(warehouse == rarb_warehouse){
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", true);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true)
				var rarb_warehouse_name = [];
				 cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
						var d = locals[cdt][cdn];
						var t_warehouse = d.warehouse;
						var rarb_warehouse_list = get_rarb_warehouse_item_name(t_warehouse);
						//console.log("rarb_warehouse-------trg--------"+rarb_warehouse_list);
						 return {
							    "filters": [
								["RARB ID", "name", "in", rarb_warehouse_list],

							]
							}
						cur_frm.refresh_field("items");
						cur_frm.refresh_field("pch_rarb_location_trg");
					});
					//rarb_warehouse_list = [1,2,3,4];
				//	frappe.meta.get_docfield("Purchase Receipt Item", "pch_rarb_location_trg", frm.docname).options = rarb_warehouse_list;
						refresh_field("pch_rarb_location_trg");
						refresh_field("items");
			}else{
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
			}
		}else{
			//console.log("targer is undifined---------");
			//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
			 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
		}
		frappe.ui.form.on("Purchase Receipt Item",{
			warehouse: function(frm,cdt,cdn){
				var d = locals[cdt][cdn];
				var child_warehouse = d.warehouse;
				if(child_warehouse != undefined){
					var rarb_warehouse = get_rarb_warehouse(child_warehouse);
					//console.log("target is not undefined");
					//console.log("rarb_warehouse------------"+rarb_warehouse);
					if(child_warehouse == rarb_warehouse){
						var rarb_warehouse_name = []
						//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", true);
						 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true)
						 cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
						var d = locals[cdt][cdn];
						var t_warehouse = d.warehouse;
						var rarb_warehouse_list = get_rarb_warehouse_item_name(t_warehouse);
						//console.log("rarb_warehouse-------trg--------"+rarb_warehouse_list);
						 return {
							    "filters": [
								["RARB ID", "name", "in", rarb_warehouse_list],

							]
							}
						cur_frm.refresh_field("items");
						cur_frm.refresh_field("pch_rarb_location_trg");
					});
					//rarb_warehouse_list = [1,2,3,4];
					//frappe.meta.get_docfield("Purchase Receipt Item", "pch_rarb_location_trg", frm.docname).options = rarb_warehouse_list;
						refresh_field("pch_rarb_location_trg");
						refresh_field("items");
						
					}else{
						//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
						 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
					}
				}else{
					//console.log("targer is undifined---------");
					//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
					 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
				}
			}
		})
	}
})
frappe.ui.form.on("Purchase Receipt","before_save", function(frm,cdt,cdn){
	
	 $.each(frm.doc.items, function(i, d) {
		var item_code = d.item_code;
		var warehouse = d.warehouse;
		//console.log("on save warehosue------------"+warehouse);
		var pch_rarb_location_trg = d.pch_rarb_location_trg;
		if(pch_rarb_location_trg != undefined){
		var get_items_details = get_rarb_items_detail(warehouse,pch_rarb_location_trg);
		//console.log("get_items_details------------"+get_items_details);
		if(get_items_details != undefined){
			if(get_items_details != item_code){
				frappe.msgprint('"'+pch_rarb_location_trg+'"'+" This RARB Location(Source Warehouse) is reserved for specific item "+'"'+get_items_details+'"');
				frappe.validated = false;
			}
		}
		}
	})
})
function get_rarb_warehouse(warehouse){
	var supplier_criticality = "";
	frappe.call({
		method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_rarb_warehouse',
		args: {
		   "warehouse":warehouse
		},
		async: false,
		callback: function(r) {
		   if(r.message != undefined){
			    //console.log("supplier criticality..." + JSON.stringify(r.message));
			   supplier_criticality = r.message[0].warehouse;
			  // //console.log("warehnouse=============="+supplier_criticality);
			}
		}
    });
    return supplier_criticality;
}
function get_rarb_warehouse_item_name(warehouse){
	var supplier_criticality = [];
	frappe.call({
		method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_rarb_warehouse_item_name',
		args: {
		   "warehouse":warehouse
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
			 for (var i = 0; i < r.message.length; i++) {
				    supplier_criticality.push(r.message[i].rarb_id);
				    
				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
    return supplier_criticality;
}
function get_rarb_items_detail(warehouse,pch_rarb_location_src){
	var supplier_criticality = ""
	frappe.call({
		method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_rarb_items_detail',
		args: {
		   "warehouse":warehouse,
		   "pch_rarb_location_src":pch_rarb_location_src
		},
		async: false,
		callback: function(r) {
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
			 for (var i = 0; i < r.message.length; i++) {
				    supplier_criticality = r.message[i].rarb_item;
				    
				}
			//console.log("supplier_criticality---11111----" + supplier_criticality);
		}
    });
    return supplier_criticality
}



//for revision number

frappe.ui.form.on("Purchase Receipt Item", {


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
        var df = frappe.meta.get_docfield("Purchase Receipt Item", "revision_number", cur_frm.doc.name);

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

/*
frappe.ui.form.on("Purchase Receipt", "after_save", function(frm, cdt, cdn) {

    $.each(frm.doc.items, function(i, d) {
        var item_code = d.item_code;
        var revision_number = d.revision_number;
        console.log("revision_number", revision_number);
        if (revision_number != "") {
            var df = frappe.meta.get_docfield("Purchase Receipt Item", "revision_number", cur_frm.doc.name);

            df.read_only = 1;
        }
    })
});

*/
//autofill revision in serialNo doctype
frappe.ui.form.on("Purchase Receipt", "on_submit", function(frm, cdt, cdn) {
	var parent = frm.doc.name;
    console.log("parent", parent);
    $.each(frm.doc.items, function(i, d) {
        var item_code = d.item_code;
        var revision_number = d.revision_number;
        console.log("revision_number", revision_number);
        var serial_no= d.serial_no;
        console.log("serial_no", serial_no);
        //var revision_number = d.revision_number;
        //console.log("revision_number", revision_number);
	var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
        var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
       if(HasSerialNumber==1 ){
           console.log("entered in if error block");
          var serial=fetch_revision_number(item_code,parent)
           console.log("-----------------",serial);
        }
    })
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
function fetch_revision_number(item_code,parent){
    console.log("entered into fetch_revision_number function");
    var revision_list = "";
    frappe.call({
        method: "nhance.api.get_purchase_revision_no",
        args: {
            
            "item_code":item_code,
            "parent":parent
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                revision_list = r.message;
                console.log("checking--------------" + revision_list);
                console.log("readings-----------" + JSON.stringify(r.message));
               

            }
        }

   });
    console.log("revision_list", revision_list);
    return revision_list
}

//To check Item has has serial or batch number
frappe.ui.form.on("Purchase Receipt", "before_save", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    //console.log("Entered------" + d);
    ////console.log(".........."+JSON.stringify(d));
    var work_order = frm.doc.work_order;
    //console.log("work_order...." + work_order);
    var docstatus = frm.doc.docstatus;
    //console.log("docstatus...." + docstatus);
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
	console.log("item has no batch or no serial number not  make feild mandondatory");

}//end of else manufacture block
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
