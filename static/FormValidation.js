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

        // Username validation (3-20 characters)
        if (username && username.value.trim() === "") {
            errors.push("Username is required");
        } else if (username && (username.value.length < 3 || username.value.length > 20)) {
            errors.push("Username must be 3-20 characters");
        }

        // Email validation
        if (email) {
            if (email.value.trim() === "") {
                errors.push("Email is required");
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
                errors.push("Invalid email format");
            }
        }

        // Password validation (8+ chars, uppercase, lowercase, digit, special character)
        if (password) {
            const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&]{8,}$/;
            if (password.value.trim() === "") {
                errors.push("Password is required");
            } else if (!passwordRegex.test(password.value)) {
                errors.push("Password must be 8+ characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character from @, $, !, %, *, ?, &");
            }
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