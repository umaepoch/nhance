// Copyright (c) 2019, Epoch and contributors
// For license information, please see license.txt
frappe.ui.form.on('BOQ Lite', {
    refresh: function(frm) {
        if (frm.doc.docstatus == "1") {
            cur_frm.add_custom_button(__('Make BOM'), cur_frm.cscript['Make BOM'], __("Make"));
            cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
        }
    }
});


cur_frm.cscript['Make BOM'] = function(cdt, cdn) {
    $.each(cur_frm.doc.items, function(i, d) {
            var item = d.item_code;
	    var obj = fetch_parent_list(cur_frm.doc.name);
	    var parentList = obj.toString().split(",");
            //console.log("------parentList------" + parentList);
            if (parentList.includes(item)) {
                d.is_raw_material = "No";
            } else {
                d.is_raw_material = "Yes";
            }
            refresh_field("is_raw_material");

            update_boq_lite_item(item, cur_frm.doc.name, d.is_raw_material);
           
        }); //end of each...
        refresh_field("items");

    frappe.model.open_mapped_doc({
        method: "nhance.api.make_bom_for_boq_lite",
        frm: cur_frm
    })
}


frappe.ui.form.on("BOQ Lite", "refresh", function(frm) {
    cur_frm.set_query("stock_uom", "items", function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var uom_list = [];
        console.log("Item Code:: " + d.item_code);
        frappe.call({
            method: "nhance.api.get_stock_uom",
            args: {
                "item_code": d.item_code,
            },
            async: false,
            callback: function(r) {
                console.log("Length" + r.message.length);
                console.log("uom_list :" + uom_list);
                for (var i = 0; i < r.message.length; i++) {
                    uom_list.push(r.message[i][0]);
                    console.log("uom_list" + uom_list);
                }
            }
        });

        return {
            "filters": [
                ["UOM", "name", "in", uom_list]
            ]
        }

        refresh_field("stock_uom");
        refresh_field("items");
    });

});


function fetch_parent_list(boq_lite){
var parentList = [];
frappe.call({
        method: "nhance.nhance.doctype.boq_lite.boq_lite.fetch_parent_list",
        args: {
            "parent": boq_lite,
        },
        async: false,
        callback: function(r) {
		if (r.message){
			//console.log("ParentList-----"+r.message + "length---"+ r.message.length);
			parentList = r.message;
		}
	}
    });
return parentList;
}

function update_boq_lite_item(item_code, name, is_raw_material) {
    frappe.call({
        method: "nhance.api.update_boq_lite_item",
        args: {
            "item_code": item_code,
            "name": name,
            "is_raw_material": is_raw_material
        },
        async: false,
        callback: function(r) {}
    });
}


// Start of- Repeat item validation with respective immediate_parent_item
frappe.ui.form.on("BOQ Lite Item", "immediate_parent_item", function(frm, doctype, name) {
    var itemsMap = new Map();
    var items = frm.doc.items;
    var row = locals[doctype][name];
    var row_parent = row.immediate_parent_item;
    for (var i = 0; i < items.length; i++) {
        var item = items[i]['item_code'];
        var parent = items[i]['immediate_parent_item'];
        if (parent == row_parent) {
            if (itemsMap.has(item)) {
                frappe.throw(__("Please remove Duplicate Entry of Item " + row.item_code + " for Immediate Parent Item: " + row_parent));
                frappe.validated = false;
            } else {
                itemsMap.set(item, parent);
            }
        }
    }
});
// End of- Repeat item validation with respective immediate_parent_item
