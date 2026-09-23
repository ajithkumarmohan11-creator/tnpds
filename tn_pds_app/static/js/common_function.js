document.addEventListener('DOMContentLoaded', function () {

            document.querySelectorAll('.add-btn').forEach(btn => {
            
            btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyBox = document.getElementById(`qty-box-${id}`);
            const qtyVal = document.getElementById(`qty-val-${id}`);
            const addBtn=this;

        fetch(`/add_to_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        addBtn.classList.add('d-none');
                        qtyBox.classList.remove('d-none');
                        qtyBox.classList.add('d-flex');
                        qtyVal.innerText = data.item_qty;
                    }
                })
                .catch(err => console.error("Error:", err));
            });
        });

    document.querySelectorAll('.plus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyVal = document.getElementById(`qty-val-${id}`);
            
            fetch(`/add_to_cart/${id}/`)
                            .then(res => res.json())
                            .then(data => {
                                if (data.status === 'success') {
                                    qtyVal.innerText = data.item_qty;
                                }
                            })
                            .catch(err => console.error("Error:", err));          
            });
        });

    document.querySelectorAll('.minus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyBox = document.getElementById(`qty-box-${id}`);
            const qtyVal = document.getElementById(`qty-val-${id}`);
            const addBtn = this.closest('.cart-action-container').querySelector('.add-btn');

           

            fetch(`/remove_from_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (data.item_qty > 0) {
                            qtyVal.innerText = data.item_qty;
                        } else {
                            qtyBox.classList.add('d-none');
                            qtyBox.classList.remove('d-flex');
                            addBtn.classList.remove('d-none');
                        }
                    }
                })
                .catch(err => console.error("Error:", err));

            });
        });

    });


    document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.cart-plus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyVal = document.getElementById(`cart-qty-val-${id}`);

            fetch(`/add_to_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (qtyVal) qtyVal.innerText = data.item_qty;
                    } else if (data.status === 'limit_reached') {
                    alert(data.message);
                    
                    }
                })
                .catch(err => console.error("Cart Increment Error:", err));
        });
    });

    document.querySelectorAll('.cart-minus-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.getAttribute('data-id');
            const qtyVal = document.getElementById(`cart-qty-val-${id}`);
            const row = document.getElementById(`cart-row-${id}`);

            fetch(`/remove_from_cart/${id}/`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        if (data.item_qty > 0) {
                            if (qtyVal) qtyVal.innerText = data.item_qty;
                        } else {
                            if (row) {
                                row.remove();
                            }
                        }
                    }
                })
                .catch(err => console.error("Cart Decrement Error:", err));
        });
    });

});