frappe.ui.form.on("Serial No", "refresh", function(frm, cdt, cdn) {
    console.log("Entered------");
    var d = locals[cdt][cdn];
    var attached_to_name = d.name;
    console.log("attached_to_name", attached_to_name);
    var attached_to_doctype = d.doctype;
    console.log("attached_to_doctype", attached_to_doctype);
   
    var file_url_pressure_test = fetch_file_url_pressure(attached_to_name);
    console.log("file_url_pressure_test", file_url_pressure_test);
    var file_link1 = "<a href=" + file_url_pressure_test[0]['File_url'] + " " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>"
    console.log("file_link1", file_link1);
    cur_frm.set_value("pch1_pressure_test", file_link1.toString())
    frm.refresh_field("pch1_pressure_test")
   frm.set_df_property("pch1_pressure_test", "read_only", frm.doc.__islocal ? 0 : 1);

   var file_url_coc = fetch_file_url_coc(attached_to_name);
    console.log("file_url_coc", file_url_coc);
    var file_link2 = "<a href="+ file_url_coc[0]['File_url'] +" " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>"
     
    cur_frm.set_value("pch1_coc", file_link2.toString())
    frm.refresh_field("pch1_coc")
    frm.set_df_property("pch1_coc", "read_only", frm.doc.__islocal ? 0 : 1);

    var file_url_build_sheet = fetch_file_url_build_sheet(attached_to_name);
    console.log("file_url_build_sheet", file_url_build_sheet);
    var file_link3 ="<a href="+ file_url_build_sheet[0]['File_url'] +" " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>"
    cur_frm.set_value("pch1_build_sheet", file_link3.toString())
    frm.refresh_field("pch1_build_sheet")
     frm.set_df_property("pch1_build_sheet", "read_only", frm.doc.__islocal ? 0 : 1);
     
     var file_url_dnv_gl = fetch_file_dnv_gl(attached_to_name);
    console.log("file_url_dnv_gl", file_url_dnv_gl);
    var file_link4 = "<a href="+ file_url_dnv_gl[0]['File_url'] +" " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>"
     
    cur_frm.set_value("pch1_dnv_gl_product_certificate", file_link4.toString())
    frm.refresh_field("pch1_dnv_gl_product_certificate")
    frm.set_df_property("pch1_dnv_gl_product_certificate", "read_only", frm.doc.__islocal ? 0 : 1);

var file_url_eu_declaration = fetch_file_eu_declaration(attached_to_name);
    console.log("file_url_eu_declaration", file_url_eu_declaration);
    var file_link5 = "<a href="+ file_url_eu_declaration[0]['File_url'] +" " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>"
     
    cur_frm.set_value("pch1_eu_declaration_of_conformity", file_link5.toString())
    frm.refresh_field("pch1_eu_declaration_of_conformity")
    frm.set_df_property("pch1_eu_declaration_of_conformity", "read_only", frm.doc.__islocal ? 0 : 1);



var merger_pdf = fetch_file_link(cur_frm.doc.name,attached_to_name);
     console.log("merged_pdf............",merger_pdf);
   
    var combined_file_url = fetch_combined_file(attached_to_name);
    console.log("combined_file_url", combined_file_url);
    var file_link4 = "<a href= " + combined_file_url[0]['File_url']+" " + "target='_blank'><img src='/files/pdf.jpg'  width='25' height='25'></a>"
    cur_frm.set_value("pch1_combined_pdf", file_link4.toString())
    frm.refresh_field("pch1_combined_pdf")
	frm.set_df_property("pch1_combined_pdf", "read_only", frm.doc.__islocal ? 0 : 1);


});


function fetch_file_url_pressure(attached_to_name) {
    console.log("entered into fetch_file_url_pressure function");
    var pressure_test = "";
    frappe.call({
        method: "nhance.api.get_file_url_pressure",
        args: {
            "attached_to_name": attached_to_name
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                pressure_test = r.message;
                console.log("checking--------------" + pressure_test);
                console.log("readings-----------" + JSON.stringify(r.message));


            }
        }

    });
    console.log("pressure_test", pressure_test);
    return pressure_test
}

function fetch_file_url_coc( attached_to_name) {
    console.log("entered into fetch_file_url_coc function");
    var coc = "";
    frappe.call({
        method: "nhance.api.get_file_url_coc",
        args: {
            "attached_to_name": attached_to_name
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                coc = r.message;
                console.log("checking--------------" + coc);
                console.log("readings-----------" + JSON.stringify(r.message));


            }
        }

    });
    console.log("coc", coc);
    return coc
}


function fetch_file_url_build_sheet(attached_to_name) {
    console.log("entered into fetch_file_url_build_sheet function");
    var build_sheet = "";
    frappe.call({
        method: "nhance.api.get_file_url_build_sheet",
        args: {
            "attached_to_name": attached_to_name
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                build_sheet = r.message;
                console.log("checking--------------" + build_sheet);
                console.log("readings-----------" + JSON.stringify(r.message));


            }
        }

    });
    console.log("build_sheet", build_sheet);
    return build_sheet
}

function fetch_file_dnv_gl(attached_to_name) {
    console.log("entered into fetch_file_dnv_gl function");
    var DNV_GL_Product_Certificate = "";
    frappe.call({
        method: "nhance.api.get_file_url_DNV_GL_Product_Certificate",
        args: {
            "attached_to_name": attached_to_name
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                DNV_GL_Product_Certificate = r.message;
                console.log("checking--------------" + DNV_GL_Product_Certificate);
                console.log("readings-----------" + JSON.stringify(r.message));


            }
        }

    });
    console.log("DNV_GL_Product_Certificate", DNV_GL_Product_Certificate);
    return DNV_GL_Product_Certificate
}

function fetch_file_eu_declaration(attached_to_name) {
    console.log("entered into fetch_file_dnv_gl function");
    var EU_Declaration = "";
    frappe.call({
        method: "nhance.api.get_file_url_EU_Declaration",
        args: {
            "attached_to_name": attached_to_name
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                EU_Declaration = r.message;
                console.log("checking--------------" + EU_Declaration);
                console.log("readings-----------" + JSON.stringify(r.message));


            }
        }

    });
    console.log("EU_Declaration", EU_Declaration);
    return EU_Declaration
}

function fetch_file_link(attached_to_name){
    console.log("entered into get_merge_file_url function");
    var file_url_list = "";
    frappe.call({
        method: "nhance.api.get_merge_file_url",
        args: {
            
            "attached_to_name":attached_to_name
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                file_url_list = r.message;
                console.log("checking--------------" + file_url_list);
                console.log("readings-----------" + JSON.stringify(r.message));
               for (var i = 0; i < file_url_list.length; i++) {
                    console.log("Name:" + file_url_list[i]);
                   
                }

            }
        }

   });
    console.log("file_url_list.............", file_url_list);
    return file_url_list
}

function fetch_combined_file(attached_to_name) {
    console.log("entered into fetch_combined_file function");
    var combined = "";
    frappe.call({
        method: "nhance.api.get_combined_pdf",
        args: {
            "attached_to_name":attached_to_name
            
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                combined = r.message;
                console.log("checking--------------" + combined);
                console.log("readings-----------" + JSON.stringify(r.message));


            }
        }

    });
    console.log("combined", combined);
    return combined
}
