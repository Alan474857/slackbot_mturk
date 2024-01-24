$(document).ready(function() {
    // Settings
    $.notify.defaults({
        className:"error", 
        elementPosition:"right",
        autoHideDelay: 2500,
    });

    // click function
	$(document).on("click", ".radio_answer", function() {
        // reset
        $(this).parents(".radio_button").find(".radio_answer[checked='checked']").removeAttr("checked");
        // set
        $(this).attr("checked", "checked");
    });

	// locks
    var time_lock = new TimeLock(60, "#submit_btn");

    // submit
    $(document).on("click", "#submit_btn", function(evt) {
        var target = $(evt.target);

        $("#warning").text("");

        // check locks
        if (time_lock.is_locked) {
            $.notify(target, "Please rank the instances carefully.")
            return;
        }

        // check answers
        var questions = $(".radio_button");
        var answers = $('.radio_answer[checked="checked"]');
        if (questions.length != answers.length) {
            $.notify(target, "Please fill up all the questions.")
            return;
        }

        // gather answers
        var results = {};
        for(var i = 0; i < answers.length; i++) {
            results[$(questions[i]).attr("name")] = $(answers[i]).attr("value");
        }
        $('input[name="answer"]').val(JSON.stringify(results));

		console.log(JSON.stringify(results));

        // submit
        $.notify($("#submit_btn"), "Submitting...", {
            className:"success", 
            elementPosition:"right",
            autoHideDelay: 5000,
            showDuration: 100,
            position: "top",
        });
        setTimeout(check_and_submit, 1500);
        
    });

    // delaying submit for checking
    var check_and_submit = function() {
        if ($('input[name="answer"]').val().trim() == "") {
            $.notify($("#submit_btn"), "Please fill up all the questions.");
            return;
        } else {
            $("#mturk_form").submit();
        }
    };

});
