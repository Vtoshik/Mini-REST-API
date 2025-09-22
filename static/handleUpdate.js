async function handleUpdate(event) {
    const pathParts = window.location.pathname.split('/');
    const pageId = pathParts[pathParts.length - 1];
    const { route, alertText, method, updatedData } = checkRoute('update');
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    const errorDiv = document.getElementById('client-error');
    const errorText = document.getElementById('client-error-text');
    const submitBtn = document.querySelector("button.update-btn");

    if (!csrfToken) {
        errorText.textContent = 'CSRF token is missing';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        await apiRequest(method, `/api/v1${route}/${pageId}`, alertText, updatedData, true, csrfToken);
        alert(`${alertText} updated successfully`);
        loadInfo();
    } catch (error) {
        console.error(`${alertText} update error:`, error);
        errorText.textContent = error.message || `Failed to update ${alertText}`;
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Update';
    }
}