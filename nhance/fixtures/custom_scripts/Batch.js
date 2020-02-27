frappe.ui.form.on("Batch", "after_save", function(frm, cdt, cdn) {
 
 var d = locals[cdt][cdn];
    var item_code = d.item;
    console.log("item_code", item_code);

var df = frappe.meta.get_docfield("Batch", "revision_number", cur_frm.doc.name);
                df.read_only = 1;


});

