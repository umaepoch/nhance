//RARB Location (Source Warehouse) and RARB Location (Target Warehouse) start from here.....
 
frappe.ui.form.on("Stock Entry", "refresh", function(frm ,cdt , cdn){
	frappe.ui.form.on("Stock Entry Detail", {
		t_warehouse : function(frm, cdt , cdn){
			cur_frm.refresh_field("items")
			var d = locals[cdt][cdn];
			var s_warehouse = d.s_warehouse;
			var t_warehouse = d.t_warehouse;
			
			////console.log("t_warehouse----------------"+t_warehouse);
			////console.log("s_warehouse----------------"+s_warehouse);
			if(t_warehouse != undefined){
				var rarb_warehouse = get_rarb_warehouse(t_warehouse);
				//console.log("target is not undefined");
				//console.log("rarb_warehouse------------"+rarb_warehouse);
				if(t_warehouse == rarb_warehouse){
					//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", true);
					// cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true)
					 var rarb_warehouse_list = [];
					 cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
						var d = locals[cdt][cdn];
						var t_warehouse = d.t_warehouse;
						 rarb_warehouse_list = get_rarb_warehouse_item_name(t_warehouse);
						//console.log("rarb_warehouse-------trg--------"+rarb_warehouse_list);
						 return {
							    "filters": [
								["RARB ID", "name", "in", rarb_warehouse_list],

							]
							}
						cur_frm.refresh_field("items");
						cur_frm.refresh_field("pch_rarb_location_trg");
					});
					// rarb_warehouse = get_rarb_warehouse_item_name(t_warehouse);
					//frappe.meta.get_docfield("Stock Entry Detail", "pch_rarb_location_trg", frm.docname).options = rarb_warehouse;
				}else{
					//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
					 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
					
				}
			}else{
				//console.log("targer is undifined---------");
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
			}
			if(s_warehouse == undefined){
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", false);
			 	cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
			}
			
			
		},
		s_warehouse : function(frm, cdt , cdn){
			var d = locals[cdt][cdn];
			var s_warehouse = d.s_warehouse;
			var t_warehouse = d.t_warehouse;
			//console.log("t_warehouse----------------"+t_warehouse);
			//console.log("s_warehouse----------------"+s_warehouse);
			if(s_warehouse != undefined){
				//console.log("target is not undefined");
				var rarb_warehouse = get_rarb_warehouse(s_warehouse);
				//console.log("rarb_warehouse------------"+rarb_warehouse);
				//console.log("target is not undefined");
				if(s_warehouse == rarb_warehouse){
					//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", true);
					 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", true);
					var rarb_warehouse_list = [];
					//console.log("true");
					 cur_frm.set_query("pch_rarb_location_src", "items", function(frm, cdt, cdn) {
						var d = locals[cdt][cdn];
						var s_warehouse = d.s_warehouse;
						 rarb_warehouse_list = get_rarb_warehouse_item_name(s_warehouse);
						
						//console.log("rarb_warehouse--------src-------"+JSON.stringify(rarb_warehouse_list));
						
						 return {
							    "filters": [
								["RARB ID", "name", "in", rarb_warehouse_list]
							    ]
							}
						refresh_field("pch_rarb_location_src");
						refresh_field("items");
					});
					//rarb_warehouse = get_rarb_warehouse_item_name(t_warehouse);
					//frappe.meta.get_docfield("Stock Entry Detail", "pch_rarb_location_src1", frm.docname).options = rarb_warehouse;
					
				}else{
					//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", false);
			 		cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
				}
		
			}else{
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", false);
			 	cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
			}
			if(t_warehouse == undefined){
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_trg", false);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false)
			}
			
			
			
		},
		pch_rarb_location_src : function(frm){
			var rarb_warehouse_list = []
			 cur_frm.set_query("pch_rarb_location_src", "items", function(frm, cdt, cdn) {
				var d = locals[cdt][cdn];
				var s_warehouse = d.s_warehouse;
				 rarb_warehouse_list = get_rarb_warehouse_item_name(s_warehouse);
				//console.log("rarb_warehouse_list------src---------"+rarb_warehouse_list);
				 return {
					    "filters": [
						["RARB ID", "name", "in", rarb_warehouse_list]
					    ]
					}
			});
		},
		pch_rarb_location_trg : function(frm){
			var rarb_warehouse_list = []
			 cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
				var d = locals[cdt][cdn];
				var t_warehouse = d.t_warehouse;
				 rarb_warehouse_list = get_rarb_warehouse_item_name(t_warehouse);
				//console.log("rarb_warehouse----trg-----------"+rarb_warehouse_list);
				 return {
					    "filters": [
						["RARB ID", "name", "in", rarb_warehouse_list]
					    ]
					}
			});
		}
		
	});
	
})
frappe.ui.form.on("Stock Entry","before_save", function(frm,cdt,cdn){
	
	 $.each(frm.doc.items, function(i, d) {
		var item_code = d.item_code;
		var warehouse = d.s_warehouse;
		//console.log("on save warehosue------------"+warehouse);
		var pch_rarb_location_src = d.pch_rarb_location_src;
		if(pch_rarb_location_src != undefined){
		var get_items_details = get_rarb_items_detail(warehouse,pch_rarb_location_src);
		//console.log("get_items_details------------"+get_items_details);
		if(get_items_details != undefined){
			if(get_items_details != item_code){
				frappe.msgprint('"'+pch_rarb_location_src+'"'+" This RARB Location(Source Warehouse) is reserved for specific item "+'"'+get_items_details+'"');
				frappe.validated = false;
			}
		}}
		
	})
})
frappe.ui.form.on("Stock Entry","before_save", function(frm,cdt,cdn){
	
	 $.each(frm.doc.items, function(i, d) {
		var item_code = d.item_code;
		var warehouse = d.t_warehouse;
		//console.log("on save warehosue------------"+warehouse);
		var pch_rarb_location_src = d.pch_rarb_location_trg;
		if(pch_rarb_location_src != undefined){
		var get_items_details = get_rarb_items_detail(warehouse,pch_rarb_location_src);
		//console.log("get_items_details------------"+get_items_details);
		if(get_items_details != undefined){
			if(get_items_details != item_code){
				frappe.msgprint('"'+pch_rarb_location_src+'"'+" This RARB Location (Target Warehouse) is reserved for specific item "+'"'+get_items_details+'"');
				frappe.validated = false;
			}
		}}
		
	})
})
frappe.ui.form.on("Stock Entry","before_submit", function(frm,cdt,cdn){
	//console.log("hello stock entry saved");
 	$.each(frm.doc.items, function(i, item) {
		if(item.s_warhouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(item.s_warhouse);
			if(item.s_warehouse == rarb_warehouse){
				//console.log("source warehouse matched");
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", true);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", true);
			}
			else{
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
			}
		}
		else{
			 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
		}
		if(item.t_warehouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(item.t_warehouse);
			if(item.t_warehouse == rarb_warehouse){
				//console.log("targer warehouuse matched");
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", true);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true);
			}
			else{
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false);
			}
		}
		else{
			 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false);
		}
		
	})

})
frappe.ui.form.on("Stock Entry","onload", function(frm,cdt,cdn){
	//console.log("hello stock entry saved");
 	$.each(frm.doc.items, function(i, item) {
		if(item.s_warehouse != undefined){
			//console.log("s warehosue ------------"+item.s_warehouse);
			var rarb_warehouse = get_rarb_warehouse(item.s_warehouse);
			if(item.s_warehouse == rarb_warehouse){
				//console.log("source warehouse matched");
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", true);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", true);
				cur_frm.set_query("pch_rarb_location_src", "items", function(frm, cdt, cdn) {
					var d = locals[cdt][cdn];
					var s_warehouse = d.s_warehouse;
					var rarb_warehouse_list = get_rarb_warehouse_item_name(s_warehouse);
					//console.log("rarb_warehouse_list------src---------"+rarb_warehouse_list);
					 return {
						    "filters": [
							["RARB ID", "name", "in", rarb_warehouse_list]
						    ]
						}
					refresh_field("items");
					refresh_field("pch_rarb_location_src");
				});
			}
			else{
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
			}
		}
		else{
			 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_src", false);
		}
		if(item.t_warehouse != undefined){
			var rarb_warehouse = get_rarb_warehouse(item.t_warehouse);
			if(item.t_warehouse == rarb_warehouse){
				//console.log("targer warehouuse matched");
				//cur_frm.fields_dict.items.grid.toggle_display("pch_rarb_location_src", true);
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", true);
				cur_frm.set_query("pch_rarb_location_trg", "items", function(frm, cdt, cdn) {
					var d = locals[cdt][cdn];
					var s_warehouse = d.s_warehouse;
					var rarb_warehouse_list = get_rarb_warehouse_item_name(s_warehouse);
					//console.log("rarb_warehouse_list------src---------"+rarb_warehouse_list);
					 return {
						    "filters": [
							["RARB ID", "name", "in", rarb_warehouse_list]
						    ]
						}
					refresh_field("items");
					refresh_field("pch_rarb_location_trg");
				});
			}
			else{
				 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false);
			}
		}
		else{
			 cur_frm.fields_dict.items.grid.toggle_reqd("pch_rarb_location_trg", false);
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
		    //console.log("supplier criticality..." + JSON.stringify(r.message));
		   supplier_criticality = r.message[0].warehouse;
		   //console.log("warehnouse=============="+supplier_criticality);
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






//rarb location end here

//make pick list button and child table of pick list********************************************************

frappe.ui.form.on("Stock Entry", {
    refresh: function(frm, cdt, cdn) {
        if (cur_frm.doc.__islocal) {
            if (cur_frm.doc.amended_from == undefined) {
                cur_frm.set_df_property("pch_pick_list", "hidden", true);
            }
        }



    },
    purpose: function(frm, cdt, cdn) {

        if (cur_frm.doc.purpose == "Material Transfer" || cur_frm.doc.purpose == "Material Issue") {

            cur_frm.set_df_property("make_pick_list", "hidden", false);

        } else {
            cur_frm.set_df_property("make_pick_list", "hidden", true);
        }
    },
    make_pick_list: function(frm, cdt, cdn) {
        cur_frm.set_df_property("pch_pick_list", "hidden", false);

        $.each(frm.doc.items, function(i, d) {
            var item_code = d.item_code;
            var qty = d.qty;
            var stock_uom = d.stock_uom;
            var rarb_location = d.pch_rarb_location_src;
            var s_warehouse = d.s_warehouse;
            ////console.log("rarb_location--------------" + rarb_location);
	    var rarb_warehouse_doc =  get_rarb_warehouses(s_warehouse);
            var parent = cur_frm.doc.name;
	    if (rarb_warehouse_doc.length != 0){
		    if (rarb_location != undefined) {
		        var item_qty_available = get_qty_available(item_code, s_warehouse);
		        ////console.log("item_qty_available--------------" + JSON.stringify(item_qty_available));
		        var available_qty = 0.0;
		        if (item_qty_available.length != 0) {
		            available_qty = item_qty_available[0].actual_qty;
		        }
		       // //console.log("available_qty--------------" + available_qty);
		        if (d.transfer_qty <= available_qty) {
		            var child = cur_frm.add_child("pch_pick_list");
		            frappe.model.set_value(child.doctype, child.name, "item", item_code);
		            frappe.model.set_value(child.doctype, child.name, "qty", d.transfer_qty);
		            frappe.model.set_value(child.doctype, child.name, "stock_uom", stock_uom);
		            frappe.model.set_value(child.doctype, child.name, "rarb_location", rarb_location);
		            frappe.model.set_value(child.doctype, child.name, "warehouse", s_warehouse);
		            var get_batch = get_batch_name(item_code);
		         //   //console.log("get batch --------------" + get_batch);
		            var get_name = "";
		            if (get_batch.length != 0) {
		                get_name = get_batch[0].name;
		            }
		            if (get_name != "" && get_name != undefined) {
		                frappe.model.set_value(child.doctype, child.name, "batch_number", get_name);
		                var serial_no = get_serial_no(s_warehouse, get_name, item_code, d.transfer_qty);
		                var serial_no_list = "";
		                for (var i = 0; i < serial_no.length; i++) {
		                    serial_no_list = serial_no_list.concat((serial_no[i].name).concat("\n"));
		                    //serial_no_list.push("\n");

		                   // //console.log("serial no---------------" + serial_no_list);


		                }
		                /*for(var i=0; i < serial_no_list.length; i++) {
		                	var comma = /,/;
		                	 serial_no_list[i] = serial_no_list[i].replace(comma, '\n');
		                	}*/
		                ////console.log("serial_no_list---------2------------" + serial_no_list);
		                frappe.model.set_value(child.doctype, child.name, "serial_numbers", serial_no_list.toString());
				 frappe.model.set_value(child.doctype, child.name, "picked_qty", serial_no.length);
		            }
		            cur_frm.refresh_field("pch_pick_list");
		        }else{
				frappe.msgprint("Qty "+d.transfer_qty+".00 is not available in selected source warehosue");
			}
		    } else {
		        frappe.msgprint("RARB Location(Source Warehouse) not provided please specify the RARB Location for Source Warehouse")
		    }
		}else{
			 var child = cur_frm.add_child("pch_pick_list");
		            frappe.model.set_value(child.doctype, child.name, "warehouse", s_warehouse);
			cur_frm.refresh_field("pch_pick_list");
		}
        })
    },
    onload: function(frm) {
        if (!cur_frm.doc.__islocal) {
            var stock = cur_frm.doc.name;

            $.each(frm.doc.pch_pick_list, function(i, d) {
                var item = d.item;
                var name = get_name(stock, item);
                ////console.log("name -------------" + JSON.stringify(name));
                ////console.log("second name------------" + name[0].name);
                d.id = name[0].name;
            })
        }
    }


})

function get_name(parent, item) {
    var supplier_criticality = ""
    frappe.call({
        method: 'nhance.nhance.doctype.pick_list.pick_list.get_name',
        args: {
            "parent": parent,
            "item": item
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                supplier_criticality = r.message;

            }

        }
    });
    return supplier_criticality
}

function get_batch_name(item_code) {
    var batch_name = ""
    frappe.call({
        method: 'nhance.nhance.doctype.pick_list.pick_list.get_batch_name',
        args: {
            "item_code": item_code
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                batch_name = r.message;
               // //console.log("bach name-------------------" + JSON.stringify(batch_name));
            }

        }
    });
    return batch_name
}

function get_qty_available(item_code, warehouse) {
    var item_available_qty = ""
    frappe.call({
        method: 'nhance.nhance.doctype.pick_list.pick_list.get_qty_available',
        args: {
            "item_code": item_code,
            "warehouse": warehouse

        },
        async: false,
        callback: function(r) {
            if (r.message) {
                item_available_qty = r.message;
                ////console.log("bach name-------------------"+JSON.stringify(batch_name));
            }

        }
    });
    return item_available_qty

}

function get_serial_no(s_warehouse, batch, item_code, qty) {
    var serial_no = ""
    frappe.call({
        method: 'nhance.nhance.doctype.pick_list.pick_list.get_serial_no',
        args: {
            "s_warehouse": s_warehouse,
            "batch": batch,
            "item_code": item_code,
            "qty": qty

        },
        async: false,
        callback: function(r) {
            if (r.message) {
                serial_no = r.message;
                ////console.log("bach name-------------------"+JSON.stringify(batch_name));
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
			    ////console.log("supplier criticality..." + JSON.stringify(r.message));
			   supplier_criticality = r.message[0].warehouse;
			  // //console.log("warehnouse=============="+supplier_criticality);
			}
		}
    });
    return supplier_criticality;
}
//end of make pick list button and child table of pick list


//revision number
frappe.ui.form.on("Stock Entry Detail", {


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
           // if( d.revision_number!=""){
          //frappe.msgprint("The Revision number for "+'"'+batch_no+'"'+" numbers is set in the Batch Number document. "+'"'+batch_no+'"'+" number has been set with Revision Number "+'"'+HasRevisionNumber+'"'+".You cannot change it in this transaction.");
            
           //}//end of revision test
        }//end of if
        //var df = frappe.meta.get_docfield("Stock Entry Detail", "revision_number", cur_frm.doc.name);

        //df.read_only = 1;
        cur_frm.refresh_field("items")
    }


})


