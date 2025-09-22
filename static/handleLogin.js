document.addEventListener('DOMContentLoaded', () => {
    async function handleLogin(event) {
        event.preventDefault();

        const username = document.getElementById('username')?.value;
        const password = document.getElementById('password')?.value;
        const errorDiv = document.getElementById('client-error');
        const errorText = document.getElementById('client-error-text');
        const submitBtn = document.querySelector("button[type='submit']");
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;

        if (!username || !password) {
            errorText.textContent = 'Username and password are required';
            errorDiv.style.display = 'block';
            return;
        }

        const data = { username, password };

        try {
            result = await apiRequest('POST', '/api/v1/login', 'login', data, false, csrfToken);
            const objects = result.objects;
            const access_token = objects.access_token;
            const user_id = objects.user_id;
            const user_status= objects.user_status;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('user_id', user_id);
            localStorage.setItem('user_status', user_status);
            const redirectUrl = user_status === 'admin' ? '/admin/' : '/';
            window.location.href = redirectUrl;
        } catch (error) {
            console.error('Login error:', error);
            errorText.textContent = error.message || 'An unexpected error occurred. Check console for details.';
            errorDiv.style.display = 'block';
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Login'; // Reset button
        }
    }

    const form = document.getElementById('login-form');
    if (form) form.onsubmit = handleLogin;
    else console.error('Login form not found');
});