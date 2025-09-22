async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('username')?.value;
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    const errorDiv = document.getElementById('client-error');
    const errorText = document.getElementById('client-error-text');
    const submitBtn = document.querySelector("button[type='submit']");
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;

    if (!username || !email || !password) {
        errorText.textContent = 'All fields are required';
        errorDiv.style.display = 'block';
        return;
    }

    const data = { username, email, password };

    try {
        result = await apiRequest('POST', '/api/v1/register', 'registration', data, false, csrfToken);
        alert('Registration successful! Please log in.');
        window.location.href = '/login';
    } catch (error) {
        console.error('Registration error:', error);
        errorText.textContent = error.message || 'An unexpected error occurred';
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Register'; // Reset button
    }
}