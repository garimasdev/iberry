$(document).ready(function() {
    // order update
    $(document).on("click", ".update-order", function(e) {
        const complainId = $(this).attr("id")
        const token = $(this).attr("token");
        const compalinStatus = $("#" + complainId + "-order_status").val();
        const note = $("#" + complainId + "-note").val();
        console.log("Complain Status", note)
        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            type: "PUT",
            url: "/dashboard/complaints/update/" + complainId + "/",
            data: {
                status: compalinStatus,
                note: note,
            },
            success: function(response) {
                $('.response').empty().show().html('<div class="alert alert-success" role="alert">The complain has been updated.</div>').delay(2000).fadeOut(500);
                window.location.reload();
            },
            error: function(error) {
                $('.response').empty().show().html('<div class="alert alert-danger">' + error.responseJSON + '</div>').delay(1500).fadeOut(3000);
            }
        });

    });
});