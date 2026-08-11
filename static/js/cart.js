function changeQuantity(button, amount) {

    const form = button.closest('.quantity-form');

    const input = form.querySelector('.quantity-input');

    let quantity = parseInt(input.value);

    quantity += amount;

    if (quantity < 1) {
        quantity = 1;
    }

    input.value = quantity;

    form.submit();
}