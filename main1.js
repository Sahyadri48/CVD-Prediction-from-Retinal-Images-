$(document).ready(function () {
    // Init
    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        readURL(this);
    });

    // Predict
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);
        
        // Show loading animation
        $(this).hide();
        $('.loader').show();
        // console.log(form_data)
        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result
                key= Object.keys(data)[0];
                console.log("Risk Assessment Data "+key)
                $('.loader').hide();
                $('#result').fadeIn(600);
                $('#result').text(' Result:  ' + data);
                $("#patient-submit-button").show()
                $('#riskAssesment').val(key)
                console.log("Data"+data)
                console.log("Actual Value"+ $('#riskAssesment').val())
                console.log('Success!');

            },
        });
    });

        // $('#patient-data').on('submit', function(e) {
        $('#patient-submit-button').click(function() {
            // e.preventDefault();
            console.log("ajax used for patient-data form submission")
            var form = $("#patient-data"); // Reference to the form
            var url = form.attr('action');
            console.log("form-url")
            console.log(url);
            console.log(form.serialize());

            $.ajax({
                url: url,
                type: 'POST',
                data: form.serialize(),
                success: function(response) {
                    $('#database-msg').html(`${response.message}`);
                    console.log("Is it taking success from resonse")
                    if (response.success) {
                        // Add a button for adding a new patient
                        $("#add-new-data").show();
                        $("#patient-submit-button").hide();
                        
                    } else {
                       $("#patient-submit-button").val("Send Again")
                       $("#add-new-data").show();
                    }
                },
                error: function(xhr) {
                    $('#errorMessage').text("An error occurred: " + xhr.status + " " + xhr.statusText);
                }
            });
            return false;
        });

        $('#add-new-data').click(function() {
            window.location.href = 'index'; // Redirects the user to index.html
        });
    
    

});