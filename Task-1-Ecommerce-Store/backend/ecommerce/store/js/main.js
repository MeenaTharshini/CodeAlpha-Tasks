// Auto-hide Django messages
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        const alert = document.querySelector(".alert-message");
        if (alert) {
            alert.remove();
        }
    }, 3000);
});
