frappe.ui.form.on("Serial No", {
    create_single_pdf: function(frm, cdt, cdn) {
     console.log("Entered------");
     var d = locals[cdt][cdn];
     var attached_to_name = d.name;
     console.log("attached_to_name", attached_to_name);
     var attached_to_doctype = d.doctype;
     console.log("attached_to_doctype", attached_to_doctype);
 
    
     var merger_pdf = fetch_file_link(cur_frm.doc.name,attached_to_name);
     console.log("merged_pdf............", merger_pdf);
     
     var file_link4 = "<a href="+ merger_pdf+" " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>";
     cur_frm.set_value("pch1_combined_pdf", file_link4.toString());
     frm.refresh_field("pch1_combined_pdf");
     frm.set_df_property("pch1_combined_pdf", "read_only", frm.doc.__islocal ? 0 : 1);
     frm.save();
    }
 });
 
 
 function fetch_file_link(attached_to_name){
     console.log("entered into get_merge_file_url function");
     var file_url_list = "";
     frappe.call({
         method: "jiq.api.combine",
        args: {
             
             "attached_to_name":attached_to_name
         },
         async: false,
         callback: function(r) {
             if (r.message) {
                 file_url_list = r.message;
                 //console.log("checking--------------" + build_sheet);
                 //console.log("readings-----------" + JSON.stringify(r.message));
             }
         }
 
    });
     //console.log("file_url_list.............", file_url_list);
     return file_url_list
 }