document.addEventListener('DOMContentLoaded', () => {
    async function logout() {
        try {
            const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;
            await apiRequest('POST', '/api/v1/logout', 'logout', null, false, csrfToken);
        } catch (error) {
            console.error('Logout API error:', error);
        }
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_status');
        window.location.href = '/login';
    }

    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('logout-btn')) {
            event.preventDefault();
            logout();
        }
    });
});