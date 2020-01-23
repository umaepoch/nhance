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