frappe.ui.form.on("Stock Entry Detail", {


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
        //if( d.revision_number!=""){
         
         //frappe.msgprint("The Revision number for "+'"'+serial_no+'"'+" numbers is set in the Serial Number document. "+'"'+serial_no+'"'+" number has been set with Revision Number "+'"'+HasRevisionNumberSerial+'"'+".You cannot change it in this transaction.");
            
         //  }//end of if revision test
        }
        //var df = frappe.meta.get_docfield("Stock Entry Detail", "revision_number", cur_frm.doc.name);

        //df.read_only = 1;
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

/*
frappe.ui.form.on("Stock Entry", "after_save", function(frm, cdt, cdn) {

    $.each(frm.doc.items, function(i, d) {
        var item_code = d.item_code;
        var revision_number = d.revision_number;
        console.log("revision_number", revision_number);
        if (revision_number != "") {
            var df = frappe.meta.get_docfield("Stock Entry Detail", "revision_number", cur_frm.doc.name);

            df.read_only = 1;
        }
    })
});*/

//Serial_no
frappe.ui.form.on("Stock Entry", "after_save", function(frm, cdt, cdn) {
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
        var Hs = null;
        Hs = fetch_has_serial_no(item_code);
        //console.log("Hs", Hs);
	if(purpose == "Manufacture"){
        console.log("work order is given");
        var work_order_update = work_order.concat("-");
        //console.log("work_order_update..", work_order_update);
        var duplicate_serial = item_code.concat("-").concat(work_order).concat("-");
        //console.log("duplicate_serial---------", duplicate_serial);

        var duplicate_serial_no = fetch_duplicate_serial_no(duplicate_serial);
        //console.log("duplicate_serial_no", duplicate_serial_no);
        var array = "";
        var num = 1;

        function pad(n) {
            var string = "" + n;
            var pad = "0000";
            n = pad.substring(0, pad.length - string.length) + string;
            return n;
        }
        if (target_warehouse != undefined && Hs == 1 && docstatus != 1 && purpose == "Manufacture") {

	    cur_frm.fields_dict.items.grid.toggle_reqd("revision_number", true)
            //console.log("entered in if");

            var test = duplicate_serial_no[0].serial_no;
            //console.log("nor", test);


            if (duplicate_serial_no[0].serial_no == null) {
                //console.log("test is null");

               
                for (var num = 1; num <= child_received_qty; num += 1) { //appending loop start
                    //console.log("num", num);
                    array = array.concat(item_code).concat("-").concat(work_order).concat("-").concat(pad(num)).concat("\n");

                    //console.log("Serial No", array);
                }
		 items[i]['serial_no'] = "";
                items[i]['serial_no'] = items[i]['serial_no'].concat(array);

            } else {
                //console.log("entered in if in else");
                var test = duplicate_serial_no[0].serial_no;
                //console.log("nor", test);
                var test1 = test.split('-');
                //console.log(">>>>>>>", test1);
                //console.log(test1.length - 1);
                var nor = test1[2];
                var nor = test1[test1.length - 1];
                //console.log("...........", nor);


                

                for (var z = 1; z <= child_received_qty; z += 1) {

                    nor++;
                    array = array.concat(item_code).concat("-").concat(work_order).concat("-").concat(pad(nor)).concat("\n");


                }
		items[i]['serial_no'] = "";
                items[i]['serial_no'] = items[i]['serial_no'].concat(array);




            }

        } else {

            //console.log("entered in else");
        	}
	}//end of manufacture block
	else{
	console.log("type is other than manufacture");

}//end of else manufacture block
    }//end of for loop
});

