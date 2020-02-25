frappe.ui.form.on("Batch", "refresh", function(frm, cdt, cdn) {
 
 var d = locals[cdt][cdn];
    var item_code = d.item;
    console.log("item_code", item_code);



var revision=fetch_batch_revision_no(item_code);
console.log("revision",revision[0].revision_number);
var RevisionNumber=revision[0].revision_number;
cur_frm.set_value("revision_number",RevisionNumber)
    //frm.refresh_field("revision_number")
});
function fetch_batch_revision_no(item_code){
    console.log("entered into fggggggggggggggggg function");
    var batch_revision_no = "";
    frappe.call({
        method: "nhance.api.get_batch_revision_no",
        args: {
            
            "item_code":item_code
           
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                batch_revision_no = r.message;
                console.log("checking--------------" + batch_revision_no[0].revision_number);
                console.log("readings-----------" + JSON.stringify(r.message));
               

            }
        }

   });
    console.log("batch_revision_no", batch_revision_no);
    return batch_revision_no
}
