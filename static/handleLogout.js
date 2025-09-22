document.addEventListener('DOMContentLoaded', () => {
    function logout() {
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