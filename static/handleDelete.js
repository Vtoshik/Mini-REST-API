async function handleDelete(eventOrId, pageId) {
    // Determine if first argument is an event object or pageId
    const isEvent = eventOrId && typeof eventOrId.preventDefault === 'function';
    const event = isEvent ? eventOrId : null;
    const id = isEvent ? pageId : eventOrId;

    if (isEvent) {
        event.preventDefault();
    }

    const { route, alertText } = checkRoute();
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
    const errorDiv = document.getElementById('client-error');
    const errorText = errorDiv ? document.getElementById('client-error-text') : null;

    if (!csrfToken) {
        const errorMessage = 'CSRF token is missing';
        if (errorDiv && errorText) {
            errorText.textContent = errorMessage;
            errorDiv.style.display = 'block';
        } else {
            alert(errorMessage);
        }
        return;
    }

    if (!id) {
        const errorMessage = 'Note ID is missing';
        if (errorDiv && errorText) {
            errorText.textContent = errorMessage;
            errorDiv.style.display = 'block';
        } else {
            alert(errorMessage);
        }
        return;
    }

    try {
        await apiRequest('DELETE', `/api/v1${route}/${id}`, alertText, null, true, csrfToken);
        alert(`${alertText} deleted successfully`);
        loadObjects();
    } catch (error) {
        console.error(`${alertText} delete error:`, error);
        const errorMessage = error.message || `Failed to delete ${alertText}`;
        if (errorDiv && errorText) {
            errorText.textContent = errorMessage;
            errorDiv.style.display = 'block';
        } else {
            alert(errorMessage);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('delete-object')) {
            event.preventDefault();
            const pageId = event.target.getAttribute('data-id');
            if (pageId) {
                handleDelete(event, pageId);
            }
        }
    });
});

// Expose handleDelete globally for onclick attributes
window.handleDelete = handleDelete;