function fetch_has_serial_no(arg2) {
    //console.log("entered into function");
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
                //console.log(has_serial_no);
                //console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    return has_serial_no
}

function fetch_duplicate_serial_no(duplicate_serial) {
    //console.log("entered into 2nd function");
    //console.log("duplicate_serial", duplicate_serial);
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
                //console.log("checking--------------" + duplicate_serial_no_list);
                //console.log("readings-----------" + JSON.stringify(r.message));

            }
        }
    });
    //console.log("duplicate_serial_no_list", duplicate_serial_no_list);
    return duplicate_serial_no_list
}




frappe.ui.form.on("Stock Entry Detail", {


    revision_number: function(frm, cdt, cdn) {
        console.log("-----------");
        cur_frm.refresh_field("items")
        var d = locals[cdt][cdn];
        var item_code = d.item_code;
	var serial_no = d.serial_no;
        var batch_no = d.batch_no;
        var revision_no = d.revision_number;
	var source_warehouse=d.s_warehouse;
        console.log("revision_no----------------" + revision_no);

       console.log("source_warehouse----------------" + source_warehouse);

        var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
        var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
        var HasRevisionNumber = null;
        HasRevisionNumber = fetch_has_revision_number(batch_no);
        console.log("HasRevisionNumber", HasRevisionNumber);
         var HasRevisionNumberSerial = null;
        HasRevisionNumberSerial = fetch_has_revision_number_serial(serial_no) ;
        console.log("HasRevisionNumberSerial", HasRevisionNumberSerial);
        
            if(d.s_warehouse!=""&& d.revision_number!="" && HasRevisionNumberSerial!=""){
      
         frappe.msgprint("The Revision number for "+'"'+serial_no+'"'+" numbers is set in the Serial Number document. "+'"'+serial_no+'"'+" number has been set with Revision Number "+'"'+HasRevisionNumberSerial+'"'+".You cannot change it in this transaction.");
          frm.refresh_field("items")
	   
            d.revision_number = HasRevisionNumberSerial;
  
           }//end of revision test
        else  if(d.s_warehouse!=""&& d.revision_number!="" && HasRevisionNumber!=""){
      
         frappe.msgprint("The Revision number for "+'"'+batch_no+'"'+" numbers is set in the Batch Number document. "+'"'+batch_no+'"'+" number has been set with Revision Number "+'"'+HasRevisionNumber+'"'+".You cannot change it in this transaction.");
          frm.refresh_field("items")
	   
            d.revision_number = HasRevisionNumber;
  
           }//end of revision test
        
       
    }


})


