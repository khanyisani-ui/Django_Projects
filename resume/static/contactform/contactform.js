jQuery(document).ready(function($) {
  "use strict";

  // Contact Form Submission
  $('form.contactForm').submit(function() {
    var f = $(this).find('.form-group'),
        ferror = false,
        emailExp = /^[^\s()<>@,;:\/]+@\w[\w\.-]+\.[a-z]{2,}$/i;

    // Validate form fields
    f.children('input').each(function() {
      var i = $(this);
      var rule = i.attr('data-rule');
      
      if (rule !== undefined) {
        var ierror = false;
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }

        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;

          case 'minlen':
            if (i.val().length < parseInt(exp)) {
              ferror = ierror = true;
            }
            break;

          case 'email':
            if (!emailExp.test(i.val())) {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validation').html((ierror ? (i.attr('data-msg') !== undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });

    f.children('textarea').each(function() {
      var i = $(this);
      var rule = i.attr('data-rule');
      
      if (rule !== undefined) {
        var ierror = false;
        var pos = rule.indexOf(':', 0);
        if (pos >= 0) {
          var exp = rule.substr(pos + 1, rule.length);
          rule = rule.substr(0, pos);
        } else {
          rule = rule.substr(pos + 1, rule.length);
        }

        switch (rule) {
          case 'required':
            if (i.val() === '') {
              ferror = ierror = true;
            }
            break;

          case 'minlen':
            if (i.val().length < parseInt(exp)) {
              ferror = ierror = true;
            }
            break;
        }
        i.next('.validation').html((ierror ? (i.attr('data-msg') != undefined ? i.attr('data-msg') : 'wrong Input') : '')).show('blind');
      }
    });

    // If there are no validation errors
    if (ferror) return false;
    else var str = $(this).serialize();

    $.ajax({
      type: "POST",
      url: "/send-message/",
      data: str + '&csrfmiddlewaretoken=' + csrf_token,  // Include CSRF token
      success: function(response) {
        // If everything went well, the backend will handle the redirect
        window.location.href = '/';  // Redirect to the homepage after successful submission
      },
      error: function() {
        // Show a generic error message in case of failure
        $("#sendmessage").removeClass("show");
        $("#errormessage").addClass("show").html("An error occurred. Please try again later.");
      }
    });

    return false; // Prevent default form submission
  });
});
