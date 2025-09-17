async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('client-error');
    const errorText = document.getElementById('client-error-text');

    if (!username || !email || !password) {
        errorText.textContent = 'All fields are required';
        errorDiv.style.display = 'block';
        return;
    }

    const data = { username, email, password };

    try {
        result = await apiRequest('POST', '/api/v1/register', 'registration', data, false);
        window.location.href = '/login';
    } catch (error) {
        console.error('Fetch error:', error);
        const errorDiv = document.getElementById('client-error');
        const errorText = document.getElementById('client-error-text');
        errorText.textContent = 'An unexpected error occurred';
        errorDiv.style.display = 'block';
    }
}