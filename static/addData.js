async function addData(event) {
    event.preventDefault();
    const { route, alertText, data, backroute } = checkRoute('add');
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    const errorDiv = document.getElementById('client-error');
    const errorText = document.getElementById('client-error-text');
    const submitBtn = document.querySelector("button[type='submit']");

    if (!csrfToken) {
        errorText.textContent = 'CSRF token is missing';
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Add ' + alertText;
        return;
    }

    try {
        await apiRequest('POST', `/api/v1${route}`, alertText, data, true, csrfToken);
        alert(`${alertText} created successfully`);
        window.location.href = backroute;
    } catch (error) {
        console.error(`${alertText} creation error:`, error);
        errorText.textContent = error.message || `Failed to create ${alertText}`;
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Add ' + alertText;
    }
}