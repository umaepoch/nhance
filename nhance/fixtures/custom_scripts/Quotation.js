frappe.ui.form.on("Quotation", "refresh", function(frm) {
        cur_frm.add_custom_button(__('Make Interactions'), cur_frm.cscript['Make Interactions'], __("Make"));
	             
});
cur_frm.cscript['Make Interactions'] = function() {
    frappe.model.open_mapped_doc({
        method: "nhance.api.make_interactions_quotation",
        frm: cur_frm
    })
}
