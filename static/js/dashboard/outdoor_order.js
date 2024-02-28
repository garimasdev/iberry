$(document).ready(function() {

    // Function to fetch updated order data
    function fetchOrders() {
        // Perform AJAX request to fetch updated order data
        $.ajax({
            type: "GET",
            url: "/dashboard/foods/outdoor-orders/", // Endpoint to fetch orders
            dataType: "json",
            success: function(response) {
                // Update the order page with the fetched data
                // You may need to implement this logic based on your page structure
                console.log("Fetched updated outdoor order data:", response);
                // Reload the page or update the UI as per your requirements
                window.location.reload();
            },
            error: function(error) {
                console.error("Error fetching outdoor orders:", error);
            }
        });
    }

    // Set interval to fetch orders every 30 seconds
    setInterval(fetchOrders, 30000);

    //place order
    $(document).on("click", ".delete-order", function(e) {
        e.preventDefault();
        const orderId = $(this).attr("id");
        const token = $(this).attr("token");
        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            type: "DELETE",
            url: "/outdoor-order/" + orderId + "/",
            contentType: 'application/json',
            success: function(response) {
                $(".order-" + orderId).remove();
                $('.response').empty().show().html('<div class="alert alert-success" role="alert">The order has been deleted.</div>').delay(2000).fadeOut(500);
                // refresh the current page
                window.location.reload();
            },
            error: function(error) {
                $('.response').empty().show().html('<div class="alert alert-danger">' + error.responseJSON + '</div>').delay(1500).fadeOut(3000);
            }
        });
    });

    // order update
    $(document).on("click", ".update-order", function(e) {
        const orderId = $(this).attr("id")
        const token = $(this).attr("token");
        const orderStatus = $("#" + orderId + "-order_status").val();
        const note = $("#" + orderId + "-note").val();
        console.log("Order Status", note)
        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            type: "PUT",
            url: "/outdoor-order/" + orderId + "/",
            data: {
                status: orderStatus,
                note: note,
            },
            success: function(response) {
                $('.response').empty().show().html('<div class="alert alert-success" role="alert">The order has been updated.</div>').delay(2000).fadeOut(500);
                window.location.reload();
            },
            error: function(error) {
                $('.response').empty().show().html('<div class="alert alert-danger">' + error.responseJSON + '</div>').delay(1500).fadeOut(3000);
            }
        });

    });

    // Export admission card to pdf
    $(document).on("click", ".print-order-btn", function() {
        const id = $(this).attr("id");
        const token = $(this).attr("token");

        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            type: "POST",
            url: "/dashboard/foods/outdoor-orders/" + id + "/",
            data: {},
            dataType: "json",
            beforeSend: function() {
                $("#print-modal .modal-body .order-slip").remove()
                $("#pdf-modal .modal-body").append('<div class="d-flex justify-content-center admission-export-loader">' +
                    '<div class="spinner-border" role="status">' +
                    '<span class="visually-hidden">Loading...</span>' +
                    '</div>' +
                    '</div>');
            },
            success: function(response) {
                console.log(response);
                $("#print-modal .modal-body .spinner-border").hide();
                // Construct the HTML for table rows using a loop
                var tableRows = '';
                response.outdoor_orders.items.forEach(function(element) {
                    tableRows += '<tr>' +
                        '<td>' + element.item.title + '</td>' +
                        '<td>' + element.quantity + '</td>' +
                        '<td>₹ ' + element.price + '</td>' +
                        '</tr>';
                });

                $("#print-modal .modal-body").append('<div class="container text-center mt-5 order-slip">' +
                    '<h2>Iberry</h2>' +
                    '<p class="lead">Order Voucher</p>' +
                    '<hr>' +
                    '<div class="row">' +
                    '<div class="col-md-4">' +
                    '<p><strong>Order ID:</strong> ' + response.outdoor_orders.order_id + '</p>' +
                    '</div>' +
                    '<div class="col-md-8">' +
                    '<p><strong>Customer Name:</strong> ' + response.name + '</p>' +
                    '</div>' +
                    '</div>' +
                    '<table class="table">' +
                    '    <thead>' +
                    '        <tr>' +
                    '            <th>Item</th>' +
                    '            <th>Quantity</th>' +
                    '            <th>Price</th>' +
                    '        </tr>' +
                    '    </thead>' +
                    '    <tbody>' + tableRows +
                    '    </tbody>' +
                    '</table>' +
                    '<p class="text-right"><strong>Total Price:</strong> ₹ ' + response.outdoor_orders.total_price + '</p>' +
                    '<p class="text-right"><strong>Mobile:</strong> ' + response.phone + '</p>' +
                    '<p class="text-right"><strong>Email:</strong> ' + response.email + '</p>' +
                    '<hr>' +
                    '<p class="text-right"><strong>Address:</strong> ' + response.address + '</p>' +
                    '<p class="text-right"><strong>Date:</strong> ' + response.outdoor_orders.created_at + '<strong></p>' +
                    '<hr>' +
                    '<p><em>Note: Thank you for your order!</em></p>' +
                    '</div>');
            },
            error: function(error) {
                $("#print-modal .modal-body .spinner-border").hide();
                $("#print-modal .modal-body").append('<div class="alert alert-danger" role="alert">' + error + '</div>');
            }
        });
    });
    $(".print-btn").on('click', function() {
        $('#print-modal .modal-body').printThis();
    });
});