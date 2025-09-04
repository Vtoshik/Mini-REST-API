document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (!form) return;

    const errorBox = document.getElementById("client-error");
    const errorText = document.getElementById("client-error-text");
    const submitBtn = form.querySelector("button[type='submit']");

    form.addEventListener("submit", function (event) {
        let errors = [];

        const username = document.getElementById("username");
        const email = document.getElementById("email");
        const password = document.getElementById("password");

        if (username && username.value.trim() === "") {
            errors.push("Username is required");
        }

        if (email) {
            if (email.value.trim() === "") {
                errors.push("Email is required");
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
                errors.push("Invalid email format");
            }
        }

        if (password && password.value.trim().length < 6) {
            errors.push("Password must be at least 6 characters");
        }

        if (errors.length > 0) {
            event.preventDefault();
            errorText.textContent = errors.join(" • ");
            errorBox.style.display = "flex";
            return;
        }

        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = `${originalText} <span class="spinner"></span>`;
    });
});