// Copyright (c) 2019, Epoch and contributors
// For license information, please see license.txt

frappe.ui.form.on('RARB Warehouse', {
	onload: function(frm) {
		cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_type", true)
		if (cur_frm.doc.__islocal){
			if(cur_frm.doc.amended_from == undefined){
				cur_frm.set_df_property("rarbs", "hidden", true);
			}
			else if(cur_frm.doc.amended_from != undefined){
				cur_frm.set_df_property("make_rarbs", "hidden", true);
			}
		}
		if(cur_frm.doc.warehouse != undefined){
			cur_frm.set_df_property("warehouse", "read_only", true);
		}
		//console.log("current date -----------"+cur_frm.doc.start_date);
		if (!cur_frm.doc.__islocal){
			
				
			
			//console.log("end date from new changes-----------"+cur_frm.doc.end_date);
			var today = new Date();
			//console.log("today -------------"+today);
			//var cur_date = today.getDate();
			var cur_date_py = "";
			if(cur_frm.doc.end_date != undefined && cur_frm.doc.end_date != ""){
				var higher_date = get_higher_date(cur_frm.doc.warehouse,cur_frm.doc.start_date,cur_frm.doc.name);
				if(higher_date != undefined){
					//console.log("higher_date--------------"+higher_date);
					cur_frm.set_value("end_date", higher_date);
				}
				else{
					//console.log("hieger date is not coming");
					cur_frm.set_value("end_date", "");
				}
				//console.log("higher_date----------------"+higher_date);
				cur_date_py = get_current_date_format(cur_frm.doc.end_date, cur_frm.doc.start_date, cur_frm.doc.warehouse);
				set_is_active(cur_frm.doc.name,cur_date_py,cur_frm.doc.docstatus);
				//console.log("cur_date_py-------------"+cur_date_py);
				/*if(cur_date_py == true){
				    if(cur_frm.doc.docstatus ==1){
					cur_frm.set_value("is_active", 1);
				    }
				     else if(cur_frm.doc.docstatus == 2){
						cur_frm.set_value("is_active", 0);
					}
				}else if (cur_date_py == false){
					cur_frm.set_value("is_active", 0);
				}*/
				
			}else{
				var higher_date = get_higher_date(cur_frm.doc.warehouse,cur_frm.doc.start_date,cur_frm.doc.name);
				if(higher_date != undefined){
					cur_frm.set_value("end_date", higher_date);
				}
				else{
					cur_frm.set_value("end_date", "");
				}
				var next_start_date = get_next_start_date(cur_frm.doc.warehouse,cur_frm.doc.start_date,cur_frm.doc.name);
				//console.log("next_start_date------------"+next_start_date);
				set_is_active(cur_frm.doc.name,next_start_date,cur_frm.doc.docstatus);
				//console.log("cur_date_py-------------"+next_start_date);
				/*if(next_start_date == true){
				     if(cur_frm.doc.docstatus ==1){
					cur_frm.set_value("is_active", 1);
					}
				     else if(cur_frm.doc.docstatus == 2){
						cur_frm.set_value("is_active", 0);
					}
				}else if (next_start_date == false){
					cur_frm.set_value("is_active", 0);
				}*/
			}
				}
		
	},
	make_rarbs : function(){
		cur_frm.set_df_property("rarbs", "hidden", false);
		for(var i = 1; i <= cur_frm.doc.number_of_rooms; i++){
			for(var j = 1; j <=  cur_frm.doc.number_of_aisles_per_room; j++){
				for(var k =1; k <= cur_frm.doc.number_of_racks_per_aisle; k++){
					for(var l = 1; l <= cur_frm.doc.number_of_bins_per_rack; l++){
						var rarb_id = i+"-"+j+"-"+k+"-"+l;
						var child = cur_frm.add_child("rarbs");
						//console.log(rarb_id);
				                frappe.model.set_value(child.doctype, child.name, "rarb_id", rarb_id);
					}
				}
			}
		cur_frm.refresh_field('rarbs');
		}
		cur_frm.set_df_property("make_rarbs", "hidden", true);
	},
	on_submit: function(frm){
		var rarb_id = create_rarb_id(cur_frm.doc.name, cur_frm.doc.warehouse,cur_frm.doc.rarbs);
	}/*,
	start_date : function(frm){
		if (cur_frm.doc.start_date == frappe.datetime.get_today()){
			frappe.msgprint("Start Date Cannot be Today date please select future date");
		}
	}*/
		
});
frappe.ui.form.on('RARB Warehouse', "on_submit", function(frm , cdt , cdn){
	//console.log("submitted-----------------");
	
	var update_previouse_doc_status = get_update_pre_doc(cur_frm.doc.warehouse, cur_frm.doc.start_date, cur_frm.doc.name);
});
frappe.ui.form.on("RARB Warehouse" ,{
	is_active: function(frm){
		if(cur_frm.doc.docstatus = 1){
			var update_doc_end_date_is_active = get_update_is_active(cur_frm.doc.name, cur_frm.doc.is_active);
		}
		if(cur_frm.doc.docstatus == 0){
			cur_frm.save();
		}
	}

});
frappe.ui.form.on("RARB Warehouse","onload", function(frm, cdt, cdn){
	$.each(frm.doc.rarbs, function(i, item) {
		//console.log("rarb active ---------"+item.rarb_active);
		if(item.rarb_active == "Yes"){
			 cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_type", true)
			}
		else{
			 cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_type", false)
		}
	})
	frappe.ui.form.on("RARB Warehouse Item", {

		 rarb_active: function (frm, cdt, cdn){
			//console.log("hello-------------");
			var d = locals[cdt][cdn];
			if(d.rarb_active == "Yes"){
				 cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_type", true)
				}
			else if(d.rarb_active == "No"){
				 cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_type", false)
			}
		},
		rarb_type: function(frm ,cdt ,cdn){
			var d = locals[cdt][cdn];
			if(d.rarb_type == "Specific Item"){
				 cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_item", true)
				}
			else if(d.rarb_type == "Any Item"){
				//console.log("rarb type is not specific item");
				 cur_frm.fields_dict.rarbs.grid.toggle_reqd("rarb_item", false)
			}
		}
	});
});
function get_higher_date(warehouse,start_date,name){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_higher_date',
        args: {
	    "warehouse":warehouse,
            "start_date":start_date,
	    "name":name
        },
        async: false,
        callback: function(r) {
            //console.log("supplier criticality..." + JSON.stringify(r.message));
           supplier_criticality = r.message;
	   // end_date = (new Date(supplier_criticality-1));
	  // console.log("end date -------------"+supplier_criticality);
        }
    });
    return supplier_criticality;


}
function get_current_date_format(end_date,start_date,warehouse){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_end_foramte_date',
        args: {
	    "end_date":end_date,
	    "start_date":start_date,
	    "warehouse": warehouse
        },
        async: false,
        callback: function(r) {
           // console.log("supplier criticality..." + JSON.stringify(r.message));
           supplier_criticality = r.message;
	   // end_date = (new Date(supplier_criticality-1));
	  // console.log("end date -------------"+supplier_criticality);
        }
    });
    return supplier_criticality;


}
function get_next_start_date(warehouse,start_date,name){
	//console.log("no end date");
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_next_start_date',
        args: {
	  "start_date":start_date,
	   "warehouse":warehouse,
	   "name":name
        },
        async: false,
        callback: function(r) {
           // console.log("supplier criticality..." + JSON.stringify(r.message));
           supplier_criticality = r.message;
	   // end_date = (new Date(supplier_criticality-1));
	  // console.log("current date------------"+supplier_criticality);
        }
    });
    return supplier_criticality;


}
function get_update_pre_doc(warehouse,start_date,name){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_update_pre_doc',
        args: {
	  "start_date":start_date,
	   "warehouse":warehouse,
	   "name":name
        },
        async: false,
        callback: function(r) {
            //console.log("supplier criticality..." + JSON.stringify(r.message));
           supplier_criticality = r.message;
	   // end_date = (new Date(supplier_criticality-1));
	//   console.log("current date------------"+supplier_criticality);
        }
    });
    return supplier_criticality;


}
function get_update_doc(name,end_date){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_update_doc',
        args: {
	   "name":name,
	   "end_date":end_date
        },
        async: false,
        callback: function(r) {
           // console.log("supplier criticality..." + JSON.stringify(r.message));
           supplier_criticality = r.message;
	   // end_date = (new Date(supplier_criticality-1));
	//   console.log("current date------------"+supplier_criticality);
        }
    });
    return supplier_criticality;
}
function get_update_is_active(name,is_active){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.get_update_is_active',
        args: {
	   "name":name,
	   "is_active":is_active
        },
        async: false,
        callback: function(r) {
           // console.log("supplier criticality..." + JSON.stringify(r.message));
           supplier_criticality = r.message;
	   // end_date = (new Date(supplier_criticality-1));
	//  console.log("current date------------"+supplier_criticality);
        }
    });
    return supplier_criticality;

}
function create_rarb_id(name, warehouse,rarbs){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.create_rarb_id',
        args: {
	   "name":name,
	   "warehouse":warehouse,
	   "rarbs":rarbs
        },
        async: false,
        callback: function(r) {
           // console.log("supplier criticality..." + JSON.stringify(r.message));
           
        }
    });
    return supplier_criticality;
}
function set_is_active(name,cur_date_py,docstatus){
	var supplier_criticality = "";
	  frappe.call({
        method: 'nhance.nhance.doctype.rarb_warehouse.rarb_warehouse.set_is_active',
        args: {
	   "name":name,
	   "cur_date_py":cur_date_py,
	   "docstatus":docstatus
        },
        async: false,
        callback: function(r) {
           // console.log("supplier criticality..." + JSON.stringify(r.message));
           
        }
    });
}
