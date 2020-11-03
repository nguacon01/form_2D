$(document).ready(function () {
    //upload experiment folder
    $('#upload_2_btn').click(function (e) {
        e.preventDefault();
        var form_data = new FormData($('#uploadform')[0]);

        $.ajax({
            type: 'POST',
            url: '/metadata/upload_folder',
            data: form_data,
            contentType: false,
            processData: false,
            dataType: 'json',
            success: function (response) {
                console.log(response);
                var data = JSON.parse(response.data);
                var select_str = "";
                $.each(data, function (key, val) {
                    select_str += "<option value='" + key + "'>" + val + "</option>";
                });
                $("select#expList").append(select_str);
                //pop up notification
                toastr.success(response.success);
            },
            error: function (response) {
                //pop up notification
                toastr.warning(reponse.error);
            }
        })
    });

    //selet experiment
    $("#expList").on("change", function () {
        var selected_val = $(this).val();
        console.log(JSON.stringify({ "selected_exp": selected_val }));
        $.ajax({
            type: "POST",
            dataType: "json",
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ "selected_exp": selected_val }),
            url: "/metadata/select_experiment_2",
            success: function (response) {
                var data = JSON.parse(response.data);
                console.log(data);
                $.each(data, function (key, val) {
                    $("input#selected_exp").val(selected_val);
                    if (val) {
                        if ($("#" + key).is("input") || $("#" + key).attr("type", "date").is("input")) {
                            $("#" + key).val(val);
                        }
                        if ($("input[name=" + key + "]").is("input:radio") || $("input[name=" + key + "]").is("input:checkbox")) {
                            $("input[name=" + key + "][value=" + val +"]").attr("checked", true);
                        }
                    }
                });
                toastr.success(response.success);
            },
            error: function (response) {
                toastr.warning(reponse.error);
            }
        });
    });
});