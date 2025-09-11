document.addEventListener('DOMContentLoaded', () => {
    async function handleLogin(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            const errorDiv = document.getElementById('client-error');
            const errorText = document.getElementById('client-error-text');
            errorText.textContent = 'Username and password are required';
            errorDiv.style.display = 'block';
            return;
        }

        const data = { username, password };

        try {
            const response = await fetch('/api/v1/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const errorDiv = document.getElementById('client-error');
            const errorText = document.getElementById('client-error-text');
            if (!response.ok) {
                const text = await response.text();
                errorText.textContent = `Error ${response.status}: ${text || 'Unknown error'}`;
                errorDiv.style.display = 'block';
                return;
            }

            const result = await response.json();
            const accessToken = result.access_token;
            const userId = result.user_id;
            const userStatus = result.user_status;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('user_id', userId);
            localStorage.setItem('user_status', userStatus);

            const redirectUrl = userStatus === 'admin' ? '/admin/' : '/';
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