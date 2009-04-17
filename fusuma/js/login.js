/* login.js */

var fsmLogin = {
	onSubmit: function() {

		form = document.forms["fsm-login-form"];

		if( form.use_challenge.checked ) {
			cr_key = form.cr_key.value;
			cr_auth = form.cr_auth.value;
			password = form.password.value;

			key = cr_key + $.sha1(password);
			hashedPasswd = $.sha1(key);

			form.cr_auth.value = "on";
			form.password.value = hashedPasswd;
		}
		//form.submit()
		return true;
	
	}
};

$(function(){
		$("#fsm-login-form").submit(fsmLogin.onSubmit);
		document.forms["fsm-login-form"].use_challenge.checked = true;
	});
