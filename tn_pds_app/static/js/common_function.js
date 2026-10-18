
console.log("JS is working fine!");
document.addEventListener('DOMContentLoaded', function () {

    // 1. ADD TO CART BUTTON (Product Cards)

    document.querySelectorAll('.add-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyBox = document.getElementById(`qty-box-${id}`);
            const qtyVal = document.getElementById(`qty-val-${id}`);
            const addBtn = this;

            fetch(`/add_to_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        addBtn.classList.add('d-none');
                        if (qtyBox) {
                            qtyBox.classList.remove('d-none');
                            qtyBox.classList.add('d-flex');
                        }
                        if (qtyVal) qtyVal.innerText = data.item_qty;
                    } else if (data.status === 'limit_reached') {
                        alert(data.message);
                    }
                })
                .catch(err => console.error("Add Error:", err));
        });
    });

    // 2. PRODUCT CARDS PLUS (+) BUTTON

    document.querySelectorAll('.plus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyVal = document.getElementById(`qty-val-${id}`);

            fetch(`/add_to_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (qtyVal) qtyVal.innerText = data.item_qty;
                    } else if (data.status === 'limit_reached') {
                        alert(data.message || "Allocated Limit reached for this card type!");
                    }
                })
                .catch(err => console.error("Plus Error:", err));
        });
    });

    // 3. PRODUCT CARDS MINUS (-) BUTTON

    document.querySelectorAll('.minus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyBox = document.getElementById(`qty-box-${id}`);
            const qtyVal = document.getElementById(`qty-val-${id}`);
            const parent = this.closest('.cart-action-container');
            const addBtn = parent ? parent.querySelector('.add-btn') : null;

            fetch(`/remove_from_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (data.item_qty > 0) {
                            if (qtyVal) qtyVal.innerText = data.item_qty;
                        } else {
                            if (qtyBox) {
                                qtyBox.classList.add('d-none');
                                qtyBox.classList.remove('d-flex');
                            }
                            if (addBtn) addBtn.classList.remove('d-none');
                        }
                    }
                })
                .catch(err => console.error("Minus Error:", err));
        });
    });

    // 4. CART VIEW PLUS (+) BUTTON - (Auto reload for updated total amount)
    document.querySelectorAll('.cart-plus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');

            fetch(`/add_to_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload(); 
                    } else if (data.status === 'limit_reached') {
                        alert(data.message || "Quota limit reached!");
                    }
                })
                .catch(err => console.error("Cart Increment Error:", err));
        });
    });

    // 5. CART VIEW MINUS (-) BUTTON - (Auto reload for updated total amount)
    document.querySelectorAll('.cart-minus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');

            fetch(`/remove_from_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload(); 
                    }
                })
                .catch(err => console.error("Cart Decrement Error:", err));
        });
    });

 // 6. DJANGO MESSAGES AUTO-DISMISS (Independent & Bulletproof)
(function () {
    setTimeout(function () {
        const alertElements = document.querySelectorAll(".alert, .messages, #alert-messages-box, .message-container, .message-item");

        if (alertElements.length > 0) {
            alertElements.forEach(function (alert) {
                alert.style.transition = "opacity 0.6s ease, transform 0.6s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translateY(-10px)";

                setTimeout(function () {
                    alert.remove();
                }, 600);
            });
        }
    }, 3000);
})();

});

document.addEventListener("DOMContentLoaded", function() {
    // Django generated IDs for password and confirm password fields
    const passwordField = document.getElementById('id_password');
    const confirmPasswordField = document.getElementById('id_confirm_password');

    if (passwordField && confirmPasswordField) {
        function checkPasswordMatch() {
            if (confirmPasswordField.value !== "" && passwordField.value !== confirmPasswordField.value) {
                // Custom error message or border style
                confirmPasswordField.style.borderColor = "red";
                
                // Oruvela error text element already irunthal update panrom, illana create panrom
                let errDiv = document.getElementById('js-password-error');
                if (!errDiv) {
                    errDiv = document.createElement('div');
                    errDiv.id = 'js-password-error';
                    errDiv.className = 'text-danger small mt-1';
                    errDiv.style.fontSize = '0.75rem';
                    confirmPasswordField.parentNode.appendChild(errDiv);
                }
                errDiv.innerHTML = '<i class="fa-solid fa-triangle-exclamation me-1"></i> confirm Passwords do not match with passowrd';
            } else {
                confirmPasswordField.style.borderColor = "#28a745"; // Green border if match
                const errDiv = document.getElementById('js-password-error');
                if (errDiv) {
                    errDiv.remove();
                }
            }
        }

        passwordField.addEventListener('input', checkPasswordMatch);
        confirmPasswordField.addEventListener('input', checkPasswordMatch);
    }
});