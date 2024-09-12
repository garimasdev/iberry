$(document).ready(function () {
    const cart_badge = $('#cart-badge');
    const floaing_cart = $('#float-cart');
    let cart_items = 0
  
    $('.cart-icon').on('click', function (e) {
      $('.cart-bar').toggleClass('active');
    })
  
    $('.float-cart-btn').on('click', function (e) {
      $('.cart-bar').toggleClass('active');
    })
  
    const roomID = $('#room_ID').val();
    const user = $('#user').val();
    const token = $('csrfmiddlewaretoken').val();
  
    const renderEmptyCart = `
    <div class="d-flex justify-content-center align-items-center w-100 flex-column" id="float-cart-empty">
    <span class="bowl-icon">
      <i class="bx bx-bowl-hot bx-sm"></i>
    </span>
    <p class="m-0">Your cart is empty</p>
  </div>
  
    `
  
    // get cart items
    function fetchCartsByRoomId(roomId) {
      const user_id = localStorage.getItem('user_id')
      // AJAX request
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: `/outdoor-cart/?room_id=${roomID}&user_id=${user_id}`,
        type: 'GET',
        dataType: 'json',
  
        success: function (response) {
          cart_items += response.results[0].quantity
          cart_badge.html(cart_items)
          var total = 0
          var selectedData = []
  
      // // Loop through each checked checkbox input
      // $('.price-input-' + food_id + ':checked').each(function () {
      //   var value = $(this).val()
      //   var price = $(this).attr('price')
      //   var sell_price = $(this).attr('sell_price')
      //   selectedData.push({ id: value, price: price, sell_price: sell_price })
      // })
          for (var obj of response.results) {
            total += obj.price
          $('#add-to-cart-' + obj.id).modal('hide')}
          // const cart_id = obj.id
          // const image = $('.item-' + obj.item)
          //   .find('.image img')
          //   .attr('src')
          // const name = $('.item-' + obj.item)
          //   .find('.product_name').first()
          //   .text()
          // // const price = $(".item-" + food_id).find(".product_price strong").text();
          // $('.cart-bar .cart-list').append(
          //   '<li id="cart-item-' +
          //     obj.id +
          //     '" cart_id="' +
          //     obj.id +
          //     '" class="cart">' +
          //     '<div class="product-box">' +
          //     '<img src="' +
          //     image +
          //     '"/>' +
          //     '<div class="content">' +
          //     '<p class="name">' +
          //     name +
          //     '</p>' +
          //     '<strong class="price">Price: ₹ ' +
          //     obj.price +
          //     // (selectedData[0].sell_price != 'None'
          //     //   ? selectedData[0].sell_price
          //     //   : selectedData[0].price) +
          //     '  </strong>' +
          //     '<span class="quantity"> Qty: ' +
          //     obj.quantity +
          //     '</span>' +
          //     '</div>' +
          //     '</div>' +
          //     '<span class="close delete-cart-item" id="' +
          //     cart_id +
          //     '" token="' +
          //     token +
          //     '"><i class="bi bi-x-lg"></i></span>' +
          //     '</li>'
          // )
          // }
          // $('.total_price').text('₹ ' + total)
          // $('.cart-icon span').text(response.results.length)
  
          // // render  floating cart
          // $('#float-cart-empty').remove()
  
          // if (floaing_cart.children().attr('id') === 'float-cart-filled') {
          //   $('.float-total-price').text('₹ ' + response.total_price)
          //   $('.float-total-items').text(
          //     response.total_items + ' items in your cart'
          //   )
          // } else {
          //   $('#float-cart').append(
          //     `
          //     <div
          //     class="d-flex justify-content-between w-100 align-items-center"
          //     id="float-cart-filled"
          //   >
          //     <img
          //       src="https://b.zmtcdn.com/data/dish_photos/6b2/53c20eaec8cb89832ed50a3d545a56b2.jpg?fit=around|130:130&crop=130:130;*,*"
          //       alt=""
          //     />
          //     <div>
          //       <h2 class="fw-bold title" id="cart">${user}</h2>
          //       <span class="float subtitle float-total-items"> ${response.total_items} items in your cart</span>
          //     </div>
          //     <button class="d-flex btn btn-primary flex-column align-items-center float-cart-btn">
          //       <span class="float-total-price">₹${response.total_price}</span> <span>View Cart</span>
          //     </button>
          //     <button class="btn-close btn btn-light" aria-label="close"></button>
          //   </div>
          //     `
          //   )
  
          //   $('.float-cart-btn').on('click', function (e) {
          //     $('.cart-bar').toggleClass('active')
          //   })
          // }
          // console.log('Carts:', response)
        },
        error: function (error) {
          console.error('Error fetching carts:', error)
        },
      })
    }
  
    fetchCartsByRoomId(roomID)
  
    //add to cart
    $('.add-to-cart').on('click', function (e) {
      e.preventDefault();
      const user_id = localStorage.getItem('user_id')
      const room_id = $(this).attr('room_id')
      const token = $(this).attr('token')
      const food_id = $(this).attr('id')
      const anonymous_user_id = $(this).attr('anonymous_user_id')
      const quantity = $('#quantity-' + food_id).val()
      // const price_id = $("#price-" + food_id).attr('id');
      var selectedData = []
  
      // Loop through each checked checkbox input
      $('.price-input-' + food_id + ':checked').each(function () {
        var value = $(this).val()
        var price = $(this).attr('price')
        var sell_price = $(this).attr('sell_price')
        selectedData.push({ id: value, price: price, sell_price: sell_price })
      })
      // console.log("The prices", selectedData)
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: '/outdoor-cart/',
        type: 'POST',
        data: {
          user: room_id,
          item: food_id,
          price: selectedData[0].id,
          quantity: quantity,
          anonymous_user_id: anonymous_user_id,
          cart_user_id: user_id
        },
        dataType: 'json',
        success: function (response) {
          $('#add-to-cart-' + food_id).modal('hide');
          cart_badge.html(response.total_items);
          
          const cart_id = response.id
          const image = $('.item-' + food_id).find('.image img').attr('src')
          const name = $('.item-' + food_id).find('.product_name').first().text()
          // const price = $(".item-" + food_id).find(".product_price strong").text();
          
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
  
          // render  floating cart
          $('#float-cart-empty').remove()
  
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
            </div>
              `
            );
  
            $('.float-cart-btn').on('click', function (e) {
              $('.cart-bar').toggleClass('active');
            });
          }
        },
        error: function (error) {
          $('#add-to-cart-' + food_id).modal('hide')
          if (error.responseJSON.non_field_errors[0] === 'The fields room, item must make a unique set.') {
            $('.response').empty().show().html('<div class="alert alert-danger" role="alert">The item already added to your cart.</div>').delay(2000).fadeOut(500);
          } else {
            alert('An error occurred while adding the product to cart')
          }
        },
      });
    });
    
    
    // decrease item from cart
    $(document).on('click', '.delete-cart-item', function (e) {
      e.preventDefault(); // Prevent default action
      const cartId = $(this).attr('id')
      const token = $(this).attr('token')
      const user_id  = localStorage.getItem('user_id')
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: '/outdoor-cart/' + cartId + '/?user_id=' + user_id,
        type: 'DELETE',
        data: {
          id: cartId,
        },
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
          
          // update the cart summary
          // overall tax and total items
          $('.items_amount').html('Item Total: <b>₹ ' + response.items_amount + '</b>')
          $('.total_tax').html('Overall Tax: <b>₹ ' + response.total_tax + '</b>')
          // price including tax
          $('.total_price').text('₹ ' + response.total_price)
          $('.cart-icon span').text(response.total_items)
          
          if (response.total_items > 0) {
            //   floating total price
            $('.float-total-price').text('₹ ' + response.total_price)
            $('.float-total-items').text(response.total_items + ' items in your cart')
            } else {
              $('#float-cart-filled').remove()
              // window.location.reload()
              $('#float-cart').append(renderEmptyCart)
          }
        },
        error: function (xhr, status, error) {
          // Handle the error case
          console.log(error)
        },
      })
    });
    
    
    
    // increase item in cart
    $(document).on('click', '.add-cart-item', function (e) {
      e.preventDefault(); // Prevent default action
      const cartId = $(this).attr('id')
      const token = $(this).attr('token')
      const user_id  = localStorage.getItem('user_id')
      
      
      $.ajax({
        headers: {
          'X-CSRFToken': token,
        },
        url: '/outdoor-cart/' + cartId + '/?user_id=' + user_id,
        type: 'PUT',
        data: {
          id: cartId,
        },
        success: function (response) {
          const cartItem = $('#cart-item-' + cartId);
          const quantityElement = cartItem.find('.quantity');
          const currentQuantity = parseInt(quantityElement.text().replace('Qty: ', ''));
  
          // Increase quantity
          quantityElement.text('Qty: ' + (currentQuantity + 1));
          
          // update the cart summary
          // overall tax and total items
          $('.items_amount').html('Item Total: <b>₹ ' + response.items_amount + '</b>');
          $('.total_tax').html('Overall Tax: <b>₹ ' + response.total_tax + '</b>')
          // price including tax
          $('.total_price').text('₹ ' + response.total_price);
          $('.cart-icon span').text(response.total_items);
          
          if (response.total_items > 0) {
            //   floating total price
            $('.float-total-price').text('₹ ' + response.total_price);
            $('.float-total-items').text(response.total_items + ' items in your cart');
            }
        },
        error: function (xhr, status, error) {
          // Handle the error case
          console.log(error)
        },
      })
    });
  
  });
  