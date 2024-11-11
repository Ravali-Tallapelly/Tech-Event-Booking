// Display an alert when a ticket is successfully booked
document.addEventListener("DOMContentLoaded", function() {
    const confirmButton = document.querySelector(".button");
    if (confirmButton) {
        confirmButton.addEventListener("click", function() {
            alert("Ticket successfully booked!");
        });
    }
});
