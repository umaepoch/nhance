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
    console.log("Make BOM--------");

 	frappe.call({
        method: "nhance.nhance.doctype.boq_lite.boq_lite.validate_cf",
        args: {
            "items": cur_frm.doc.items,
        },
        async: false,
        callback: function(r) {
		    console.log("Response--------" + r.message);
		    if (r.message){
			frappe.model.open_mapped_doc({
        			method: "nhance.api.make_bom_for_boq_lite",
        			frm: cur_frm,
    			})
		    }
	}
    });
}

frappe.ui.form.on("BOQ Lite", "refresh", function(frm) {
    console.log("onload--------");
    if (cur_frm.doc.docstatus == 1 || cur_frm.doc.docstatus == 0) {
        var items = cur_frm.doc.items;
        var parentList = [];
        var main_item = cur_frm.doc.item;
        for (var i = 0; i < items.length; i++) {
            var item = items[i]['item_code'];
            var parentItem = items[i]['immediate_parent_item'];
            if (!parentList.includes(parentItem)) {
                parentList.push(parentItem);
            }
        } // end of for loop..

        $.each(frm.doc.items, function(i, d) {
            var item = d.item_code;
            var unit_of_measure = d.unit_of_measure;
            //console.log("------parentList------" + parentList);
            if (parentList.includes(item)) {
                d.is_raw_material = "No";
            } else {
                d.is_raw_material = "Yes";
            }
            refresh_field("is_raw_material");

            var cf = getConversionFactor(item, unit_of_measure);
            if (cf != 0) {
                d.conversion_factor = cf;
                update_boq_item(item, cf, cur_frm.doc.name, d.is_raw_material);
            } else {
                d.conversion_factor = cf;
                refresh_field("conversion_factor");
                refresh_field("items");
            }
        }); //end of each...
        refresh_field("items");
    }

});

frappe.ui.form.on("BOQ Lite", "before_submit", function(frm) {
    var items = cur_frm.doc.items;
    var parentList = [];
    var main_item = cur_frm.doc.item;
    for (var i = 0; i < items.length; i++) {
        var item = items[i]['item_code'];
        var parentItem = items[i]['immediate_parent_item'];
        if (!parentList.includes(parentItem)) {
            parentList.push(parentItem);
        }
    } // end of for loop..

    $.each(frm.doc.items, function(i, d) {
        var item = d.item_code;
        console.log("------parentList------" + parentList);
        if (parentList.includes(item)) {
            d.is_raw_material = "No";
        } else {
            d.is_raw_material = "Yes";
        }
        refresh_field("is_raw_material");
    }); //end of each...
    refresh_field(frm.doc.items);
});


frappe.ui.form.on("BOQ Lite", "refresh", function(frm) {
    cur_frm.set_query("unit_of_measure", "items", function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var uom_list = [];
        console.log("Item Code:: " + d.item_code);
        frappe.call({
            method: "nhance.api.get_uom_list",
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

        refresh_field("unit_of_measure");
        refresh_field("items");
    });

});


frappe.ui.form.on("BOQ Lite Item", {
    unit_of_measure: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item_code) {
            var cf = getConversionFactor(row.item_code, row.unit_of_measure);
            console.log("cf------" + cf);
            if (cf != 0) {
                row.conversion_factor = cf;
            } else {
                row.conversion_factor = cf;
                refresh_field("conversion_factor");
                refresh_field("items");
                frappe.throw(__("The UOM " + row.unit_of_measure + " you are using for Item " + row.item_code + " does not have a conversion factor defined in the Item Master for the Item's Stock UOM " + row.unit_of_measure + ". Please define the conversion factor in the item master and try again."));
                frappe.validated = false;
            }
        }
        refresh_field("conversion_factor");
        refresh_field("items");
    }
});

function update_boq_item(item_code, conversion_factor, name, is_raw_material) {
    frappe.call({
        method: "nhance.api.update_boq_item",
        args: {
            "item_code": item_code,
            "conversion_factor": conversion_factor,
            "name": name,
            "is_raw_material": is_raw_material
        },
        async: false,
        callback: function(r) {}
    });
}

function getConversionFactor(item_code, unit_of_measure) {
    var cf = 0;
    frappe.call({
        method: "nhance.api.get_conversion_factor",
        args: {
            "parent": item_code,
            "uom": unit_of_measure
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                //console.log("conversion_factor------" + r.message);
                cf = r.message;
            }
        }
    });
    return cf;
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
