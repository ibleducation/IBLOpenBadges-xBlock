function StudentViewBadge(runtime, element) {
	$("#badge_claimer").submit(function(event) {
		// Stop the browser from submitting the form.
		event.preventDefault();
        	//events
        	var $formdata = $("#badge_claimer").serialize();
		var handlerUrl = runtime.handlerUrl(element, 'student_claim_save');
        	$.ajax({
                	type : 'POST',
	                url : handlerUrl,
        	        data : JSON.stringify($formdata),
                	success : function(data, status) {
                        	$('#resForm').show();
                        	$('#resForm').html(data['result']);
	                        $('#badge_claimer').hide();
                	},
	                error : function() {
        	                alert("Could not proceed");
                	}
	        });    
	});
}