//autofill revision in serial no doctype
frappe.ui.form.on("Stock Entry", "on_submit", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    
    var work_order = frm.doc.work_order;
   
    var docstatus = frm.doc.docstatus;
   
    var purpose = frm.doc.purpose;
    console.log("purpose",purpose);
    var parent=frm.doc.name;
    var items = frm.doc.items;
    
    for (var i = 0; i < items.length; i++) {
        var item_code = items[i]['item_code'];
        var source_warehouse = items[i]['s_warehouse'];
        console.log("source_warehouse.." + source_warehouse);
        var target_warehouse = items[i]['t_warehouse'];
    	var HasSerialNumber = null;
        HasSerialNumber = fetch_has_serial_no(item_code);
        console.log("HasSerialNumber", HasSerialNumber);
        var HasBatchNumber = null;
        HasBatchNumber = fetch_has_batch_no(item_code);
        console.log("HasBatchNumber", HasBatchNumber);
        if ((purpose=="Manufacture" ||purpose=="Material Receipt") && source_warehouse==undefined && HasSerialNumber==1){
        console.log("entered in if block after submit source_warehouse ");
        var serial_no= items[i]['serial_no'];
        console.log("serial_no", serial_no);
        
          var serial=fetch_revision_number_stock_entry(item_code,parent)
           console.log("-----------------",serial);
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

function fetch_revision_number_stock_entry(item_code,parent){
    console.log("entered into fetch_revision_number function");
    var revision_list = "";
    frappe.call({
        method: "nhance.api.get_revision_no_stock",
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

//To check item has serial or batch number
frappe.ui.form.on("Stock Entry Detail", "item_code", function(frm, cdt, cdn) {
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


