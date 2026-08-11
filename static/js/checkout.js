document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("checkout-form");

    if (!form) {
        return;
    }


    form.addEventListener("submit", function (event) {

        const depositConfirmed =
            document.getElementById("deposit-confirmed");


        if (!depositConfirmed.checked) {

            event.preventDefault();

            alert(
                "Please confirm that you have transferred the 50% deposit."
            );

            return;
        }

    });

});

