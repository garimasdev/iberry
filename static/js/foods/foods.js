$(document).ready(function () {
    const cart_badge = $('#cart-badge');
    const floaing_cart = $('#float-cart');
  
    $('.cart-icon').on('click', function (e) {
      $('.cart-bar').toggleClass('active');
    });
  
    $('.float-cart-btn').on('click', function (e) {
      $('.cart-bar').toggleClass('active');
    });
  
    const roomID = $('#room_ID').val();
    const user = $('#user').val();
    const token = $('input[name="csrfmiddlewaretoken"]').val();
  
    const renderEmptyCart = `
    <div class="d-flex justify-content-center align-items-center w-100 flex-column" id="float-cart-empty">
      <span class="bowl-icon"><i class="bx bx-bowl-hot bx-sm"></i></span>
      <p class="m-0">Your cart is empty</p>
    </div>
    `;
  
    // Fetch cart items
    function fetchCartsByRoomId(roomId) {
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: `/cart/?room_id=${roomID}`,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
          // Process the response if needed
        },
        error: function (error) {
          console.error('Error fetching carts:', error);
        },
      });
    }
  
    fetchCartsByRoomId(roomID);
  
    // Add to cart
    $('.add-to-cart').on('click', function (e) {
      const room_id = $(this).attr('room_id');
      const token = $(this).attr('token');
      const food_id = $(this).attr('id');
      const quantity = $('#quantity-' + food_id).val();
      var selectedData = [];
  
      // Loop through each checked checkbox input
      $('.price-input-' + food_id + ':checked').each(function () {
        var value = $(this).val();
        var price = $(this).attr('price');
        var sell_price = $(this).attr('sell_price');
        selectedData.push({ id: value, price: price, sell_price: sell_price });
      });
  
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: '/cart/',
        type: 'POST',
        data: {
          room: room_id,
          item: food_id,
          price: selectedData[0].id,
          quantity: quantity,
        },
        dataType: 'json',
        success: function (response) {
          $('#add-to-cart-' + food_id).modal('hide');
          cart_badge.html(response.total_items);
  
          const cart_id = response.id;
          const image = $('.item-' + food_id).find('.image img').attr('src');
          const name = $('.item-' + food_id).find('.product_name').first().text();
          console.log(response);
  
          $('.cart-bar .cart-list').append(
            `<li id="cart-item-${cart_id}" cart_id="${cart_id}" class="cart">
              <div class="product-box" style="width: 80%;">
                <img src="${image}"/>
                <div class="content">
                  <p class="name">${name}</p>
                  <strong class="price">Price: ₹ ${selectedData[0].sell_price != 'None' ? selectedData[0].sell_price : selectedData[0].price}</strong>
                  <span class="quantity"> Qty: ${quantity}</span>
                </div>
              </div>
              <span class="close delete-cart-item" id="${cart_id}" token="${token}">
                <i class="bi bi-dash-lg"></i>
              </span>
              <span class="close add-cart-item" id="${cart_id}" token="${token}">
                <i class="bi bi-plus-lg"></i>
              </span>
            </li>`
          );
  
          // Update the cart summary
          $('.items_amount').html(`Item Total: <b>₹ ${response.items_amount}</b>`);
          $('.total_tax').html(`Overall Tax: <b>₹ ${response.total_tax}</b>`);
          $('.total_price').text(`₹ ${response.total_price}`);
          $('.cart-icon span').text(response.total_items);
  
          // Render floating cart
          $('#float-cart-empty').remove();
          if ($('#float-cart').children().attr('id') === 'float-cart-filled') {
            $('.float-total-price').text(`₹ ${response.total_price}`);
            $('.float-total-items').text(`${response.total_items} items in your cart`);
          } else {
            $('#float-cart').append(`
              <div class="d-flex justify-content-between w-100 align-items-center" id="float-cart-filled">
                <img src="https://b.zmtcdn.com/data/dish_photos/6b2/53c20eaec8cb89832ed50a3d545a56b2.jpg?fit=around|130:130&crop=130:130;*,*" alt=""/>
                <div>
                  <h2 class="fw-bold title" id="cart">${user}</h2>
                  <span class="float subtitle float-total-items"> ${response.total_items} items in your cart</span>
                </div>
                <button class="d-flex btn btn-primary flex-column align-items-center float-cart-btn">
                  <span class="float-total-price">₹${response.total_price}</span> <span>View Cart</span>
                </button>
                <button class="btn-close btn btn-light" aria-label="close"></button>
              </div>`
            );
            $('.float-cart-btn').on('click', function (e) {
              $('.cart-bar').toggleClass('active');
            });
          }
        },
        error: function (error) {
          $('#add-to-cart-' + food_id).modal('hide');
          if (error.responseJSON.non_field_errors[0] === 'The fields room, item must make a unique set.') {
            $('.response').empty().show().html('<div class="alert alert-danger" role="alert">The item is already added to your cart.</div>').delay(2000).fadeOut(500);
          } else {
            alert('An error occurred while adding the product to the cart');
          }
        },
      });
    });
  
    
    // Delete item from cart
    $(document).on('click', '.delete-cart-item', function (e) {
      e.preventDefault(); // Prevent default action
      const cartId = $(this).attr('id');
      const token = $(this).attr('token');
  
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: '/cart/' + cartId + '/',
        type: 'DELETE',
        success: function (response) {
          const cartItem = $('#cart-item-' + cartId);
          const quantityElement = cartItem.find('.quantity');
          const currentQuantity = parseInt(quantityElement.text().replace('Qty: ', ''));
  
          if (currentQuantity > 1) {
            // Decrease quantity
            quantityElement.text('Qty: ' + (currentQuantity - 1));
            // cartItem.find('.price').text('Price: ₹ ' + response.items_amount); // Update price if needed
          } else {
            // Remove item
            cartItem.remove();
          }
  
          // Update the cart summary
          $('.items_amount').html(`Item Total: <b>₹ ${response.items_amount}</b>`);
          $('.total_tax').html(`Overall Tax: <b>₹ ${response.total_tax}</b>`);
          $('.total_price').text(`₹ ${response.total_price}`);
          $('.cart-icon span').text(response.total_items);
  
          if (response.total_items > 0) {
            $('.float-total-price').text(`₹ ${response.total_price}`);
            $('.float-total-items').text(`${response.total_items} items in your cart`);
          } else {
            $('#float-cart-filled').remove();
            $('#float-cart').append(renderEmptyCart);
          }
        },
        error: function (xhr, status, error) {
          console.log(error);
        },
      });
    });
    
    
    // increase item in cart
    $(document).on('click', '.add-cart-item', function (e) {
      e.preventDefault(); // Prevent default action
      const cartId = $(this).attr('id');
      const token = $(this).attr('token');
  
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: '/cart/' + cartId + '/',
        type: 'PUT',
        success: function (response) {
          const cartItem = $('#cart-item-' + cartId);
          const quantityElement = cartItem.find('.quantity');
          const currentQuantity = parseInt(quantityElement.text().replace('Qty: ', ''));
  
          // Increase quantity
          quantityElement.text('Qty: ' + (currentQuantity + 1));
          
  
          // Update the cart summary
          $('.items_amount').html(`Item Total: <b>₹ ${response.items_amount}</b>`);
          $('.total_tax').html(`Overall Tax: <b>₹ ${response.total_tax}</b>`);
          $('.total_price').text(`₹ ${response.total_price}`);
          $('.cart-icon span').text(response.total_items);
  
          if (response.total_items > 0) {
            $('.float-total-price').text(`₹ ${response.total_price}`);
            $('.float-total-items').text(`${response.total_items} items in your cart`);
          }
        },
        error: function (xhr, status, error) {
          console.log(error);
        },
      });
    });
  
    // Place order
    $(document).on('click', '.place-order', function (e) {
      e.preventDefault();
      const roomId = $(this).attr('room_id');
      const token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        type: 'POST',
        url: '/order/',
        contentType: 'application/json',
        data: JSON.stringify({
          room: roomId,
        }),
        success: function (response) {
          $('.response').empty().show().html('<div class="alert alert-success" role="alert">Your order has been placed.</div>').delay(2000).fadeOut(500);
          $('.cart-icon span').text('0');
          $('.cart').remove();
          $('.total_price').text('₹ 0');
          location.href = '/order_status/' + response.room_id + '/' + response.order_id + '/';
        },
        error: function (error) {
          $('.response').empty().show().html('<div class="alert alert-danger">' + error + '</div>').delay(1500).fadeOut(3000);
        },
      });
    });
  });
