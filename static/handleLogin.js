document.addEventListener('DOMContentLoaded', () => {
    async function handleLogin(event) {
        event.preventDefault();

        const username = document.getElementById('username')?.value;
        const password = document.getElementById('password')?.value;
        const errorDiv = document.getElementById('client-error');
        const errorText = document.getElementById('client-error-text')

        if (!username || !password) {
            errorText.textContent = 'Username and password are required';
            errorDiv.style.display = 'block';
            return;
        }

        const data = { username, password };

        try {
            result = await apiRequest('POST', '/api/v1/login', 'login', data, false);
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
            console.error('Fetch error:', error);
            const errorDiv = document.getElementById('client-error');
            const errorText = document.getElementById('client-error-text');
            errorText.textContent = 'An unexpected error occurred. Check console for details.';
            errorDiv.style.display = 'block';
        }
    }

    const form = document.getElementById('login-form');
    if (form) form.onsubmit = handleLogin;
    else console.error('Login form not found');
});