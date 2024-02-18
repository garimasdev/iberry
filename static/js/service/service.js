$(document).ready(function() {

    $(".cart-icon").on("click", function(e) {
        $(".cart-bar").toggleClass('active');
    });


    //add to cart
    $(".add-to-cart").on("click", function(e) {
        const room_id = $(this).attr('room_id');
        const token = $(this).attr('token');
        const service_id = $(this).attr('id');
        const qunatity = $("#quantity-" + service_id).val();
        const price = $(this).attr('price');

        // console.log("The prices", selectedData)
        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            url: '/service-cart/',
            type: 'POST',
            data: {
                room: room_id,
                service: service_id,
                qunatity: qunatity,
                price: price,

            },
            dataType: 'json',
            success: function(response) {
                $('#add-to-cart-' + service_id).modal('hide');
                const cart_id = response.id;
                const image = $(".item-" + service_id).find("img").attr("src");
                const name = $(".item-" + service_id).find(".service_name").text();
                const price = $(".item-" + service_id).find(".price").attr("value");

                // const price = $(".item-" + food_id).find(".product_price strong").text();
                $(".cart-bar .cart-list").append('<li id="cart-item-' + cart_id + '" cart_id="' + cart_id + '" class="cart">' +
                    '<div class="product-box">' +
                    '<img src="' + image + '"/>' +
                    '<div class="content">' +
                    '<p class="name">' + name + '</p>' +
                    '<strong class="price">₹ ' + price + '</strong>' +
                    '<span class="quantity"> Qty: ' + qunatity + '</span>' +
                    '</div>' +
                    '</div>' +
                    '<span class="close delete-cart-item" id="' + cart_id + '" token="' + token + '"><i class="bi bi-x-lg"></i></span>' +
                    '</li>');
                $(".total_price").text("₹ " + response.total_price);
                $(".cart-icon span").text(response.total_items);
            },
            error: function(error) {
                $('#add-to-cart-' + service_id).modal('hide');
                console.log("The error", error.responseJSON);
                if (error.responseJSON.non_field_errors[0] == "The fields room, service must make a unique set.") {
                    $('.response').empty().show().html('<div class="alert alert-danger" role="alert">The service already added to your cart.</div>').delay(2000).fadeOut(500);
                } else {
                    alert('An error occurred while adding the service to cart');
                }
            }
        });
    });
    //delete item from to cart
    $(document).on("click", ".delete-cart-item", function(e) {
        const cartId = $(this).attr("id");
        const token = $(this).attr("token");
        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            url: "/service-cart/" + cartId + "/",
            type: "DELETE",
            data: {
                id: cartId
            },
            success: function(response) {
                $("#cart-item-" + cartId).remove();
                $(".total_price").text("₹ " + response.total_price);
                $(".cart-icon span").text(response.total_items);
            },
            error: function(xhr, status, error) {
                // Handle the error case
                console.log(error);
            }
        });
    });


    //place order
    $(document).on("click", ".place-order", function(e) {
        e.preventDefault();
        const roomId = $(this).attr("room_id");
        const token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            type: "POST",
            url: "/service-order/",
            contentType: 'application/json',
            data: JSON.stringify({
                room: roomId,
            }),
            success: function(response) {
                $('.response').empty().show().html('<div class="alert alert-success" role="alert">Your order has been placed.</div>').delay(2000).fadeOut(500);
                $(".cart-icon span").text("0");
                $(".cart").remove();
                $(".total_price").text("₹ 0");
                console.log("Get data", response)
                location.href = "/service_order_status/" + response.room_id + "/" + response.order_id + "/";
            },
            error: function(error) {
                $('.response').empty().show().html('<div class="alert alert-danger">' + error + '</div>').delay(1500).fadeOut(3000);
            }
        });
    });

});