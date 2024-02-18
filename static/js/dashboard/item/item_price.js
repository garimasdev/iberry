$(document).ready(function() {
    $(".add-price").click(function() {
        $(document).find(".price-save-btn").removeClass("price-update-btn");
        $('.create-price')[0].reset();
    });
    $(".create-price").submit(function(event) {
        event.preventDefault()
        var formData = $(this).serialize();
        const token = "{{csrf_token}}";
        const is_update = $(document).find(".price-save-btn").hasClass("price-update-btn");
        let id;
        if (is_update) {
            id = $(".price-save-btn").attr("id");
            console.log("Update Price", id);
        } else {
            console.log("Create this");
        }

        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            url: is_update ? '/dashboard/food/price/' + id + '/' : '/dashboard/food/price/',
            method: is_update ? 'PUT' : 'POST',
            data: formData,
            success: function(response) {
                $('.modal').modal('hide');
                if (is_update) {
                    sell_price = response.sell_price == null ? '' : '-' + response.sell_price;
                    $('.price-' + response.id + ' span').text(response.name + '-' + response.price + '' + sell_price);
                    $('.price-update.' + response.id).attr("name", response.name);
                    $('.price-update.' + response.id).attr("price", response.price);
                    $('.price-update.' + response.id).attr("sell_price", response.sell_price);
                } else {
                    sell_price = response.sell_price == null ? '' : '-' + response.sell_price;
                    $('.price-list').append('<li class="price price-' + response.id + '" id="' + response.id + '">' +
                        '<input type="number" name="prices" value="' + response.id + '" hidden>' +
                        '<span>' + response.name + '-' + response.price + '' + sell_price + '</span>' +
                        '<div class="buttons">' +
                        '<button type="button" class="btn btn-outline-secondary price-update ' + response.id + '" id="' + response.id + '" name="' + response.name + '" price="' + response.price + '" sell_price="' + response.sell_price + '"><i class="bi bi-pencil-square"></i></button>' +
                        '<button type="button" class="btn btn-outline-danger price-delete" id="' + response.id + '"><i class="bi bi-x-lg"></i></button>' +
                        '</div></li>');
                }
                console.log("Success Response", response);
            },
            error: function(error) {
                console.error(error); // Handle the error response
            }
        });
    });
    //update price
    // Open modal and populate with data when an item is clicked
    $(document).on("click", ".price-update", function(e) {
        e.preventDefault();
        const id = $(this).attr("id");
        const name = $(this).attr("name");
        const price = $(this).attr("price");
        const sell_price = $(this).attr("sell_price");
        $("#id_name").val(name);
        $("#id_price").val(price);
        $("#id_sell_price").val(sell_price);
        $(".price-save-btn").attr("id", id);
        $(".price-save-btn").addClass("price-update-btn");
        $("#price").modal("show");
    });

    //delete price 
    $(document).on("click", ".price-delete", function(e) {
        e.preventDefault()
        const id = $(this).attr('id');
        const token = "{{csrf_token}}";

        $.ajax({
            headers: {
                "X-CSRFToken": token
            },
            url: '/dashboard/food/price/' + id + '/',
            method: 'DELETE',
            success: function(response) {
                $('.price-' + id).remove();
                console.log("Price has been deleted");
            },
            error: function(error) {
                console.error(error); // Handle the error response
            }
        });
    });
});