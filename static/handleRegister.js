async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!username || !email || !password) {
        const errorDiv = document.getElementById('client-error');
        const errorText = document.getElementById('client-error-text');
        errorText.textContent = 'All fields are required';
        errorDiv.style.display = 'block';
        return;
    }

    const data = { username, email, password };

    try {
        const response = await fetch('/api/v1/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            window.location.href = '/login';
        } else {
            const error = await response.text();
            const errorDiv = document.getElementById('client-error');
            const errorText = document.getElementById('client-error-text');
            errorText.textContent = `Error: ${error}`;
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Fetch error:', error);
        const errorDiv = document.getElementById('client-error');
        const errorText = document.getElementById('client-error-text');
        errorText.textContent = 'An unexpected error occurred';
        errorDiv.style.display = 'block';
    }
}