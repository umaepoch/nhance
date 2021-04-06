frappe.ui.form.on("Sales Invoice", {
    flag_qr_code_as_public: function(frm, cdt, cdn)  {
var d = locals[cdt][cdn];
var attached_to_name = d.name;
var name=fetch_has_serial_no(attached_to_name);
console.log("---",name);
var qr_code_path=update_file_to_public(name);
console.log("qr_code_path",qr_code_path);
cur_frm.refresh();
cur_frm.save();
}
        });

function fetch_has_serial_no(attached_to_name) {
    console.log("entered into function");
    var name_of_file = "";
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            'doctype': 'File',
            'fieldname': "name",

            'filters': {
                attached_to_name: attached_to_name,
                attached_to_field:"qrcode_image",
            }
        },
        async: false,
        callback: function(r) {
            if (r.message) {
                name_of_file = r.message.name;
               

            }
        }
    });
    return name_of_file
}

function update_file_to_public(name){
	
	frappe.call({
		method: 'nhance.api.qr_code_path_to_public',
		args: {
		   "name":name
		},
		async: false,
		callback: function(r) {
		    
		}
    });
    
}
